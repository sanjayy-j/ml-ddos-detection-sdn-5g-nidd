"""
Feature Extraction and Discretization Module for M2 — Entropy-Based Statistical Detection.

Provides modular feature validation, categorical extraction, numerical discretization (binning),
and missing-value handling for flow records prior to Shannon entropy calculation.

Design Rationale:
-----------------
1. Standard network flow datasets (e.g., 5G-NIDD Combined.csv) contain both nominal categorical
   fields (Proto, State, sDSb) and high-cardinality continuous numeric fields (TotPkts, TotBytes, Rate, Dur).
2. Direct Shannon entropy over high-cardinality continuous floats spreads probability mass thin,
   yielding uninformative entropy scores. Discretizing numerical features into quantile/uniform bins
   produces discrete categorical distributions suitable for Shannon entropy calculation.
3. Row order, row count, and original DataFrame index are strictly preserved.
4. Target and metadata fields (Label, Attack Type, Attack Tool, Offset, Seq, Unnamed: 0) are excluded
   by default to prevent ground-truth leakage or acquisition artifact bias.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import numpy as np
import pandas as pd


DEFAULT_EXCLUDE_COLS: List[str] = [
    "Label",
    "Attack Type",
    "Attack Tool",
    "Unnamed: 0",
    "Seq",
    "Offset",
]


@dataclass
class FeatureConfig:
    """Configuration container for feature extraction and numerical discretization.

    Attributes:
        categorical_cols: List of column names to extract as discrete categorical features.
        numerical_cols: List of numerical column names to discretize into categorical bins.
        n_bins: Number of bins for numerical discretization (default 5).
        binning_strategy: Strategy for binning ('quantile', 'uniform', 'log_quantile', 'custom').
        custom_bins: Dict mapping column names to explicit bin boundary lists.
        categorical_missing_fill: String token used for missing categorical entries.
        numeric_missing_fill: Policy for missing numeric values ('median', 'zero', 'mean').
        exclude_cols: List of columns barred from entropy feature matrices.
    """

    categorical_cols: List[str] = field(
        default_factory=lambda: ["Proto", "State", "sTtl", "sDSb"]
    )
    numerical_cols: List[str] = field(
        default_factory=lambda: ["TotPkts", "TotBytes", "Rate", "Dur"]
    )
    n_bins: int = 5
    binning_strategy: str = "quantile"
    custom_bins: Dict[str, List[float]] = field(default_factory=dict)
    categorical_missing_fill: str = "__missing__"
    numeric_missing_fill: str = "median"
    exclude_cols: List[str] = field(default_factory=lambda: list(DEFAULT_EXCLUDE_COLS))


class FeatureExtractor:
    """Extractor class for feature validation, categorical extraction, and numerical discretization."""

    VALID_BINNING_STRATEGIES: Set[str] = {"quantile", "uniform", "log_quantile", "custom"}
    VALID_NUMERIC_FILL_STRATEGIES: Set[str] = {"median", "zero", "mean"}

    def __init__(self, config: Optional[FeatureConfig] = None):
        """Initialize FeatureExtractor with optional configuration."""
        self.config = config or FeatureConfig()
        self._validate_config()

    def _validate_config(self) -> None:
        """Validate configuration settings."""
        if self.config.n_bins < 2:
            raise ValueError(f"n_bins must be >= 2, got {self.config.n_bins}")

        if self.config.binning_strategy not in self.VALID_BINNING_STRATEGIES:
            raise ValueError(
                f"Invalid binning_strategy '{self.config.binning_strategy}'. "
                f"Must be one of {sorted(self.VALID_BINNING_STRATEGIES)}"
            )

        if self.config.numeric_missing_fill not in self.VALID_NUMERIC_FILL_STRATEGIES:
            raise ValueError(
                f"Invalid numeric_missing_fill '{self.config.numeric_missing_fill}'. "
                f"Must be one of {sorted(self.VALID_NUMERIC_FILL_STRATEGIES)}"
            )

        if self.config.binning_strategy == "custom":
            for col in self.config.numerical_cols:
                if col not in self.config.custom_bins:
                    raise ValueError(
                        f"Custom binning requested, but missing bin boundaries for column '{col}'"
                    )

    def validate_columns(
        self,
        df: pd.DataFrame,
        allow_excluded: bool = False,
    ) -> Tuple[List[str], List[str]]:
        """Validate requested feature columns against DataFrame columns.

        Parameters:
            df: Input pandas DataFrame.
            allow_excluded: If True, bypass exclusion checks (for evaluation-only uses).

        Returns:
            Tuple of (valid_categorical_cols, valid_numerical_cols).

        Raises:
            KeyError: If a requested column does not exist in df.columns.
            ValueError: If a requested column is in exclude_cols and allow_excluded is False.
        """
        exclude_set = set(self.config.exclude_cols) if not allow_excluded else set()

        valid_cat: List[str] = []
        for col in self.config.categorical_cols:
            if col in exclude_set:
                raise ValueError(
                    f"Column '{col}' is in the excluded list and cannot be used for entropy extraction."
                )
            if col not in df.columns:
                raise KeyError(f"Requested categorical column '{col}' not found in DataFrame columns.")
            valid_cat.append(col)

        valid_num: List[str] = []
        for col in self.config.numerical_cols:
            if col in exclude_set:
                raise ValueError(
                    f"Column '{col}' is in the excluded list and cannot be used for entropy extraction."
                )
            if col not in df.columns:
                raise KeyError(f"Requested numerical column '{col}' not found in DataFrame columns.")
            valid_num.append(col)

        return valid_cat, valid_num

    def extract_features(
        self,
        df: pd.DataFrame,
        allow_excluded: bool = False,
    ) -> pd.DataFrame:
        """Extract categorical and discretized numerical features into a new feature DataFrame.

        Row order, row count, and index of the original DataFrame are strictly preserved.

        Parameters:
            df: Input pandas DataFrame containing flow records.
            allow_excluded: If True, bypass exclusion checks (for evaluation-only uses).

        Returns:
            pd.DataFrame: Processed categorical features ready for entropy calculation.
        """
        valid_cat, valid_num = self.validate_columns(df, allow_excluded=allow_excluded)

        if len(df) == 0:
            out_cols = [f"{c}" for c in valid_cat] + [f"{c}_bin" for c in valid_num]
            return pd.DataFrame(columns=out_cols, index=df.index)

        feature_df = pd.DataFrame(index=df.index)

        # 1. Process Categorical Columns
        for col in valid_cat:
            series = df[col].copy()
            # Handle missing categorical values explicitly
            if series.isnull().any():
                series = series.fillna(self.config.categorical_missing_fill)
            feature_df[col] = series.astype(str)

        # 2. Process Numerical Columns (Discretization / Binning)
        for col in valid_num:
            series = df[col].copy()

            # Handle missing numeric values explicitly
            if series.isnull().any():
                series = self._impute_numeric(series)

            binned_series = self._discretize_series(series, col)
            feature_df[f"{col}_bin"] = binned_series

        return feature_df

    def _impute_numeric(self, series: pd.Series) -> pd.Series:
        """Impute missing values in numeric series according to policy."""
        strategy = self.config.numeric_missing_fill
        if strategy == "median":
            fill_val = series.median()
            if pd.isna(fill_val):
                fill_val = 0.0
            return series.fillna(fill_val)
        elif strategy == "mean":
            fill_val = series.mean()
            if pd.isna(fill_val):
                fill_val = 0.0
            return series.fillna(fill_val)
        elif strategy == "zero":
            return series.fillna(0.0)
        return series

    def _discretize_series(self, series: pd.Series, col_name: str) -> pd.Series:
        """Discretize a continuous numeric series into categorical bin labels."""
        strategy = self.config.binning_strategy
        n_bins = self.config.n_bins

        if strategy == "log_quantile":
            # Apply log1p before quantile binning (safe for non-negative numerical values)
            min_val = series.min()
            if min_val < 0:
                # shift non-negative
                transformed = np.log1p(series - min_val)
            else:
                transformed = np.log1p(series)
            return self._apply_qcut(transformed, n_bins)

        elif strategy == "quantile":
            return self._apply_qcut(series, n_bins)

        elif strategy == "uniform":
            try:
                binned = pd.cut(series, bins=n_bins, labels=False, duplicates="drop")
                return binned.apply(lambda b: f"bin_{int(b)}" if pd.notna(b) else f"bin_{self.config.categorical_missing_fill}")
            except Exception:
                return pd.Series([f"bin_0"] * len(series), index=series.index)

        elif strategy == "custom":
            bins = self.config.custom_bins[col_name]
            binned = pd.cut(series, bins=bins, labels=False, include_lowest=True)
            return binned.apply(lambda b: f"bin_{int(b)}" if pd.notna(b) else f"bin_{self.config.categorical_missing_fill}")

        raise ValueError(f"Unsupported strategy '{strategy}'")

    def _apply_qcut(self, series: pd.Series, n_bins: int) -> pd.Series:
        """Apply pandas qcut safely, handling constant values / duplicate edges."""
        if series.nunique() <= 1:
            return pd.Series(["bin_0"] * len(series), index=series.index)

        try:
            binned = pd.qcut(series, q=n_bins, labels=False, duplicates="drop")
            return binned.apply(lambda b: f"bin_{int(b)}" if pd.notna(b) else f"bin_{self.config.categorical_missing_fill}")
        except Exception:
            # Fallback to uniform cut if qcut fails due to edge collisions
            try:
                binned = pd.cut(series, bins=n_bins, labels=False, duplicates="drop")
                return binned.apply(lambda b: f"bin_{int(b)}" if pd.notna(b) else f"bin_{self.config.categorical_missing_fill}")
            except Exception:
                return pd.Series(["bin_0"] * len(series), index=series.index)


def extract_categorical_and_binned_features(
    df: pd.DataFrame,
    config: Optional[FeatureConfig] = None,
    allow_excluded: bool = False,
) -> pd.DataFrame:
    """Convenience function to extract features using FeatureExtractor.

    Parameters:
        df: Input pandas DataFrame.
        config: Optional FeatureConfig instance.
        allow_excluded: If True, bypass exclusion checks.

    Returns:
        pd.DataFrame containing discrete categorical features and binned numerical features.
    """
    extractor = FeatureExtractor(config=config)
    return extractor.extract_features(df, allow_excluded=allow_excluded)
