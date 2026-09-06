"""Stage F tests — evaluation metrics.

Correctness is checked against hand-computed confusion matrices so that a
sign/orientation error cannot pass silently. Malicious = 1 is positive.
"""

import numpy as np
import pytest

from evaluation.metrics import (
    compute_metrics,
    confusion_counts,
    group_breakdown,
    threshold_sweep,
)


# --- confusion matrix orientation ------------------------------------------

def test_confusion_counts_hand_computed():
    #            true: 1  1  1  0  0  0  0
    y_true = np.array([1, 1, 1, 0, 0, 0, 0])
    y_pred = np.array([1, 1, 0, 1, 0, 0, 0])
    # TP=2 (both predicted 1 & true 1), FN=1, FP=1, TN=3
    counts = confusion_counts(y_true, y_pred)
    assert counts == {"TP": 2, "FN": 1, "FP": 1, "TN": 3}


def test_malicious_is_the_positive_class():
    """All-malicious truth, all-malicious prediction => TP only."""
    y = np.ones(10, dtype=np.int8)
    counts = confusion_counts(y, y)
    assert counts["TP"] == 10
    assert counts["TN"] == 0

    benign = np.zeros(10, dtype=np.int8)
    counts = confusion_counts(benign, benign)
    assert counts["TN"] == 10
    assert counts["TP"] == 0


def test_confusion_orientation_stable_with_single_class_present():
    """labels=[0,1] must pin orientation even if one class is absent."""
    y_true = np.zeros(5, dtype=np.int8)
    y_pred = np.zeros(5, dtype=np.int8)
    assert confusion_counts(y_true, y_pred) == {
        "TP": 0, "TN": 5, "FP": 0, "FN": 0}


# --- metric formulas --------------------------------------------------------

def test_metrics_match_hand_computation():
    y_true = np.array([1, 1, 1, 1, 0, 0, 0, 0, 0, 0])
    y_pred = np.array([1, 1, 1, 0, 1, 1, 0, 0, 0, 0])
    # TP=3 FN=1 FP=2 TN=4
    m = compute_metrics(y_true, y_pred)
    assert (m["TP"], m["FN"], m["FP"], m["TN"]) == (3, 1, 2, 4)
    assert m["accuracy"] == pytest.approx(7 / 10)
    assert m["precision"] == pytest.approx(3 / 5)
    assert m["recall"] == pytest.approx(3 / 4)
    assert m["f1"] == pytest.approx(2 * (0.6 * 0.75) / (0.6 + 0.75))
    assert m["tnr"] == pytest.approx(4 / 6)


def test_fpr_formula_is_fp_over_fp_plus_tn():
    y_true = np.array([0, 0, 0, 0, 1, 1])
    y_pred = np.array([1, 1, 0, 0, 1, 1])
    m = compute_metrics(y_true, y_pred)
    assert m["FP"] == 2 and m["TN"] == 2
    assert m["fpr"] == pytest.approx(2 / (2 + 2))


def test_perfect_and_inverted_predictions():
    y_true = np.array([0, 1, 0, 1])
    perfect = compute_metrics(y_true, y_true)
    assert perfect["accuracy"] == 1.0 and perfect["fpr"] == 0.0
    assert perfect["recall"] == 1.0

    inverted = compute_metrics(y_true, 1 - y_true)
    assert inverted["accuracy"] == 0.0 and inverted["fpr"] == 1.0
    assert inverted["recall"] == 0.0


def test_zero_division_is_safe():
    """No positives predicted => precision 0, not a crash."""
    y_true = np.array([1, 1, 0, 0])
    y_pred = np.zeros(4, dtype=np.int8)
    m = compute_metrics(y_true, y_pred)
    assert m["precision"] == 0.0
    assert m["f1"] == 0.0
    assert m["fpr"] == 0.0


def test_auc_metrics_present_and_none_when_single_class():
    rng = np.random.default_rng(0)
    y_true = (rng.random(200) < 0.5).astype(np.int8)
    score = np.where(y_true == 1, rng.random(200) * 0.5 + 0.5, rng.random(200) * 0.5)
    m = compute_metrics(y_true, (score >= 0.5).astype(np.int8), score)
    assert 0.9 < m["roc_auc"] <= 1.0
    assert 0.0 < m["pr_auc"] <= 1.0

    single = compute_metrics(np.ones(10, dtype=np.int8), np.ones(10, dtype=np.int8),
                             np.linspace(0, 1, 10))
    assert single["roc_auc"] is None and single["pr_auc"] is None


# --- threshold sweep --------------------------------------------------------

def test_threshold_sweep_is_monotone_in_predicted_positives():
    rng = np.random.default_rng(1)
    y_true = (rng.random(500) < 0.6).astype(np.int8)
    score = rng.random(500)
    rows = threshold_sweep(y_true, score, np.array([0.1, 0.3, 0.5, 0.7, 0.9]))

    predicted_positive = [r["TP"] + r["FP"] for r in rows]
    assert predicted_positive == sorted(predicted_positive, reverse=True)
    # recall and FPR both fall as the threshold rises
    assert [r["recall"] for r in rows] == sorted(
        [r["recall"] for r in rows], reverse=True)
    assert [r["fpr"] for r in rows] == sorted(
        [r["fpr"] for r in rows], reverse=True)
    assert all(r["threshold"] is not None for r in rows)


# --- per-group breakdown ----------------------------------------------------

def test_group_breakdown_reports_recall_for_attacks_and_fpr_for_benign():
    y_true = np.array([0, 0, 0, 1, 1, 1, 1])
    y_pred = np.array([1, 0, 0, 1, 1, 0, 1])
    groups = np.array(["Benign", "Benign", "Benign",
                       "UDPFlood", "UDPFlood", "UDPFlood", "SYNScan"])
    rows = {r["group"]: r for r in group_breakdown(y_true, y_pred, groups)}

    benign = rows["Benign"]
    assert benign["support"] == 3
    assert benign["false_positives"] == 1 and benign["true_negatives"] == 2
    assert benign["fpr"] == pytest.approx(1 / 3)
    assert benign["recall"] is None

    udp = rows["UDPFlood"]
    assert udp["support"] == 3 and udp["detected"] == 2 and udp["missed"] == 1
    assert udp["recall"] == pytest.approx(2 / 3)
    assert udp["fpr"] is None

    assert rows["SYNScan"]["recall"] == pytest.approx(1.0)


def test_group_breakdown_supports_sum_to_total():
    rng = np.random.default_rng(2)
    n = 300
    y_true = (rng.random(n) < 0.5).astype(np.int8)
    y_pred = (rng.random(n) < 0.5).astype(np.int8)
    groups = rng.choice(["Benign", "A", "B"], size=n)
    rows = group_breakdown(y_true, y_pred, groups)
    assert sum(r["support"] for r in rows) == n
