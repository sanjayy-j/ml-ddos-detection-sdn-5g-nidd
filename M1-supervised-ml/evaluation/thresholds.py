"""Stage G — the locked FPR-constrained operating-point protocol.

Shared by every M1 model (RF / SVM / CNN) so the comparison is made at
the same alarm budget:

    choose the threshold maximising recall subject to FPR <= cap,
    breaking ties toward the HIGHEST threshold

The threshold is always fitted on validation scores and frozen before any
test evaluation. Works with any real-valued score — SVM
`decision_function` margins are fine, no probability calibration is
required.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.metrics import roc_curve

# Project-wide primary constraint agreed before Stage G.
PRIMARY_FPR_CAP = 0.01
# Reported alongside it, because a quantised score distribution can make
# several caps collapse onto one operating point for some models.
FPR_BUDGETS = (0.001, 0.01, 0.05, 0.10)


def select_threshold_at_fpr(
    y_true: np.ndarray, scores: np.ndarray, max_fpr: float = PRIMARY_FPR_CAP
) -> dict[str, Any]:
    """Highest-recall threshold subject to ``FPR <= max_fpr``.

    Returns the chosen threshold plus the operating point it achieves.
    `satisfiable` is False when the constraint yields no positive
    detections at all (recall 0), which must be reported rather than
    worked around by relaxing the cap.
    """
    y_true = np.asarray(y_true)
    scores = np.asarray(scores, dtype=np.float64)

    fpr, tpr, thresholds = roc_curve(y_true, scores)
    eligible = np.flatnonzero(fpr <= max_fpr)
    if eligible.size == 0:
        # roc_curve always includes an all-negative point (fpr=0), so this
        # is unreachable in practice; handled for safety.
        return {
            "max_fpr": float(max_fpr),
            "threshold": float("inf"),
            "recall": 0.0,
            "fpr": 0.0,
            "satisfiable": False,
            "reason": "no ROC point satisfies the FPR constraint",
        }

    best_recall = float(tpr[eligible].max())
    # tie-break: among thresholds reaching that recall, take the highest
    # (most conservative, furthest from the decision boundary)
    tied = eligible[tpr[eligible] == best_recall]
    finite = thresholds[tied][np.isfinite(thresholds[tied])]
    threshold = float(finite.max()) if finite.size else float(
        np.nanmax(scores)) + 1.0
    achieved = float(fpr[tied][np.argmax(thresholds[tied])])

    return {
        "max_fpr": float(max_fpr),
        "threshold": threshold,
        "recall": best_recall,
        "fpr": achieved,
        "satisfiable": bool(best_recall > 0.0),
        "reason": "" if best_recall > 0.0 else (
            "constraint satisfied only by predicting no positives "
            "(recall 0) — the model cannot meet this operating point"
        ),
    }


def recall_at_fpr_budgets(
    y_true: np.ndarray,
    scores: np.ndarray,
    budgets: tuple[float, ...] = FPR_BUDGETS,
) -> list[dict[str, Any]]:
    """Operating point at each alarm budget (validation reporting)."""
    return [select_threshold_at_fpr(y_true, scores, cap) for cap in budgets]
