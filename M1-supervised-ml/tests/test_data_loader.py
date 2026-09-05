"""Stage B tests — data loader.

Uses only synthetic data (tests/data/synthetic_sample.csv, obviously
fake feature_1..feature_8/label columns) and the synthetic M1 config.
Never touches or assumes anything about the real 5G-NIDD dataset.
"""

from pathlib import Path

import pandas as pd
import pytest

from preprocessing.data_loader import load_config_file, load_raw_data

TESTS_DIR = Path(__file__).parent
SYNTHETIC_CSV = TESTS_DIR / "data" / "synthetic_sample.csv"
SYNTHETIC_CONFIG = TESTS_DIR.parent / "config" / "m1_config.synthetic.yaml"
REAL_CONFIG = TESTS_DIR.parent / "config" / "m1_config.yaml"


def _config_with_raw_path(raw_path) -> dict:
    """Load the synthetic config and point it at a given CSV path."""
    config = load_config_file(SYNTHETIC_CONFIG)
    config["dataset"]["raw_path"] = str(raw_path)
    return config


def test_load_config_file_parses_synthetic_config():
    config = load_config_file(SYNTHETIC_CONFIG)
    assert config["schema"]["label_column"] == "label"
    assert config["schema"]["feature_columns"] == [
        f"feature_{i}" for i in range(1, 9)
    ]


def test_load_config_file_missing_path_raises():
    with pytest.raises(FileNotFoundError):
        load_config_file(TESTS_DIR / "does_not_exist.yaml")


def test_load_raw_data_reads_synthetic_csv_unmodified():
    config = _config_with_raw_path(SYNTHETIC_CSV)
    df = load_raw_data(config)

    expected = pd.read_csv(SYNTHETIC_CSV)
    pd.testing.assert_frame_equal(df, expected)

    # loader must not drop/rename/add columns
    assert list(df.columns) == list(expected.columns)
    assert df.shape == expected.shape


def test_load_raw_data_missing_raw_path_raises_value_error():
    config = load_config_file(SYNTHETIC_CONFIG)
    config["dataset"]["raw_path"] = None
    with pytest.raises(ValueError, match="raw_path"):
        load_raw_data(config)


def test_load_raw_data_nonexistent_file_raises_file_not_found():
    config = _config_with_raw_path(TESTS_DIR / "data" / "does_not_exist.csv")
    with pytest.raises(FileNotFoundError):
        load_raw_data(config)


def test_load_raw_data_unsupported_format_raises_value_error():
    config = _config_with_raw_path(SYNTHETIC_CSV)
    config["dataset"]["format"] = "parquet"
    with pytest.raises(ValueError, match="Unsupported dataset format"):
        load_raw_data(config)


def test_load_raw_data_missing_dataset_section_raises_value_error():
    with pytest.raises(ValueError, match="dataset"):
        load_raw_data({})


def test_load_raw_data_empty_csv_raises_value_error(tmp_path):
    empty_csv = tmp_path / "empty.csv"
    empty_csv.write_text("")
    config = _config_with_raw_path(empty_csv)
    with pytest.raises(ValueError):
        load_raw_data(config)


def test_real_config_raw_path_is_unset_placeholder():
    """The real (non-synthetic) config must not have a dataset path
    baked in yet — it is intentionally left for local configuration."""
    config = load_config_file(REAL_CONFIG)
    assert config["dataset"]["raw_path"] is None
    with pytest.raises(ValueError, match="raw_path"):
        load_raw_data(config)
