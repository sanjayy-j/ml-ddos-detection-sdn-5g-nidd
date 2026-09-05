"""Stage B — M1 data loading.

Responsible ONLY for getting the configured dataset off disk and into a
pandas DataFrame, unmodified. It does not know about labels, features,
or schema — that is handled later by validation.py / preprocess.py.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

SUPPORTED_FORMATS = ("csv",)


def load_config_file(config_path: str | Path) -> dict[str, Any]:
    """Read an M1 YAML config file into a plain dict.

    Raises FileNotFoundError if the config file itself does not exist,
    and ValueError if the file does not parse into a mapping.
    """
    config_path = Path(config_path)
    if not config_path.is_file():
        raise FileNotFoundError(f"M1 config file not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as fh:
        config = yaml.safe_load(fh)

    if not isinstance(config, dict):
        raise ValueError(
            f"M1 config file did not parse into a mapping: {config_path}"
        )

    return config


def load_raw_data(config: dict[str, Any]) -> pd.DataFrame:
    """Load the raw dataset described by config['dataset'].

    This function is intentionally column-agnostic: it does not drop,
    rename, encode, scale, impute, or otherwise transform anything, and
    it does not infer or touch the label column. It only reads the
    configured file, as-is, into a DataFrame.

    Raises:
        ValueError: if the 'dataset' section, its 'raw_path', or its
            'format' is missing/unset, or the format is unsupported.
        FileNotFoundError: if raw_path does not point to an existing file.
    """
    dataset_cfg = config.get("dataset")
    if not isinstance(dataset_cfg, dict):
        raise ValueError(
            "M1 config is missing a 'dataset' section — cannot load data."
        )

    raw_path = dataset_cfg.get("raw_path")
    if not raw_path:
        raise ValueError(
            "config['dataset']['raw_path'] is not set. Set it to the local "
            "path of the 5G-NIDD dataset file before running the pipeline "
            "(this is intentionally left unset in version control)."
        )

    raw_path = Path(raw_path)
    if not raw_path.is_file():
        raise FileNotFoundError(
            f"Configured dataset path does not exist or is not a file: "
            f"{raw_path}"
        )

    dataset_format = dataset_cfg.get("format")
    if not dataset_format:
        raise ValueError("config['dataset']['format'] is not set.")
    dataset_format = str(dataset_format).lower()

    if dataset_format not in SUPPORTED_FORMATS:
        raise ValueError(
            f"Unsupported dataset format '{dataset_format}'. "
            f"Supported formats: {SUPPORTED_FORMATS}."
        )

    try:
        df = pd.read_csv(raw_path)
    except pd.errors.EmptyDataError as exc:
        raise ValueError(f"Dataset file is empty: {raw_path}") from exc
    except pd.errors.ParserError as exc:
        raise ValueError(
            f"Dataset file could not be parsed as CSV: {raw_path} ({exc})"
        ) from exc

    if df.shape[0] == 0:
        raise ValueError(f"Dataset file loaded but contains zero rows: {raw_path}")

    return df
