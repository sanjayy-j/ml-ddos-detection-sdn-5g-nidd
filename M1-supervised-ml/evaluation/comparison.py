"""Stage K — fact gathering and claim checking for the final comparison.

Every number in the generated comparison is read from the canonical
Stage D/I artifacts at generation time; nothing is hard-coded. This
module also enforces the Stage K wording rules, so an unsupported claim
cannot silently reach the report artifact.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pandas as pd

from evaluation.plots import ATTACK_ORDER, MODEL_LABELS, MODEL_ORDER

# Claims the Stage K brief explicitly forbids. Matched case-insensitively
# against the generated markdown.
FORBIDDEN_CLAIMS = (
    r"universally the best",
    r"\bbest model\b",
    r"more robust",
    r"generali[sz]es better",
    r"practically equivalent",
    r"proves? real-world",
    r"real-world deployment performance",
    r"unseen[- ](?:session|capture|attack)s? generali[sz]ation is (?:demonstrated|established|shown)",
    r"theoretical (?:ceiling|maximum) for (?:any|every) model",
)

# Hedged phrasing the comparison is expected to carry.
REQUIRED_HEDGES = (
    "under the current feature representation",
    "under the common operating-point protocol",
    "broadly similar discrimination",
    "does not establish unseen-session generalisation",
)


class ComparisonDataError(Exception):
    """Raised when a required comparison input is missing or malformed."""


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ComparisonDataError(f"required artifact not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.is_file():
        raise ComparisonDataError(f"required artifact not found: {path}")
    frame = pd.read_csv(path)
    if frame.empty:
        raise ComparisonDataError(f"artifact is empty: {path}")
    return frame


def gather_comparison_facts(results_root: Path) -> dict[str, Any]:
    """Read every fact the comparison needs from canonical artifacts."""
    results_root = Path(results_root)
    ev = results_root / "evaluation"

    summary = _read_csv(ev / "three_model_fpr1pct_summary.csv")
    budgets = _read_csv(ev / "three_model_fpr_budget.csv")
    per_attack = _read_csv(ev / "three_model_per_attack_type.csv")
    confusion = _read_csv(ev / "three_model_confusion_matrices.csv")
    preprocessing = _read_json(results_root / "preprocessing_metadata.json")

    missing = set(MODEL_ORDER) - set(summary["model"])
    if missing:
        raise ComparisonDataError(f"summary missing models: {sorted(missing)}")

    summary = summary.set_index("model")
    confusion = confusion.set_index("model")
    attack = per_attack.set_index("group")
    duplicates = preprocessing["duplicates"]

    models: dict[str, dict[str, Any]] = {}
    for model in MODEL_ORDER:
        row = summary.loc[model]
        conf = confusion.loc[model]
        models[model] = {
            "label": MODEL_LABELS[model],
            "threshold": float(row["threshold"]),
            "val_recall": float(row["val_recall"]),
            "val_fpr": float(row["val_fpr"]),
            "accuracy": float(row["test_accuracy"]),
            "precision": float(row["test_precision"]),
            "recall": float(row["test_recall"]),
            "f1": float(row["test_f1"]),
            "fpr": float(row["test_fpr"]),
            "specificity": float(row["test_specificity"]),
            "roc_auc": float(row["roc_auc"]),
            "pr_auc": float(row["pr_auc"]),
            "throughput_ms_per_flow": float(row["batch_throughput_ms_per_flow"]),
            "train_seconds": float(row["train_seconds"]),
            "model_size": int(row["model_size"]),
            "model_size_kind": str(row["model_size_kind"]),
            "TN": int(conf["TN"]), "FP": int(conf["FP"]),
            "FN": int(conf["FN"]), "TP": int(conf["TP"]),
            "n": int(conf["n"]),
        }

    budget_table: dict[float, dict[str, float]] = {}
    for cap in sorted(budgets["max_fpr"].unique()):
        sub = budgets[budgets["max_fpr"] == cap].set_index("model")
        budget_table[float(cap)] = {
            m: float(sub.loc[m, "recall"]) for m in MODEL_ORDER
        }
    collapsed = {
        m: bool(budgets[budgets["model"] == m]["threshold"].nunique() == 1)
        for m in MODEL_ORDER
    }

    attacks: dict[str, dict[str, Any]] = {}
    for name in ATTACK_ORDER:
        if name not in attack.index:
            raise ComparisonDataError(f"per-attack table missing: {name}")
        row = attack.loc[name]
        attacks[name] = {
            "support": int(row["support"]),
            **{m: float(row[m]) for m in MODEL_ORDER},
        }

    return {
        "models": models,
        "budgets": budget_table,
        "budgets_collapsed": collapsed,
        "attacks": attacks,
        "benign_fpr": {m: float(attack.loc["Benign", m]) for m in MODEL_ORDER},
        "representation": {
            "n_output_features": int(preprocessing["n_output_features"]),
            "n_rows": int(duplicates["n_rows"]),
            "n_unique_vectors": int(duplicates["n_unique_feature_vectors"]),
            "n_conflicting_vectors": int(duplicates["n_ambiguous_groups"]),
            "forced_errors": int(duplicates["bayes_error_rows"]),
            "overall_ceiling_pct": float(duplicates["max_achievable_accuracy_pct"]),
            "rows_sharing_vector_across_splits": int(
                duplicates["rows_whose_vector_appears_in_another_split"]),
        },
        "splits": {k: int(v["rows"]) for k, v in preprocessing["splits"].items()},
    }


def check_claims(text: str) -> dict[str, list[str]]:
    """Scan generated prose for forbidden claims and missing hedges."""
    lowered = text.lower()
    violations = [pattern for pattern in FORBIDDEN_CLAIMS
                  if re.search(pattern, lowered)]
    missing = [hedge for hedge in REQUIRED_HEDGES
               if hedge.lower() not in lowered]
    return {"forbidden_claims_found": violations, "missing_hedges": missing}


def best_by(facts: dict[str, Any], metric: str, maximise: bool = True) -> str:
    """Which model leads on a metric (used for evidence-backed statements)."""
    models = facts["models"]
    if metric not in next(iter(models.values())):
        raise ComparisonDataError(f"unknown metric: {metric}")
    chooser = max if maximise else min
    return chooser(MODEL_ORDER, key=lambda m: models[m][metric])
