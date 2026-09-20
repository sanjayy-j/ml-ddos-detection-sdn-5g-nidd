"""
End-to-End Offline Pipeline Integration Module for M2 — Entropy-Based Statistical Detection.

Connects:
  Raw Flow DataFrame / CSV sample
  -> Flow-count sliding windows (windowing.py)
  -> Window-level Shannon entropy computation (window_entropy.py, features.py, entropy.py)
  -> EWMA noise-reduction smoothing (ewma.py)
  -> Adaptive baseline and MAD thresholding (thresholds.py)
  -> Final anomaly-annotated pandas DataFrame

Design Rationale:
-----------------
1. Modular, reproducible, label-free pipeline execution.
2. Target labels (Label, Attack Type, Attack Tool) are strictly isolated and never passed into feature extraction or thresholding logic.
3. Completely decoupled from evaluation metrics (ROC-AUC, Precision, Recall are excluded from detection execution).
4. Configurable parameters (nrows, window_size, step_size, EWMA alpha, threshold history, sensitivity, voting threshold).
5. Immutable execution: input DataFrame is preserved intact.
"""

from dataclasses import dataclass, field
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd

# Ensure M2-entropy is in sys.path
SYS_PATH_M2 = str(Path(__file__).resolve().parent)
if SYS_PATH_M2 not in sys.path:
    sys.path.insert(0, SYS_PATH_M2)

from ewma import METADATA_COLUMNS as EWMA_METADATA_COLS, smooth_entropy_dataframe
from features import DEFAULT_EXCLUDE_COLS, FeatureConfig
from thresholds import AdaptiveThresholdEngine, ThresholdConfig
from window_entropy import compute_entropy_over_windows
from windowing import generate_flow_windows


@dataclass
class PipelineConfig:
    """Configuration container for end-to-end M2 offline entropy pipeline.

    Attributes:
        input_path: Path to input CSV file.
        df: Direct input pandas DataFrame (overrides input_path if provided).
        nrows: Number of rows to read from CSV if loading from file (default 5000 for safe sample).
        window_size: Number of flow records per sliding window (default 100).
        step_size: Number of flow records to advance between windows (default 50).
        drop_incomplete: If True, partial final windows are omitted (default False).
        alpha: EWMA smoothing factor in (0, 1] (default 0.2).
        feature_config: Custom FeatureConfig instance (or default if None).
        threshold_config: Custom ThresholdConfig instance (or default if None).
        session_col: Optional column name for session-aware windowing & threshold resets.
        output_path: Optional CSV output path to save window results.
        label_cols: Ground-truth target columns to preserve for evaluation-only tracking.
    """

    input_path: Optional[str] = None
    df: Optional[pd.DataFrame] = None
    nrows: Optional[int] = 5000
    window_size: int = 100
    step_size: int = 50
    drop_incomplete: bool = False
    alpha: float = 0.2
    feature_config: Optional[FeatureConfig] = None
    threshold_config: Optional[ThresholdConfig] = None
    session_col: Optional[str] = None
    output_path: Optional[str] = None
    label_cols: List[str] = field(
        default_factory=lambda: ["Label", "Attack Type", "Attack Tool"]
    )


@dataclass
class PipelineResult:
    """Structured container holding pipeline execution results.

    Attributes:
        input_row_count: Total number of rows processed from input dataset.
        number_of_windows: Total number of generated sliding windows.
        number_of_complete_windows: Count of windows containing full `window_size` flows.
        entropy_columns: List of raw feature entropy column names.
        ewma_columns: List of EWMA-smoothed entropy column names.
        output_df: Processed pandas DataFrame containing metadata, entropy, EWMA, thresholds, and anomaly decisions.
        output_path: Saved output CSV file path (if saved).
        config: PipelineConfig instance used for execution.
    """

    input_row_count: int
    number_of_windows: int
    number_of_complete_windows: int
    entropy_columns: List[str]
    ewma_columns: List[str]
    output_df: pd.DataFrame
    output_path: Optional[str]
    config: PipelineConfig


