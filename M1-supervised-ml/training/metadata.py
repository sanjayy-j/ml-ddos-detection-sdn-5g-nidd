"""Stage F — per-split analysis metadata (Attack Type / Tool / block).

The Stage D processed matrices deliberately contain no metadata, but
per-attack-type and per-tool reporting needs `Attack Type` / `Attack Tool`
aligned to each split's rows.

This module does NOT re-implement the split. It calls the same Stage D/E
functions (`build_target`, `detect_capture_blocks`, `detect_base_station`,
`make_split`) on a narrow column subset of the raw CSV, so the assignment
is identical by construction, then caches the result so the raw file is
read once rather than on every evaluation run.

The metadata produced here is analysis-only and must never reach a model.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from preprocessing.features import build_target
from preprocessing.pipeline import resolve_path
from preprocessing.splitting import (
    SPLIT_NAMES,
    detect_base_station,
    detect_capture_blocks,
    make_split,
)

METADATA_COLUMNS = ["attack_type", "attack_tool", "block", "base_station"]


def _cache_path(config: dict[str, Any], root: Path, split: str) -> Path:
    processed = resolve_path(
        root,
        (config.get("output") or {}).get(
            "processed_dir", "M1-supervised-ml/data/processed"
        ),
    )
    return processed / f"metadata_{split}.csv"


def build_split_metadata(
    config: dict[str, Any], root: Path
) -> dict[str, pd.DataFrame]:
    """Recompute the split and return per-split metadata frames."""
    schema = config["schema"]
    label_column = schema["label_column"]
    metadata_columns = list(schema.get("metadata_columns") or [])
    blocks_cfg = config.get("blocks") or {}

    needed = sorted(
        {
            label_column,
            *metadata_columns,
            blocks_cfg.get("detect_column", "Offset"),
            blocks_cfg.get("base_station_column", "Unnamed: 0"),
        }
    )
    raw_path = resolve_path(root, config["dataset"]["raw_path"])
    # narrow read: only the columns the split and the metadata need
    df = pd.read_csv(raw_path, usecols=needed, low_memory=False)

    y = build_target(df, config).to_numpy()
    block_ids = detect_capture_blocks(df, config)
    base_station_ids = detect_base_station(df, config)
    assignment = make_split(y, block_ids, config)

    frames: dict[str, pd.DataFrame] = {}
    for split in SPLIT_NAMES:
        mask = assignment == split
        frames[split] = pd.DataFrame(
            {
                "attack_type": df.loc[mask, metadata_columns[0]].to_numpy()
                if metadata_columns else "unknown",
                "attack_tool": df.loc[mask, metadata_columns[1]].to_numpy()
                if len(metadata_columns) > 1 else "unknown",
                "block": block_ids[mask],
                "base_station": base_station_ids[mask],
                "target": y[mask].astype(np.int8),
            }
        )
    return frames


def load_split_metadata(
    config: dict[str, Any], root: Path, split: str, rebuild: bool = False
) -> pd.DataFrame:
    """Load cached metadata for one split, building the cache if needed."""
    path = _cache_path(config, root, split)
    if path.is_file() and not rebuild:
        return pd.read_csv(path)

    frames = build_split_metadata(config, root)
    for name, frame in frames.items():
        frame.to_csv(_cache_path(config, root, name), index=False)
    return frames[split]


def verify_metadata_alignment(metadata: pd.DataFrame, y: np.ndarray) -> None:
    """The metadata's target column must match the processed split target."""
    if len(metadata) != len(y):
        raise ValueError(
            f"metadata rows ({len(metadata):,}) != split rows ({len(y):,})"
        )
    if not np.array_equal(metadata["target"].to_numpy().astype(np.int8),
                          np.asarray(y).astype(np.int8)):
        raise ValueError(
            "metadata target does not match the processed split target — "
            "the metadata is not aligned with the feature matrix."
        )
