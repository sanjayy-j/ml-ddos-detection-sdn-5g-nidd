"""Stage D — capture-block detection and the M1 train/val/test split.

The 5G-NIDD Combined.csv concatenates 20 contiguous capture sessions
(2 base stations x 10 sessions). Blocks are detected where the Argus
byte `Offset` resets; the single decrease in the CSV index column marks
the base-station boundary. Row order inside a block is capture order
(verified: `Offset` is non-decreasing inside every block).

Split strategy — `block_label_contiguous`
-----------------------------------------
Within each capture block, and within each label stream separately,
rows are cut by position: first `train_ratio` -> train, next
`val_ratio` -> val, remainder -> test.

Why not the obvious alternatives:
  * plain random row split — scatters adjacent, highly-correlated flows
    from the same attack burst across train and test (optimistic).
  * plain contiguous cut per block — attacks occupy a time window inside
    each capture, so the class prior shifts severely across splits
    (measured: train 69.4% -> val 47.8% -> test 32.9% malicious) and
    several blocks yield single-class validation/test segments.
  * full block hold-out — each attack type exists in only 2 blocks (one
    per base station), so holding blocks out removes whole attack types
    from training.
  * base-station split (BS0 train / BS1 test) — prior shifts 44.1% ->
    85.5% malicious.

Stratifying by (block, label) keeps the class prior identical across
splits by construction, keeps all 20 blocks / both base stations / all
attack types in every split, and still respects capture order within
each class stream.

The split is fully deterministic: it uses no random number generator.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

TRAIN = "train"
VAL = "val"
TEST = "test"
PURGED = "purged"
SPLIT_NAMES = (TRAIN, VAL, TEST)


class SplitError(Exception):
    """Raised when the split configuration or result is invalid."""


def detect_capture_blocks(df: pd.DataFrame, config: dict[str, Any]) -> np.ndarray:
    """Assign a contiguous capture-block id to every row.

    A new block starts wherever the detection column (Argus `Offset`)
    decreases, i.e. the byte offset resets at the start of a new capture.
    """
    column = (config.get("blocks") or {}).get("detect_column", "Offset")
    if column not in df.columns:
        raise SplitError(f"Block-detection column '{column}' not in DataFrame.")

    values = df[column].to_numpy()
    resets = np.flatnonzero(np.diff(values) < 0) + 1
    block_ids = np.zeros(len(df), dtype=np.int32)
    if len(resets):
        # cumulative count of resets seen so far == block index
        block_ids[resets] = 1
        block_ids = np.cumsum(block_ids, dtype=np.int32)
    return block_ids


def detect_base_station(df: pd.DataFrame, config: dict[str, Any]) -> np.ndarray:
    """Assign a base-station id (0/1) using the single index reset.

    The two base-station capture files were concatenated, so the CSV index
    column restarts exactly once at the boundary.
    """
    column = (config.get("blocks") or {}).get("base_station_column", "Unnamed: 0")
    if column not in df.columns:
        raise SplitError(f"Base-station column '{column}' not in DataFrame.")

    values = df[column].to_numpy()
    decreases = np.flatnonzero(np.diff(values) < 0) + 1
    ids = np.zeros(len(df), dtype=np.int8)
    for boundary in decreases:
        ids[boundary:] += 1
    return ids


def _ratios(config: dict[str, Any]) -> tuple[float, float, float, int]:
    split_cfg = config.get("split") or {}
    train = float(split_cfg.get("train_ratio", 0.70))
    val = float(split_cfg.get("val_ratio", 0.15))
    test = float(split_cfg.get("test_ratio", 0.15))
    purge = int(split_cfg.get("purge_rows", 0) or 0)

    if min(train, val, test) <= 0:
        raise SplitError("train/val/test ratios must all be > 0.")
    total = train + val + test
    if abs(total - 1.0) > 1e-6:
        raise SplitError(f"train+val+test ratios must sum to 1.0 (got {total}).")
    if purge < 0:
        raise SplitError("split.purge_rows must be >= 0.")
    return train, val, test, purge


def make_split(
    y: pd.Series | np.ndarray,
    block_ids: np.ndarray,
    config: dict[str, Any],
) -> np.ndarray:
    """Return a per-row array of 'train' / 'val' / 'test' / 'purged'.

    Deterministic: identical inputs always produce an identical result.
    """
    train_ratio, val_ratio, _, purge = _ratios(config)
    y_arr = np.asarray(y)
    n = len(y_arr)
    if len(block_ids) != n:
        raise SplitError("block_ids and y must have the same length.")

    assignment = np.empty(n, dtype=object)

    strata = pd.DataFrame({"block": block_ids, "label": y_arr})
    # `.indices` gives the original positional order within each stratum,
    # which is capture order — exactly what the contiguous cut needs.
    for _, positions in strata.groupby(["block", "label"], sort=True).indices.items():
        k = len(positions)
        train_end = int(k * train_ratio)
        val_end = int(k * (train_ratio + val_ratio))

        assignment[positions[:train_end]] = TRAIN
        assignment[positions[train_end:val_end]] = VAL
        assignment[positions[val_end:]] = TEST

        # Purge a gap at each boundary to reduce adjacency correlation
        # between the tail of one segment and the head of the next.
        if purge > 0:
            if train_end > 0:
                assignment[positions[max(0, train_end - purge):train_end]] = PURGED
            if val_end > train_end:
                assignment[positions[max(train_end, val_end - purge):val_end]] = PURGED

    if (assignment == None).any():  # noqa: E711 - object array identity check
        raise SplitError("Internal error: some rows were left unassigned.")
    return assignment


def build_split_manifest(
    block_ids: np.ndarray,
    base_station_ids: np.ndarray,
    y: pd.Series | np.ndarray,
    assignment: np.ndarray,
    attack_types: pd.Series | None = None,
) -> pd.DataFrame:
    """Per-block manifest describing the split, for reproducibility."""
    y_arr = np.asarray(y)
    frame = pd.DataFrame(
        {
            "block": block_ids,
            "base_station": base_station_ids,
            "label": y_arr,
            "split": assignment,
        }
    )
    if attack_types is not None:
        frame["attack_type"] = np.asarray(attack_types)

    rows = []
    for block, group in frame.groupby("block", sort=True):
        record: dict[str, Any] = {
            "block": int(block),
            "base_station": int(group["base_station"].iloc[0]),
            "rows": int(len(group)),
            "benign": int((group["label"] == 0).sum()),
            "malicious": int((group["label"] == 1).sum()),
        }
        if attack_types is not None:
            non_benign = sorted(
                set(group["attack_type"].dropna().unique()) - {"Benign"}
            )
            record["attack_types"] = "|".join(non_benign) if non_benign else "Benign"
        for split_name in (*SPLIT_NAMES, PURGED):
            sub = group[group["split"] == split_name]
            record[f"{split_name}_rows"] = int(len(sub))
            record[f"{split_name}_benign"] = int((sub["label"] == 0).sum())
            record[f"{split_name}_malicious"] = int((sub["label"] == 1).sum())
        rows.append(record)

    return pd.DataFrame(rows)


def assert_split_is_disjoint(assignment: np.ndarray) -> None:
    """Every row belongs to exactly one split (object array => single value)."""
    values = set(pd.unique(assignment))
    unexpected = values - set(SPLIT_NAMES) - {PURGED}
    if unexpected:
        raise SplitError(f"Unexpected split labels: {sorted(unexpected)}")
    for name in SPLIT_NAMES:
        if not (assignment == name).any():
            raise SplitError(f"Split '{name}' is empty.")
