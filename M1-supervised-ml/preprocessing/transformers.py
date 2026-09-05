"""Stage D — the fitted preprocessing transformation.

A single canonical feature representation is produced and shared by all
three M1 models, so that Random Forest, SVM and the 1-D CNN see exactly
the same information in exactly the same column order. Only the final
model-specific handling differs (see pipeline.py).

Numeric path:  median impute -> skew-gated log1p -> standardise
Categorical path: constant '__missing__' -> one-hot

Everything is fitted on the TRAINING split only.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .features import get_categorical_columns, get_numeric_columns

MISSING_CATEGORY = "__missing__"


class SkewedLog1pTransformer(BaseEstimator, TransformerMixin):
    """Apply log1p only to heavy-tailed, non-negative columns.

    5G-NIDD flow statistics are extremely heavy-tailed (`Load` skew ~188,
    `DstRate` ~191, `TotBytes` ~21) which would otherwise dominate the
    scaled representation and cripple the distance-based SVM and the CNN.
    Transforming *every* column would needlessly distort already
    well-behaved features, so the decision is made per column from the
    TRAINING data only:

        log1p is applied iff  training skew > threshold  AND  min >= 0

    The non-negativity guard keeps log1p mathematically valid; all
    retained 5G-NIDD numeric features were verified non-negative.
    """

    def __init__(self, skew_threshold: float = 2.0):
        self.skew_threshold = skew_threshold

    @staticmethod
    def _skew(x: np.ndarray) -> np.ndarray:
        """Population skewness per column, NaN-safe, 0 for constant columns."""
        mean = np.nanmean(x, axis=0)
        centered = x - mean
        std = np.sqrt(np.nanmean(centered**2, axis=0))
        with np.errstate(divide="ignore", invalid="ignore"):
            skew = np.nanmean(centered**3, axis=0) / (std**3)
        return np.where(std > 0, np.nan_to_num(skew), 0.0)

    def fit(self, X, y=None):
        arr = np.asarray(X, dtype=np.float64)
        self.n_features_in_ = arr.shape[1]
        minimums = np.nanmin(arr, axis=0)
        skews = self._skew(arr)
        self.skews_ = skews
        self.log_mask_ = (skews > self.skew_threshold) & (minimums >= 0)
        return self

    def transform(self, X):
        arr = np.asarray(X, dtype=np.float64).copy()
        if arr.shape[1] != self.n_features_in_:
            raise ValueError(
                f"Expected {self.n_features_in_} columns, got {arr.shape[1]}."
            )
        if self.log_mask_.any():
            arr[:, self.log_mask_] = np.log1p(arr[:, self.log_mask_])
        return arr

    def get_feature_names_out(self, input_features=None):
        # column count and order are unchanged by this transformer
        return np.asarray(input_features, dtype=object)


def build_preprocessor(config: dict[str, Any]) -> ColumnTransformer:
    """Build the (unfitted) canonical M1 preprocessing transformer."""
    pre_cfg = config.get("preprocessing") or {}
    numeric = get_numeric_columns(config)
    categorical = get_categorical_columns(config)

    numeric_pipeline = Pipeline(
        [
            # keep_empty_features guarantees a fixed output width even if a
            # column is entirely missing in the training split
            (
                "impute",
                SimpleImputer(
                    strategy=pre_cfg.get("numeric_imputation", "median"),
                    keep_empty_features=True,
                ),
            ),
            (
                "log1p",
                SkewedLog1pTransformer(
                    skew_threshold=float(pre_cfg.get("log1p_skew_threshold", 2.0))
                ),
            ),
            ("scale", StandardScaler()),
        ]
    )

    categorical_pipeline = Pipeline(
        [
            (
                "impute",
                SimpleImputer(
                    strategy="constant",
                    fill_value=pre_cfg.get("categorical_imputation", MISSING_CATEGORY),
                ),
            ),
            (
                "onehot",
                # handle_unknown='ignore' => categories unseen in training
                # become an all-zero row rather than an error at transform time
                OneHotEncoder(
                    handle_unknown="ignore",
                    sparse_output=False,
                    dtype=np.float32,
                ),
            ),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, numeric),
            ("categorical", categorical_pipeline, categorical),
        ],
        remainder="drop",  # nothing outside the declared feature list can leak in
        verbose_feature_names_out=False,
    )


def get_output_feature_names(preprocessor: ColumnTransformer) -> list[str]:
    """Final feature ordering after fitting (numeric block, then one-hot)."""
    return [str(name) for name in preprocessor.get_feature_names_out()]
