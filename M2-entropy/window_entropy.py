"""
Window-Level Entropy Computation Module for M2 — Entropy-Based Statistical Detection.

Connects windowing.py, features.py, and entropy.py to calculate per-feature Shannon
entropy scores over flow-count sliding windows.

Design Rationale:
-----------------
1. Accepts individual `FlowWindow` objects or iterables of `FlowWindow` objects.
2. Extracts discrete categorical and binned numerical features for each window using `FeatureExtractor`.
3. Computes Shannon entropy H(X) independently for each feature using `calculate_shannon_entropy`.
4. Returns a clean, immutable result dataclass (`WindowEntropyResult`) preserving window metadata
   (window_id, start_idx, end_idx, flow_count, is_complete, session_id).
5. Does NOT mutate input window data.
6. Strictly excludes target metadata and ground-truth labels via FeatureExtractor defaults.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Union

import numpy as np

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    pd = None  # type: ignore
    HAS_PANDAS = False

from entropy import calculate_shannon_entropy
from features import FeatureConfig, FeatureExtractor
from windowing import FlowWindow


@dataclass
class WindowEntropyResult:
    """Structured container holding per-feature Shannon entropy scores and window metadata.

    Attributes:
        window_id: 0-indexed window identifier.
        start_idx: Positional start index (inclusive, 0-indexed) in the source dataset.
        end_idx: Positional end index (exclusive, 0-indexed) in the source dataset.
        flow_count: Number of flow records (rows) in this window.
        is_complete: True if the window contains exactly `window_size` flows; False if partial.
        session_id: Optional session identifier if session-aware windowing was used.
        entropy_scores: Dict mapping feature entropy names (e.g. 'Proto_entropy') to float scores.
    """

    window_id: int
    start_idx: int
    end_idx: int
    flow_count: int
    is_complete: bool
    entropy_scores: Dict[str, float] = field(default_factory=dict)
    session_id: Optional[Any] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert window metadata and per-feature entropy scores to a flat dictionary."""
        d = {
            "window_id": self.window_id,
            "start_idx": self.start_idx,
            "end_idx": self.end_idx,
            "flow_count": self.flow_count,
            "is_complete": self.is_complete,
            "session_id": self.session_id,
        }
        d.update(self.entropy_scores)
        return d


def compute_window_entropy(
    window: FlowWindow,
    feature_config: Optional[FeatureConfig] = None,
    base: float = 2.0,
) -> WindowEntropyResult:
    """Compute Shannon entropy for all extracted features over a single FlowWindow.

    Parameters:
        window: A FlowWindow instance containing data slice and positional metadata.
        feature_config: Optional FeatureConfig specifying feature selection & binning settings.
        base: Logarithm base for Shannon entropy (default 2.0 for bits).

    Returns:
        WindowEntropyResult containing window metadata and per-feature entropy scores.

    Raises:
        TypeError: If window is not a FlowWindow instance.
    """
    if not isinstance(window, FlowWindow):
        raise TypeError(f"Expected FlowWindow instance for 'window', got {type(window).__name__}")

    extractor = FeatureExtractor(config=feature_config)

    # Support DataFrame, Series, or generic dictionary/sequence in window.data
    data_slice = window.data

    if HAS_PANDAS and isinstance(data_slice, pd.DataFrame):
        df_input = data_slice.copy()
    elif HAS_PANDAS and isinstance(data_slice, pd.Series):
        df_input = data_slice.to_frame().copy()
    elif isinstance(data_slice, dict):
        df_input = pd.DataFrame(data_slice) if HAS_PANDAS else data_slice
    elif isinstance(data_slice, (list, tuple, np.ndarray)):
        df_input = pd.DataFrame({"value": data_slice}) if HAS_PANDAS else data_slice
    else:
        df_input = pd.DataFrame(data_slice) if HAS_PANDAS else data_slice

    # Extract features
    if HAS_PANDAS and isinstance(df_input, pd.DataFrame):
        feature_df = extractor.extract_features(df_input)

        entropy_scores: Dict[str, float] = {}
        if len(feature_df) == 0:
            for col in feature_df.columns:
                score_name = f"{col}_entropy" if not col.endswith("_entropy") else col
                entropy_scores[score_name] = 0.0
        else:
            for col in feature_df.columns:
                score_name = f"{col}_entropy" if not col.endswith("_entropy") else col
                series = feature_df[col]
                score = calculate_shannon_entropy(series, base=base)
                entropy_scores[score_name] = float(score)
    else:
        # Fallback sequence handling if pandas is absent
        entropy_scores = {}
        score = calculate_shannon_entropy(data_slice, base=base)
        entropy_scores["sequence_entropy"] = float(score)

    return WindowEntropyResult(
        window_id=window.window_id,
        start_idx=window.start_idx,
        end_idx=window.end_idx,
        flow_count=window.flow_count,
        is_complete=window.is_complete,
        session_id=window.session_id,
        entropy_scores=entropy_scores,
    )


def compute_entropy_over_windows(
    windows: Iterable[FlowWindow],
    feature_config: Optional[FeatureConfig] = None,
    base: float = 2.0,
    as_dataframe: bool = False,
) -> Union[List[WindowEntropyResult], Any]:
    """Compute per-window entropy scores over an iterable of FlowWindow objects.

    Parameters:
        windows: Iterable yielding FlowWindow objects.
        feature_config: Optional FeatureConfig specifying feature selection & binning.
        base: Logarithm base for Shannon entropy (default 2.0).
        as_dataframe: If True, return results as a pandas DataFrame (if pandas is installed).
            If False, return a List[WindowEntropyResult].

    Returns:
        List[WindowEntropyResult] or pandas DataFrame.
    """
    results: List[WindowEntropyResult] = []
    for win in windows:
        res = compute_window_entropy(window=win, feature_config=feature_config, base=base)
        results.append(res)

    if as_dataframe and HAS_PANDAS:
        if not results:
            return pd.DataFrame(
                columns=[
                    "window_id",
                    "start_idx",
                    "end_idx",
                    "flow_count",
                    "is_complete",
                    "session_id",
                ]
            )
        flat_records = [r.to_dict() for r in results]
        return pd.DataFrame(flat_records)

    return results
