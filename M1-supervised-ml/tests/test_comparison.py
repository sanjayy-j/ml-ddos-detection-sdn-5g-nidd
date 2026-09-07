"""Stage K tests — comparison fact gathering and claim checking.

The claim checker is the meaningful protection here: it prevents an
unsupported conclusion from reaching the report artifact.
"""

import json
from pathlib import Path

import pandas as pd
import pytest

from evaluation.comparison import (
    FORBIDDEN_CLAIMS,
    REQUIRED_HEDGES,
    ComparisonDataError,
    best_by,
    check_claims,
    gather_comparison_facts,
)
from evaluation.plots import ATTACK_ORDER, MODEL_ORDER

RESULTS = Path(__file__).resolve().parents[1] / "results"


# --- claim checking ---------------------------------------------------------

@pytest.mark.parametrize("claim", [
    "RF is universally the best model here",
    "the CNN is more robust to noise",
    "the SVM generalises better to new traffic",
    "the SVM generalizes better to new traffic",
    "the three families are practically equivalent",
    "this proves real-world deployment performance",
    "real-world deployment performance is demonstrated",
])
def test_forbidden_claims_are_detected(claim):
    found = check_claims(claim)["forbidden_claims_found"]
    assert found, f"claim not caught: {claim}"


def test_hedged_text_passes_the_claim_check():
    text = (
        "Under the current feature representation and under the common "
        "operating-point protocol the models show broadly similar "
        "discrimination. This comparison does not establish unseen-session "
        "generalisation."
    )
    result = check_claims(text)
    assert result["forbidden_claims_found"] == []
    assert result["missing_hedges"] == []


def test_missing_hedges_are_reported():
    result = check_claims("Random Forest scored highest on F1.")
    assert set(result["missing_hedges"]) == set(REQUIRED_HEDGES)


def test_claim_check_is_case_insensitive():
    assert check_claims("PRACTICALLY EQUIVALENT")["forbidden_claims_found"]


def test_forbidden_and_required_lists_are_populated():
    assert len(FORBIDDEN_CLAIMS) >= 7
    assert "under the current feature representation" in REQUIRED_HEDGES


# --- the generated artifact -------------------------------------------------

@pytest.mark.skipif(not (RESULTS / "evaluation" / "model_comparison.md").is_file(),
                    reason="comparison artifact not generated")
def test_generated_comparison_contains_no_forbidden_claims():
    text = (RESULTS / "evaluation" / "model_comparison.md").read_text(
        encoding="utf-8")
    result = check_claims(text)
    assert result["forbidden_claims_found"] == []
    assert result["missing_hedges"] == []


@pytest.mark.skipif(not (RESULTS / "evaluation" / "model_comparison.md").is_file(),
                    reason="comparison artifact not generated")
def test_generated_comparison_matches_canonical_summary():
    """Every headline number must equal the Stage I artifact."""
    text = (RESULTS / "evaluation" / "model_comparison.md").read_text(
        encoding="utf-8")
    summary = pd.read_csv(
        RESULTS / "evaluation" / "three_model_fpr1pct_summary.csv"
    ).set_index("model")
    for model in MODEL_ORDER:
        for column in ("test_accuracy", "test_precision", "test_recall",
                       "test_f1", "test_fpr", "test_specificity",
                       "roc_auc", "pr_auc"):
            assert f"{float(summary.loc[model, column]):.6f}" in text, (
                f"{model}.{column} not present in the comparison")


@pytest.mark.skipif(not (RESULTS / "evaluation" / "model_comparison.md").is_file(),
                    reason="comparison artifact not generated")
def test_generated_comparison_states_scope_and_timing_caveats():
    text = (RESULTS / "evaluation" / "model_comparison.md").read_text(
        encoding="utf-8").lower()
    for phrase in ("within-capture", "not single-flow latency",
                   "unseen-capture generalisation",
                   "analysis metadata", "empirical ceiling"):
        assert phrase in text, f"missing required statement: {phrase}"


# --- fact gathering ---------------------------------------------------------

