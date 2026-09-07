"""Stage I — consolidation and audit of the frozen model results.

Read-only with respect to every Stage F/G/H artifact: this module loads
the saved records, re-derives each metric from the saved confusion
matrix, and assembles directly comparable tables. It never recomputes a
model score, never re-selects a threshold, and never writes back to a
source artifact.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

# Canonical model order used by every consolidated table.
MODEL_ORDER = ("RandomForest", "SVM", "CNN_1D")

# Where each model's frozen FPR-constrained result lives. RF's comes from
# the authorised secondary evaluation, not its original threshold-0.30 run.
SOURCES: dict[str, dict[str, str]] = {
    "RandomForest": {
        "record": "random_forest/rf_fpr_constrained_record.json",
        "test_metrics_key": "test_metrics_fpr_constrained",
        "budgets": "random_forest/validation_fpr_budgets.csv",
        "per_attack": "random_forest/per_attack_type_fpr_constrained.csv",
        # The secondary record reuses the Stage F forest and so carries no
        # training time or forest structure; those belong to the original
        # Stage F run of the same model and are read (read-only) from there.
        "cost_record": "random_forest/rf_run_record.json",
    },
    "SVM": {
        "record": "svm/svm_run_record.json",
        "test_metrics_key": "test_metrics",
        "budgets": "svm/validation_fpr_budgets.csv",
        "per_attack": "svm/per_attack_type.csv",
    },
    "CNN_1D": {
        "record": "cnn/cnn_run_record.json",
        "test_metrics_key": "test_metrics",
        "budgets": "cnn/validation_fpr_budgets.csv",
        "per_attack": "cnn/per_attack_type.csv",
    },
}

ATTACK_TYPES = (
    "HTTPFlood", "ICMPFlood", "SYNFlood", "SYNScan",
    "TCPConnectScan", "SlowrateDoS", "UDPScan", "UDPFlood",
)

# Tolerance for "recomputed == stored". The stored values came from
# sklearn on the same integer counts, so agreement should be near exact;
# anything above this is a genuine inconsistency, not rounding.
METRIC_TOLERANCE = 1e-9


class ArtifactError(Exception):
    """Raised when a required result artifact is missing or malformed."""


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ArtifactError(f"required artifact not found: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ArtifactError(f"artifact is not valid JSON: {path} ({exc})") from exc


def verify_metric_consistency(metrics: dict[str, Any]) -> list[dict[str, Any]]:
    """Re-derive every rate metric from TP/TN/FP/FN and compare.

    Returns one row per metric with the stored value, the recomputed
    value and the absolute deviation. Nothing is corrected here.
    """
    for key in ("TP", "TN", "FP", "FN"):
        if key not in metrics:
            raise ArtifactError(f"confusion count '{key}' missing from metrics")

    tp, tn = float(metrics["TP"]), float(metrics["TN"])
    fp, fn = float(metrics["FP"]), float(metrics["FN"])
    total = tp + tn + fp + fn

    def div(num: float, den: float) -> float:
        return num / den if den else 0.0

    precision = div(tp, tp + fp)
    recall = div(tp, tp + fn)
    recomputed = {
        "accuracy": div(tp + tn, total),
        "precision": precision,
        "recall": recall,
        "f1": div(2 * precision * recall, precision + recall),
        "fpr": div(fp, fp + tn),
        "tnr": div(tn, tn + fp),
    }

    rows = []
    for name, value in recomputed.items():
        stored = metrics.get(name)
        deviation = None if stored is None else abs(float(stored) - value)
        rows.append({
            "metric": name,
            "stored": stored,
            "recomputed": value,
            "abs_deviation": deviation,
            "consistent": bool(deviation is not None
                               and deviation <= METRIC_TOLERANCE),
        })
    # N is a count, checked separately
    rows.append({
        "metric": "n",
        "stored": metrics.get("n"),
        "recomputed": int(total),
        "abs_deviation": (None if metrics.get("n") is None
                          else abs(int(metrics["n"]) - int(total))),
        "consistent": metrics.get("n") == int(total),
    })
    return rows


def load_model_results(results_root: Path) -> dict[str, dict[str, Any]]:
    """Load the three frozen FPR-constrained results from disk."""
    results_root = Path(results_root)
    loaded: dict[str, dict[str, Any]] = {}
    for model in MODEL_ORDER:
        source = SOURCES[model]
        record = _read_json(results_root / source["record"])
        key = source["test_metrics_key"]
        if key not in record:
            raise ArtifactError(
                f"{model}: '{key}' missing from {source['record']}")
        # optional supplementary record holding cost/structure fields
        cost_record = record
        cost_path = source.get("cost_record")
        if cost_path:
            candidate = results_root / cost_path
            if candidate.is_file():
                cost_record = _read_json(candidate)

        loaded[model] = {
            "record": record,
            "cost_record": cost_record,
            "test_metrics": record[key],
            "operating_point": record.get("operating_point", {}),
        }
    return loaded


def _model_cost(model: str, record: dict[str, Any]) -> dict[str, Any]:
    """Training time and a model-appropriate size measure."""
    timings = record.get("timings_seconds") or {}
    if model == "RandomForest":
        structure = record.get("forest_structure") or {}
        size = structure.get("total_nodes")
        size_kind = "tree nodes"
        # the secondary RF record carries no timing block; training time
        # belongs to the Stage F fit that produced the reused model
        train = timings.get("train")
    elif model == "SVM":
        structure = record.get("model_structure") or {}
        components = structure.get("n_components")
        size = None if components is None else int(components) + 1
        size_kind = "linear weights (+bias)"
        train = timings.get("train")
    else:
        structure = record.get("model_structure") or {}
        size = structure.get("total_parameters")
        size_kind = "trainable parameters"
        train = timings.get("train")
    return {"train_seconds": train, "model_size": size, "size_kind": size_kind}


def build_summary_table(loaded: dict[str, dict[str, Any]]) -> pd.DataFrame:
    """Canonical three-model table at the frozen FPR <= 1% operating point."""
    rows = []
    for model in MODEL_ORDER:
        entry = loaded[model]
        record, test = entry["record"], entry["test_metrics"]
        operating = entry["operating_point"]
        validation = (record.get("validation_metrics_at_frozen_threshold")
                      or {})
        cost = _model_cost(model, entry.get("cost_record", record))
        rows.append({
            "model": model,
            "operating_point": "validation FPR <= 1%",
            "threshold": operating.get("threshold"),
            "val_recall": operating.get("recall"),
            "val_fpr": operating.get("fpr"),
            "val_precision": validation.get("precision"),
            "test_accuracy": test["accuracy"],
            "test_precision": test["precision"],
            "test_recall": test["recall"],
            "test_f1": test["f1"],
            "test_fpr": test["fpr"],
            "test_specificity": test["tnr"],
            "roc_auc": test.get("roc_auc"),
            "pr_auc": test.get("pr_auc"),
            # amortised batch throughput, NOT single-flow latency
            "batch_throughput_ms_per_flow": test.get("per_flow_inference_ms"),
            "train_seconds": cost["train_seconds"],
            "model_size": cost["model_size"],
            "model_size_kind": cost["size_kind"],
        })
    return pd.DataFrame(rows)


def build_confusion_table(loaded: dict[str, dict[str, Any]]) -> pd.DataFrame:
    """TN/FP/FN/TP per model, with the totals they must reconcile to."""
    rows = []
    for model in MODEL_ORDER:
        test = loaded[model]["test_metrics"]
        tn, fp = int(test["TN"]), int(test["FP"])
        fn, tp = int(test["FN"]), int(test["TP"])
        rows.append({
            "model": model,
            "TN": tn, "FP": fp, "FN": fn, "TP": tp,
            "n": tn + fp + fn + tp,
            "actual_benign": tn + fp,
            "actual_malicious": tp + fn,
            "predicted_malicious": tp + fp,
        })
    return pd.DataFrame(rows)


def build_fpr_budget_table(
    loaded: dict[str, dict[str, Any]], results_root: Path
) -> pd.DataFrame:
    """Validation recall at each alarm budget, for all three models."""
    frames = []
    for model in MODEL_ORDER:
        path = Path(results_root) / SOURCES[model]["budgets"]
        if not path.is_file():
            raise ArtifactError(f"required artifact not found: {path}")
        frame = pd.read_csv(path)
        frame.insert(0, "model", model)
        # a discrete score distribution makes several budgets share one
        # threshold; flag it rather than hiding it
        frame["budgets_collapsed"] = frame["threshold"].nunique() == 1
        frames.append(frame)
    return pd.concat(frames, ignore_index=True)


def build_per_attack_table(
    loaded: dict[str, dict[str, Any]], results_root: Path
) -> pd.DataFrame:
    """Per-attack-type recall for all three models, side by side."""
    collected = {}
    benign = {}
    for model in MODEL_ORDER:
        path = Path(results_root) / SOURCES[model]["per_attack"]
        if not path.is_file():
            raise ArtifactError(f"required artifact not found: {path}")
        frame = pd.read_csv(path).set_index("group")
        collected[model] = frame["recall"]
        if "Benign" in frame.index:
            benign[model] = frame.loc["Benign", "fpr"]

    rows = []
    for attack in ATTACK_TYPES:
        row: dict[str, Any] = {"group": attack, "metric": "recall"}
        for model in MODEL_ORDER:
            series = collected[model]
            row[model] = (float(series.loc[attack])
                          if attack in series.index else None)
        support = None
        for model in MODEL_ORDER:
            path = Path(results_root) / SOURCES[model]["per_attack"]
            frame = pd.read_csv(path).set_index("group")
            if attack in frame.index:
                support = int(frame.loc[attack, "support"])
                break
        row["support"] = support
        rows.append(row)

    benign_row: dict[str, Any] = {"group": "Benign", "metric": "fpr"}
    for model in MODEL_ORDER:
        benign_row[model] = float(benign[model]) if model in benign else None
    benign_row["support"] = None
    rows.append(benign_row)
    return pd.DataFrame(rows)
