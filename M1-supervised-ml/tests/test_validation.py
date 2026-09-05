"""Stage C tests — schema/data validation.

Uses only synthetic data/config (fake feature_1..8/label columns) plus
small in-memory DataFrames built for specific edge cases. Also checks
that the REAL m1_config.yaml (schema still TBD) is correctly rejected.
Never assumes anything about the real 5G-NIDD dataset.
"""

from pathlib import Path

import pandas as pd
import pytest

from preprocessing.data_loader import load_config_file, load_raw_data
from preprocessing.validation import (
    SchemaValidationError,
    validate_and_raise,
    validate_schema,
)

TESTS_DIR = Path(__file__).parent
SYNTHETIC_CSV = TESTS_DIR / "data" / "synthetic_sample.csv"
SYNTHETIC_CONFIG = TESTS_DIR.parent / "config" / "m1_config.synthetic.yaml"
REAL_CONFIG = TESTS_DIR.parent / "config" / "m1_config.yaml"


def _synthetic_config_and_df():
    config = load_config_file(SYNTHETIC_CONFIG)
    config["dataset"]["raw_path"] = str(SYNTHETIC_CSV)
    df = load_raw_data(config)
    return config, df


# ---------------------------------------------------------------------------
# Valid synthetic schema
# ---------------------------------------------------------------------------

def test_valid_synthetic_schema_passes_with_no_errors():
    config, df = _synthetic_config_and_df()
    result = validate_schema(config, df)

    assert result.is_valid
    assert result.errors == []


def test_valid_synthetic_schema_does_not_raise():
    config, df = _synthetic_config_and_df()
    result = validate_and_raise(config, df)
    assert result.is_valid


# ---------------------------------------------------------------------------
# Null/TBD real schema
# ---------------------------------------------------------------------------

def test_real_config_schema_is_tbd_and_rejected():
    config = load_config_file(REAL_CONFIG)
    assert config["schema"]["label_column"] is None
    assert config["schema"]["feature_columns"] is None

    # Schema validity does not depend on having real data loaded, so any
    # placeholder DataFrame is enough to exercise the schema-level checks.
    placeholder_df = pd.DataFrame({"some_column": [1, 2, 3]})
    result = validate_schema(config, placeholder_df)

    assert not result.is_valid
    assert any("label_column" in e and "TBD" in e for e in result.errors)
    assert any("feature_columns" in e and "TBD" in e for e in result.errors)


def test_real_config_raises_via_validate_and_raise():
    config = load_config_file(REAL_CONFIG)
    placeholder_df = pd.DataFrame({"some_column": [1, 2, 3]})
    with pytest.raises(SchemaValidationError):
        validate_and_raise(config, placeholder_df)


# ---------------------------------------------------------------------------
# Missing label column
# ---------------------------------------------------------------------------

def test_missing_label_column_is_an_error():
    config, df = _synthetic_config_and_df()
    config["schema"]["label_column"] = "not_a_real_column"

    result = validate_schema(config, df)

    assert not result.is_valid
    assert any("not_a_real_column" in e for e in result.errors)
    # since the label column doesn't exist, no distribution can be reported
    assert result.label_distribution is None


# ---------------------------------------------------------------------------
# Missing feature column
# ---------------------------------------------------------------------------

def test_missing_feature_column_is_an_error():
    config, df = _synthetic_config_and_df()
    config["schema"]["feature_columns"] = config["schema"]["feature_columns"] + [
        "feature_does_not_exist"
    ]

    result = validate_schema(config, df)

    assert not result.is_valid
    assert any("feature_does_not_exist" in e for e in result.errors)


# ---------------------------------------------------------------------------
# Invalid configured column (categorical / identifier / drop)
# ---------------------------------------------------------------------------

