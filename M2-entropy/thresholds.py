"""
Adaptive Baseline and Threshold Engine for M2 — Entropy-Based Statistical Detection.

Provides robust, label-free statistical thresholding over EWMA-smoothed entropy series
using rolling Median and Median Absolute Deviation (MAD).

Design Rationale:
-----------------
1. Operating in a strictly label-free, unsupervised environment, detection thresholds
   adapt dynamically to baseline traffic changes rather than using static hard-coded limits.
2. Uses Median and MAD instead of Mean and Standard Deviation to ensure robust baseline
   estimation resistant to outlier pollution from attack bursts.
3. Strict temporal causality: threshold for window t is calculated ONLY from previous valid
   historical observations [t - H, t - 1]. Current values NEVER influence their own threshold.
4. Multithreshold consensus voting: combines independent feature alarms (Proto, State, sTtl, TotPkts_bin)
   using a voting threshold to generate window-level anomaly decisions.
5. Target metadata and labels (Label, Attack Type, Attack Tool) are NEVER used in detection logic.
"""

from collections import deque
from dataclasses import dataclass, field
import math
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import numpy as np

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    pd = None  # type: ignore
    HAS_PANDAS = False


METADATA_COLUMNS: Set[str] = {
    "window_id",
    "start_idx",
    "end_idx",
    "flow_count",
    "is_complete",
    "session_id",
}


