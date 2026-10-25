"""
Window-level evaluation for M2 against the dataset's actual labels.

Labels are used ONLY here (after detection). They are never given to feature extraction,
EWMA, or thresholding.

Ground-truth rule (explicit, configurable):
    A window is an ATTACK window if the fraction of its flows whose Label == malicious_label
    is >= attack_fraction (default 0.5). Otherwise it is a BENIGN window. The malicious
    fraction of every window is saved so any other rule can be re-applied offline.
    NOTE: the team's agreed evaluation protocol was not present in the uploaded M2 sources;
    this is a documented default, not a claim about the protocol of M1/M3.

Prediction:
    y_pred = window_anomaly from the thresholding stage. Windows in warm-up or with an
    unevaluable feature (NaN entropy) carry window_anomaly=False by construction.

Two scopes are reported so nothing is hidden:
    "all_windows"       - every window; warm-up/unevaluable windows count as "no alarm".
    "evaluable_windows" - only windows that are not warm-up and are valid.
"""

from typing import Any, Dict, Optional

import numpy as np
import pandas as pd


def label_windows(
    window_df: pd.DataFrame,
    flows: pd.DataFrame,
    label_col: str = "Label",
    malicious_label: str = "Malicious",
    attack_type_col: Optional[str] = "Attack Type",
    benign_label: str = "Benign",
    attack_fraction: float = 0.5,
) -> pd.DataFrame:
    """Add ground-truth columns to the window result using positional start_idx/end_idx.

    Adds: malicious_fraction, y_true (1 attack / 0 benign), dominant_attack_type
    (most frequent Attack Type among the window's malicious flows, '' for none).
    """
    if not 0.0 < attack_fraction <= 1.0:
        raise ValueError(f"attack_fraction must be in (0, 1], got {attack_fraction}")
    if label_col not in flows.columns:
        raise KeyError(f"Label column '{label_col}' not found; cannot evaluate.")

    out = window_df.copy()
    if len(out) == 0:
        out["malicious_fraction"] = pd.Series(dtype=float)
        out["y_true"] = pd.Series(dtype=int)
        out["dominant_attack_type"] = pd.Series(dtype=object)
        return out

    mal = (flows[label_col].to_numpy() == malicious_label).astype(np.int64)
    cs = np.concatenate([[0], np.cumsum(mal)])
    s = out["start_idx"].to_numpy(dtype=np.int64)
    e = out["end_idx"].to_numpy(dtype=np.int64)
    n = e - s
    frac = (cs[e] - cs[s]) / np.maximum(n, 1)
    out["malicious_fraction"] = frac
    out["y_true"] = (frac >= attack_fraction).astype(int)

    dom = np.full(len(out), "", dtype=object)
    if attack_type_col and attack_type_col in flows.columns:
        at = flows[attack_type_col].to_numpy()
        types = [t for t in pd.unique(at) if t != benign_label]
        best = np.zeros(len(out), dtype=np.int64)
        for t in types:
            c = np.concatenate([[0], np.cumsum((at == t).astype(np.int64))])
            cnt = c[e] - c[s]
            better = cnt > best
            dom[better] = t
            best = np.where(better, cnt, best)
    out["dominant_attack_type"] = dom
    return out


def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, Any]:
    """Confusion matrix and standard rates. Undefined ratios are reported as null, not 0."""
    y_true = np.asarray(y_true).astype(int)
    y_pred = np.asarray(y_pred).astype(int)
    tp = int(((y_true == 1) & (y_pred == 1)).sum())
    fp = int(((y_true == 0) & (y_pred == 1)).sum())
    fn = int(((y_true == 1) & (y_pred == 0)).sum())
    tn = int(((y_true == 0) & (y_pred == 0)).sum())
    return metrics_from_counts(tp, fp, fn, tn)


def metrics_from_counts(tp: int, fp: int, fn: int, tn: int) -> Dict[str, Any]:
    """Standard rates and chance-level references from a confusion matrix.

    A detector that alarms independently of the labels has an expected precision equal to
    the base rate (share of attack windows) at any alarm rate, a balanced accuracy of 0.5
    and an MCC of 0. precision_lift = precision / base_rate is below 1 when the detector's
    alarms are less often attacks than randomly chosen windows are.
    """
    n = tp + fp + fn + tn

    def ratio(a: float, b: float) -> Optional[float]:
        return float(a / b) if b > 0 else None

    precision = ratio(tp, tp + fp)
    recall = ratio(tp, tp + fn)
    specificity = ratio(tn, tn + fp)
    base_rate = ratio(tp + fn, n)
    f1 = None
    if precision is not None and recall is not None and (precision + recall) > 0:
        f1 = float(2 * precision * recall / (precision + recall))
    balanced_accuracy = None
    if recall is not None and specificity is not None:
        balanced_accuracy = float((recall + specificity) / 2)
    mcc_den = float((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
    mcc = float((tp * tn - fp * fn) / np.sqrt(mcc_den)) if mcc_den > 0 else None
    return {
        "n_windows": int(n),
        "n_attack_windows": int(tp + fn),
        "n_benign_windows": int(tn + fp),
        "tp": int(tp), "fp": int(fp), "fn": int(fn), "tn": int(tn),
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "false_positive_rate": ratio(fp, fp + tn),
        "accuracy": ratio(tp + tn, n),
        "base_rate": base_rate,
        "alarm_rate": ratio(tp + fp, n),
        "precision_lift": ratio(precision, base_rate) if precision is not None and base_rate else None,
        "balanced_accuracy": balanced_accuracy,
        "mcc": mcc,
    }


def evaluate_windows(labelled: pd.DataFrame) -> Dict[str, Any]:
    """Compute metrics for all windows and for evaluable windows, plus per-attack-type recall."""
    if len(labelled) == 0:
        return {"all_windows": compute_metrics([], []), "evaluable_windows": compute_metrics([], [])}

    y_pred = labelled["window_anomaly"].astype(bool).to_numpy().astype(int)
    evaluable = (~labelled["threshold_is_warmup"].astype(bool)) & labelled["threshold_is_valid"].astype(bool)

    result: Dict[str, Any] = {
        "all_windows": compute_metrics(labelled["y_true"].to_numpy(), y_pred),
        "evaluable_windows": compute_metrics(
            labelled.loc[evaluable, "y_true"].to_numpy(), y_pred[evaluable.to_numpy()]
        ),
        "n_warmup_or_unevaluable_windows": int((~evaluable).sum()),
    }

    per_type: Dict[str, Any] = {}
    atk = labelled[labelled["y_true"] == 1]
    for t, g in atk.groupby("dominant_attack_type"):
        if t == "":
            continue
        ev = (~g["threshold_is_warmup"].astype(bool)) & g["threshold_is_valid"].astype(bool)
        per_type[str(t)] = {
            "attack_windows": int(len(g)),
            "alarmed": int(g["window_anomaly"].astype(bool).sum()),
            "recall_all": float(g["window_anomaly"].astype(bool).mean()),
            "evaluable_attack_windows": int(ev.sum()),
            "recall_evaluable": float(g.loc[ev, "window_anomaly"].astype(bool).mean()) if ev.any() else None,
        }
    result["per_attack_type_recall"] = per_type
    return result
