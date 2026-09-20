"""
Unit tests for fixed flow-count sliding-window framework in M2-entropy/windowing.py.
"""

import sys
import unittest
from pathlib import Path

# Add parent directory (M2-entropy) to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from windowing import FlowWindow, generate_flow_windows, slice_flow_windows

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    pd = None  # type: ignore
    HAS_PANDAS = False


class TestFlowCountWindowing(unittest.TestCase):
    """Test suite for slice_flow_windows and generate_flow_windows."""

    def setUp(self):
        """Create sample dataset fixtures for testing."""
        # 10-item sample list fixture (works with or without pandas)
        self.sample_list = list(range(10))

        if HAS_PANDAS:
            self.df_10 = pd.DataFrame(
                {
                    "flow_id": range(10),
                    "proto": ["tcp", "udp", "tcp", "icmp", "udp", "tcp", "udp", "tcp", "icmp", "udp"],
                    "val": [10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
                }
            )

    def test_normal_non_overlapping_windows_sequence(self):
        """Test non-overlapping windows on Python list/sequence."""
        windows = slice_flow_windows(self.sample_list, window_size=5, step_size=5)
        self.assertEqual(len(windows), 2)

        self.assertEqual(windows[0].window_id, 0)
        self.assertEqual((windows[0].start_idx, windows[0].end_idx), (0, 5))
        self.assertEqual(windows[0].data, [0, 1, 2, 3, 4])
        self.assertTrue(windows[0].is_complete)

        self.assertEqual(windows[1].window_id, 1)
        self.assertEqual((windows[1].start_idx, windows[1].end_idx), (5, 10))
        self.assertEqual(windows[1].data, [5, 6, 7, 8, 9])
        self.assertTrue(windows[1].is_complete)

    def test_overlapping_windows_sequence(self):
        """Test overlapping windows on Python list/sequence."""
        windows = slice_flow_windows(self.sample_list, window_size=4, step_size=2, drop_incomplete=False)
        # Windows: [0..4], [2..6], [4..8], [6..10], [8..10] (partial)
        self.assertEqual(len(windows), 5)

        self.assertEqual((windows[0].start_idx, windows[0].end_idx), (0, 4))
        self.assertEqual((windows[1].start_idx, windows[1].end_idx), (2, 6))
        self.assertEqual((windows[2].start_idx, windows[2].end_idx), (4, 8))
        self.assertEqual((windows[3].start_idx, windows[3].end_idx), (6, 10))
        self.assertEqual((windows[4].start_idx, windows[4].end_idx), (8, 10))

        self.assertTrue(windows[0].is_complete)
        self.assertTrue(windows[3].is_complete)
        self.assertFalse(windows[4].is_complete)
        self.assertEqual(windows[4].flow_count, 2)

    def test_drop_incomplete_true_and_false(self):
        """Test partial final window behavior under drop_incomplete=True/False."""
        # 10 items, window_size=4, step_size=3
        # pos 0: 0..4 (complete)
        # pos 3: 3..7 (complete)
        # pos 6: 6..10 (complete)
        # pos 9: 9..10 (partial, size 1)
        windows_keep = slice_flow_windows(self.sample_list, window_size=4, step_size=3, drop_incomplete=False)
        self.assertEqual(len(windows_keep), 4)
        self.assertFalse(windows_keep[-1].is_complete)
        self.assertEqual(windows_keep[-1].flow_count, 1)
        self.assertEqual((windows_keep[-1].start_idx, windows_keep[-1].end_idx), (9, 10))

        windows_drop = slice_flow_windows(self.sample_list, window_size=4, step_size=3, drop_incomplete=True)
        self.assertEqual(len(windows_drop), 3)
        self.assertTrue(all(w.is_complete for w in windows_drop))
        self.assertEqual((windows_drop[-1].start_idx, windows_drop[-1].end_idx), (6, 10))

    def test_dataset_smaller_than_window_size(self):
        """Test behavior when dataset length is smaller than window_size."""
        # 10 items, window_size=20, step_size=5
        windows_keep = slice_flow_windows(self.sample_list, window_size=20, step_size=5, drop_incomplete=False)
        self.assertEqual(len(windows_keep), 1)
        self.assertEqual((windows_keep[0].start_idx, windows_keep[0].end_idx), (0, 10))
        self.assertFalse(windows_keep[0].is_complete)
        self.assertEqual(windows_keep[0].flow_count, 10)

        windows_drop = slice_flow_windows(self.sample_list, window_size=20, step_size=5, drop_incomplete=True)
        self.assertEqual(len(windows_drop), 0)

    def test_invalid_window_size(self):
        """Test validation for invalid window_size (<= 0 or non-integer)."""
        with self.assertRaises(ValueError):
            slice_flow_windows(self.sample_list, window_size=0, step_size=2)

        with self.assertRaises(ValueError):
            slice_flow_windows(self.sample_list, window_size=-5, step_size=2)

        with self.assertRaises(TypeError):
            slice_flow_windows(self.sample_list, window_size=4.5, step_size=2)  # type: ignore

        with self.assertRaises(TypeError):
            slice_flow_windows(self.sample_list, window_size=True, step_size=2)  # type: ignore

    def test_invalid_step_size(self):
        """Test validation for invalid step_size (<= 0 or non-integer)."""
        with self.assertRaises(ValueError):
            slice_flow_windows(self.sample_list, window_size=4, step_size=0)

        with self.assertRaises(ValueError):
            slice_flow_windows(self.sample_list, window_size=4, step_size=-2)

        with self.assertRaises(TypeError):
            slice_flow_windows(self.sample_list, window_size=4, step_size="2")  # type: ignore

    def test_empty_sequence(self):
        """Test windowing on an empty sequence."""
        windows = slice_flow_windows([], window_size=5, step_size=2, drop_incomplete=False)
        self.assertEqual(len(windows), 0)

    def test_preservation_of_original_row_order(self):
        """Test that original row order and slice values are preserved exactly."""
        data_order = list(range(100, 150))
        windows = slice_flow_windows(data_order, window_size=10, step_size=10)

        for i, win in enumerate(windows):
            expected_seq = list(range(100 + i * 10, 100 + (i + 1) * 10))
            self.assertEqual(win.data, expected_seq)

    def test_pandas_dataframe_windowing_if_available(self):
        """Test DataFrame windowing if pandas is installed."""
        if HAS_PANDAS:
            windows = slice_flow_windows(self.df_10, window_size=5, step_size=5)
            self.assertEqual(len(windows), 2)
            self.assertEqual(list(windows[0].data["flow_id"]), [0, 1, 2, 3, 4])
            self.assertEqual(list(windows[1].data["flow_id"]), [5, 6, 7, 8, 9])

    def test_session_boundary_windowing_if_pandas_available(self):
        """Test session-boundary windowing when session_col is provided."""
        if HAS_PANDAS:
            df_sessions = pd.DataFrame(
                {
                    "session": ["A"] * 6 + ["B"] * 5,
                    "flow_id": range(11),
                }
            )
            # Session A (6 rows): [0..4] (complete), [4..6] (partial, len 2)
            # Session B (5 rows): [6..10] (complete), [10..11] (partial, len 1)
            windows = slice_flow_windows(df_sessions, window_size=4, step_size=4, session_col="session", drop_incomplete=False)
            self.assertEqual(len(windows), 4)

            self.assertEqual(windows[0].session_id, "A")
            self.assertEqual((windows[0].start_idx, windows[0].end_idx), (0, 4))
            self.assertTrue(windows[0].is_complete)

            self.assertEqual(windows[1].session_id, "A")
            self.assertEqual((windows[1].start_idx, windows[1].end_idx), (4, 6))
            self.assertFalse(windows[1].is_complete)

            self.assertEqual(windows[2].session_id, "B")
            self.assertEqual((windows[2].start_idx, windows[2].end_idx), (6, 10))
            self.assertTrue(windows[2].is_complete)

            self.assertEqual(windows[3].session_id, "B")
            self.assertEqual((windows[3].start_idx, windows[3].end_idx), (10, 11))
            self.assertFalse(windows[3].is_complete)

    def test_session_col_key_error(self):
        """Test that missing session_col raises KeyError."""
        if HAS_PANDAS:
            with self.assertRaises(KeyError):
                slice_flow_windows(self.df_10, window_size=5, step_size=5, session_col="non_existent_col")


if __name__ == "__main__":
    unittest.main()
