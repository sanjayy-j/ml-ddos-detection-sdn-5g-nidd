"""Stage D — the feature decision report.

Produces a per-column KEEP/DROP record with the evidence behind each
decision, so that every exclusion in the M1 feature matrix is auditable
rather than folklore.
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from .features import get_categorical_columns, get_feature_columns

# Curated rationale per excluded column. Each reason states the *evidence*
# observed during Stage D inspection of the real Combined.csv.
EXCLUSION_REASONS: dict[str, tuple[str, str, str]] = {
    # column: (reason, leakage_concern, notes)
    "Unnamed: 0": (
        "CSV row-index artifact; monotonic capture position",
        "HIGH - encodes capture order, which is target-associated",
        "Used only to locate the base-station boundary (single decrease)",
    ),
    "Seq": (
        "Argus sequence number (identifier)",
        "HIGH - acquisition counter, not a network property",
        "137,210 distinct values",
    ),
    "Offset": (
        "Argus byte offset into the capture file (identifier)",
        "HIGH - encodes position within the capture",
        "Used only for capture-block detection (19 resets)",
    ),
    "RunTime": ("Byte-identical copy of Dur", "None - redundant", "Verified equal"),
    "Mean": ("Byte-identical copy of Dur", "None - redundant", "Verified equal"),
    "Sum": ("Byte-identical copy of Dur", "None - redundant", "Verified equal"),
    "Min": ("Byte-identical copy of Dur", "None - redundant", "Verified equal"),
    "Max": ("Byte-identical copy of Dur", "None - redundant", "Verified equal"),
    "sTos": (
        "Bijective 1:1 with retained sDSb (12 <-> 12 levels)",
        "None - redundant encoding",
        "Numeric ToS byte; sDSb keeps the nominal DSCP semantics",
    ),
    "dTos": (
        "1:1 into retained dDSb (7 -> 6 levels)",
        "None - redundant encoding",
        "Only 550 rows are finer-grained than dDSb",
    ),
    "sHops": (
        "Deterministic function of retained sTtl",
        "None - redundant",
        "Each sTtl value maps to exactly one sHops value",
    ),
    "dHops": (
        "Deterministic function of retained dTtl",
        "None - redundant",
        "Each dTtl value maps to exactly one dHops value",
    ),
    "SrcGap": (
        "Near-zero variance: 77.08% missing; ~all present values are 0.0",
        "MEDIUM - missingness is exactly Proto != tcp",
        "Only ~11 non-zero rows in 1.2M",
    ),
    "DstGap": (
        "Near-zero variance: 77.08% missing; ~all present values are 0.0",
        "MEDIUM - missingness is exactly Proto != tcp",
        "Only ~70 non-zero rows in 1.2M",
    ),
    "SrcTCPBase": (
        "TCP initial sequence number: pseudo-random identifier",
        "HIGH - identifier-like, 203,756 distinct values up to 2^32",
        "Excluded by project mandate and confirmed by inspection",
    ),
    "DstTCPBase": (
        "TCP initial sequence number: pseudo-random identifier",
        "HIGH - identifier-like, 135,743 distinct values up to 2^32",
        "Excluded by project mandate and confirmed by inspection",
    ),
    "sVid": (
        "Constant (single value 610) with 90.58% missing",
        "HIGH - P(malicious | present) = 0.00, a pure capture artifact",
        "Zero variance: no predictive content, only capture provenance",
    ),
    "dVid": (
        "Constant (single value 610) with 99.83% missing",
        "HIGH - P(malicious | present) = 0.00, a pure capture artifact",
        "Zero variance: no predictive content, only capture provenance",
    ),
    "Label": ("Prediction target", "TARGET", "Benign=0, Malicious=1"),
    "Attack Type": (
        "Target-derived metadata (perfectly aligned with Label)",
        "TARGET-DERIVED - would trivially reveal the label",
        "Retained outside the feature matrix for per-attack analysis",
    ),
    "Attack Tool": (
        "Target-derived metadata (perfectly aligned with Label)",
        "TARGET-DERIVED - would trivially reveal the label",
        "Retained outside the feature matrix for per-tool analysis",
    ),
}

KEEP_NOTES: dict[str, str] = {
    "Proto": "Genuine L3/L4 protocol; nominal one-hot",
    "State": "Genuine Argus flow state; nominal one-hot",
    "Cause": (
        "Argus record type (Start/Status/Shutdown). Acquisition-related but a "
        "legitimate flow attribute; flagged for ablation in Stage E"
    ),
    "sDSb": "Symbolic source DSCP class; nominal one-hot (replaces sTos)",
    "dDSb": "Symbolic destination DSCP class; nominal one-hot (replaces dTos)",
    "sTtl": "Source TTL; retained instead of the coarser sHops",
    "dTtl": "Destination TTL; retained instead of the coarser dHops",
    "Dur": "Flow duration; the single retained copy of six identical columns",
}


def build_feature_decision_report(
    df: pd.DataFrame, config: dict[str, Any]
) -> pd.DataFrame:
    """One row per raw dataset column with its KEEP/DROP decision."""
    features = set(get_feature_columns(config))
    categorical = set(get_categorical_columns(config))
    n = len(df)

    records = []
    for column in df.columns:
        series = df[column]
        missing = int(series.isna().sum())
        keep = column in features

        if keep:
            reason = (
                "Genuine network-flow feature retained in the M1 matrix "
                f"({'categorical' if column in categorical else 'numeric'})"
            )
            leakage = "None identified"
            notes = KEEP_NOTES.get(column, "")
        else:
            reason, leakage, notes = EXCLUSION_REASONS.get(
                column, ("Not selected as an M1 feature", "Unassessed", "")
            )

        records.append(
            {
                "column": column,
                "decision": "KEEP" if keep else "DROP",
                "role": (
                    ("categorical_feature" if column in categorical else
                     "numeric_feature") if keep else _role(column, config)
                ),
                "dtype": str(series.dtype),
                "missing_pct": round(100.0 * missing / n, 4) if n else 0.0,
                "cardinality": int(series.nunique(dropna=True)),
                "reason": reason,
                "leakage_concern": leakage,
                "notes": notes,
            }
        )

    return pd.DataFrame(records)


def _role(column: str, config: dict[str, Any]) -> str:
    schema = config.get("schema") or {}
    if column == schema.get("label_column"):
        return "target"
    if column in (schema.get("metadata_columns") or []):
        return "target_metadata"
    if column in (schema.get("identifier_columns") or []):
        return "identifier"
    if column in (schema.get("drop_columns") or []):
        return "excluded"
    return "unused"


def report_to_markdown(report: pd.DataFrame) -> str:
    """Render the decision report as a Markdown table."""
    kept = int((report["decision"] == "KEEP").sum())
    dropped = int((report["decision"] == "DROP").sum())
    lines = [
        "# M1 Feature Decision Report",
        "",
        f"- Columns in raw dataset: **{len(report)}**",
        f"- Retained as model features: **{kept}**",
        f"- Excluded: **{dropped}**",
        "",
        "| Column | Decision | Role | Dtype | Missing % | Cardinality | "
        "Reason | Leakage concern | Notes |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for row in report.itertuples(index=False):
        lines.append(
            f"| `{row.column}` | {row.decision} | {row.role} | {row.dtype} | "
            f"{row.missing_pct} | {row.cardinality} | {row.reason} | "
            f"{row.leakage_concern} | {row.notes} |"
        )
    return "\n".join(lines) + "\n"