@pytest.fixture
def results_root(tmp_path):
    ev = tmp_path / "evaluation"
    ev.mkdir(parents=True)
    pd.DataFrame({
        "model": list(MODEL_ORDER),
        "threshold": [0.478734, -0.062874, 0.471731],
        "val_recall": [0.534044, 0.535083, 0.531380],
        "val_fpr": [0.000754, 0.009992, 0.000181],
        "test_accuracy": [0.655771, 0.653874, 0.650985],
        "test_precision": [0.988566, 0.982406, 0.997443],
        "test_recall": [0.438040, 0.437687, 0.426182],
        "test_f1": [0.607079, 0.605575, 0.597197],
        "test_fpr": [0.007828, 0.012111, 0.001688],
        "test_specificity": [0.992172, 0.987889, 0.998312],
        "roc_auc": [0.852824, 0.850177, 0.850978],
        "pr_auc": [0.867387, 0.879445, 0.864283],
        "batch_throughput_ms_per_flow": [0.001703, 0.006808, 0.003808],
        "train_seconds": [31.11, 3093.58, 159.63],
        "model_size": [172630, 513, 10561],
        "model_size_kind": ["tree nodes", "linear weights", "parameters"],
    }).to_csv(ev / "three_model_fpr1pct_summary.csv", index=False)

    rows = []
    for model in MODEL_ORDER:
        for cap in (0.001, 0.01, 0.05, 0.1):
            rows.append({"model": model, "max_fpr": cap, "threshold": 0.5,
                         "recall": 0.53, "fpr": cap / 10})
    pd.DataFrame(rows).to_csv(ev / "three_model_fpr_budget.csv", index=False)

    attack_rows = [{"group": a, "metric": "recall", "support": 100,
                    **{m: 0.99 for m in MODEL_ORDER}} for a in ATTACK_ORDER]
    attack_rows.append({"group": "Benign", "metric": "fpr", "support": 71670,
                        **{m: 0.005 for m in MODEL_ORDER}})
    pd.DataFrame(attack_rows).to_csv(ev / "three_model_per_attack_type.csv",
                                     index=False)
    pd.DataFrame({
        "model": list(MODEL_ORDER), "TN": [71109, 70802, 71549],
        "FP": [561, 868, 121], "FN": [62227, 62266, 63540],
        "TP": [48505, 48466, 47192], "n": [182402] * 3,
    }).to_csv(ev / "three_model_confusion_matrices.csv", index=False)

    (tmp_path / "preprocessing_metadata.json").write_text(json.dumps({
        "n_output_features": 67,
        "splits": {"train": {"rows": 851106}, "val": {"rows": 182382},
                   "test": {"rows": 182402}},
        "duplicates": {"n_rows": 1215890, "n_unique_feature_vectors": 345621,
                       "n_ambiguous_groups": 33709, "bayes_error_rows": 281533,
                       "max_achievable_accuracy_pct": 76.8455,
                       "rows_whose_vector_appears_in_another_split": 686830},
    }), encoding="utf-8")
    return tmp_path


def test_gather_returns_all_required_facts(results_root):
    facts = gather_comparison_facts(results_root)
    assert list(facts["models"]) == list(MODEL_ORDER)
    assert set(facts["attacks"]) == set(ATTACK_ORDER)
    assert sorted(facts["budgets"]) == [0.001, 0.01, 0.05, 0.1]
    rep = facts["representation"]
    assert rep["n_output_features"] == 67
    assert rep["n_conflicting_vectors"] == 33709
    assert rep["forced_errors"] == 281533
    assert rep["overall_ceiling_pct"] == pytest.approx(76.8455)


def test_gather_confusion_reconciles(results_root):
    facts = gather_comparison_facts(results_root)
    for model in MODEL_ORDER:
        m = facts["models"][model]
        assert m["TN"] + m["FP"] + m["FN"] + m["TP"] == m["n"] == 182402


def test_best_by_identifies_leaders(results_root):
    facts = gather_comparison_facts(results_root)
    assert best_by(facts, "accuracy") == "RandomForest"
    assert best_by(facts, "recall") == "RandomForest"
    assert best_by(facts, "f1") == "RandomForest"
    assert best_by(facts, "precision") == "CNN_1D"
    assert best_by(facts, "fpr", maximise=False) == "CNN_1D"
    assert best_by(facts, "pr_auc") == "SVM"


def test_best_by_rejects_unknown_metric(results_root):
    with pytest.raises(ComparisonDataError, match="unknown metric"):
        best_by(gather_comparison_facts(results_root), "nonexistent")


def test_missing_artifact_raises(tmp_path):
    with pytest.raises(ComparisonDataError, match="not found"):
        gather_comparison_facts(tmp_path)


def test_summary_missing_model_raises(results_root):
    path = results_root / "evaluation" / "three_model_fpr1pct_summary.csv"
    frame = pd.read_csv(path)
    frame[frame["model"] != "SVM"].to_csv(path, index=False)
    with pytest.raises(ComparisonDataError, match="missing models"):
        gather_comparison_facts(results_root)


def test_missing_attack_type_raises(results_root):
    path = results_root / "evaluation" / "three_model_per_attack_type.csv"
    frame = pd.read_csv(path)
    frame[frame["group"] != "UDPFlood"].to_csv(path, index=False)
    with pytest.raises(ComparisonDataError, match="UDPFlood"):
        gather_comparison_facts(results_root)
