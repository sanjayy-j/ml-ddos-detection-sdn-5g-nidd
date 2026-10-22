"""Tests for the 5G-NIDD loader: schema validation, sessions from Rank resets, missing values."""

import os
import sys
import tempfile
import unittest
from pathlib import Path

SYS_PATH_M2 = str(Path(__file__).resolve().parent.parent)
if SYS_PATH_M2 not in sys.path:
    sys.path.insert(0, SYS_PATH_M2)

import numpy as np
import pandas as pd

from data_loader import load_flows, validate_header


def write_csv(path, rows, header=None):
    header = header or ["", "SrcAddr", "Rank", "StartTime", "Proto", "Dport", "Label", "Attack Type", "Attack Tool", "Unused"]
    with open(path, "w") as fh:
        fh.write(",".join(header) + "\n")
        for i, r in enumerate(rows):
            fh.write(",".join([str(i)] + [str(x) for x in r]) + "\n")


# (SrcAddr, Rank, StartTime, Proto, Dport, Label, Attack Type, Attack Tool, Unused)
ROWS = [
    ("10.0.0.1", 1, "30:02.6", "tcp", "http", "Benign", "Benign", "Benign", "x"),
    ("10.0.0.2", 2, "30:03.6", "udp", "", "Malicious", "UDPFlood", "Hping3", "x"),
    ("10.0.0.1", 3, "30:04.6", "icmp", "0x0800", "Benign", "Benign", "Benign", "x"),
    ("10.0.0.3", 1, "10:00.0", "tcp", "853", "Malicious", "SYNScan", "Nmap", "x"),   # Rank reset
    ("10.0.0.3", 2, "09:59.0", "udp", " ", "Benign", "Benign", "Benign", "x"),       # whitespace-only
    ("10.0.0.4", 1, "00:01.0", "tcp", "22", "Benign", "Benign", "Benign", "x"),      # Rank reset
]


class TestLoader(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "flows.csv")
        write_csv(self.path, ROWS)

    def tearDown(self):
        self.tmp.cleanup()

    def test_only_needed_columns_are_loaded(self):
        df = load_flows(self.path).df
        self.assertNotIn("Unused", df.columns)
        self.assertNotIn("StartTime", df.columns)
        for c in ("SrcAddr", "Dport", "Rank", "Label", "session_id"):
            self.assertIn(c, df.columns)

    def test_sessions_from_rank_resets_and_order_preserved(self):
        df = load_flows(self.path).df
        self.assertEqual(df["session_id"].tolist(), [1, 1, 1, 2, 2, 3])
        self.assertEqual(df["Rank"].tolist(), [1, 2, 3, 1, 2, 1])      # file order untouched

    def test_missing_dport_is_nan_and_counted_not_invented(self):
        res = load_flows(self.path)
        self.assertEqual(int(res.df["Dport"].isna().sum()), 2)           # '' and ' '
        self.assertEqual(res.stats["dport_missing"], 2)
        self.assertEqual(res.stats["dport_missing_by_attack_type"], {"UDPFlood": 1, "Benign": 1})
        self.assertEqual(res.stats["dport_missing_by_label"], {"Malicious": 1, "Benign": 1})
        self.assertEqual(res.stats["dport_missing_by_proto"], {"udp": 2})

    def test_port_tokens_kept_verbatim(self):
        df = load_flows(self.path).df
        self.assertEqual(df["Dport"].dropna().tolist(), ["http", "0x0800", "853", "22"])
        kinds = load_flows(self.path).stats["dport_token_kinds"]
        self.assertEqual(kinds, {"decimal": 2, "service_name": 1, "hex": 1, "missing": 2})

    def test_session_stats(self):
        st = load_flows(self.path).stats
        self.assertEqual(st["n_sessions"], 3)
        self.assertEqual(st["session_sizes"], {1: 3, 2: 2, 3: 1})
        self.assertEqual(st["rank_gaps_within_sessions"], 0)

    def test_rank_gap_inside_session_is_reported_not_split(self):
        rows = [r for r in ROWS]
        rows[1] = ("10.0.0.2", 3, "30:03.6", "udp", "", "Malicious", "UDPFlood", "Hping3", "x")  # 1 -> 3 (gap)
        rows[2] = ("10.0.0.1", 4, "30:04.6", "icmp", "0x0800", "Benign", "Benign", "Benign", "x")
        write_csv(self.path, rows)
        res = load_flows(self.path)
        self.assertEqual(res.stats["rank_gaps_within_sessions"], 1)
        self.assertEqual(res.df["session_id"].tolist()[:3], [1, 1, 1])      # gap does not split a session

    def test_max_rows(self):
        self.assertEqual(len(load_flows(self.path, max_rows=4).df), 4)

    def test_chunked_equals_single_read(self):
        a = load_flows(self.path, chunksize=2).df
        b = load_flows(self.path, chunksize=1000).df
        pd.testing.assert_frame_equal(a, b)

    def test_missing_required_column_gives_clear_error(self):
        header = ["", "SrcAddr", "Rank", "Proto", "Label"]            # no Dport
        write_csv(self.path, [("a", 1, "tcp", "Benign")], header=header)
        with self.assertRaises(ValueError) as cm:
            load_flows(self.path)
        self.assertIn("Dport", str(cm.exception))
        self.assertIn("will not guess", str(cm.exception))

    def test_unexpected_label_value_rejected(self):
        rows = list(ROWS)
        rows[0] = ("10.0.0.1", 1, "30:02.6", "tcp", "http", "Weird", "Benign", "Benign", "x")
        write_csv(self.path, rows)
        with self.assertRaises(ValueError):
            load_flows(self.path)

    def test_validate_header_lists_found_columns(self):
        self.assertIn("SrcAddr", validate_header(self.path))


if __name__ == "__main__":
    unittest.main()
