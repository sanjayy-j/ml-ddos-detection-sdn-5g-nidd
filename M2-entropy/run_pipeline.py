"""
Command-Line Runner for M2 End-to-End Offline Entropy Detection Pipeline.

Usage:
    python M2-entropy/run_pipeline.py [OPTIONS]

Examples:
    # Run on synthetic flow dataset (default if no input provided):
    python M2-entropy/run_pipeline.py

    # Run on a specific dataset sample:
    python M2-entropy/run_pipeline.py --input path/to/dataset.csv --nrows 5000 --window-size 100 --step-size 50
"""

import argparse
import os
import sys
from pathlib import Path

# Ensure M2-entropy is in sys.path
SYS_PATH_M2 = str(Path(__file__).resolve().parent)
if SYS_PATH_M2 not in sys.path:
    sys.path.insert(0, SYS_PATH_M2)

import pandas as pd
from pipeline import PipelineConfig, run_entropy_pipeline
from thresholds import ThresholdConfig


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run M2 End-to-End Entropy-Based Statistical Detection Pipeline."
    )
    parser.add_argument("--input", type=str, default=None, help="Path to input CSV flow dataset.")
    parser.add_argument("--nrows", type=int, default=5000, help="Number of rows to load from input CSV.")
    parser.add_argument("--window-size", type=int, default=100, help="Flow-count window size W.")
    parser.add_argument("--step-size", type=int, default=50, help="Flow-count step size S.")
    parser.add_argument("--alpha", type=float, default=0.2, help="EWMA smoothing factor alpha in (0, 1].")
    parser.add_argument("--history-len", type=int, default=50, help="Threshold historical buffer length.")
    parser.add_argument("--min-history", type=int, default=10, help="Threshold min history for warm-up.")
    parser.add_argument("--k-sensitivity", type=float, default=3.0, help="MAD sensitivity multiplier k.")
    parser.add_argument("--voting-threshold", type=int, default=2, help="Consensus voting threshold.")
    parser.add_argument("--session-col", type=str, default=None, help="Optional session column name.")
    parser.add_argument(
        "--output",
        type=str,
        default=os.path.join(SYS_PATH_M2, "results", "pipeline_output.csv"),
        help="Path to save output CSV result.",
    )

    args = parser.parse_args()

    input_path = args.input
    df_input = None

    if input_path is None:
        # Check standard Combined.csv location at root if present, else synthetic demo
        root_combined = os.path.abspath(os.path.join(SYS_PATH_M2, "..", "Combined.csv"))
        if os.path.exists(root_combined):
            input_path = root_combined
            print(f"[INFO] Using dataset found at: {input_path}")
        else:
            print("[INFO] No input dataset specified or found. Generating synthetic demo flow dataset.")
            df_input = pd.DataFrame({
                "Proto": ["tcp", "udp", "icmp", "tcp", "tcp"] * 200,
                "State": ["CON", "FIN", "INT", "CON", "REQ"] * 200,
                "sTtl": [64, 128, 64, 255, 64] * 200,
                "sDSb": [0, 0, 0, 0, 0] * 200,
                "TotPkts": [10, 20, 5, 100, 15] * 200,
                "TotBytes": [1000, 2000, 500, 10000, 1500] * 200,
                "Rate": [100.0, 50.0, 20.0, 500.0, 80.0] * 200,
                "Dur": [0.1, 0.4, 0.25, 0.2, 0.18] * 200,
                "Label": [0, 0, 0, 1, 0] * 200,
                "Attack Type": ["Benign", "Benign", "Benign", "UDP-Flood", "Benign"] * 200,
            })

    thresh_cfg = ThresholdConfig(
        history_len=args.history_len,
        min_history=args.min_history,
        k_sensitivity=args.k_sensitivity,
        voting_threshold=args.voting_threshold,
    )

    cfg = PipelineConfig(
        input_path=input_path,
        df=df_input,
        nrows=args.nrows,
        window_size=args.window_size,
        step_size=args.step_size,
        alpha=args.alpha,
        threshold_config=thresh_cfg,
        session_col=args.session_col,
        output_path=args.output,
    )

    print("Running M2 End-to-End Pipeline...")
    res = run_entropy_pipeline(cfg)

    print("\n--- Pipeline Execution Summary ---")
    print(f"Input Rows Processed:       {res.input_row_count}")
    print(f"Generated Windows:          {res.number_of_windows}")
    print(f"Complete Windows:           {res.number_of_complete_windows}")
    print(f"Raw Entropy Features ({len(res.entropy_columns)}):  {res.entropy_columns}")
    print(f"EWMA Smoothed Features ({len(res.ewma_columns)}): {res.ewma_columns}")
    print(f"Output DataFrame Shape:     {res.output_df.shape}")
    if res.output_path:
        print(f"Results Saved To:           {res.output_path}")
    print("-----------------------------------\n")


if __name__ == "__main__":
    main()
