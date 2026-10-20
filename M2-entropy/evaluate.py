"""Evaluation utilities for M2 window-level anomaly detection.

Ground-truth labels are used only to evaluate predictions produced by
the detector. They must never be passed into the detection pipeline.
"""

from typing import Any, Dict

import numpy as np
import pandas as pd


def evaluate_predictions(
    y_true: Any,
    y_pred: Any,
) -> Dict[str, Any]:
    """Calculate binary classification metrics.

    Positive class: malicious window / anomaly detected.
    Negative class: benign window / no anomaly detected.
    """
    true_values = np.asarray(y_true)
    pred_values = np.asarray(y_pred)

    if true_values.ndim != 1 or pred_values.ndim != 1:
        raise ValueError("y_true and y_pred must be one-dimensional.")

    if len(true_values) != len(pred_values):
        raise ValueError("y_true and y_pred must have equal lengths.")

    if len(true_values) == 0:
        raise ValueError("Cannot evaluate empty predictions.")

    if pd.isna(true_values).any() or pd.isna(pred_values).any():
        raise ValueError("y_true and y_pred must not contain missing values.")

    if not np.isin(true_values, [False, True, 0, 1]).all():
        raise ValueError("y_true must contain only binary values (0/1 or False/True).")

    if not np.isin(pred_values, [False, True, 0, 1]).all():
        raise ValueError("y_pred must contain only binary values (0/1 or False/True).")

    true_values = true_values.astype(bool)
    pred_values = pred_values.astype(bool)

    tp = int(np.sum(true_values & pred_values))
    tn = int(np.sum(~true_values & ~pred_values))
    fp = int(np.sum(~true_values & pred_values))
    fn = int(np.sum(true_values & ~pred_values))

    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall
        else 0.0
    )
    fpr = fp / (fp + tn) if fp + tn else 0.0
    accuracy = (tp + tn) / len(true_values)

    return {
        "window_count": len(true_values),
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
        "false_positive_rate": fpr,
    }


def assign_window_ground_truth(
    labels: Any,
    start_idx: int,
    end_idx: int,
    malicious_label: str = "Malicious",
) -> Dict[str, Any]:
    """Summarize row labels for one positional window.

    A window is malicious if at least one row is labelled malicious.
    The malicious fraction is returned to expose mixed windows.
    """
    label_values = np.asarray(labels, dtype=object)

    if label_values.ndim != 1:
        raise ValueError("labels must be one-dimensional.")

    if start_idx < 0 or end_idx <= start_idx or end_idx > len(label_values):
        raise ValueError("Window indices are outside the label array.")

    window_labels = label_values[start_idx:end_idx]
    if pd.isna(window_labels).any():
        raise ValueError("Window labels contain missing values.")

    malicious_count = int(np.sum(window_labels == malicious_label))
    flow_count = len(window_labels)

    return {
        "ground_truth_malicious": malicious_count > 0,
        "malicious_flow_count": malicious_count,
        "flow_count": flow_count,
        "malicious_fraction": malicious_count / flow_count,
    }


def evaluate_window_results(
    source_df: pd.DataFrame,
    predictions_df: pd.DataFrame,
    label_col: str = "Label",
    malicious_label: str = "Malicious",
) -> tuple[Dict[str, Any], pd.DataFrame]:
    """Evaluate detector decisions against labels using window row indices."""
    required_source = {label_col}
    required_predictions = {"start_idx", "end_idx", "window_anomaly"}

    if not required_source.issubset(source_df.columns):
        raise ValueError(f"Missing source label column: {label_col}")
    if not required_predictions.issubset(predictions_df.columns):
        raise ValueError(
            f"Predictions must contain: {sorted(required_predictions)}"
        )

    records = []
    for _, row in predictions_df.iterrows():
        truth = assign_window_ground_truth(
            source_df[label_col].to_numpy(),
            int(row["start_idx"]),
            int(row["end_idx"]),
            malicious_label=malicious_label,
        )
        records.append({
            "window_id": row.get("window_id"),
            "start_idx": int(row["start_idx"]),
            "end_idx": int(row["end_idx"]),
            "ground_truth_malicious": truth["ground_truth_malicious"],
            "malicious_flow_count": truth["malicious_flow_count"],
            "flow_count": truth["flow_count"],
            "malicious_fraction": truth["malicious_fraction"],
            "window_anomaly": bool(row["window_anomaly"]),
        })

    per_window = pd.DataFrame(records)
    metrics = evaluate_predictions(
        per_window["ground_truth_malicious"],
        per_window["window_anomaly"],
    )
    metrics["ground_truth_rule"] = "Any malicious flow makes the window malicious"
    metrics["label_column"] = label_col
    return metrics, per_window
