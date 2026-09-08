"""Stage L tests — feature-vector novelty and conflict analysis."""

import numpy as np
import pytest

from evaluation.novelty import (
    compare_populations,
    conflicting_vectors,
    novelty_report,
    vector_ids,
)


# --- vector identity --------------------------------------------------------

def test_identical_rows_share_a_vector_id():
    X = np.array([[1.0, 2.0], [1.0, 2.0], [3.0, 4.0]], dtype=np.float32)
    ids, n = vector_ids(X)
    assert n == 2
    assert ids[0] == ids[1] != ids[2]


def test_distinct_rows_get_distinct_ids():
    X = np.arange(12, dtype=np.float32).reshape(4, 3)
    ids, n = vector_ids(X)
    assert n == 4 and len(set(ids.tolist())) == 4


# --- conflicting vectors ----------------------------------------------------

def test_conflicting_vector_detected():
    X = np.array([[1.0], [1.0], [2.0], [2.0]], dtype=np.float32)
    y = np.array([0, 1, 1, 1])          # vector 1.0 carries both labels
    ids, n = vector_ids(X)
    conflicting = conflicting_vectors(ids, y, n)
    assert conflicting[ids[0]]          # 1.0 -> conflicting
    assert not conflicting[ids[2]]      # 2.0 -> pure


def test_pure_vectors_are_not_flagged():
    X = np.array([[1.0], [1.0], [2.0]], dtype=np.float32)
    y = np.array([1, 1, 0])
    ids, n = vector_ids(X)
    assert not conflicting_vectors(ids, y, n).any()


# --- novelty report ---------------------------------------------------------

def test_fully_seen_population_reports_zero_novelty():
    X_ref = np.array([[1.0], [2.0], [3.0]], dtype=np.float32)
    y_ref = np.array([1, 0, 1])
    report = novelty_report(X_ref, y_ref, X_ref.copy(), y_ref.copy(), "same")
    assert report["pct_rows_vector_seen_in_reference"] == 100.0
    assert report["pct_rows_vector_unseen_in_reference"] == 0.0
    assert report["unseen_vectors_in_evaluation"] == 0


def test_fully_novel_population_reports_full_novelty():
    X_ref = np.array([[1.0], [2.0]], dtype=np.float32)
    X_eval = np.array([[7.0], [8.0]], dtype=np.float32)
    report = novelty_report(X_ref, np.array([1, 0]), X_eval, np.array([1, 0]),
                            "novel")
    assert report["pct_rows_vector_seen_in_reference"] == 0.0
    assert report["pct_rows_vector_unseen_in_reference"] == 100.0
    assert report["unseen_vectors_in_evaluation"] == 2


def test_partial_overlap_percentages():
    X_ref = np.array([[1.0], [2.0]], dtype=np.float32)
    X_eval = np.array([[1.0], [1.0], [9.0], [9.0]], dtype=np.float32)
    report = novelty_report(X_ref, np.array([1, 0]), X_eval,
                            np.array([1, 1, 0, 0]), "half")
    assert report["pct_rows_vector_seen_in_reference"] == 50.0
    assert report["pct_rows_vector_unseen_in_reference"] == 50.0
    assert report["evaluation_rows"] == 4


def test_conflict_percentage_reported():
    # vector 5.0 appears with both labels across reference and evaluation
    X_ref = np.array([[5.0], [6.0]], dtype=np.float32)
    y_ref = np.array([0, 0])
    X_eval = np.array([[5.0], [6.0]], dtype=np.float32)
    y_eval = np.array([1, 0])
    report = novelty_report(X_ref, y_ref, X_eval, y_eval, "conflict")
    assert report["pct_rows_in_conflicting_vectors"] == 50.0


def test_report_contains_all_required_fields():
    X = np.random.default_rng(0).normal(size=(50, 4)).astype(np.float32)
    y = (np.arange(50) % 2).astype(np.int8)
    report = novelty_report(X[:30], y[:30], X[30:], y[30:], "scope")
    for field in ("scope", "reference_rows", "evaluation_rows",
                  "distinct_vectors_combined", "unseen_vectors_in_evaluation",
                  "pct_rows_vector_seen_in_reference",
                  "pct_rows_vector_unseen_in_reference",
                  "pct_rows_in_conflicting_vectors",
                  "pct_unseen_vectors_that_are_conflicting"):
        assert field in report


def test_seen_and_unseen_percentages_sum_to_100():
    rng = np.random.default_rng(1)
    X = rng.integers(0, 5, size=(200, 2)).astype(np.float32)
    y = (rng.random(200) < 0.5).astype(np.int8)
    report = novelty_report(X[:120], y[:120], X[120:], y[120:], "s")
    assert (report["pct_rows_vector_seen_in_reference"]
            + report["pct_rows_vector_unseen_in_reference"]) == pytest.approx(100.0)


def test_mismatched_feature_width_rejected():
    with pytest.raises(ValueError, match="feature width"):
        novelty_report(np.zeros((3, 4), dtype=np.float32), np.zeros(3),
                       np.zeros((3, 5), dtype=np.float32), np.zeros(3), "bad")


def test_report_is_deterministic():
    rng = np.random.default_rng(2)
    X = rng.integers(0, 4, size=(80, 3)).astype(np.float32)
    y = (rng.random(80) < 0.5).astype(np.int8)
    a = novelty_report(X[:50], y[:50], X[50:], y[50:], "d")
    b = novelty_report(X[:50], y[:50], X[50:], y[50:], "d")
    assert a == b


# --- population comparison --------------------------------------------------

def test_compare_populations_reports_differences():
    rng = np.random.default_rng(3)
    X = rng.integers(0, 4, size=(120, 2)).astype(np.float32)
    y = (rng.random(120) < 0.5).astype(np.int8)
    a = novelty_report(X[:60], y[:60], X[60:], y[60:], "A")
    b = novelty_report(X[:80], y[:80], X[80:], y[80:], "B")
    result = compare_populations([a, b])

    assert result["a"] == "A" and result["b"] == "B"
    assert "pct_rows_in_conflicting_vectors" in result["differences_pp"]
    # the caveat against over-reading novelty must be carried
    assert "does not by itself demonstrate" in result["note"]


def test_compare_populations_requires_exactly_two():
    with pytest.raises(ValueError, match="exactly two"):
        compare_populations([{"scope": "only-one"}])
