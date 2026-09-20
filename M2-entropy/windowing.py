"""
Sliding-Window Framework for M2 — Entropy-Based Statistical Detection.

Provides fixed flow-count windowing over pandas DataFrames and generic sequences.

Flow-Count Windowing Rationale:
-------------------------------
Because standard flow dataset representations (like 5G-NIDD Combined.csv) lack
reliable absolute wall-clock timestamps or detailed packet inter-arrival times,
this framework defines sliding windows strictly in terms of sequential flow records (rows).

A flow-count window aggregates a fixed count of sequential flow records (e.g., W=100 flows),
sliding forward by a fixed step count (e.g., S=50 flows). 

Important Constraints:
- Offset is NOT treated as a physical timestamp or concurrency metric.
- Row order within the dataset is strictly preserved.
- Label and target metadata are NEVER used to determine window boundaries.
"""

from dataclasses import dataclass
from typing import Any, Generator, List, Optional, Union

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    pd = None  # type: ignore
    HAS_PANDAS = False


@dataclass
class FlowWindow:
    """Represents a single flow-count window slice of data.

    Attributes:
        window_id: 0-indexed window identifier across the execution.
        start_idx: Positional start index (inclusive, 0-indexed) in the source dataset.
        end_idx: Positional end index (exclusive, 0-indexed) in the source dataset.
        data: The data slice (DataFrame, Series, or sequence) corresponding to this window.
        session_id: Optional session identifier if session-boundary windowing was used.
        is_complete: True if the window contains exactly `window_size` flows; False if partial.
    """

    window_id: int
    start_idx: int
    end_idx: int
    data: Any
    session_id: Optional[Any] = None
    is_complete: bool = True

    @property
    def flow_count(self) -> int:
        """Return the number of flows (rows) in this window."""
        return len(self.data)


def slice_flow_windows(
    df: Any,
    window_size: int,
    step_size: int,
    drop_incomplete: bool = False,
    session_col: Optional[str] = None,
) -> List[FlowWindow]:
    """Slice a DataFrame or sequence into a list of fixed flow-count sliding windows.

    Parameters:
        df: Input pandas DataFrame, Series, or sequence containing flow records.
        window_size: Number of flow records per window (must be an integer > 0).
        step_size: Number of flow records to advance between windows (must be an integer > 0).
        drop_incomplete: If True, partial final windows containing fewer than `window_size`
            flows are omitted. If False, partial final windows (if non-empty) are retained.
        session_col: Optional column name identifying capture session blocks. When provided,
            windowing is executed within each contiguous session block independently.

    Returns:
        List[FlowWindow]: Ordered list of FlowWindow dataclass objects.

    Raises:
        ValueError: If window_size <= 0 or step_size <= 0.
        TypeError: If window_size or step_size are not integers.
        KeyError: If session_col is provided but does not exist in df.columns.
    """
    return list(
        generate_flow_windows(
            df=df,
            window_size=window_size,
            step_size=step_size,
            drop_incomplete=drop_incomplete,
            session_col=session_col,
        )
    )


