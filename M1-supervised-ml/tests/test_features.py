"""Stage D tests — target construction and feature policy."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from fixtures import make_synthetic_5gnidd, synthetic_config
from preprocessing.data_loader import load_config_file
from preprocessing.features import (
    FeaturePolicyError,
    build_feature_frame,
    build_target,
    forbidden_columns,
    get_categorical_columns,
    get_feature_columns,
    get_numeric_columns,
)

REAL_CONFIG = Path(__file__).parent.parent / "config" / "m1_config.yaml"


# --- target mapping ---------------------------------------------------------

def test_target_maps_benign_to_zero_and_malicious_to_one():
    df = make_synthetic_5gnidd()
    config = synthetic_config()
    y = build_target(df, config)

    assert set(np.unique(y)) <= {0, 1}
    assert (y[df["Label"] == "Benign"] == 0).all()
    assert (y[df["Label"] == "Malicious"] == 1).all()
    assert int((y == 1).sum()) == int((df["Label"] == "Malicious").sum())


def test_target_rejects_unrecognised_label_value():
    df = make_synthetic_5gnidd()
    df.loc[0, "Label"] = "Suspicious"
    with pytest.raises(FeaturePolicyError, match="Unrecognised values"):
        build_target(df, synthetic_config())


def test_target_rejects_missing_label():
    df = make_synthetic_5gnidd()
    df.loc[0, "Label"] = None
    with pytest.raises(FeaturePolicyError):
        build_target(df, synthetic_config())


# --- forbidden columns ------------------------------------------------------

def test_forbidden_columns_never_enter_feature_matrix():
    config = synthetic_config()
    features = set(get_feature_columns(config))
    assert not (features & forbidden_columns(config))


@pytest.mark.parametrize("column", ["Attack Type", "Attack Tool"])
def test_attack_metadata_cannot_be_a_feature(column):
    config = synthetic_config()
    config["schema"]["feature_columns"].append(column)
    with pytest.raises(FeaturePolicyError, match="Forbidden columns"):
        get_feature_columns(config)


@pytest.mark.parametrize("column", ["Unnamed: 0", "Seq", "Offset"])
def test_identifiers_cannot_be_a_feature(column):
    config = synthetic_config()
    config["schema"]["feature_columns"].append(column)
    with pytest.raises(FeaturePolicyError, match="Forbidden columns"):
        get_feature_columns(config)


def test_label_cannot_be_a_feature():
    config = synthetic_config()
    config["schema"]["feature_columns"].append("Label")
    with pytest.raises(FeaturePolicyError, match="Forbidden columns"):
        get_feature_columns(config)


@pytest.mark.parametrize(
    "column",
    ["RunTime", "Mean", "Sum", "Min", "Max", "sTos", "dTos", "sHops", "dHops",
     "SrcGap", "DstGap", "SrcTCPBase", "DstTCPBase", "sVid", "dVid"],
)
def test_redundant_and_banned_columns_are_excluded(column):
    """Every documented exclusion must be absent from the feature list."""
    for config in (synthetic_config(), load_config_file(REAL_CONFIG)):
        assert column not in get_feature_columns(config)
        assert column in forbidden_columns(config)


def test_duplicate_feature_entries_rejected():
    config = synthetic_config()
    config["schema"]["feature_columns"].append("Dur")
    with pytest.raises(FeaturePolicyError, match="Duplicate entries"):
        get_feature_columns(config)


# --- ordering / composition -------------------------------------------------

def test_feature_ordering_is_deterministic():
    config = synthetic_config()
    first = get_feature_columns(config)
    second = get_feature_columns(synthetic_config())
    assert first == second

    df = make_synthetic_5gnidd()
    frame = build_feature_frame(df, config)
    assert list(frame.columns) == first


def test_numeric_and_categorical_partition_the_feature_set():
    config = synthetic_config()
    features = get_feature_columns(config)
    numeric = get_numeric_columns(config)
    categorical = get_categorical_columns(config)

    assert set(numeric) | set(categorical) == set(features)
    assert not (set(numeric) & set(categorical))
    # both subsets follow feature ordering
    assert numeric == [c for c in features if c in set(numeric)]
    assert categorical == [c for c in features if c in set(categorical)]


def test_build_feature_frame_rejects_absent_columns():
    df = make_synthetic_5gnidd().drop(columns=["Rate"])
    with pytest.raises(FeaturePolicyError, match="absent"):
        build_feature_frame(df, synthetic_config())


# --- the real configuration -------------------------------------------------

def test_real_config_feature_policy_is_valid():
    config = load_config_file(REAL_CONFIG)
    features = get_feature_columns(config)

    assert len(features) == 31
    assert len(get_numeric_columns(config)) == 26
    assert get_categorical_columns(config) == [
        "Proto", "sDSb", "dDSb", "Cause", "State"
    ]
    assert not (set(features) & forbidden_columns(config))
    assert config["schema"]["label_column"] == "Label"
    assert config["schema"]["positive_class_values"] == ["Malicious"]
    assert config["schema"]["negative_class_values"] == ["Benign"]


def test_real_config_excludes_exactly_the_documented_columns():
    config = load_config_file(REAL_CONFIG)
    expected_dropped = {
        "RunTime", "Mean", "Sum", "Min", "Max",
        "sTos", "dTos", "sHops", "dHops",
        "SrcGap", "DstGap",
        "SrcTCPBase", "DstTCPBase", "sVid", "dVid",
    }
    assert set(config["schema"]["drop_columns"]) == expected_dropped
