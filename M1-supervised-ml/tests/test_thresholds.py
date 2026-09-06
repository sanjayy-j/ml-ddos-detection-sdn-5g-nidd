"""Stage G tests — FPR-constrained operating-point selection."""

import numpy as np
import pytest

from evaluation.metrics import compute_metrics
from evaluation.thresholds import (
    FPR_BUDGETS,
    PRIMARY_FPR_CAP,
    recall_at_fpr_budgets,
    select_threshold_at_fpr,
)


def test_primary_cap_is_one_percent():
    assert PRIMARY_FPR_CAP == 0.01
    assert FPR_BUDGETS == (0.001, 0.01, 0.05, 0.10)


def test_selected_threshold_respects_the_constraint():
    rng = np.random.default_rng(0)
    y = (rng.random(4000) < 0.6).astype(np.int8)
    scores = np.where(y == 1, rng.normal(1.0, 1.0, 4000),
                      rng.normal(-1.0, 1.0, 4000))

    result = select_threshold_at_fpr(y, scores, 0.01)
    assert result["satisfiable"]
    assert result["fpr"] <= 0.01 + 1e-12

    # applying the threshold reproduces the reported operating point
    pred = (scores >= result["threshold"]).astype(np.int8)
    m = compute_metrics(y, pred)
    assert m["fpr"] <= 0.01 + 1e-9
    assert m["recall"] == pytest.approx(result["recall"], abs=1e-6)


def test_looser_constraint_never_reduces_recall():
    rng = np.random.default_rng(1)
    y = (rng.random(3000) < 0.5).astype(np.int8)
    scores = np.where(y == 1, rng.normal(1.0, 1.0, 3000),
                      rng.normal(-1.0, 1.0, 3000))

    recalls = [select_threshold_at_fpr(y, scores, cap)["recall"]
               for cap in (0.001, 0.01, 0.05, 0.10)]
    assert recalls == sorted(recalls)


def test_tie_break_picks_the_highest_threshold():
    """With ties in recall, the most conservative threshold must win."""
    # scores are far apart, so several thresholds give identical recall
    y = np.array([0, 0, 0, 0, 1, 1, 1, 1])
    scores = np.array([0.0, 0.1, 0.2, 0.3, 10.0, 11.0, 12.0, 13.0])

    result = select_threshold_at_fpr(y, scores, 0.0)
    # every positive is separable; recall 1.0 at FPR 0
    assert result["recall"] == 1.0
    assert result["fpr"] == 0.0
    # the highest threshold still capturing all positives is 10.0
    assert result["threshold"] == pytest.approx(10.0)

    pred = (scores >= result["threshold"]).astype(np.int8)
    assert compute_metrics(y, pred)["recall"] == 1.0
    assert compute_metrics(y, pred)["fpr"] == 0.0


def test_unsatisfiable_constraint_is_reported_not_relaxed():
    """Perfectly inverted scores: no positive detection at FPR 0."""
    y = np.array([0, 0, 0, 1, 1, 1])
    scores = np.array([9.0, 8.0, 7.0, 1.0, 2.0, 3.0])  # benign score highest

    result = select_threshold_at_fpr(y, scores, 0.0)
    assert result["recall"] == 0.0
    assert result["satisfiable"] is False
    assert "cannot meet" in result["reason"]
    # the cap itself is never widened
    assert result["max_fpr"] == 0.0


def test_perfectly_separable_scores_give_full_recall_at_zero_fpr():
    y = np.array([0, 0, 0, 1, 1, 1])
    scores = np.array([0.0, 0.1, 0.2, 5.0, 6.0, 7.0])
    result = select_threshold_at_fpr(y, scores, 0.0)
    assert result["recall"] == 1.0
    assert result["fpr"] == 0.0


def test_quantised_scores_collapse_budgets_onto_one_point():
    """The RF-style failure mode the budget table exists to expose."""
    rng = np.random.default_rng(2)
    n = 2000
    y = (rng.random(n) < 0.6).astype(np.int8)
    # one huge ambiguous mass at a single score, plus clean tails
    scores = np.full(n, 0.46)
    clean = rng.random(n) < 0.3
    scores[clean & (y == 1)] = 0.99
    scores[clean & (y == 0)] = 0.01

    rows = recall_at_fpr_budgets(y, scores)
    assert len(rows) == len(FPR_BUDGETS)
    # all budgets land on the same recall because the mass flips together
    assert len({round(r["recall"], 9) for r in rows}) == 1


def test_budget_table_shape_and_fields():
    rng = np.random.default_rng(3)
    y = (rng.random(1000) < 0.6).astype(np.int8)
    scores = rng.random(1000)
    rows = recall_at_fpr_budgets(y, scores)

    assert [r["max_fpr"] for r in rows] == list(FPR_BUDGETS)
    for row in rows:
        assert {"threshold", "recall", "fpr", "satisfiable"} <= set(row)
        assert row["fpr"] <= row["max_fpr"] + 1e-12


def test_works_with_unbounded_margin_scores():
    """SVM decision_function values are not probabilities."""
    rng = np.random.default_rng(4)
    y = (rng.random(2000) < 0.6).astype(np.int8)
    scores = np.where(y == 1, rng.normal(3.0, 2.0, 2000),
                      rng.normal(-3.0, 2.0, 2000))

    result = select_threshold_at_fpr(y, scores, 0.01)
    assert result["satisfiable"]
    assert not (0.0 <= result["threshold"] <= 1.0)  # a margin, not a probability
    pred = (scores >= result["threshold"]).astype(np.int8)
    assert compute_metrics(y, pred)["fpr"] <= 0.01 + 1e-9
