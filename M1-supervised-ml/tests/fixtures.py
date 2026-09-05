"""Synthetic 5G-NIDD-shaped test data.

The real schema was verified programmatically in Stage D, so these
fixtures reuse the real column names with entirely synthetic values.
This lets the full pipeline be tested without the 263 MB Combined.csv.

Data produced here is SYNTHETIC and must never be reported as an
experimental result.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

# Real column order of Combined.csv (verified during Stage D inspection).
COLUMN_ORDER = [
    "Unnamed: 0", "Seq", "Dur", "RunTime", "Mean", "Sum", "Min", "Max",
    "Proto", "sTos", "dTos", "sDSb", "dDSb", "sTtl", "dTtl", "sHops", "dHops",
    "Cause", "TotPkts", "SrcPkts", "DstPkts", "TotBytes", "SrcBytes",
    "DstBytes", "Offset", "sMeanPktSz", "dMeanPktSz", "Load", "SrcLoad",
    "DstLoad", "Loss", "SrcLoss", "DstLoss", "pLoss", "SrcGap", "DstGap",
    "Rate", "SrcRate", "DstRate", "State", "SrcWin", "DstWin", "sVid", "dVid",
    "SrcTCPBase", "DstTCPBase", "TcpRtt", "SynAck", "AckDat",
    "Label", "Attack Type", "Attack Tool",
]

PROTOCOLS = ["udp", "tcp", "icmp", "sctp"]
STATES = ["REQ", "INT", "CON", "RST", "FIN"]
CAUSES = ["Status", "Start", "Shutdown"]
DSCP = ["cs0", "ef", "af11"]
ATTACKS = [
    ("SYNScan", "Nmap"),
    ("UDPFlood", "Hping3"),
    ("HTTPFlood", "Goldeneye"),
    ("SlowrateDoS", "Torshammer"),
]


def make_synthetic_5gnidd(
    n_blocks: int = 4,
    rows_per_block: int = 240,
    seed: int = 0,
    benign_only_blocks: tuple[int, ...] = (),
) -> pd.DataFrame:
    """Build a small frame mimicking Combined.csv's structure.

    Reproduces the structural properties the pipeline depends on:
      * contiguous capture blocks separated by `Offset` resets
      * a single `Unnamed: 0` reset marking the base-station boundary
      * attacks occupying a contiguous window inside each block (so a
        naive contiguous split would suffer prior shift)
      * `Dur` duplicated into RunTime/Mean/Sum/Min/Max
      * structured missingness on destination-side and TCP-only columns
    """
    rng = np.random.default_rng(seed)
    frames = []
    offset_base = 128
    index_counter = 0
    bs_boundary_block = n_blocks // 2

    for block in range(n_blocks):
        if block == bs_boundary_block:
            index_counter = 0  # base-station boundary: index restarts

        k = rows_per_block
        attack_type, attack_tool = ATTACKS[block % len(ATTACKS)]

        # attacks occupy a contiguous middle window of the capture
        labels = np.array(["Benign"] * k, dtype=object)
        if block not in benign_only_blocks:
            start = int(k * 0.25)
            end = int(k * 0.75)
            labels[start:end] = "Malicious"
        is_mal = labels == "Malicious"

        proto = rng.choice(PROTOCOLS, size=k, p=[0.6, 0.3, 0.07, 0.03])
        is_tcp = proto == "tcp"
        # destination-side fields exist only when reverse traffic was seen
        has_reverse = rng.random(k) < 0.35

        dur = np.abs(rng.exponential(0.4, size=k)).round(6)
        tot_pkts = rng.integers(1, 60, size=k)
        src_pkts = rng.integers(0, tot_pkts + 1)
        dst_pkts = tot_pkts - src_pkts
        tot_bytes = (tot_pkts * rng.integers(42, 1200, size=k)).astype(np.int64)
        src_bytes = (src_pkts * rng.integers(42, 900, size=k)).astype(np.int64)
        dst_bytes = np.maximum(tot_bytes - src_bytes, 0)

        def maybe(values, mask, dtype=float):
            out = np.full(k, np.nan, dtype=dtype)
            out[mask] = values[mask]
            return out

        data = {
            "Unnamed: 0": np.arange(index_counter, index_counter + k),
            "Seq": rng.integers(1, 100000, size=k),
            "Dur": dur,
            "Proto": proto,
            "sTos": rng.choice([0.0, 186.0], size=k, p=[0.98, 0.02]),
            "dTos": maybe(rng.choice([0.0, 186.0], size=k), has_reverse),
            "sDSb": rng.choice(DSCP, size=k, p=[0.96, 0.03, 0.01]),
            "dDSb": pd.Series(
                np.where(has_reverse, rng.choice(DSCP, size=k), None), dtype=object
            ),
            "sTtl": rng.integers(36, 256, size=k).astype(float),
            "dTtl": maybe(rng.integers(37, 256, size=k).astype(float), has_reverse),
            "sHops": rng.integers(0, 29, size=k).astype(float),
            "dHops": maybe(rng.integers(0, 51, size=k).astype(float), has_reverse),
            "Cause": rng.choice(CAUSES, size=k, p=[0.6, 0.39, 0.01]),
            "TotPkts": tot_pkts,
            "SrcPkts": src_pkts,
            "DstPkts": dst_pkts,
            "TotBytes": tot_bytes,
            "SrcBytes": src_bytes,
            "DstBytes": dst_bytes,
            # monotonically increasing within a block, reset at each block
            # start — this is what makes block boundaries detectable
            "Offset": offset_base + np.cumsum(rng.integers(1, 50, size=k)),
            "sMeanPktSz": (tot_bytes / np.maximum(tot_pkts, 1)).round(3),
            "dMeanPktSz": (dst_bytes / np.maximum(dst_pkts, 1)).round(3),
            # heavy-tailed, as in the real data
            "Load": rng.lognormal(6, 3, size=k).round(3),
            "SrcLoad": rng.lognormal(5, 3, size=k).round(3),
            "DstLoad": rng.lognormal(4, 3, size=k).round(3),
            "Loss": rng.integers(0, 3, size=k),
            "SrcLoss": rng.integers(0, 2, size=k),
            "DstLoss": rng.integers(0, 2, size=k),
            "pLoss": rng.random(k).round(4) * 10,
            "SrcGap": maybe(np.zeros(k), is_tcp),
            "DstGap": maybe(np.zeros(k), is_tcp),
            "Rate": rng.lognormal(3, 2.5, size=k).round(3),
            "SrcRate": rng.lognormal(2, 2.5, size=k).round(3),
            "DstRate": rng.lognormal(2, 2.5, size=k).round(3),
            "State": rng.choice(STATES, size=k),
            "SrcWin": maybe(rng.integers(0, 65536, size=k).astype(float), is_tcp),
            "DstWin": maybe(rng.integers(0, 65536, size=k).astype(float), is_tcp),
            "sVid": np.where(rng.random(k) < 0.1, 610.0, np.nan),
            "dVid": np.where(rng.random(k) < 0.02, 610.0, np.nan),
            "SrcTCPBase": maybe(
                rng.integers(1, 2**32, size=k).astype(float), is_tcp
            ),
            "DstTCPBase": maybe(
                rng.integers(1, 2**32, size=k).astype(float), is_tcp
            ),
            "TcpRtt": rng.random(k).round(6),
            "SynAck": rng.random(k).round(6),
            "AckDat": rng.random(k).round(6),
            "Label": labels,
            "Attack Type": np.where(is_mal, attack_type, "Benign"),
            "Attack Tool": np.where(is_mal, attack_tool, "Benign"),
        }

        block_df = pd.DataFrame(data)
        # Dur is duplicated across six identically-valued columns
        for twin in ("RunTime", "Mean", "Sum", "Min", "Max"):
            block_df[twin] = block_df["Dur"]

        frames.append(block_df[COLUMN_ORDER])
        index_counter += k

    return pd.concat(frames, ignore_index=True)


def synthetic_config(seed: int = 42) -> dict:
    """Config matching the real one, sized for the synthetic frame."""
    return {
        "seed": seed,
        "dataset": {"raw_path": None, "format": "csv"},
        "schema": {
            "label_column": "Label",
            "positive_class_values": ["Malicious"],
            "negative_class_values": ["Benign"],
            "metadata_columns": ["Attack Type", "Attack Tool"],
            "identifier_columns": ["Unnamed: 0", "Seq", "Offset"],
            "drop_columns": [
                "RunTime", "Mean", "Sum", "Min", "Max",
                "sTos", "dTos", "sHops", "dHops",
                "SrcGap", "DstGap",
                "SrcTCPBase", "DstTCPBase", "sVid", "dVid",
            ],
            "feature_columns": [
                "Dur", "Proto", "sDSb", "dDSb", "sTtl", "dTtl", "Cause",
                "TotPkts", "SrcPkts", "DstPkts", "TotBytes", "SrcBytes",
                "DstBytes", "sMeanPktSz", "dMeanPktSz", "Load", "SrcLoad",
                "DstLoad", "Loss", "SrcLoss", "DstLoss", "pLoss", "Rate",
                "SrcRate", "DstRate", "State", "SrcWin", "DstWin", "TcpRtt",
                "SynAck", "AckDat",
            ],
            "categorical_columns": ["Proto", "sDSb", "dDSb", "Cause", "State"],
        },
        "blocks": {"detect_column": "Offset", "base_station_column": "Unnamed: 0"},
        "split": {
            "strategy": "block_label_contiguous",
            "train_ratio": 0.70,
            "val_ratio": 0.15,
            "test_ratio": 0.15,
            "purge_rows": 0,
        },
        "duplicates": {"drop_exact_duplicates": False, "report": True},
        "class_imbalance": {"strategy": "class_weight"},
        "preprocessing": {
            "numeric_imputation": "median",
            "categorical_imputation": "__missing__",
            "log1p_skew_threshold": 2.0,
            "scaler": "standard",
            "add_missing_indicators": False,
        },
        "models": {"svm": {"train_subsample": 100}},
        "output": {
            "results_dir": "M1-supervised-ml/results",
            "processed_dir": "M1-supervised-ml/data/processed",
        },
    }