def generate_flow_windows(
    df: Any,
    window_size: int,
    step_size: int,
    drop_incomplete: bool = False,
    session_col: Optional[str] = None,
) -> Generator[FlowWindow, None, None]:
    """Generator yielding fixed flow-count sliding windows from a DataFrame or sequence.

    Parameters:
        df: Input pandas DataFrame, Series, or sequence containing flow records.
        window_size: Number of flow records per window (must be an integer > 0).
        step_size: Number of flow records to advance between windows (must be an integer > 0).
        drop_incomplete: If True, partial final windows containing fewer than `window_size`
            flows are omitted. If False, partial final windows (if non-empty) are retained.
        session_col: Optional column name identifying capture session blocks. When provided,
            windowing is executed within each contiguous session block independently.

    Yields:
        FlowWindow: Dataclass containing window metadata and data slice.
    """
    _validate_window_params(window_size, step_size)

    if session_col is not None:
        if HAS_PANDAS and isinstance(df, pd.DataFrame):
            if session_col not in df.columns:
                raise KeyError(f"Session column '{session_col}' not found in DataFrame columns.")
        elif isinstance(df, dict):
            if session_col not in df:
                raise KeyError(f"Session column '{session_col}' not found in dictionary keys.")
        else:
            if not hasattr(df, "columns") or session_col not in getattr(df, "columns", []):
                raise KeyError(f"Session column '{session_col}' not found in input data.")

    total_len = len(df)
    if total_len == 0:
        return

    window_counter = 0

    if session_col is None:
        yield from _window_single_sequence(
            df=df,
            window_size=window_size,
            step_size=step_size,
            drop_incomplete=drop_incomplete,
            global_offset=0,
            start_window_id=window_counter,
            session_id=None,
        )
    else:
        # Group by contiguous session block without changing row order
        if HAS_PANDAS and isinstance(df, pd.DataFrame):
            session_series = df[session_col]
            session_changes = session_series.ne(session_series.shift()).cumsum()
            for _, group in df.groupby(session_changes, sort=False):
                session_val = group[session_col].iloc[0]
                pos_indices = df.index.get_indexer(group.index)
                global_start_offset = pos_indices[0]

                for window in _window_single_sequence(
                    df=group,
                    window_size=window_size,
                    step_size=step_size,
                    drop_incomplete=drop_incomplete,
                    global_offset=global_start_offset,
                    start_window_id=window_counter,
                    session_id=session_val,
                ):
                    yield window
                    window_counter += 1
        else:
            # Fallback grouping for non-pandas iterables/lists
            session_vals = df[session_col] if isinstance(df, dict) else [getattr(row, session_col, None) for row in df]
            curr_session = None
            group_start = 0
            for idx, sess in enumerate(session_vals):
                if idx == 0:
                    curr_session = sess
                elif sess != curr_session:
                    group_data = df[group_start:idx]
                    for window in _window_single_sequence(
                        df=group_data,
                        window_size=window_size,
                        step_size=step_size,
                        drop_incomplete=drop_incomplete,
                        global_offset=group_start,
                        start_window_id=window_counter,
                        session_id=curr_session,
                    ):
                        yield window
                        window_counter += 1
                    curr_session = sess
                    group_start = idx
            
            if group_start < total_len:
                group_data = df[group_start:total_len]
                for window in _window_single_sequence(
                    df=group_data,
                    window_size=window_size,
                    step_size=step_size,
                    drop_incomplete=drop_incomplete,
                    global_offset=group_start,
                    start_window_id=window_counter,
                    session_id=curr_session,
                ):
                    yield window
                    window_counter += 1


def _validate_window_params(window_size: int, step_size: int) -> None:
    """Validate window_size and step_size parameters."""
    if not isinstance(window_size, int) or isinstance(window_size, bool):
        raise TypeError(f"window_size must be an integer, got {type(window_size).__name__}")
    if not isinstance(step_size, int) or isinstance(step_size, bool):
        raise TypeError(f"step_size must be an integer, got {type(step_size).__name__}")
    if window_size <= 0:
        raise ValueError(f"window_size must be a positive integer (> 0), got {window_size}")
    if step_size <= 0:
        raise ValueError(f"step_size must be a positive integer (> 0), got {step_size}")


def _slice_data(data: Any, start: int, end: int) -> Any:
    """Slice data safely whether it is a DataFrame, Series, numpy array, or list."""
    if HAS_PANDAS and isinstance(data, (pd.DataFrame, pd.Series)):
        return data.iloc[start:end]
    return data[start:end]


def _window_single_sequence(
    df: Any,
    window_size: int,
    step_size: int,
    drop_incomplete: bool,
    global_offset: int,
    start_window_id: int,
    session_id: Optional[Any] = None,
) -> Generator[FlowWindow, None, None]:
    """Helper generator for windowing a contiguous block of rows."""
    total_rows = len(df)
    window_id = start_window_id
    pos = 0

    while pos < total_rows:
        end_pos = pos + window_size
        is_complete = end_pos <= total_rows
        actual_end_pos = min(end_pos, total_rows)

        if not is_complete:
            if not drop_incomplete:
                slice_data = _slice_data(df, pos, actual_end_pos)
                yield FlowWindow(
                    window_id=window_id,
                    start_idx=global_offset + pos,
                    end_idx=global_offset + actual_end_pos,
                    data=slice_data,
                    session_id=session_id,
                    is_complete=False,
                )
            break

        slice_data = _slice_data(df, pos, end_pos)
        yield FlowWindow(
            window_id=window_id,
            start_idx=global_offset + pos,
            end_idx=global_offset + end_pos,
            data=slice_data,
            session_id=session_id,
            is_complete=True,
        )
        window_id += 1
        pos += step_size
