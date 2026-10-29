import copy
import math

import pytest

from m3.config import RunConfig
from m3.experimental_variants import (
    CANDIDATES,
    EXPECTED_CELLS,
    assess_candidate,
    compare,
    make_models,
    replay_variants,
)


def trial_matrix():
    trials = []
    for s, n, t in sorted(EXPECTED_CELLS):
        baseline = {"false_positive_rate": 0.1, "recall": 0.9, "f1": 0.9,
                    "precision": 0.9, "roc_auc": 0.9}
        candidate = {**baseline, "false_positive_rate": 0.05, "f1": 0.92}
        trials.append({"scenario": s, "sampling_rate": n, "trial_id": t,
                       "baseline_prediction_mismatches": 0, "max_baseline_score_error": 0.0,
                       "baseline_metrics_reproduced": True,
                       "models": {"current": {"metrics": baseline, "confusion": dict.fromkeys(
                           ("tp", "fp", "tn", "fn"), 1)}, "candidate": {
                               "metrics": candidate, "confusion": dict.fromkeys(
                                   ("tp", "fp", "tn", "fn"), 1)}}})
    return trials


def test_gate_requires_better_values_but_never_deploys_reused_offline_evidence():
    result = assess_candidate(trial_matrix(), "candidate")
    assert result["offline_quality_pass"] is True
    assert result["deployment_ready"] is False
    assert len(result["deployment_blockers"]) == 2


@pytest.mark.parametrize("key,value", [("recall", 0.8), ("f1", 0.8), ("false_positive_rate", 0.2)])
def test_averages_cannot_hide_a_scenario_rate_regression(key, value):
    data = trial_matrix()
    for row in data:
        if row["scenario"] == "drift" and row["sampling_rate"] == 50:
            row["models"]["candidate"]["metrics"][key] = value
    result = assess_candidate(data, "candidate")
    assert result["offline_quality_pass"] is False
    assert any(f"drift/N=50: {key}" in f for f in result["quality_failures"])


def test_n2_recall_regression_is_not_hidden_by_other_repeats():
    data = trial_matrix()
    for row in data:
        if row["sampling_rate"] == 2:
            row["models"]["candidate"]["metrics"]["recall"] = 0.89 if row["trial_id"] == 1 else 0.95
    assert compare([t for t in data if t["sampling_rate"] == 2], "candidate")[
        "changes"]["recall"]["percentage_points"] > 0
    result = assess_candidate(data, "candidate")
    assert result["offline_quality_pass"] is False
    assert any("N=2 recall regression" in f for f in result["quality_failures"])


@pytest.mark.parametrize("mutation", ["missing", "duplicate", "nan", "null", "missing_baseline",
                                     "bad_score", "missing_metric", "out_of_range", "equal"])
def test_quality_gate_fails_closed(mutation):
    data = trial_matrix()
    row = next(t for t in data if t["sampling_rate"] == 2)
    if mutation == "missing":
        data.pop()
    elif mutation == "duplicate":
        data[-1] = copy.deepcopy(data[0])
    elif mutation == "nan":
        row["models"]["candidate"]["metrics"]["f1"] = math.nan
    elif mutation == "null":
        row["max_baseline_score_error"] = None
    elif mutation == "missing_baseline":
        row.pop("baseline_metrics_reproduced")
    elif mutation == "bad_score":
        row["max_baseline_score_error"] = 0.1
    elif mutation == "missing_metric":
        row["models"]["candidate"]["metrics"].pop("f1")
    elif mutation == "out_of_range":
        row["models"]["candidate"]["metrics"]["roc_auc"] = 2
    elif mutation == "equal":
        for t in data:
            t["models"]["candidate"]["metrics"] = dict(t["models"]["current"]["metrics"])
    assert assess_candidate(data, "candidate")["offline_quality_pass"] is False


def test_undefined_precision_is_preserved_not_imputed_or_silently_dropped():
    data = trial_matrix()
    data[0]["models"]["candidate"]["metrics"]["precision"] = None
    summary = compare(data, "candidate")
    assert summary["candidate"]["mean_metrics"]["precision"] is None
    assert summary["candidate"]["metric_coverage"]["precision"] == 53
    assert summary["changes"]["precision"]["percentage_points"] is None
    assert assess_candidate(data, "candidate")["offline_quality_pass"] is False