def test_invalid_categorical_column_is_an_error():
    config, df = _synthetic_config_and_df()
    config["schema"]["categorical_columns"] = ["not_a_column"]

    result = validate_schema(config, df)

    assert not result.is_valid
    assert any(
        "categorical_columns" in e and "not_a_column" in e for e in result.errors
    )


def test_invalid_identifier_column_is_an_error():
    config, df = _synthetic_config_and_df()
    config["schema"]["identifier_columns"] = ["ghost_id_column"]

    result = validate_schema(config, df)

    assert not result.is_valid
    assert any(
        "identifier_columns" in e and "ghost_id_column" in e for e in result.errors
    )


def test_invalid_drop_column_is_an_error():
    config, df = _synthetic_config_and_df()
    config["schema"]["drop_columns"] = ["ghost_drop_column"]

    result = validate_schema(config, df)

    assert not result.is_valid
    assert any(
        "drop_columns" in e and "ghost_drop_column" in e for e in result.errors
    )


# ---------------------------------------------------------------------------
# Label leaking into features -> error; other overlaps -> warnings
# ---------------------------------------------------------------------------

def test_label_column_inside_feature_columns_is_an_error():
    config, df = _synthetic_config_and_df()
    config["schema"]["feature_columns"] = config["schema"]["feature_columns"] + [
        config["schema"]["label_column"]
    ]

    result = validate_schema(config, df)

    assert not result.is_valid
    assert any("leak" in e.lower() for e in result.errors)


def test_categorical_column_not_in_features_is_a_warning_not_error():
    config, df = _synthetic_config_and_df()
    # feature_2 exists in the dataset but is deliberately left out of
    # feature_columns while being flagged as categorical.
    config["schema"]["feature_columns"] = [
        c for c in config["schema"]["feature_columns"] if c != "feature_2"
    ]
    config["schema"]["categorical_columns"] = ["feature_2"]

    result = validate_schema(config, df)

    assert result.is_valid  # warning only, not fatal
    assert any("categorical_columns" in w for w in result.warnings)


# ---------------------------------------------------------------------------
# Missing values report
# ---------------------------------------------------------------------------

def test_missing_value_counts_reported_correctly():
    df = pd.DataFrame(
        {
            "feature_1": [1.0, None, 3.0, None],
            "feature_2": [1, 2, 3, 4],
            "label": [0, 1, 0, 1],
        }
    )
    config = {
        "schema": {
            "label_column": "label",
            "feature_columns": ["feature_1", "feature_2"],
            "categorical_columns": [],
            "identifier_columns": [],
            "drop_columns": [],
        }
    }

    result = validate_schema(config, df)

    assert result.is_valid
    assert result.missing_value_counts == {
        "feature_1": 2,
        "feature_2": 0,
        "label": 0,
    }


# ---------------------------------------------------------------------------
# Label / class distribution
# ---------------------------------------------------------------------------

def test_label_distribution_reported_correctly():
    df = pd.DataFrame(
        {
            "feature_1": [1, 2, 3, 4, 5, 6],
            "label": [0, 0, 0, 1, 1, 0],
        }
    )
    config = {
        "schema": {
            "label_column": "label",
            "feature_columns": ["feature_1"],
            "categorical_columns": [],
            "identifier_columns": [],
            "drop_columns": [],
        }
    }

    result = validate_schema(config, df)

    assert result.is_valid
    assert result.label_distribution["0"]["count"] == 4
    assert result.label_distribution["1"]["count"] == 2
    assert result.label_distribution["0"]["proportion"] == pytest.approx(4 / 6)
    assert result.label_distribution["1"]["proportion"] == pytest.approx(2 / 6)


def test_synthetic_dataset_label_distribution():
    config, df = _synthetic_config_and_df()
    result = validate_schema(config, df)

    assert result.is_valid
    # synthetic_sample.csv has 4 rows with label=0 and 4 with label=1
    assert result.label_distribution["0"]["count"] == 4
    assert result.label_distribution["1"]["count"] == 4
