"""Phase 3.4 — positional window aggregates over preceding flow records.

Faculty correction item 3 asked for per-source and per-second aggregates
(flows per source per second, bytes per second) to test whether the
42-byte single-packet UDP vector becomes separable under richer features.

Neither is computable from `Combined.csv`:

  * there is no source identifier — the 51 columns are Argus flow
    statistics with no address or port field, so rows cannot be grouped
    by source;
  * there is no clock — `Offset` is an int64 byte offset into the capture
    (it reaches 38,032,036 over 1,215,890 rows, ~1 distinct value per
    row), and `Dur`/`RunTime` are durations, not timestamps, so rows
    cannot be binned per second.

This script therefore builds the nearest computable substitute: causal
aggregates over the K flow records immediately *preceding* each row
within its own capture block. It tests TEMPORAL aggregation using row
order as a proxy for time — the same proxy M2 already relies on — and it
is NOT per-source aggregation. The per-session Fairdata Argus/PCAP
files, which do carry addresses and epoch times, remain the stronger
test of the faculty's actual request.

Guarantees:

  * windows never cross a capture-block boundary (blocks are detected
    exactly as `preprocessing.splitting` detects them, from `Offset`
    resets);
  * windows are strictly backward-looking, so no row sees its own value
    or any later row — there is no look-ahead;
  * only feature columns feed the aggregates. `Label`, `Attack Type` and
    `Attack Tool` are never read.

Output is one augmented CSV carrying the original columns plus 7 derived
columns per K, so the existing preprocessing pipeline can consume it
unchanged and recompute the Eq. (5) label-conflict bound for the
enlarged representation.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

M1_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = M1_ROOT.parent
if str(M1_ROOT) not in sys.path:
    sys.path.insert(0, str(M1_ROOT))

from preprocessing.data_loader import load_config_file  # noqa: E402
from preprocessing.pipeline import resolve_path  # noqa: E402

DEFAULT_KS = (10, 50, 100)

# Columns the aggregates are computed from. All are retained features of
# the primary representation; no label-derived column appears here.
BYTES_COL = "TotBytes"
PKTS_COL = "TotPkts"
PROTO_COL = "Proto"
BLOCK_COL = "Offset"


def detect_blocks(offset: pd.Series) -> np.ndarray:
    """Block id per row: a new block starts where `Offset` decreases.

    This mirrors `preprocessing.splitting`: `Offset` is non-decreasing
    inside every capture block, so a decrease marks a block boundary.
    """
    resets = offset.diff() < 0
    resets.iloc[0] = False
    return resets.cumsum().to_numpy()


def trailing(frame: pd.DataFrame, block: np.ndarray, col: str, k: int,
             how: str) -> np.ndarray:
    """Aggregate of `col` over the k rows strictly before each row."""
    grouped = frame.groupby(block, sort=False)[col]
    # shift(1) drops the current row; min_periods=1 keeps short windows
    # at the start of a block instead of producing NaN.
    rolled = grouped.transform(
        lambda s: s.shift(1).rolling(window=k, min_periods=1).agg(how))
    return rolled.to_numpy()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config",
                        default=str(M1_ROOT / "config" / "m1_config.yaml"))
    parser.add_argument("--ks", default=",".join(str(k) for k in DEFAULT_KS),
                        help="comma-separated window sizes (default 10,50,100)")
    parser.add_argument("--out", default=None,
                        help="output CSV (default: data/processed/"
                             "window_features/Combined_windowed.csv)")
    args = parser.parse_args()

    ks = [int(k) for k in args.ks.split(",") if k.strip()]
    config = load_config_file(args.config)
    raw_path = resolve_path(
        REPO_ROOT, (config.get("dataset") or {}).get("raw_path",
                                                     "data/raw/Combined.csv"))
    out_path = Path(args.out) if args.out else resolve_path(
        REPO_ROOT,
        "M1-supervised-ml/data/processed/window_features/Combined_windowed.csv")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    print("[1/4] reading " + str(raw_path), flush=True)
    t0 = time.perf_counter()
    df = pd.read_csv(raw_path, low_memory=False)
    print("      {:,} rows x {} columns in {:.1f}s".format(
        len(df), df.shape[1], time.perf_counter() - t0), flush=True)

    print("[2/4] detecting capture blocks from " + BLOCK_COL, flush=True)
    block = detect_blocks(df[BLOCK_COL])
    n_blocks = int(block.max()) + 1
    print("      {} blocks (expected 20)".format(n_blocks), flush=True)
    if n_blocks != 20:
        print("      STOP: block detection disagrees with the documented 20 "
              "capture sessions; not writing output", flush=True)
        return 1

    print("[3/4] building causal window aggregates for K=" + str(ks), flush=True)
    proto = df[PROTO_COL].astype(str).str.lower()
    is_udp = (proto == "udp").astype(np.float32)
    is_tcp = (proto == "tcp").astype(np.float32)
    work = pd.DataFrame({
        BYTES_COL: df[BYTES_COL].astype(np.float64),
        PKTS_COL: df[PKTS_COL].astype(np.float64),
        "_udp": is_udp,
        "_tcp": is_tcp,
        "_one": np.ones(len(df), dtype=np.float64),
    })

    new_cols: dict[str, np.ndarray] = {}
    for k in ks:
        t0 = time.perf_counter()
        p = f"win{k}_"
        new_cols[p + "flow_count"] = trailing(work, block, "_one", k, "sum")
        new_cols[p + "bytes_sum"] = trailing(work, block, BYTES_COL, k, "sum")
        new_cols[p + "bytes_mean"] = trailing(work, block, BYTES_COL, k, "mean")
        new_cols[p + "pkts_sum"] = trailing(work, block, PKTS_COL, k, "sum")
        new_cols[p + "pkts_mean"] = trailing(work, block, PKTS_COL, k, "mean")
        new_cols[p + "frac_udp"] = trailing(work, block, "_udp", k, "mean")
        new_cols[p + "frac_tcp"] = trailing(work, block, "_tcp", k, "mean")
        print("      K={:<4} 7 columns in {:.1f}s".format(
            k, time.perf_counter() - t0), flush=True)

    augmented = pd.concat([df, pd.DataFrame(new_cols, index=df.index)], axis=1)

    # The first row of each block has no predecessor; those windows are
    # empty and are filled with 0 (no preceding traffic observed).
    fill = {c: 0.0 for c in new_cols}
    augmented = augmented.fillna(value=fill)

    print("[4/4] writing " + str(out_path), flush=True)
    t0 = time.perf_counter()
    augmented.to_csv(out_path, index=False)
    print("      {:,} rows x {} columns ({} new) in {:.1f}s".format(
        len(augmented), augmented.shape[1], len(new_cols),
        time.perf_counter() - t0), flush=True)
    print("      new columns: " + ", ".join(sorted(new_cols)), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
