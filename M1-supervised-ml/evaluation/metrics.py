"""Stage F — binary classification metrics for M1.

Positive class is **Malicious = 1**; negative is **Benign = 0**.

False Positive Rate is computed explicitly rather than inferred, because
for DDoS detection a false positive means dropping/flagging legitimate
traffic, and Stage D established an irreducible FPR floor on this
representation. Accuracy is never reported without the confusion matrix.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    roc_auc_score,
)

POSITIVE_LABEL = 1  # Malicious
NEGATIVE_LABEL = 0  # Benign


def confusion_counts(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, int]:
    """TN/FP/FN/TP with Malicious=1 as the positive class.

    `labels=[0, 1]` pins the orientation so the matrix cannot silently
    transpose when a split happens to contain a single class.
    """
    tn, fp, fn, tp = confusion_matrix(
        y_true, y_pred, labels=[NEGATIVE_LABEL, POSITIVE_LABEL]
    ).ravel()
    return {"TN": int(tn), "FP": int(fp), "FN": int(fn), "TP": int(tp)}


def _safe_div(numerator: float, denominator: float) -> float:
    return float(numerator / denominator) if denominator else 0.0


def compute_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_score: np.ndarray | None = None,
) -> dict[str, Any]:
    """Full metric set. `y_score` = P(malicious), used for AUC metrics."""
    counts = confusion_counts(y_true, y_pred)
    tp, tn, fp, fn = counts["TP"], counts["TN"], counts["FP"], counts["FN"]

    precision = _safe_div(tp, tp + fp)
    recall = _safe_div(tp, tp + fn)            # TPR / detection rate
    fpr = _safe_div(fp, fp + tn)               # FP / (FP + TN)
    tnr = _safe_div(tn, tn + fp)               # specificity

    metrics: dict[str, Any] = {
        "n": int(len(y_true)),
        "accuracy": _safe_div(tp + tn, tp + tn + fp + fn),
        "precision": precision,
        "recall": recall,
        "f1": _safe_div(2 * precision * recall, precision + recall),
        "fpr": fpr,
        "tnr": tnr,
        **counts,
    }

    if y_score is not None:
        # AUCs are undefined with a single class present
        if len(np.unique(y_true)) > 1:
            metrics["roc_auc"] = float(roc_auc_score(y_true, y_score))
            metrics["pr_auc"] = float(average_precision_score(y_true, y_score))
        else:
            metrics["roc_auc"] = None
            metrics["pr_auc"] = None
    return metrics


def threshold_sweep(
    y_true: np.ndarray, y_score: np.ndarray, thresholds: np.ndarray
) -> list[dict[str, Any]]:
    """Metrics at each decision threshold (for validation-only analysis)."""
    rows = []
    for threshold in thresholds:
        y_pred = (y_score >= threshold).astype(np.int8)
        row = compute_metrics(y_true, y_pred)
        row["threshold"] = round(float(threshold), 4)
        rows.append(row)
    return rows


def group_breakdown(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    groups: np.ndarray,
    benign_group: str = "Benign",
) -> list[dict[str, Any]]:
    """Per-group results using analysis metadata (e.g. Attack Type).

    The grouping column is metadata only and is never a model input. For a
    malicious group every row has y_true=1, so recall is the meaningful
    quantity (precision is undefined within the group and is omitted);
    for the benign group the false-positive rate is what matters.
    """
    rows = []
    for group in sorted(set(map(str, groups))):
        mask = np.asarray(groups).astype(str) == group
        gt, gp = np.asarray(y_true)[mask], np.asarray(y_pred)[mask]
        row: dict[str, Any] = {
            "group": group,
            "support": int(mask.sum()),
            "n_malicious": int((gt == POSITIVE_LABEL).sum()),
            "n_benign": int((gt == NEGATIVE_LABEL).sum()),
            "predicted_malicious": int((gp == POSITIVE_LABEL).sum()),
        }
        if group == benign_group:
            fp = int(((gt == NEGATIVE_LABEL) & (gp == POSITIVE_LABEL)).sum())
            tn = int(((gt == NEGATIVE_LABEL) & (gp == NEGATIVE_LABEL)).sum())
            row["false_positives"] = fp
            row["true_negatives"] = tn
            row["fpr"] = _safe_div(fp, fp + tn)
            row["recall"] = None
        else:
            tp = int(((gt == POSITIVE_LABEL) & (gp == POSITIVE_LABEL)).sum())
            fn = int(((gt == POSITIVE_LABEL) & (gp == NEGATIVE_LABEL)).sum())
            row["detected"] = tp
            row["missed"] = fn
            row["recall"] = _safe_div(tp, tp + fn)
            row["fpr"] = None
        rows.append(row)
    return rows
