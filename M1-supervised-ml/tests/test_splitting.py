"""Stage D tests — capture-block detection and the train/val/test split."""

import numpy as np
import pytest

from fixtures import make_synthetic_5gnidd, synthetic_config
from preprocessing.features import build_target
from preprocessing.splitting import (
    PURGED,
    SPLIT_NAMES,
    SplitError,
    assert_split_is_disjoint,
    build_split_manifest,
    detect_base_station,
    detect_capture_blocks,
    make_split,
)


def _setup(n_blocks=4, rows_per_block=240, seed=0):
    df = make_synthetic_5gnidd(n_blocks=n_blocks, rows_per_block=rows_per_block,
                               seed=seed)
    config = synthetic_config()
    y = build_target(df, config).to_numpy()
    blocks = detect_capture_blocks(df, config)
    return df, config, y, blocks


# --- block detection --------------------------------------------------------

def test_detects_expected_number_of_capture_blocks():
    df, config, _, blocks = _setup(n_blocks=4)
    assert blocks.min() == 0
    assert blocks.max() == 3
    assert len(np.unique(blocks)) == 4


def test_blocks_are_contiguous():
    _, _, _, blocks = _setup(n_blocks=5, rows_per_block=100)
    # a contiguous labelling never revisits a block id after leaving it
    changes = np.flatnonzero(np.diff(blocks) != 0)
    assert len(changes) == len(np.unique(blocks)) - 1
    assert (np.diff(blocks) >= 0).all()


def test_base_station_boundary_detected():
    df, config, _, _ = _setup(n_blocks=4, rows_per_block=240)
    bs = detect_base_station(df, config)
    assert set(np.unique(bs)) == {0, 1}
    # exactly one transition, and it is monotonic
    assert (np.diff(bs) >= 0).all()
    assert int((np.diff(bs) != 0).sum()) == 1


# --- split correctness ------------------------------------------------------

def test_split_assigns_every_row_exactly_once():
    _, config, y, blocks = _setup()
    assignment = make_split(y, blocks, config)

    assert len(assignment) == len(y)
    assert set(np.unique(assignment)) <= set(SPLIT_NAMES) | {PURGED}
    counts = sum(int((assignment == name).sum()) for name in SPLIT_NAMES)
    assert counts == len(y)  # purge_rows=0 by default
    assert_split_is_disjoint(assignment)


def test_no_index_overlap_between_splits():
    _, config, y, blocks = _setup()
    assignment = make_split(y, blocks, config)

    index_sets = {
        name: set(np.flatnonzero(assignment == name)) for name in SPLIT_NAMES
    }
    assert not (index_sets["train"] & index_sets["val"])
    assert not (index_sets["train"] & index_sets["test"])
    assert not (index_sets["val"] & index_sets["test"])


def test_class_prior_is_preserved_across_splits():
    """The whole point of stratifying by (block, label)."""
    _, config, y, blocks = _setup(n_blocks=4, rows_per_block=400)
    assignment = make_split(y, blocks, config)

    priors = {
        name: y[assignment == name].mean() for name in SPLIT_NAMES
    }
    overall = y.mean()
    for name, prior in priors.items():
        assert abs(prior - overall) < 0.02, f"{name} prior {prior} vs {overall}"


def test_every_block_appears_in_every_split():
    _, config, y, blocks = _setup(n_blocks=4, rows_per_block=400)
    assignment = make_split(y, blocks, config)
    for name in SPLIT_NAMES:
        assert set(np.unique(blocks[assignment == name])) == set(np.unique(blocks))


def test_split_is_contiguous_within_each_block_and_label_stream():
    """Train rows must precede val rows, which must precede test rows."""
    _, config, y, blocks = _setup(n_blocks=3, rows_per_block=300)
    assignment = make_split(y, blocks, config)

    order = {"train": 0, "val": 1, "test": 2}
    for block in np.unique(blocks):
        for label in (0, 1):
            positions = np.flatnonzero((blocks == block) & (y == label))
            if len(positions) == 0:
                continue
            codes = [order[assignment[p]] for p in positions]
            # non-decreasing => contiguous train | val | test segments
            assert codes == sorted(codes)


def test_split_ratios_are_respected():
    _, config, y, blocks = _setup(n_blocks=4, rows_per_block=1000)
    assignment = make_split(y, blocks, config)
    n = len(y)
    assert abs((assignment == "train").sum() / n - 0.70) < 0.01
    assert abs((assignment == "val").sum() / n - 0.15) < 0.01
    assert abs((assignment == "test").sum() / n - 0.15) < 0.01


def test_split_is_reproducible():
    _, config, y, blocks = _setup()
    first = make_split(y, blocks, config)
    second = make_split(y, blocks, config)
    assert np.array_equal(first, second)


# --- purge gap --------------------------------------------------------------

def test_purge_rows_removes_boundary_rows():
    _, config, y, blocks = _setup(n_blocks=2, rows_per_block=400)
    config["split"]["purge_rows"] = 5
    assignment = make_split(y, blocks, config)

    assert int((assignment == PURGED).sum()) > 0
    # purged rows belong to no split
    for name in SPLIT_NAMES:
        assert not ((assignment == PURGED) & (assignment == name)).any()


# --- configuration validation ----------------------------------------------

def test_ratios_must_sum_to_one():
    _, config, y, blocks = _setup()
    config["split"]["test_ratio"] = 0.30
    with pytest.raises(SplitError, match="sum to 1.0"):
        make_split(y, blocks, config)


def test_negative_purge_rejected():
    _, config, y, blocks = _setup()
    config["split"]["purge_rows"] = -1
    with pytest.raises(SplitError, match="purge_rows"):
        make_split(y, blocks, config)


# --- manifest ---------------------------------------------------------------

def test_split_manifest_is_complete_and_reproducible():
    df, config, y, blocks = _setup(n_blocks=4, rows_per_block=240)
    bs = detect_base_station(df, config)
    assignment = make_split(y, blocks, config)

    manifest = build_split_manifest(blocks, bs, y, assignment, df["Attack Type"])
    again = build_split_manifest(blocks, bs, y, assignment, df["Attack Type"])

    assert len(manifest) == len(np.unique(blocks))
    assert manifest["rows"].sum() == len(y)
    for name in SPLIT_NAMES:
        assert manifest[f"{name}_rows"].sum() == int((assignment == name).sum())
    assert "attack_types" in manifest.columns
    assert manifest.equals(again)
