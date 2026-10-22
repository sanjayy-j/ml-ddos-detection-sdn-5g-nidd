"""
5G-NIDD flow-CSV loader for M2 (Entropy-Based Statistical Detection).

Reads ONLY the columns M2 needs, in chunks, validates the header against the real
dataset schema, derives explicit session IDs, and reports data-quality facts.
No values are invented or substituted.

Real schema facts this loader relies on (checked against BTS1_BTS2_fields_preserved.csv):
  * Source IP column ........ "SrcAddr"
  * Destination port column . "Dport"  (mixed tokens: decimal ints, hex like 0x0800 for ICMP,
                                        Argus service names like 'http'; EMPTY for many UDP flows)
  * Ordering column ......... "Rank"   (Argus record sequence; strictly +1 inside a capture file,
                                        restarts at 1 for every capture file)
  * Label column ............ "Label"  ('Benign' / 'Malicious'); optional "Attack Type", "Attack Tool"
  * There is NO session-ID column. "StartTime" is only 'mm:ss.f' (no hour/date), so it cannot
    be parsed to an absolute time and is NOT used for ordering.

Session definition (explicit and reproducible):
  A new session starts at the first row and at every row whose Rank is <= the previous row's
  Rank (a Rank reset = a new capture file). session_id is 1-based, in file order. Row order is
  never changed. Gaps inside a session (Rank step > 1) are counted and reported, not "repaired".

Missing values:
  Empty / whitespace-only SrcAddr or Dport cells become NaN (missing). Nothing is imputed here.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

SRC_COL = "SrcAddr"
DPORT_COL = "Dport"
RANK_COL = "Rank"
LABEL_COL = "Label"
OPTIONAL_COLS = ["Attack Type", "Attack Tool", "Proto"]  # Proto: reporting only, never a feature
REQUIRED_COLS = [SRC_COL, DPORT_COL, RANK_COL, LABEL_COL]
SESSION_COL = "session_id"


@dataclass
class LoadedData:
    """Loaded dataframe plus data-quality statistics (all computed from the real file)."""

    df: pd.DataFrame
    stats: Dict[str, Any] = field(default_factory=dict)


def validate_header(path: str, required: Optional[List[str]] = None) -> List[str]:
    """Read only the header; raise a precise error if required columns are absent."""
    required = required or REQUIRED_COLS
    header = list(pd.read_csv(path, nrows=0).columns)
    missing = [c for c in required if c not in header]
    if missing:
        raise ValueError(
            f"Input CSV '{path}' lacks required column(s) {missing}. "
            f"M2 needs {required}. Columns found ({len(header)}): {header}. "
            "Supply the 5G-NIDD flow CSV that contains these columns (e.g. "
            "BTS1_BTS2_fields_preserved.csv); M2 will not guess or substitute other fields."
        )
    return header


def _port_kind(tok: Any) -> str:
    if tok is None or (isinstance(tok, float) and np.isnan(tok)):
        return "missing"
    t = str(tok)
    if t.isdigit():
        return "decimal"
    if t.lower().startswith("0x"):
        return "hex"
    return "service_name"


def load_flows(
    path: str,
    max_rows: Optional[int] = None,
    chunksize: int = 200_000,
    malicious_label: str = "Malicious",
    benign_label: str = "Benign",
) -> LoadedData:
    """Load the M2-relevant columns of a 5G-NIDD flow CSV in chunks.

    Parameters:
        path: CSV path.
        max_rows: If given, read only the first N data rows (sessions may be truncated).
        chunksize: Rows per chunk.
        malicious_label / benign_label: The two expected Label values. Any other value raises.

    Returns:
        LoadedData(df, stats). df columns: SrcAddr, Dport (NaN where empty), Rank (int),
        Label, [Attack Type, Attack Tool, Proto if present], session_id (int, 1-based).
    """
    header = validate_header(path)
    usecols = REQUIRED_COLS + [c for c in OPTIONAL_COLS if c in header]

    parts: List[pd.DataFrame] = []
    remaining = max_rows
    for chunk in pd.read_csv(
        path, usecols=usecols, dtype=str, keep_default_na=False, chunksize=chunksize
    ):
        if remaining is not None:
            if remaining <= 0:
                break
            chunk = chunk.iloc[:remaining]
            remaining -= len(chunk)
        for c in chunk.columns:
            chunk[c] = chunk[c].str.strip()
        for c in (SRC_COL, DPORT_COL):
            chunk[c] = chunk[c].astype(object).where(chunk[c] != "", np.nan)
        parts.append(chunk)

    if not parts:
        raise ValueError(f"No data rows read from '{path}'.")
    df = pd.concat(parts, ignore_index=True)
    del parts

    # Rank must be integer-valued
    rank_num = pd.to_numeric(df[RANK_COL], errors="coerce")
    if rank_num.isna().any():
        bad = int(rank_num.isna().sum())
        raise ValueError(f"Column '{RANK_COL}' has {bad} non-integer value(s); cannot derive sessions.")
    df[RANK_COL] = rank_num.astype("int64")

    # Label must be exactly the two known values (checked, not assumed)
    label_counts = df[LABEL_COL].value_counts().to_dict()
    unknown = sorted(set(label_counts) - {malicious_label, benign_label})
    if unknown:
        raise ValueError(
            f"Unexpected Label value(s) {unknown}; expected only '{benign_label}' / '{malicious_label}'. "
            "Pass --benign-label/--malicious-label if the dataset uses different names."
        )

    # Explicit sessions from Rank resets (file order preserved)
    d = df[RANK_COL].diff()
    new_session = d.le(0).fillna(False)
    df[SESSION_COL] = (new_session.cumsum() + 1).astype("int64")
    gaps = int(((d > 1) & ~new_session).sum())

    # Share string objects to keep memory small
    for c in (SRC_COL, DPORT_COL):
        df[c] = pd.Categorical(df[c]).astype(object)

    stats = _collect_stats(df, label_counts, gaps, max_rows)
    return LoadedData(df=df, stats=stats)


def _collect_stats(df: pd.DataFrame, label_counts: Dict[str, int], gaps: int, max_rows: Optional[int]) -> Dict[str, Any]:
    dp_missing = df[DPORT_COL].isna()
    src_missing = df[SRC_COL].isna()
    kinds = df[DPORT_COL].map(_port_kind).value_counts().to_dict()
    sess_sizes = df.groupby(SESSION_COL).size()

    stats: Dict[str, Any] = {
        "n_rows": int(len(df)),
        "truncated_by_max_rows": bool(max_rows is not None),
        "n_sessions": int(sess_sizes.shape[0]),
        "session_sizes": {int(k): int(v) for k, v in sess_sizes.items()},
        "session_rule": "new session at first row and wherever Rank <= previous Rank (Rank reset)",
        "rank_gaps_within_sessions": gaps,
        "ordering": "original file order (Rank strictly increasing by 1 inside each session); "
                    "StartTime is mm:ss.f only and is not used",
        "label_counts": {str(k): int(v) for k, v in label_counts.items()},
        "n_unique_src_addr": int(df[SRC_COL].nunique()),
        "src_addr_missing": int(src_missing.sum()),
        "dport_missing": int(dp_missing.sum()),
        "dport_missing_fraction": float(dp_missing.mean()),
        "dport_token_kinds": {str(k): int(v) for k, v in kinds.items()},
        "n_unique_dport_tokens": int(df[DPORT_COL].nunique()),
        "dport_missing_by_label": {str(k): int(v) for k, v in df.loc[dp_missing, LABEL_COL].value_counts().items()},
    }
    if "Attack Type" in df.columns:
        stats["attack_type_counts"] = {str(k): int(v) for k, v in df["Attack Type"].value_counts().items()}
        stats["dport_missing_by_attack_type"] = {
            str(k): int(v) for k, v in df.loc[dp_missing, "Attack Type"].value_counts().items()
        }
    if "Proto" in df.columns:
        stats["dport_missing_by_proto"] = {str(k): int(v) for k, v in df.loc[dp_missing, "Proto"].value_counts().items()}
    stats["dport_missing_by_session"] = {
        int(k): int(v) for k, v in df.loc[dp_missing].groupby(SESSION_COL).size().items()
    }
    return stats
