"""Stage D — target construction and feature-selection policy.

This module is the single authority on *which columns may become model
inputs*. Every other M1 component must obtain its feature list from
here so that the forbidden-column rules cannot be bypassed.

Non-negotiable rules enforced here:
  * the binary target is built from `Label` only (Benign=0, Malicious=1)
  * `Attack Type` / `Attack Tool` are target-derived metadata and can
    never enter the feature matrix
  * identifier / acquisition columns (`Unnamed: 0`, `Seq`, `Offset`)
    can never enter the feature matrix
  * columns listed in schema.drop_columns (redundant copies of `Dur`,
    redundant encodings, near-degenerate and pseudo-random ID-like
    fields) can never enter the feature matrix
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


class FeaturePolicyError(Exception):
    """Raised when the configured feature set violates M1 policy."""


def _schema(config: dict[str, Any]) -> dict[str, Any]:
    schema = config.get("schema")
    if not isinstance(schema, dict):
        raise FeaturePolicyError("M1 config is missing a 'schema' section.")
    return schema


def forbidden_columns(config: dict[str, Any]) -> set[str]:
    """Every column that must never appear in the feature matrix."""
    schema = _schema(config)
    forbidden: set[str] = set()
    forbidden.add(schema["label_column"])
    for key in ("metadata_columns", "identifier_columns", "drop_columns"):
        forbidden.update(schema.get(key) or [])
    return forbidden


def get_feature_columns(config: dict[str, Any]) -> list[str]:
    """Return the ordered feature list, enforcing the policy.

    Ordering is taken verbatim from the config so that feature order is
    deterministic and reproducible across models and runs.
    """
    schema = _schema(config)
    features = schema.get("feature_columns")
    if not features:
        raise FeaturePolicyError(
            "schema.feature_columns is not set — refusing to guess features."
        )

    duplicates = [c for c in set(features) if features.count(c) > 1]
    if duplicates:
        raise FeaturePolicyError(
            f"Duplicate entries in feature_columns: {sorted(duplicates)}"
        )

    violations = sorted(set(features) & forbidden_columns(config))
    if violations:
        raise FeaturePolicyError(
            f"Forbidden columns present in feature_columns: {violations}. "
            f"Target, target-derived metadata, identifier and excluded "
            f"columns must never be model inputs."
        )

    return list(features)


def get_categorical_columns(config: dict[str, Any]) -> list[str]:
    """Categorical subset of the feature list, in feature order."""
    schema = _schema(config)
    categorical = set(schema.get("categorical_columns") or [])
    features = get_feature_columns(config)

    unknown = sorted(categorical - set(features))
    if unknown:
        raise FeaturePolicyError(
            f"categorical_columns not present in feature_columns: {unknown}"
        )
    # preserve feature ordering rather than config ordering
    return [c for c in features if c in categorical]


def get_numeric_columns(config: dict[str, Any]) -> list[str]:
    """Numeric subset of the feature list, in feature order."""
    categorical = set(get_categorical_columns(config))
    return [c for c in get_feature_columns(config) if c not in categorical]


def build_target(df: pd.DataFrame, config: dict[str, Any]) -> pd.Series:
    """Map the raw `Label` column to the binary target (Benign=0, Malicious=1).

    Raises FeaturePolicyError if the label column contains any value that
    is not declared in positive_class_values / negative_class_values —
    we never silently coerce an unrecognised label.
    """
    schema = _schema(config)
    label_column = schema["label_column"]
    if label_column not in df.columns:
        raise FeaturePolicyError(
            f"Label column '{label_column}' not found in the DataFrame."
        )

    positive = set(schema.get("positive_class_values") or [])
    negative = set(schema.get("negative_class_values") or [])
    if not positive or not negative:
        raise FeaturePolicyError(
            "schema.positive_class_values and schema.negative_class_values "
            "must both be set to build the binary target."
        )
    overlap = positive & negative
    if overlap:
        raise FeaturePolicyError(
            f"Values declared as both positive and negative: {sorted(overlap)}"
        )

    raw = df[label_column]
    observed = set(pd.unique(raw.dropna()))
    unknown = sorted(observed - positive - negative)
    if unknown:
        raise FeaturePolicyError(
            f"Unrecognised values in label column '{label_column}': {unknown}. "
            f"Declared: positive={sorted(positive)}, negative={sorted(negative)}."
        )
    if raw.isna().any():
        raise FeaturePolicyError(
            f"Label column '{label_column}' contains missing values."
        )

    y = raw.isin(positive).astype(np.int8)
    y.name = "target"
    return y


def build_feature_frame(
    df: pd.DataFrame, config: dict[str, Any]
) -> pd.DataFrame:
    """Return the feature-only DataFrame, in deterministic column order.

    No transformation is applied here — this is column selection only, so
    that the fitted preprocessing (which must see training rows only) is
    kept strictly separate from feature policy.
    """
    features = get_feature_columns(config)
    missing = [c for c in features if c not in df.columns]
    if missing:
        raise FeaturePolicyError(
            f"Configured feature columns absent from the DataFrame: {missing}"
        )
    # `df[features]` returns a new frame with exactly this column order
    return df[features]
