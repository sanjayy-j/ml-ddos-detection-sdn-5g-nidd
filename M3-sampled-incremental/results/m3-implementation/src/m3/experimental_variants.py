"""Isolated detector variants and fail-closed baseline quality checks.

Nothing in this module changes OnlineDetector or the live feature schema.
The fixed candidates each change ONE HAT setting, without threshold tuning.
"""

import heapq
import math
from statistics import mean

from m3.config import RunConfig
from m3.metrics import QualityMetrics
from m3.model import OnlineDetector
from m3.naive_bayes import likelihood

CANDIDATES = {
    "majority_leaf": {"leaf_prediction": "mc"},
    "no_bootstrap": {"bootstrap_sampling": False},
    "faster_splits": {"grace_period": 50},
}
METRICS = ("false_positive_rate", "recall", "f1", "precision", "roc_auc")
EXPECTED_CELLS = {(s, n, t) for s in ("baseline", "drift", "unseen")
                  for n in (1, 2, 5, 10, 20, 50) for t in (1, 2, 3)}


def make_models(config):
    """Clone the exact baseline configuration, overriding only the named setting."""
    baseline = OnlineDetector(config).model
    return {"current": baseline, **{name: baseline.clone(overrides)
                                   for name, overrides in CANDIDATES.items()}}


def replay_variants(rows, config):
    """Same telemetry/order/labels for every model; learn only available labels."""
    config = RunConfig(**{**config, "naive_bayes": config.get("naive_bayes", "river")})
    models = make_models(config)
    quality = {name: QualityMetrics() for name in models}
    predictions, pending = [], []
    last_time = -math.inf
    seen_scored = False
    mismatches, score_error = 0, 0.0
    for index, row in enumerate(rows):
        observed, available = float(row["observed_time"]), float(row["label_available_time"])
        if not math.isfinite(observed) or observed < last_time:
            raise ValueError("Completion times must be finite and chronological")
        if not math.isfinite(available) or available < observed:
            raise ValueError("Label availability must follow prediction")
        last_time = observed
        warm = row["warmup"]
        if type(warm) is not bool or (warm and seen_scored):
            raise ValueError("Explicit warm-up must be a chronological prefix")
        seen_scored |= not warm
        x = dict(row["features"])
        if not x or any(not math.isfinite(float(v)) for v in x.values()):
            raise ValueError("Every observation needs finite numeric recorded features")
        label = row["y_true"]
        if label is not None and (type(label) is not int or label not in (0, 1)):
            raise ValueError("Labels must be binary integers or null")
        while pending and pending[0][0] <= observed:
            _, _, old_x, old_label = heapq.heappop(pending)
            for model in models.values():
                with likelihood(config.naive_bayes):
                    model.learn_one(old_x, old_label)
        scored = label is not None and not warm
        output = {"index": row["index"], "label": label, "scored": scored,
                  "sampled_packets": row["sampled_packets"], "models": {}}
        for name, model in models.items():
            with likelihood(config.naive_bayes):
                score = float(model.predict_proba_one(x).get(1, 0.0))
            if not math.isfinite(score) or not 0 <= score <= 1:
                raise ValueError("Invalid model probability")
            predicted = int(score >= config.threshold)
            output["models"][name] = {"predicted": predicted, "score": score}
            if scored:
                quality[name].update(label, predicted, score, 0, row["attack_family"])
                if name == "current":
                    mismatches += predicted != row["y_pred"]
                    score_error = max(score_error, abs(score - row["score"]))
        predictions.append(output)
        if label is not None:
            heapq.heappush(pending, (available, index, x, label))
    return {"models": {name: {
        "metrics": {k: v["value"] for k, v in metric.summary(
            unseen_enabled=config.scenario == "unseen").items()
                    if not k.startswith("inference_latency")},
        "confusion": {"tp": metric.confusion[(1, 1)], "fp": metric.confusion[(0, 1)],
                      "tn": metric.confusion[(0, 0)], "fn": metric.confusion[(1, 0)]},
    } for name, metric in quality.items()}, "baseline_prediction_mismatches": mismatches,
        "max_baseline_score_error": score_error, "predictions": predictions}


