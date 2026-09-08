"""Stage L — feature-vector novelty and representation-conflict analysis.

Quantifies how much of a held-out population the development data has
already seen, in the exact 67-feature representation, and how much of it
sits in *conflicting* vectors (identical vectors carrying both labels).

This is a property of the data only — no model is involved. Novelty on
its own does not demonstrate generalisation; it characterises how
different the evaluation population is.
"""

from __future__ import annotations

from typing import Any

import numpy as np


def vector_ids(X: np.ndarray) -> tuple[np.ndarray, int]:
    """Map each row to an id for its exact feature vector (byte-exact)."""
    X = np.ascontiguousarray(X)
    void = X.view([(f"f{i}", X.dtype) for i in range(X.shape[1])]).ravel()
    uniq, inverse = np.unique(void, return_inverse=True)
    return inverse, len(uniq)


def conflicting_vectors(ids: np.ndarray, y: np.ndarray, n_vectors: int
                        ) -> np.ndarray:
    """Boolean mask over vector ids: True where a vector carries both labels."""
    y = np.asarray(y).astype(np.float64)
    malicious = np.bincount(ids, weights=y, minlength=n_vectors)
    total = np.bincount(ids, minlength=n_vectors).astype(np.float64)
    return np.minimum(malicious, total - malicious) > 0


def novelty_report(
    X_reference: np.ndarray,
    y_reference: np.ndarray,
    X_evaluation: np.ndarray,
    y_evaluation: np.ndarray,
    label: str,
) -> dict[str, Any]:
    """Novelty of an evaluation population relative to a reference population.

    `reference` is what the model was allowed to see (e.g. development);
    `evaluation` is the population being scored (e.g. the held-out blocks).
    """
    X_reference = np.asarray(X_reference)
    X_evaluation = np.asarray(X_evaluation)
    if X_reference.shape[1] != X_evaluation.shape[1]:
        raise ValueError("reference and evaluation must share the feature width")

    combined = np.vstack([X_reference, X_evaluation])
    combined_y = np.concatenate([np.asarray(y_reference),
                                 np.asarray(y_evaluation)])
    ids, n_vectors = vector_ids(combined)
    conflicting = conflicting_vectors(ids, combined_y, n_vectors)

    n_ref = len(X_reference)
    ref_ids, eval_ids = ids[:n_ref], ids[n_ref:]
    seen = np.isin(np.arange(n_vectors), np.unique(ref_ids))

    seen_rows = seen[eval_ids]
    conflict_rows = conflicting[eval_ids]
    n_eval = len(eval_ids)

    unseen_vector_ids = np.unique(eval_ids[~seen_rows])
    return {
        "scope": label,
        "reference_rows": int(n_ref),
        "evaluation_rows": int(n_eval),
        "distinct_vectors_combined": int(n_vectors),
        "distinct_vectors_evaluation": int(len(np.unique(eval_ids))),
        "unseen_vectors_in_evaluation": int(len(unseen_vector_ids)),
        "pct_rows_vector_seen_in_reference": round(
            100 * float(seen_rows.mean()), 4),
        "pct_rows_vector_unseen_in_reference": round(
            100 * float((~seen_rows).mean()), 4),
        "pct_rows_in_conflicting_vectors": round(
            100 * float(conflict_rows.mean()), 4),
        "pct_unseen_vectors_that_are_conflicting": round(
            100 * float(conflicting[unseen_vector_ids].mean()), 4
        ) if len(unseen_vector_ids) else 0.0,
        "pct_unseen_rows_that_are_conflicting": round(
            100 * float(conflict_rows[~seen_rows].mean()), 4
        ) if (~seen_rows).any() else 0.0,
    }


def compare_populations(reports: list[dict[str, Any]]) -> dict[str, Any]:
    """Difference between two novelty reports (e.g. Stage L vs primary)."""
    if len(reports) != 2:
        raise ValueError("compare_populations expects exactly two reports")
    a, b = reports
    keys = ("pct_rows_vector_seen_in_reference",
            "pct_rows_vector_unseen_in_reference",
            "pct_rows_in_conflicting_vectors")
    return {
        "a": a["scope"], "b": b["scope"],
        "differences_pp": {k: round(a[k] - b[k], 4) for k in keys},
        "note": (
            "Feature-vector novelty characterises how different the two "
            "evaluation populations are. It does not by itself demonstrate "
            "generalisation, and a difference in conflicting-vector exposure "
            "means the two populations are not equally difficult."
        ),
    }
