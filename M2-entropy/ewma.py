"""
Exponentially Weighted Moving Average (EWMA) Smoothing Module for M2.

Provides generic EWMA smoothing over numerical entropy sequences and pandas DataFrames.

Mathematical Definition & EWMA Formula:
----------------------------------------
For a sequence of values V = [v_0, v_1, ..., v_{n-1}] and smoothing factor alpha in (0, 1]:

    smoothed[0] = initial (if explicitly supplied) otherwise v_0
    smoothed[t] = alpha * v_t + (1 - alpha) * smoothed[t-1]  for t >= 1

Effect of Alpha (Smoothing Factor):
------------------------------------
- High alpha (alpha -> 1.0): High responsiveness to recent changes, minimal smoothing.
  When alpha = 1.0, smoothed[t] = v_t (no smoothing, exact tracking).
- Low alpha (alpha -> 0.0): Heavy smoothing, filtering out short-term fluctuations and noise,
  giving greater weight to historical trend.

Initialization & Decoupling:
----------------------------
- By default, initial smoothing starts at v_0. An explicit `initial` value can be provided
  (e.g., historical baseline entropy) to initialize early windows.
- EWMA smoothing is kept strictly decoupled from adaptive thresholding and anomaly decision logic.
  It acts purely as a statistical noise-reduction filter over entropy time-series.
"""

from typing import Any, List, Optional, Sequence, Union

try:
    import numpy as np
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    pd = None  # type: ignore
    np = None  # type: ignore
    HAS_PANDAS = False


METADATA_COLUMNS = {
    "window_id",
    "start_idx",
    "end_idx",
    "flow_count",
    "is_complete",
    "session_id",
}


def ewma(
    values: Any,
    alpha: float,
    initial: Optional[float] = None,
) -> Any:
    """Compute Exponentially Weighted Moving Average (EWMA) over a numerical sequence.

    Parameters:
        values: Sequence of numerical values (list, tuple, np.ndarray, pd.Series).
        alpha: Smoothing factor (must satisfy 0 < alpha <= 1).
        initial: Optional explicit initial value for smoothed[0].

    Returns:
        Smoothed numerical sequence matching input type (list, np.ndarray, or pd.Series).

    Raises:
        TypeError: If alpha or values are not numeric.
        ValueError: If alpha is outside (0, 1].
    """
    _validate_alpha(alpha)

    if values is None:
        raise TypeError("Input 'values' cannot be None.")

    is_series = HAS_PANDAS and isinstance(values, pd.Series)
    is_ndarray = HAS_PANDAS and isinstance(values, np.ndarray)

    if is_series:
        seq = values.to_list()
    elif is_ndarray:
        seq = values.tolist()
    elif isinstance(values, (list, tuple)):
        seq = list(values)
    else:
        try:
            seq = list(values)
        except Exception as e:
            raise TypeError(f"Could not convert input of type {type(values).__name__} to sequence: {e}")

    if len(seq) == 0:
        if is_series:
            return pd.Series([], index=values.index, dtype=float, name=values.name)
        elif is_ndarray:
            return np.array([], dtype=float)
        return []

    # Validate all elements are numeric
    num_seq: List[float] = []
    for i, val in enumerate(seq):
        if isinstance(val, bool) or not isinstance(val, (int, float, np.number if HAS_PANDAS else int)):
            raise TypeError(f"Non-numeric value '{val}' of type {type(val).__name__} encountered at index {i}")
        if pd.isna(val) if HAS_PANDAS else (val != val):
            raise ValueError(f"NaN value encountered at index {i}")
        num_seq.append(float(val))

    if initial is not None:
        if isinstance(initial, bool) or not isinstance(initial, (int, float, np.number if HAS_PANDAS else int)):
            raise TypeError(f"Initial value must be numeric, got {type(initial).__name__}")
        init_val = float(initial)
    else:
        init_val = num_seq[0]

    smoothed: List[float] = [0.0] * len(num_seq)
    smoothed[0] = init_val

    for t in range(1, len(num_seq)):
        smoothed[t] = alpha * num_seq[t] + (1.0 - alpha) * smoothed[t - 1]

    if is_series:
        return pd.Series(smoothed, index=values.index, name=values.name)
    elif is_ndarray:
        return np.array(smoothed, dtype=float)
    return smoothed


def smooth_entropy_dataframe(
    entropy_df: Any,
    alpha: float,
    entropy_columns: Optional[List[str]] = None,
    suffix: str = "_ewma",
    initial: Optional[float] = None,
) -> Any:
    """Smooth selected entropy columns in a pandas DataFrame using EWMA.

    Parameters:
        entropy_df: Input pandas DataFrame containing window entropy results.
        alpha: Smoothing factor (must satisfy 0 < alpha <= 1).
        entropy_columns: Optional list of column names to smooth. If None, automatically
            selects all columns ending with '_entropy' (excluding metadata).
        suffix: Suffix appended to smoothed column names (default '_ewma').
        initial: Optional explicit initial value for smoothing.

    Returns:
        pandas DataFrame: New DataFrame containing original columns and smoothed EWMA columns.

    Raises:
        KeyError: If a column requested in `entropy_columns` does not exist.
        TypeError: If a selected column contains non-numeric data.
        ValueError: If alpha is invalid.
    """
    _validate_alpha(alpha)

    if not HAS_PANDAS or not isinstance(entropy_df, pd.DataFrame):
        raise TypeError(f"Expected pandas DataFrame for entropy_df, got {type(entropy_df).__name__}")

    out_df = entropy_df.copy()

    if len(entropy_df) == 0:
        if entropy_columns is None:
            target_cols = [c for c in entropy_df.columns if c.endswith("_entropy") and c not in METADATA_COLUMNS]
        else:
            target_cols = list(entropy_columns)
            for c in target_cols:
                if c not in entropy_df.columns:
                    raise KeyError(f"Requested column '{c}' not found in DataFrame.")

        for c in target_cols:
            out_df[f"{c}{suffix}"] = pd.Series([], dtype=float, index=entropy_df.index)
        return out_df

    if entropy_columns is None:
        target_cols = [c for c in entropy_df.columns if c.endswith("_entropy") and c not in METADATA_COLUMNS]
    else:
        target_cols = list(entropy_columns)
        for c in target_cols:
            if c not in entropy_df.columns:
                raise KeyError(f"Requested column '{c}' not found in DataFrame.")

    for col in target_cols:
        series = entropy_df[col]
        # Check numeric data type
        if not pd.api.types.is_numeric_dtype(series):
            raise TypeError(f"Column '{col}' is non-numeric and cannot be smoothed using EWMA.")

        smoothed_series = ewma(series, alpha=alpha, initial=initial)
        out_df[f"{col}{suffix}"] = smoothed_series

    return out_df


def _validate_alpha(alpha: float) -> None:
    """Validate that alpha is a numeric value in (0, 1]."""
    if isinstance(alpha, bool) or not isinstance(alpha, (int, float, np.number if HAS_PANDAS else int)):
        raise TypeError(f"Alpha must be numeric, got {type(alpha).__name__}")
    if alpha <= 0.0 or alpha > 1.0:
        raise ValueError(f"Alpha must satisfy 0 < alpha <= 1.0, got {alpha}")