def summarize(trials, name):
    """Arithmetic mean per-trial quality, explicitly separate from pooled counts."""
    if not trials:
        raise ValueError("No trials to summarize")
    values = {key: [t["models"][name]["metrics"].get(key) for t in trials] for key in METRICS}
    if any(v is not None and (not isinstance(v, (int, float)) or isinstance(v, bool)
           or not math.isfinite(v) or not 0 <= v <= 1)
           for group in values.values() for v in group):
        raise ValueError("Quality evidence is invalid or nonfinite")
    return {"trials": len(trials), "mean_metrics": {
        k: mean(v) if all(x is not None for x in v) else None for k, v in values.items()},
            "metric_coverage": {k: sum(x is not None for x in v) for k, v in values.items()},
            "pooled_confusion": {k: sum(t["models"][name]["confusion"][k] for t in trials)
                                 for k in ("tp", "fp", "tn", "fn")}}


def compare(trials, name):
    baseline, candidate = summarize(trials, "current"), summarize(trials, name)
    changes = {}
    for key in METRICS:
        a, b = baseline["mean_metrics"][key], candidate["mean_metrics"][key]
        changes[key] = {"percentage_points": 100 * (b - a)
                       if a is not None and b is not None else None,
                        "relative_percent": 100 * (b - a) / a
                        if a and b is not None else None}
    return {"current": baseline, "candidate": candidate, "changes": changes}


def assess_candidate(trials, name):
    """No deployment from reused offline traces, even if all quality gates pass.

    Quality gate: N=2 FPR and F1 strictly improve; N=2 recall never decreases
    in any repeat; no primary metric regresses in ANY scenario/rate mean.
    Precision and ROC-AUC must not regress at N=2. Missing/invalid evidence fails.
    """
    failures = []
    cells = [(t.get("scenario"), t.get("sampling_rate"), t.get("trial_id")) for t in trials]
    if len(cells) != 54 or set(cells) != EXPECTED_CELLS:
        failures.append("Incomplete or duplicated 54-trial matrix")
    def baseline_verified(trial):
        error = trial.get("max_baseline_score_error")
        return (trial.get("baseline_prediction_mismatches") == 0
                and isinstance(error, (int, float)) and math.isfinite(error) and error <= 1e-10
                and error >= 0 and trial.get("baseline_metrics_reproduced") is True)

    if not all(baseline_verified(t) for t in trials):
        failures.append("Baseline reproduction not verified for every trial")
    try:
        n2 = [t for t in trials if t["sampling_rate"] == 2]
        pair = compare(n2, name)
        for key in ("false_positive_rate", "f1"):
            delta = pair["changes"][key]["percentage_points"]
            if (key == "false_positive_rate" and delta >= -1e-10) or (
                    key == "f1" and delta <= 1e-10):
                failures.append(f"N=2 {key} did not strictly improve")
        for trial in n2:
            if trial["models"][name]["metrics"]["recall"] < trial["models"][
                    "current"]["metrics"]["recall"] - 1e-12:
                failures.append(f"N=2 recall regression: {trial['scenario']}/{trial['trial_id']}")
        for key in ("precision", "roc_auc"):
            if pair["changes"][key]["percentage_points"] < -1e-10:
                failures.append(f"N=2 {key} regressed")
        for scenario, rate in sorted({(s, n) for s, n, _ in EXPECTED_CELLS}):
            group = [t for t in trials if t["scenario"] == scenario and t["sampling_rate"] == rate]
            if any(v is None for v in summarize(group, name)["mean_metrics"].values()):
                failures.append(f"{scenario}/N={rate}: required quality metric unavailable")
            delta = compare(group, name)["changes"]
            for key in ("false_positive_rate", "recall", "f1"):
                bad = delta[key]["percentage_points"] > 1e-10 if key == "false_positive_rate" else (
                    delta[key]["percentage_points"] < -1e-10)
                if bad:
                    failures.append(f"{scenario}/N={rate}: {key} regressed")
    except (KeyError, ValueError, TypeError):
        failures.append("Required quality evidence missing or invalid")
    return {"offline_quality_pass": not failures, "quality_failures": failures,
            "deployment_ready": False,
            "deployment_blockers": ["No independent fresh-data confirmation",
                                    "No paired live candidate latency/resource measurements"],
            "action": "Keep current default; this experiment never modifies production settings"}
