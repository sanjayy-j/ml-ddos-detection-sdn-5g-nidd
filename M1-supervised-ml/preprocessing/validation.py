"""Stage C — M1 dataset/schema validation.

Checks the configured schema against an already-loaded DataFrame
(produced by preprocessing.data_loader.load_raw_data). This module is
read-only with respect to the DataFrame: it never drops, renames, or
otherwise transforms it, and it never guesses a label or feature
column that wasn't explicitly configured.

Validation errors mean the pipeline must not proceed (e.g. the real
config still has TBD schema fields, or a configured column doesn't
exist). Warnings flag likely misconfigurations that are not
necessarily fatal (e.g. a categorical column not listed as a feature).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pandas as pd


class SchemaValidationError(Exception):
    """Raised when schema/data validation fails."""


@dataclass
class ValidationResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    missing_value_counts: dict[str, int] | None = None
    label_distribution: dict[str, dict[str, float]] | None = None

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0


def _check_columns_exist(
    result: ValidationResult, field_name: str, columns: list[str], df_columns: set[str]
) -> None:
    missing = [c for c in columns if c not in df_columns]
    if missing:
        result.errors.append(
            f"Configured {field_name} not found in dataset columns: {missing}"
        )


def validate_schema(config: dict[str, Any], df: pd.DataFrame) -> ValidationResult:
    """Validate config['schema'] against the loaded DataFrame `df`.

    Does not raise on failure — inspect `result.is_valid` /
    `result.errors`. Use `validate_and_raise` for a raising wrapper.
    """
    result = ValidationResult()

    # Missing-value report is dataset-level and independent of schema
    # correctness, so it is always computed when a DataFrame is given.
    result.missing_value_counts = {
        str(col): int(count) for col, count in df.isnull().sum().items()
    }

    schema_cfg = config.get("schema")
    if not isinstance(schema_cfg, dict):
        result.errors.append("M1 config is missing a 'schema' section.")
        return result

    label_column = schema_cfg.get("label_column")
    feature_columns = schema_cfg.get("feature_columns")
    categorical_columns = schema_cfg.get("categorical_columns") or []
    identifier_columns = schema_cfg.get("identifier_columns") or []
    drop_columns = schema_cfg.get("drop_columns") or []

    # --- TBD checks: refuse to validate further against a real dataset
    # while the required schema fields are still unset. ---
    if not label_column:
        result.errors.append(
            "schema.label_column is not set (TBD). The real 5G-NIDD label "
            "column name must be supplied before validation can proceed."
        )
    if not feature_columns:
        result.errors.append(
            "schema.feature_columns is not set (TBD). The real 5G-NIDD "
            "feature column names must be supplied before validation can "
            "proceed."
        )

    df_columns = set(df.columns)

    # --- label_column ---
    if label_column:
        if label_column not in df_columns:
            result.errors.append(
                f"Configured label_column '{label_column}' was not found "
                f"in the dataset columns."
            )
        else:
            value_counts = df[label_column].value_counts(dropna=False)
            total = int(value_counts.sum())
            result.label_distribution = {
                str(value): {
                    "count": int(count),
                    "proportion": round(count / total, 6) if total else 0.0,
                }
                for value, count in value_counts.items()
            }

    # --- feature_columns ---
    if feature_columns:
        _check_columns_exist(result, "feature_columns", feature_columns, df_columns)

    # --- categorical / identifier / drop columns ---
    _check_columns_exist(result, "categorical_columns", categorical_columns, df_columns)
    _check_columns_exist(result, "identifier_columns", identifier_columns, df_columns)
    _check_columns_exist(result, "drop_columns", drop_columns, df_columns)

    # --- cross-consistency checks (non-fatal unless noted) ---
    if feature_columns:
        feature_set = set(feature_columns)

        if label_column and label_column in feature_set:
            # This is a leakage bug, not a mere style issue: treat as an error.
            result.errors.append(
                f"Configured label_column '{label_column}' is also present "
                f"in feature_columns — this would leak the label into the "
                f"model input."
            )

        overlap_drop = feature_set & set(drop_columns)
        if overlap_drop:
            result.warnings.append(
                f"Columns configured as both feature_columns and "
                f"drop_columns: {sorted(overlap_drop)}"
            )

        overlap_identifier = feature_set & set(identifier_columns)
        if overlap_identifier:
            result.warnings.append(
                f"Columns configured as both feature_columns and "
                f"identifier_columns: {sorted(overlap_identifier)}"
            )

        cat_not_in_features = set(categorical_columns) - feature_set
        if cat_not_in_features:
            result.warnings.append(
                f"categorical_columns configured but not included in "
                f"feature_columns: {sorted(cat_not_in_features)}"
            )

    return result


def validate_and_raise(config: dict[str, Any], df: pd.DataFrame) -> ValidationResult:
    """Run validate_schema and raise SchemaValidationError if invalid."""
    result = validate_schema(config, df)
    if not result.is_valid:
        raise SchemaValidationError("\n".join(result.errors))
    return result


# ---------------------------------------------------------------------------
# Stage D — dataset-level validation
# ---------------------------------------------------------------------------

# Columns verified byte-for-byte identical to `Dur` during Stage D
# inspection. If a future dataset revision breaks this, the redundancy
# exclusion in the config is no longer justified and must be revisited.
DUR_REDUNDANT_COLUMNS = ("RunTime", "Mean", "Sum", "Min", "Max")


def validate_dataset(config: dict[str, Any], df: pd.DataFrame) -> ValidationResult:
    """Schema validation plus dataset-level integrity checks.

    Detects unexpected schema drift (row/column counts, unknown target
    values, metadata columns) and re-verifies the redundancy assumption
    that justifies excluding the duplicate `Dur` columns, rather than
    trusting a one-off inspection.
    """
    result = validate_schema(config, df)
    schema_cfg = config.get("schema")
    if not isinstance(schema_cfg, dict):
        return result

    dataset_cfg = config.get("dataset") or {}
    df_columns = set(df.columns)

    # --- expected shape (warnings: a different capture is not an error) ---
    expected_rows = dataset_cfg.get("expected_rows")
    if expected_rows is not None and len(df) != int(expected_rows):
        result.warnings.append(
            f"Row count {len(df):,} differs from expected "
            f"{int(expected_rows):,} — schema decisions were derived from "
            f"the expected dataset."
        )
    expected_columns = dataset_cfg.get("expected_columns")
    if expected_columns is not None and df.shape[1] != int(expected_columns):
        result.warnings.append(
            f"Column count {df.shape[1]} differs from expected "
            f"{int(expected_columns)}."
        )

    # --- metadata columns must exist (they are needed for later analysis) ---
    metadata_columns = schema_cfg.get("metadata_columns") or []
    _check_columns_exist(result, "metadata_columns", metadata_columns, df_columns)

    # metadata must never be declared as a feature
    feature_columns = set(schema_cfg.get("feature_columns") or [])
    metadata_in_features = sorted(set(metadata_columns) & feature_columns)
    if metadata_in_features:
        result.errors.append(
            f"Target-derived metadata columns declared as features: "
            f"{metadata_in_features}"
        )

    # --- target values ---
    label_column = schema_cfg.get("label_column")
    if label_column and label_column in df_columns:
        declared = set(schema_cfg.get("positive_class_values") or []) | set(
            schema_cfg.get("negative_class_values") or []
        )
        if declared:
            observed = set(pd.unique(df[label_column].dropna()))
            unknown = sorted(observed - declared)
            if unknown:
                result.errors.append(
                    f"Label column '{label_column}' contains values not "
                    f"declared in positive/negative class values: {unknown}"
                )

    # --- redundancy assumption behind the Dur exclusions ---
    if "Dur" in df_columns:
        still_identical = [
            c for c in DUR_REDUNDANT_COLUMNS
            if c in df_columns and df["Dur"].equals(df[c])
        ]
        present = [c for c in DUR_REDUNDANT_COLUMNS if c in df_columns]
        not_identical = sorted(set(present) - set(still_identical))
        if not_identical:
            result.warnings.append(
                f"Columns previously identical to 'Dur' are no longer "
                f"identical: {not_identical} — the redundancy-based "
                f"exclusion should be re-examined."
            )

    return result
