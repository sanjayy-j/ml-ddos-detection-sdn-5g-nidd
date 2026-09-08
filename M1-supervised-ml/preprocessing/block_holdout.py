"""Stage L — whole-block holdout partitioning for the unseen-capture experiment.

Partitions the dataset by capture block into a **development** pool and a
**held-out** test set, then carves train/validation from the development
pool only, using the same `block_label_contiguous` principle as Stage E
(contiguous by capture position within each block x label stream) but
producing a NEW assignment — primary row assignments are never reused.

Invariants enforced here:
  * every block lies wholly in development or wholly in held-out
  * held-out blocks never appear in train or validation
  * the assignment is deterministic (no RNG)
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

DEV_TRAIN = "dev_train"
DEV_VAL = "dev_val"
HELD_OUT = "held_out"
ASSIGNMENT_NAMES = (DEV_TRAIN, DEV_VAL, HELD_OUT)


class BlockHoldoutError(Exception):
    """Raised when the holdout configuration or result is invalid."""


def get_block_sets(config: dict[str, Any]) -> tuple[list[int], list[int]]:
    """Return (development_blocks, held_out_blocks), validated."""
    section = config.get("unseen_capture")
    if not isinstance(section, dict):
        raise BlockHoldoutError("config is missing the 'unseen_capture' section")

    held = sorted(int(b) for b in (section.get("held_out_blocks") or []))
    dev = sorted(int(b) for b in (section.get("development_blocks") or []))
    if not held or not dev:
        raise BlockHoldoutError("held_out_blocks and development_blocks "
                                "must both be non-empty")

    overlap = set(held) & set(dev)
    if overlap:
        raise BlockHoldoutError(
            f"blocks appear in both development and held-out: {sorted(overlap)}")
    return dev, held


def assign_blocks(
    block_ids: np.ndarray,
    y: np.ndarray,
    config: dict[str, Any],
) -> np.ndarray:
    """Per-row assignment to dev_train / dev_val / held_out.

    Deterministic: contiguous cut by position within each
    (development block, label) stream; no RNG is used anywhere.
    """
    dev_blocks, held_blocks = get_block_sets(config)
    block_ids = np.asarray(block_ids)
    y = np.asarray(y)
    if len(block_ids) != len(y):
        raise BlockHoldoutError("block_ids and y must have the same length")

    known = set(dev_blocks) | set(held_blocks)
    present = set(int(b) for b in np.unique(block_ids))
    unassigned = present - known
    if unassigned:
        raise BlockHoldoutError(
            f"blocks present in the data but not assigned: {sorted(unassigned)}")

    split_cfg = config.get("split") or {}
    train_ratio = float(split_cfg.get("train_ratio", 0.82))
    if not 0 < train_ratio < 1:
        raise BlockHoldoutError("split.train_ratio must lie in (0, 1)")

    assignment = np.empty(len(y), dtype=object)
    assignment[np.isin(block_ids, held_blocks)] = HELD_OUT

    development = np.isin(block_ids, dev_blocks)
    strata = pd.DataFrame({"block": block_ids, "label": y})
    # `.indices` preserves original positional order within each stratum,
    # which is capture order — the same principle as Stage E.
    for (block, _), positions in strata.groupby(
            ["block", "label"], sort=True).indices.items():
        if not development[positions[0]]:
            continue
        cut = int(len(positions) * train_ratio)
        assignment[positions[:cut]] = DEV_TRAIN
        assignment[positions[cut:]] = DEV_VAL

    if (assignment == None).any():  # noqa: E711
        raise BlockHoldoutError("internal error: some rows were left unassigned")
    return assignment


def verify_isolation(
    assignment: np.ndarray, block_ids: np.ndarray, config: dict[str, Any]
) -> dict[str, Any]:
    """Assert whole-block isolation and no development/held-out overlap."""
    dev_blocks, held_blocks = get_block_sets(config)
    assignment = np.asarray(assignment)
    block_ids = np.asarray(block_ids)

    # every block must map to exactly one side of the partition
    straddling = []
    for block in np.unique(block_ids):
        sides = {("held_out" if a == HELD_OUT else "development")
                 for a in np.unique(assignment[block_ids == block])}
        if len(sides) > 1:
            straddling.append(int(block))
    if straddling:
        raise BlockHoldoutError(
            f"blocks straddling the development/held-out boundary: {straddling}")

    held_mask = assignment == HELD_OUT
    blocks_in_held = set(int(b) for b in np.unique(block_ids[held_mask]))
    blocks_in_dev = set(int(b) for b in np.unique(block_ids[~held_mask]))
    if blocks_in_held != set(held_blocks):
        raise BlockHoldoutError(
            f"held-out blocks {sorted(blocks_in_held)} != configured "
            f"{sorted(held_blocks)}")
    if blocks_in_held & blocks_in_dev:
        raise BlockHoldoutError("a block appears on both sides of the split")

    # no held-out row may carry a development assignment
    for name in (DEV_TRAIN, DEV_VAL):
        leaked = np.isin(block_ids[assignment == name], held_blocks)
        if leaked.any():
            raise BlockHoldoutError(
                f"{int(leaked.sum())} held-out rows assigned to {name}")

    return {
        "held_out_blocks": sorted(blocks_in_held),
        "development_blocks": sorted(blocks_in_dev),
        "blocks_straddling": [],
        "rows": {name: int((assignment == name).sum())
                 for name in ASSIGNMENT_NAMES},
    }


def build_manifest(
    assignment: np.ndarray,
    block_ids: np.ndarray,
    base_station_ids: np.ndarray,
    y: np.ndarray,
    attack_types: np.ndarray | None = None,
) -> pd.DataFrame:
    """Per-block manifest of the Stage L partition."""
    frame = pd.DataFrame({
        "block": np.asarray(block_ids),
        "base_station": np.asarray(base_station_ids),
        "label": np.asarray(y),
        "assignment": np.asarray(assignment),
    })
    if attack_types is not None:
        frame["attack_type"] = np.asarray(attack_types)

    rows = []
    for block, group in frame.groupby("block", sort=True):
        side = ("held_out" if (group["assignment"] == HELD_OUT).all()
                else "development")
        record: dict[str, Any] = {
            "block": int(block),
            "base_station": int(group["base_station"].iloc[0]),
            "side": side,
            "rows": int(len(group)),
            "benign": int((group["label"] == 0).sum()),
            "malicious": int((group["label"] == 1).sum()),
            "malicious_pct": round(100 * float(group["label"].mean()), 4),
        }
        if attack_types is not None:
            types = sorted(set(group["attack_type"]) - {"Benign"})
            record["attack_types"] = "|".join(types) if types else "Benign"
        for name in ASSIGNMENT_NAMES:
            record[f"{name}_rows"] = int((group["assignment"] == name).sum())
        rows.append(record)
    return pd.DataFrame(rows)