def test_model_clones_have_only_declared_overrides_and_preserve_seed_and_drift():
    config = RunConfig(mode="live_sflow", seed=44)
    models = make_models(config)
    assert set(models) == {"current", *CANDIDATES}
    for model in models.values():
        assert model.seed == 44
        assert model.drift_detector.delta == config.drift_delta
        assert model.nominal_attributes == ["Proto"]
        assert model.max_size == 100
    assert models["current"].leaf_prediction == "nba"
    assert models["current"].bootstrap_sampling is True
    assert models["current"].grace_period == 200
    assert models["majority_leaf"].leaf_prediction == "mc"
    assert models["no_bootstrap"].bootstrap_sampling is False
    assert models["faster_splits"].grace_period == 50
    assert len({id(model.drift_detector) for model in models.values()}) == 4


@pytest.mark.parametrize('vote, expected', [(None, 'river'), ('log_space', 'log_space')])
def test_archived_variant_replay_resolves_vote_explicitly(monkeypatch, vote, expected):
    import m3.experimental_variants as module

    seen = []

    class FakeModel:
        def predict_proba_one(self, x):
            return {1: 0.0}

        def learn_one(self, x, y):
            pass

    def models(config):
        seen.append(config.naive_bayes)
        return {'current': FakeModel()}

    monkeypatch.setattr(module, 'make_models', models)
    config = {'mode': 'live_sflow'}
    if vote is not None:
        config['naive_bayes'] = vote
    replay_variants(rows()[:2], config)
    assert seen == [expected]


def rows():
    return [{"index": i, "features": {"rate": i % 3, "empty_window": i % 2},
             "y_true": i % 2, "warmup": i < 5, "y_pred": 0, "score": 0,
             "attack_family": "UDPFlood", "sampled_packets": 1,
             "observed_time": i, "label_available_time": i + 0.5} for i in range(25)]


def test_causal_prefix_replay_and_no_mutation():
    data = rows()
    original = copy.deepcopy(data)
    config = {"mode": "live_sflow", "grace_period": 5}
    all_rows = replay_variants(data, config)["predictions"]
    assert replay_variants(data[:10], config)["predictions"] == all_rows[:10]
    changed = copy.deepcopy(data)
    changed[10]["y_true"] = 1 - changed[10]["y_true"]
    alternative = replay_variants(changed, config)["predictions"]
    assert [r["models"] for r in alternative[:11]] == [r["models"] for r in all_rows[:11]]
    assert data == original


def test_learning_waits_for_recorded_availability(monkeypatch):
    import m3.experimental_variants as module

    class FakeModel:
        def __init__(self):
            self.seen = 0

        def predict_proba_one(self, x):
            return {1: float(self.seen > 0)}

        def learn_one(self, x, y):
            self.seen += 1

    monkeypatch.setattr(module, "make_models", lambda config: {"current": FakeModel()})
    data = rows()[:5]
    data[0]["label_available_time"] = 2.5
    for row in data[1:]:
        row["label_available_time"] = 10
    result = replay_variants(data, {"mode": "live_sflow"})["predictions"]
    assert [r["models"]["current"]["predicted"] for r in result] == [0, 0, 0, 1, 1]


def test_report_handles_undefined_precision_and_preserves_training_protocol(tmp_path):
    import importlib.util
    import json
    from pathlib import Path

    path = Path(__file__).resolve().parents[1] / "scripts/compare_detector_variants.py"
    spec = importlib.util.spec_from_file_location("compare_detector_variants", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    data = trial_matrix()
    for i, trial in enumerate(data):
        trial["run_id"] = str(i)
        candidate = trial["models"].pop("candidate")
        trial["models"].update({name: copy.deepcopy(candidate) for name in CANDIDATES})
    data[0]["models"]["majority_leaf"]["metrics"]["precision"] = None
    (tmp_path / "trials.partial.json").write_text(json.dumps(data), encoding="utf-8")
    protocol = {"candidates": CANDIDATES, "caveats": ["Exploratory offline only"]}
    original = json.dumps(protocol).encode()
    (tmp_path / "protocol.json").write_bytes(original)
    module.finish_report(tmp_path, protocol, data, reused_training=True)
    result = json.loads((tmp_path / "comparison.json").read_text(encoding="utf-8"))
    assert result["report_generation"]["reused_training"] is True
    assert result["candidates"]["majority_leaf"]["all_rates"]["candidate"][
        "mean_metrics"]["precision"] is None
    assert (tmp_path / "protocol.json").read_bytes() == original
    assert "unavailable" in (tmp_path / "REPORT.md").read_text(encoding="utf-8")
    assert (tmp_path / "per_trial.csv").exists()
