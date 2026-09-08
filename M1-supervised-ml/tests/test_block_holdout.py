"""Stage L tests — whole-block holdout partitioning."""

import numpy as np
import pandas as pd
import pytest

from preprocessing.block_holdout import (
    ASSIGNMENT_NAMES,
    DEV_TRAIN,
    DEV_VAL,
    HELD_OUT,
    BlockHoldoutError,
    assign_blocks,
    build_manifest,
    get_block_sets,
    verify_isolation,
)


def _config(held=(1, 3), dev=(0, 2), train_ratio=0.82):
    return {
        "unseen_capture": {"held_out_blocks": list(held),
                           "development_blocks": list(dev)},
        "split": {"train_ratio": train_ratio},
    }


def _data(blocks=(0, 1, 2, 3), per_block=200, seed=0):
    rng = np.random.default_rng(seed)
    block_ids, y = [], []
    for b in blocks:
        block_ids.append(np.full(per_block, b))
        y.append((rng.random(per_block) < 0.6).astype(np.int8))
    return np.concatenate(block_ids), np.concatenate(y)


# --- configuration ----------------------------------------------------------

def test_get_block_sets_returns_sorted_disjoint_sets():
    dev, held = get_block_sets(_config(held=(3, 1), dev=(2, 0)))
    assert dev == [0, 2] and held == [1, 3]


def test_overlapping_blocks_rejected():
    with pytest.raises(BlockHoldoutError, match="both"):
        get_block_sets(_config(held=(1, 2), dev=(2, 3)))


def test_missing_section_rejected():
    with pytest.raises(BlockHoldoutError, match="unseen_capture"):
        get_block_sets({})


def test_empty_block_list_rejected():
    with pytest.raises(BlockHoldoutError, match="non-empty"):
        get_block_sets(_config(held=(), dev=(0, 1)))


# --- whole-block isolation --------------------------------------------------

def test_held_out_blocks_never_appear_in_train_or_validation():
    blocks, y = _data()
    a = assign_blocks(blocks, y, _config())
    for name in (DEV_TRAIN, DEV_VAL):
        assert not np.isin(blocks[a == name], [1, 3]).any()
    assert set(np.unique(blocks[a == HELD_OUT])) == {1, 3}


def test_every_block_lies_wholly_on_one_side():
    blocks, y = _data()
    a = assign_blocks(blocks, y, _config())
    for block in np.unique(blocks):
        sides = {"held" if x == HELD_OUT else "dev" for x in np.unique(a[blocks == block])}
        assert len(sides) == 1, f"block {block} straddles the boundary"


def test_verify_isolation_passes_and_reports():
    blocks, y = _data()
    config = _config()
    report = verify_isolation(assign_blocks(blocks, y, config), blocks, config)
    assert report["held_out_blocks"] == [1, 3]
    assert report["development_blocks"] == [0, 2]
    assert report["blocks_straddling"] == []
    assert sum(report["rows"].values()) == len(y)


def test_verify_isolation_detects_a_leaked_row():
    blocks, y = _data()
    config = _config()
    a = assign_blocks(blocks, y, config)
    a[np.flatnonzero(blocks == 1)[0]] = DEV_TRAIN     # inject leakage
    with pytest.raises(BlockHoldoutError):
        verify_isolation(a, blocks, config)


def test_unassigned_block_rejected():
    blocks, y = _data(blocks=(0, 1, 2, 3, 4))
    with pytest.raises(BlockHoldoutError, match="not assigned"):
        assign_blocks(blocks, y, _config())


def test_every_row_receives_an_assignment():
    blocks, y = _data()
    a = assign_blocks(blocks, y, _config())
    assert set(np.unique(a)) <= set(ASSIGNMENT_NAMES)
    assert sum((a == n).sum() for n in ASSIGNMENT_NAMES) == len(y)


# --- determinism and split shape -------------------------------------------

def test_assignment_is_deterministic():
    blocks, y = _data()
    config = _config()
    np.testing.assert_array_equal(assign_blocks(blocks, y, config),
                                  assign_blocks(blocks, y, config))


def test_train_validation_ratio_respected_within_development():
    blocks, y = _data(per_block=1000)
    a = assign_blocks(blocks, y, _config(train_ratio=0.82))
    dev = np.isin(blocks, [0, 2])
    train_share = (a[dev] == DEV_TRAIN).mean()
    assert train_share == pytest.approx(0.82, abs=0.01)


def test_split_is_contiguous_within_block_and_label_stream():
    """Train rows must precede validation rows in capture order."""
    blocks, y = _data(per_block=500)
    a = assign_blocks(blocks, y, _config())
    order = {DEV_TRAIN: 0, DEV_VAL: 1}
    for block in (0, 2):
        for label in (0, 1):
            pos = np.flatnonzero((blocks == block) & (y == label))
            codes = [order[a[p]] for p in pos]
            assert codes == sorted(codes)


def test_invalid_train_ratio_rejected():
    blocks, y = _data()
    with pytest.raises(BlockHoldoutError, match="train_ratio"):
        assign_blocks(blocks, y, _config(train_ratio=1.5))


# --- manifest ---------------------------------------------------------------

def test_manifest_records_each_block_once_with_correct_side():
    blocks, y = _data()
    config = _config()
    a = assign_blocks(blocks, y, config)
    bs = np.where(blocks >= 2, 1, 0)
    attacks = np.where(y == 1, "SYNScan", "Benign")
    manifest = build_manifest(a, blocks, bs, y, attacks)

    assert len(manifest) == 4
    assert set(manifest[manifest.side == "held_out"]["block"]) == {1, 3}
    assert set(manifest[manifest.side == "development"]["block"]) == {0, 2}
    assert manifest["rows"].sum() == len(y)
    for row in manifest.itertuples():
        assert row.benign + row.malicious == row.rows
        assert (row.dev_train_rows + row.dev_val_rows
                + row.held_out_rows) == row.rows


def test_manifest_is_deterministic():
    blocks, y = _data()
    config = _config()
    a = assign_blocks(blocks, y, config)
    bs = np.zeros(len(y), dtype=int)
    pd.testing.assert_frame_equal(build_manifest(a, blocks, bs, y),
                                  build_manifest(a, blocks, bs, y))