@dataclass
class ThresholdConfig:
    """Configuration dataclass for Adaptive Baseline and Threshold Engine.

    Attributes:
        history_len: Maximum number of historical observations to retain in rolling buffer (>= 1).
        min_history: Number of historical windows required for warm-up phase (>= 1, <= history_len).
        min_valid_history: Minimum valid historical values required to compute baseline/MAD (>= 1).
        k_sensitivity: Sensitivity multiplier for scaled MAD (> 0).
        mad_floor: Minimum floor for MAD to handle constant zero-variability histories (> 0).
        direction: Detection direction ('lower', 'upper', or 'both').
        voting_threshold: Minimum number of feature alarms required for window anomaly (>= 1).
        warmup_policy: Action during warm-up phase ('suppress' or 'expanding').
        session_col: Optional column name for resetting historical buffers at session boundaries.
    """

    history_len: int = 50
    min_history: int = 10
    k_sensitivity: float = 3.0
    mad_floor: float = 1e-4
    direction: str = "both"
    voting_threshold: int = 2
    warmup_policy: str = "suppress"
    min_valid_history: int = 10
    session_col: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate configuration settings after initialization."""
        self.validate()

    def validate(self) -> None:
        """Validate parameter types and value bounds."""
        if not isinstance(self.history_len, int) or isinstance(self.history_len, bool):
            raise TypeError(f"history_len must be an integer, got {type(self.history_len).__name__}")
        if self.history_len < 1:
            raise ValueError(f"history_len must be >= 1, got {self.history_len}")

        if not isinstance(self.min_history, int) or isinstance(self.min_history, bool):
            raise TypeError(f"min_history must be an integer, got {type(self.min_history).__name__}")
        if self.min_history < 1:
            raise ValueError(f"min_history must be >= 1, got {self.min_history}")

        if not isinstance(self.min_valid_history, int) or isinstance(self.min_valid_history, bool):
            raise TypeError(f"min_valid_history must be an integer, got {type(self.min_valid_history).__name__}")
        if self.min_valid_history < 1:
            raise ValueError(f"min_valid_history must be >= 1, got {self.min_valid_history}")

        if self.min_history > self.history_len:
            raise ValueError(f"min_history ({self.min_history}) cannot exceed history_len ({self.history_len})")

        if self.min_valid_history > self.history_len:
            raise ValueError(f"min_valid_history ({self.min_valid_history}) cannot exceed history_len ({self.history_len})")

        if (
            not isinstance(self.k_sensitivity, (int, float))
            or isinstance(self.k_sensitivity, bool)
            or math.isnan(self.k_sensitivity)
        ):
            raise TypeError(f"k_sensitivity must be a numeric float/int, got {type(self.k_sensitivity).__name__}")
        if self.k_sensitivity <= 0:
            raise ValueError(f"k_sensitivity must be > 0, got {self.k_sensitivity}")

        if (
            not isinstance(self.mad_floor, (int, float))
            or isinstance(self.mad_floor, bool)
            or math.isnan(self.mad_floor)
        ):
            raise TypeError(f"mad_floor must be a numeric float/int, got {type(self.mad_floor).__name__}")
        if self.mad_floor <= 0:
            raise ValueError(f"mad_floor must be > 0, got {self.mad_floor}")

        valid_directions = {"lower", "upper", "both"}
        if self.direction not in valid_directions:
            raise ValueError(f"Invalid direction '{self.direction}'. Must be one of {sorted(valid_directions)}")

        valid_policies = {"suppress", "expanding"}
        if self.warmup_policy not in valid_policies:
            raise ValueError(f"Invalid warmup_policy '{self.warmup_policy}'. Must be one of {sorted(valid_policies)}")

        if not isinstance(self.voting_threshold, int) or isinstance(self.voting_threshold, bool):
            raise TypeError(f"voting_threshold must be an integer, got {type(self.voting_threshold).__name__}")
        if self.voting_threshold < 1:
            raise ValueError(f"voting_threshold must be >= 1, got {self.voting_threshold}")


@dataclass
class ThresholdResult:
    """Dataclass holding evaluation result and adaptive thresholds for a single window.

    Attributes:
        window_id: 0-indexed window identifier.
        start_idx: Positional start index in source dataset.
        end_idx: Positional end index in source dataset.
        flow_count: Number of flow records in this window.
        is_warmup: True if threshold calculation is in warm-up phase.
        is_valid: True if current observation is valid (non-NaN, finite).
        feature_alarms: Dict mapping feature name to boolean alarm flag.
        baselines: Dict mapping feature name to baseline median.
        thresholds_lower: Dict mapping feature name to lower threshold.
        thresholds_upper: Dict mapping feature name to upper threshold.
        mads: Dict mapping feature name to raw MAD.
        feature_valid: Dict mapping feature name to boolean validity flag.
        window_anomaly: True if feature_alarm count >= voting_threshold.
        session_id: Optional session identifier.
    """

    window_id: int = 0
    start_idx: int = 0
    end_idx: int = 0
    flow_count: int = 0
    is_warmup: bool = False
    is_valid: bool = True
    feature_alarms: Dict[str, bool] = field(default_factory=dict)
    baselines: Dict[str, float] = field(default_factory=dict)
    thresholds_lower: Dict[str, float] = field(default_factory=dict)
    thresholds_upper: Dict[str, float] = field(default_factory=dict)
    mads: Dict[str, float] = field(default_factory=dict)
    feature_valid: Dict[str, bool] = field(default_factory=dict)
    window_anomaly: bool = False
    session_id: Optional[Any] = None

    def to_dict(self) -> Dict[str, Any]:
        """Flatten metadata, feature statistics, and overall anomaly flags to a dict."""
        record: Dict[str, Any] = {
            "window_id": self.window_id,
            "start_idx": self.start_idx,
            "end_idx": self.end_idx,
            "flow_count": self.flow_count,
            "is_warmup": self.is_warmup,
            "is_valid": self.is_valid,
            "session_id": self.session_id,
        }
        for col, val in self.baselines.items():
            record[f"{col}_baseline"] = val
            record[f"{col}_mad"] = self.mads.get(col, np.nan if HAS_PANDAS else float("nan"))
            record[f"{col}_threshold_lower"] = self.thresholds_lower.get(col, np.nan if HAS_PANDAS else float("nan"))
            record[f"{col}_threshold_upper"] = self.thresholds_upper.get(col, np.nan if HAS_PANDAS else float("nan"))
            record[f"{col}_alarm"] = self.feature_alarms.get(col, False)
            record[f"{col}_valid"] = self.feature_valid.get(col, True)

        alarm_count = sum(1 for a in self.feature_alarms.values() if a)
        record["threshold_is_warmup"] = self.is_warmup
        record["threshold_is_valid"] = self.is_valid
        record["threshold_alarm_count"] = alarm_count
        record["window_anomaly"] = self.window_anomaly
        return record


class AdaptiveThresholdEngine:
    """Engine for historical baseline estimation, MAD thresholding, and consensus voting."""

    def __init__(self, config: Optional[ThresholdConfig] = None):
        """Initialize engine with configuration."""
        self.config = config or ThresholdConfig()

    def process_series(
        self,
        entropy_df: Any,
        entropy_columns: Optional[List[str]] = None,
    ) -> Any:
        """Process DataFrame of EWMA-smoothed entropy series and calculate adaptive thresholds.

        Parameters:
            entropy_df: pandas DataFrame containing entropy series and metadata.
            entropy_columns: Optional list of column names to evaluate. If None, automatically
                selects all columns ending with '_ewma' or '_entropy' (excluding metadata).

        Returns:
            pandas DataFrame containing original data plus baseline, threshold, alarm, and anomaly columns.

        Raises:
            TypeError: If entropy_df is not a DataFrame or column is non-numeric.
            KeyError: If a column in entropy_columns is missing.
            ValueError: If fewer features exist than voting_threshold.
        """
        if not HAS_PANDAS or not isinstance(entropy_df, pd.DataFrame):
            raise TypeError(f"Expected pandas DataFrame for entropy_df, got {type(entropy_df).__name__}")

        out_df = entropy_df.copy()

        # Identify target entropy columns
        if entropy_columns is None:
            target_cols = [
                c for c in entropy_df.columns
                if (c.endswith("_ewma") or c.endswith("_entropy")) and c not in METADATA_COLUMNS
            ]
        else:
            target_cols = list(entropy_columns)
            for c in target_cols:
                if c not in entropy_df.columns:
                    raise KeyError(f"Requested column '{c}' not found in DataFrame.")

        if len(target_cols) < self.config.voting_threshold:
            raise ValueError(
                f"Insufficient selected features ({len(target_cols)}) for "
                f"voting_threshold ({self.config.voting_threshold})."
            )

        for c in target_cols:
            if not pd.api.types.is_numeric_dtype(entropy_df[c]):
                raise TypeError(f"Column '{c}' is non-numeric and cannot be evaluated for thresholds.")

        # Handle empty DataFrame
        if len(entropy_df) == 0:
            for c in target_cols:
                out_df[f"{c}_baseline"] = pd.Series([], dtype=float, index=entropy_df.index)
                out_df[f"{c}_mad"] = pd.Series([], dtype=float, index=entropy_df.index)
                out_df[f"{c}_threshold_lower"] = pd.Series([], dtype=float, index=entropy_df.index)
                out_df[f"{c}_threshold_upper"] = pd.Series([], dtype=float, index=entropy_df.index)
                out_df[f"{c}_alarm"] = pd.Series([], dtype=bool, index=entropy_df.index)
                out_df[f"{c}_valid"] = pd.Series([], dtype=bool, index=entropy_df.index)

            out_df["threshold_is_warmup"] = pd.Series([], dtype=bool, index=entropy_df.index)
            out_df["threshold_is_valid"] = pd.Series([], dtype=bool, index=entropy_df.index)
            out_df["threshold_alarm_count"] = pd.Series([], dtype=int, index=entropy_df.index)
            out_df["window_anomaly"] = pd.Series([], dtype=bool, index=entropy_df.index)
            return out_df

        session_col = self.config.session_col
        if session_col is None:
            if "session_id" in entropy_df.columns:
                session_col = "session_id"
            elif "session" in entropy_df.columns:
                session_col = "session"

        buffers: Dict[str, deque] = {c: deque(maxlen=self.config.history_len) for c in target_cols}
        prev_session = None

        feature_outputs: Dict[str, Dict[str, List[Any]]] = {
            c: {
                "baseline": [],
                "mad": [],
                "threshold_lower": [],
                "threshold_upper": [],
                "alarm": [],
                "valid": [],
            }
            for c in target_cols
        }
        is_warmup_list: List[bool] = []
        is_valid_list: List[bool] = []
        alarm_count_list: List[int] = []
        window_anomaly_list: List[bool] = []

        for idx_pos, (orig_idx, row) in enumerate(entropy_df.iterrows()):
            curr_session = row[session_col] if session_col and session_col in entropy_df.columns else None
            if session_col and session_col in entropy_df.columns and idx_pos > 0 and curr_session != prev_session:
                for c in target_cols:
                    buffers[c].clear()
            prev_session = curr_session

            row_is_valid = True
            alarms_this_row: Dict[str, bool] = {}
            warmup_this_row_flags: List[bool] = []

            for c in target_cols:
                raw_val = row[c]
                val_valid = (
                    pd.notna(raw_val)
                    and not math.isinf(float(raw_val))
                    and not isinstance(raw_val, bool)
                )
                if not val_valid:
                    row_is_valid = False

                hist_valid = [v for v in buffers[c] if pd.notna(v) and not math.isinf(v)]
                n_valid_hist = len(hist_valid)

                # Warmup logic
                req_history = self.config.min_history
                if self.config.warmup_policy == "expanding":
                    req_history = self.config.min_valid_history

                if n_valid_hist < req_history or idx_pos < req_history:
                    feat_warmup = True
                    baseline = np.nan
                    mad = np.nan
                    lower_thresh = np.nan
                    upper_thresh = np.nan
                    alarm = False
                else:
                    feat_warmup = False
                    arr_hist = np.array(hist_valid, dtype=float)
                    baseline = float(np.median(arr_hist))
                    mad = float(np.median(np.abs(arr_hist - baseline)))
                    scaled_mad = 1.4826 * max(mad, self.config.mad_floor)
                    lower_thresh = baseline - self.config.k_sensitivity * scaled_mad
                    upper_thresh = baseline + self.config.k_sensitivity * scaled_mad

                    if val_valid:
                        c_val = float(raw_val)
                        if self.config.direction == "lower":
                            alarm = bool(c_val < lower_thresh)
                        elif self.config.direction == "upper":
                            alarm = bool(c_val > upper_thresh)
                        else:  # 'both'
                            alarm = bool(c_val < lower_thresh or c_val > upper_thresh)
                    else:
                        alarm = False

                warmup_this_row_flags.append(feat_warmup)
                alarms_this_row[c] = alarm

                feature_outputs[c]["baseline"].append(baseline)
                feature_outputs[c]["mad"].append(mad)
                feature_outputs[c]["threshold_lower"].append(lower_thresh)
                feature_outputs[c]["threshold_upper"].append(upper_thresh)
                feature_outputs[c]["alarm"].append(alarm)
                feature_outputs[c]["valid"].append(val_valid)

            row_is_warmup = any(warmup_this_row_flags)
            alarm_count = sum(1 for a in alarms_this_row.values() if a)

            if row_is_warmup or not row_is_valid:
                window_anomaly = False
            else:
                window_anomaly = alarm_count >= self.config.voting_threshold

            is_warmup_list.append(row_is_warmup)
            is_valid_list.append(row_is_valid)
            alarm_count_list.append(alarm_count)
            window_anomaly_list.append(window_anomaly)

            # Step 4: PUSH current valid observation into historical buffer AFTER evaluation
            for c in target_cols:
                raw_val = row[c]
                val_valid = (
                    pd.notna(raw_val)
                    and not math.isinf(float(raw_val))
                    and not isinstance(raw_val, bool)
                )
                if val_valid:
                    buffers[c].append(float(raw_val))

        for c in target_cols:
            out_df[f"{c}_baseline"] = pd.Series(feature_outputs[c]["baseline"], index=entropy_df.index)
            out_df[f"{c}_mad"] = pd.Series(feature_outputs[c]["mad"], index=entropy_df.index)
            out_df[f"{c}_threshold_lower"] = pd.Series(feature_outputs[c]["threshold_lower"], index=entropy_df.index)
            out_df[f"{c}_threshold_upper"] = pd.Series(feature_outputs[c]["threshold_upper"], index=entropy_df.index)
            out_df[f"{c}_alarm"] = pd.Series(feature_outputs[c]["alarm"], index=entropy_df.index)
            out_df[f"{c}_valid"] = pd.Series(feature_outputs[c]["valid"], index=entropy_df.index)

        out_df["threshold_is_warmup"] = pd.Series(is_warmup_list, index=entropy_df.index)
        out_df["threshold_is_valid"] = pd.Series(is_valid_list, index=entropy_df.index)
        out_df["threshold_alarm_count"] = pd.Series(alarm_count_list, index=entropy_df.index)
        out_df["window_anomaly"] = pd.Series(window_anomaly_list, index=entropy_df.index)

        return out_df