def run_entropy_pipeline(config: Optional[PipelineConfig] = None) -> PipelineResult:
    """Execute the end-to-end M2 offline entropy-based statistical detection pipeline.

    Parameters:
        config: Optional PipelineConfig object. Uses defaults if None.

    Returns:
        PipelineResult dataclass containing execution metrics and final output DataFrame.

    Raises:
        ValueError: If neither df nor input_path is supplied, or parameters are invalid.
        FileNotFoundError: If input_path does not exist.
    """
    cfg = config or PipelineConfig()
    feat_cfg = cfg.feature_config or FeatureConfig()
    thresh_cfg = cfg.threshold_config or ThresholdConfig()

    # Step A: Load flow data sample or use provided DataFrame
    if cfg.df is not None:
        source_df = cfg.df.copy()
    elif cfg.input_path is not None:
        if not os.path.exists(cfg.input_path):
            raise FileNotFoundError(f"Input CSV file not found: {cfg.input_path}")
        source_df = pd.read_csv(cfg.input_path, nrows=cfg.nrows)
    else:
        raise ValueError("Either 'df' or 'input_path' must be provided in PipelineConfig.")

    input_row_count = len(source_df)

    # Step B: Ground-truth isolation (preserve label columns for evaluation tracking only if present)
    # Target label columns are NEVER passed into feature extraction or detection logic
    present_label_cols = [c for c in cfg.label_cols if c in source_df.columns]

    # Determine session column availability
    session_col_to_use = cfg.session_col
    if session_col_to_use is None:
        if "session_id" in source_df.columns:
            session_col_to_use = "session_id"
        elif "session" in source_df.columns:
            session_col_to_use = "session"

    if session_col_to_use and session_col_to_use not in source_df.columns:
        raise KeyError(f"Configured session column '{session_col_to_use}' not found in DataFrame.")

    # Step C: Generate flow-count sliding windows
    windows_gen = generate_flow_windows(
        df=source_df,
        window_size=cfg.window_size,
        step_size=cfg.step_size,
        drop_incomplete=cfg.drop_incomplete,
        session_col=session_col_to_use,
    )
    windows_list = list(windows_gen)

    n_windows = len(windows_list)
    n_complete = sum(1 for w in windows_list if w.is_complete)

    # Handle case with no windows generated
    if n_windows == 0:
        empty_out = pd.DataFrame(
            columns=[
                "window_id",
                "start_idx",
                "end_idx",
                "flow_count",
                "is_complete",
                "session_id",
                "threshold_is_warmup",
                "threshold_is_valid",
                "threshold_alarm_count",
                "window_anomaly",
            ]
        )
        return PipelineResult(
            input_row_count=input_row_count,
            number_of_windows=0,
            number_of_complete_windows=0,
            entropy_columns=[],
            ewma_columns=[],
            output_df=empty_out,
            output_path=None,
            config=cfg,
        )

    # Step D & E: Compute window-level entropy scores
    raw_entropy_df = compute_entropy_over_windows(
        windows=windows_list,
        feature_config=feat_cfg,
        base=2.0,
        as_dataframe=True,
    )

    if not isinstance(raw_entropy_df, pd.DataFrame):
        raw_entropy_df = pd.DataFrame(raw_entropy_df)

    # Identify raw entropy columns
    raw_entropy_cols = [
        c for c in raw_entropy_df.columns
        if c.endswith("_entropy") and c not in EWMA_METADATA_COLS
    ]

    # Step F & G: Apply EWMA smoothing
    smoothed_df = smooth_entropy_dataframe(
        entropy_df=raw_entropy_df,
        alpha=cfg.alpha,
        entropy_columns=raw_entropy_cols,
        suffix="_ewma",
    )

    ewma_cols = [
        c for c in smoothed_df.columns
        if c.endswith("_entropy_ewma") and c not in EWMA_METADATA_COLS
    ]

    # Step H & I: Adaptive thresholding and anomaly decision
    engine = AdaptiveThresholdEngine(config=thresh_cfg)
    final_df = engine.process_series(
        entropy_df=smoothed_df,
        entropy_columns=ewma_cols if ewma_cols else None,
    )

    # Step J: Save CSV result if output_path is specified
    saved_path: Optional[str] = None
    if cfg.output_path:
        out_dir = os.path.dirname(os.path.abspath(cfg.output_path))
        os.makedirs(out_dir, exist_ok=True)
        final_df.to_csv(cfg.output_path, index=False)
        saved_path = cfg.output_path

    return PipelineResult(
        input_row_count=input_row_count,
        number_of_windows=n_windows,
        number_of_complete_windows=n_complete,
        entropy_columns=raw_entropy_cols,
        ewma_columns=ewma_cols,
        output_df=final_df,
        output_path=saved_path,
        config=cfg,
    )
