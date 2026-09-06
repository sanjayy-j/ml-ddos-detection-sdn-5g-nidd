"""Stage G — Support Vector Machine for M1.

Strategy: **RBF kernel approximation (Nystroem) + linear SVM (LinearSVC)**.

Why not a full `SVC(kernel="rbf")` on the 851,106-row training split?
Measured on this project's hardware (Stage G feasibility probe):

    n=5,000   fit 0.4s      n=10,000  fit 1.7s      n=20,000  fit 7.3s

Fit time grows quadratically, extrapolating to ~3.7 hours on the full
training split. The decisive problem is inference, not fit: ~55% of rows
become support vectors, so scoring cost grows with the training-set size
too. A true RBF SVC trained on the Stage D 50k stratified subsample
needed **246.5 s to score the validation split (1.35 ms per flow)** while
reaching only val PR-AUC 0.86877 / ROC-AUC 0.79169 — it sees just 5.9% of
the training data and is far too slow for the project's per-flow
inference-time metric.

Nystroem + LinearSVC instead trains on **all** 851,106 rows, reaches val
PR-AUC 0.90791 / ROC-AUC 0.86659, and scores at 0.0034 ms per flow
(~400x faster than the true SVC). It remains genuinely SVM-based: an
explicit finite-dimensional approximation of the RBF feature map followed
by a hinge-loss maximum-margin classifier. This is a documented
approximation of an RBF SVM, not a substitution of a different model
family.

Memory note: `Nystroem.transform` returns float64, so materialising
851,106 x 1024 would need ~7 GB and drove this machine into swap during
probing. `ChunkedNystroem` transforms in row blocks and stores float32,
capping peak memory.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.kernel_approximation import Nystroem
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

DEFAULT_CHUNK_ROWS = 100_000


def gamma_scale(X: np.ndarray) -> float:
    """sklearn's ``gamma='scale'`` heuristic: 1 / (n_features * X.var()).

    Computed on TRAINING data only and then frozen, so no validation or
    test statistic can enter the kernel definition.
    """
    variance = float(np.asarray(X).var())
    if variance <= 0:
        return 1.0 / X.shape[1]
    return 1.0 / (X.shape[1] * variance)


class ChunkedNystroem(BaseEstimator, TransformerMixin):
    """Nystroem RBF feature map that transforms in float32 row blocks.

    Functionally identical to `Nystroem` up to float32 rounding; it exists
    only to keep peak memory bounded on a 16 GB machine.
    """

    def __init__(
        self,
        n_components: int = 256,
        gamma: float = 0.1,
        random_state: int = 42,
        chunk_rows: int = DEFAULT_CHUNK_ROWS,
    ):
        self.n_components = n_components
        self.gamma = gamma
        self.random_state = random_state
        self.chunk_rows = chunk_rows

    def fit(self, X, y=None):
        self.nystroem_ = Nystroem(
            kernel="rbf",
            gamma=self.gamma,
            n_components=self.n_components,
            random_state=self.random_state,
        ).fit(X)
        self.n_features_in_ = X.shape[1]
        return self

    def transform(self, X):
        X = np.asarray(X)
        out = np.empty((X.shape[0], self.n_components), dtype=np.float32)
        for start in range(0, X.shape[0], self.chunk_rows):
            stop = min(start + self.chunk_rows, X.shape[0])
            out[start:stop] = self.nystroem_.transform(X[start:stop]).astype(
                np.float32, copy=False
            )
        return out

    def get_feature_names_out(self, input_features=None):
        return np.asarray(
            [f"nystroem_{i}" for i in range(self.n_components)], dtype=object
        )


def build_svm(
    config: dict[str, Any], gamma: float, **overrides: Any
) -> Pipeline:
    """Build the unfitted Nystroem + LinearSVC pipeline from config.

    `gamma` must be derived from training data only (see `gamma_scale`).
    """
    svm_cfg = dict(((config.get("models") or {}).get("svm") or {}))
    seed = int(svm_cfg.pop("random_state", config.get("seed", 42)))

    n_components = int(overrides.pop("n_components",
                                     svm_cfg.pop("n_components", 256)))
    C = float(overrides.pop("C", svm_cfg.pop("C", 1.0)))
    # Stage D fixed class weighting (not resampling) as the imbalance
    # strategy; it is held constant across RF/SVM/CNN for comparability
    # rather than being tuned per model.
    class_weight = overrides.pop(
        "class_weight", svm_cfg.pop("class_weight", "balanced")
    )
    max_iter = int(overrides.pop("max_iter", svm_cfg.pop("max_iter", 3000)))
    chunk_rows = int(overrides.pop("chunk_rows", DEFAULT_CHUNK_ROWS))

    return Pipeline(
        [
            (
                "nystroem",
                ChunkedNystroem(
                    n_components=n_components,
                    gamma=gamma,
                    random_state=seed,
                    chunk_rows=chunk_rows,
                ),
            ),
            (
                "linearsvc",
                LinearSVC(
                    C=C,
                    class_weight=class_weight,
                    # n_samples >> n_features after the map, so the primal
                    # form is the appropriate and much faster solver
                    dual=False,
                    random_state=seed,
                    max_iter=max_iter,
                ),
            ),
        ]
    )


def describe_svm(model: Pipeline) -> dict[str, Any]:
    """Structural summary of a fitted SVM pipeline (for the run record)."""
    nystroem = model.named_steps["nystroem"]
    linear = model.named_steps["linearsvc"]
    return {
        "approximation": "Nystroem(rbf)",
        "n_components": int(nystroem.n_components),
        "gamma": float(nystroem.gamma),
        "classifier": "LinearSVC",
        "C": float(linear.C),
        "class_weight": str(linear.class_weight),
        "dual": bool(linear.dual),
        "n_iter": int(np.max(linear.n_iter_)) if np.ndim(linear.n_iter_)
        else int(linear.n_iter_),
        "intercept": float(np.ravel(linear.intercept_)[0]),
        "coef_l2_norm": float(np.linalg.norm(linear.coef_)),
    }
