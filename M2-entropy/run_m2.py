"""
M2 command-line entry point: Entropy-Based Statistical Detection on 5G-NIDD flow data.

    python M2-entropy/run_m2.py --input /path/to/BTS1_BTS2_fields_preserved.csv

Stages (all existing M2 modules, unchanged in architecture):
  load (chunked, columns SrcAddr/Dport/Rank/Label only)
  -> sessions from Rank resets -> flow-count sliding windows (never cross a session)
  -> Shannon entropy of SrcAddr and of Dport per window (two SEPARATE features)
  -> EWMA per feature (state reset at each session boundary)
  -> adaptive median/MAD thresholds (history reset at each session boundary)
  -> per-feature alarms + voting -> window anomaly decision
  -> evaluation against the dataset's Label (after detection; labels never used by detector)

Outputs (in --output-dir, default M2-entropy/results/m2_run):
  windows.csv    one row per window: entropies, EWMA, baselines, thresholds, alarms, y_true, ...
  metrics.json   run configuration, data-quality statistics, pipeline summary, evaluation
"""

import argparse
import json
import os
import platform
import sys
from pathlib import Path

SYS_PATH_M2 = str(Path(__file__).resolve().parent)
if SYS_PATH_M2 not in sys.path:
    sys.path.insert(0, SYS_PATH_M2)

import numpy as np
import pandas as pd

from data_loader import DPORT_COL, SESSION_COL, SRC_COL, load_flows
from evaluation import evaluate_windows, label_windows
from features import FeatureConfig
from pipeline import PipelineConfig, run_entropy_pipeline
from thresholds import ThresholdConfig


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="M2 entropy-based DDoS detection (source-IP & destination-port entropy) on 5G-NIDD."
    )
    p.add_argument("--input", required=True, help="Path to the 5G-NIDD flow CSV (e.g. BTS1_BTS2_fields_preserved.csv).")
    p.add_argument("--output-dir", default=os.path.join(SYS_PATH_M2, "results", "m2_run"),
                   help="Directory for windows.csv and metrics.json (default: M2-entropy/results/m2_run).")
    p.add_argument("--max-rows", type=int, default=None,
                   help="Read only the first N data rows (quick test; truncates sessions). Default: all rows.")
    p.add_argument("--chunksize", type=int, default=200_000, help="CSV read chunk size.")
    p.add_argument("--window-size", type=int, default=100, help="Flows per window W (default 100).")
    p.add_argument("--step-size", type=int, default=50, help="Flows to advance between windows S (default 50).")
    p.add_argument("--drop-incomplete", action="store_true", help="Drop partial trailing windows of each session.")
    p.add_argument("--alpha", type=float, default=0.2, help="EWMA smoothing factor in (0,1] (default 0.2).")
    p.add_argument("--history-len", type=int, default=50, help="Threshold history length (default 50).")
    p.add_argument("--min-history", type=int, default=10, help="Warm-up windows before alarms (default 10).")
    p.add_argument("--k-sensitivity", type=float, default=3.0, help="MAD multiplier k (default 3.0).")
    p.add_argument("--direction", choices=["lower", "upper", "both"], default="both",
                   help="Alarm direction relative to baseline (default both).")
    p.add_argument("--voting-threshold", type=int, default=2,
                   help="Feature alarms required for a window alarm; 1 = either feature, 2 = both (default 2).")
    p.add_argument("--dport-missing", choices=["exclude", "category"], default="exclude",
                   help="exclude (default): entropy of Dport over OBSERVED ports only; windows with fewer than "
                        "--min-observed observed ports get NaN (not evaluable). "
                        "category: treat missing Dport as one explicit '__missing__' category.")
    p.add_argument("--min-observed", type=int, default=10,
                   help="With --dport-missing exclude: minimum observed Dport values per window (default 10).")
    p.add_argument("--attack-fraction", type=float, default=0.5,
                   help="A window is an attack window if >= this fraction of its flows are malicious (default 0.5).")
    p.add_argument("--benign-label", default="Benign")
    p.add_argument("--malicious-label", default="Malicious")
    p.add_argument("--no-eval", action="store_true", help="Skip evaluation against labels.")
    return p


def run(args: argparse.Namespace) -> dict:
    if not os.path.isfile(args.input):
        raise FileNotFoundError(
            f"Input file not found: {args.input}\n"
            "Unzip BTS1_BTS2_fields_preserved.zip and pass the extracted CSV via --input."
        )

    print(f"[1/5] Loading {args.input} (columns: {SRC_COL}, {DPORT_COL}, Rank, Label, ...)")
    loaded = load_flows(
        args.input, max_rows=args.max_rows, chunksize=args.chunksize,
        malicious_label=args.malicious_label, benign_label=args.benign_label,
    )
    df, dq = loaded.df, loaded.stats
    print(f"      rows={dq['n_rows']:,}  sessions={dq['n_sessions']}  "
          f"Dport missing={dq['dport_missing']:,} ({dq['dport_missing_fraction']:.1%})  "
          f"SrcAddr missing={dq['src_addr_missing']:,}")

    exclude_missing = args.dport_missing == "exclude"
    feat_cfg = FeatureConfig(
        categorical_cols=[SRC_COL, DPORT_COL],   # two separate features -> two separate entropies
        numerical_cols=[],
        unobserved_missing_cols=[DPORT_COL] if exclude_missing else [],
        min_observed=args.min_observed,
    )
    thr_cfg = ThresholdConfig(
        history_len=args.history_len,
        min_history=args.min_history,
        min_valid_history=args.min_history,
        k_sensitivity=args.k_sensitivity,
        direction=args.direction,
        voting_threshold=args.voting_threshold,
    )
    pipe_cfg = PipelineConfig(
        df=df,
        window_size=args.window_size,
        step_size=args.step_size,
        drop_incomplete=args.drop_incomplete,
        alpha=args.alpha,
        feature_config=feat_cfg,
        threshold_config=thr_cfg,
        session_col=SESSION_COL,
    )

    print("[2/5] Windowing, entropy, EWMA, adaptive thresholds ...")
    res = run_entropy_pipeline(pipe_cfg)
    out = res.output_df
    for need in (f"{SRC_COL}_entropy", f"{DPORT_COL}_entropy"):
        if need not in out.columns:
            raise RuntimeError(f"Expected separate entropy feature '{need}' missing from output.")
    print(f"      windows={res.number_of_windows:,} (complete={res.number_of_complete_windows:,})")

    metrics: dict = {}
    if not args.no_eval:
        print("[3/5] Evaluating against dataset labels ...")
        out = label_windows(
            out, df, label_col="Label", malicious_label=args.malicious_label,
            benign_label=args.benign_label, attack_fraction=args.attack_fraction,
        )
        metrics = evaluate_windows(out)
    else:
        print("[3/5] Evaluation skipped (--no-eval).")

    dport_nan_windows = int(out[f"{DPORT_COL}_entropy"].isna().sum()) if len(out) else 0
    summary = {
        "input_file": os.path.basename(args.input),
        "arguments": {k: v for k, v in vars(args).items() if k != "input"},
        "environment": {"python": platform.python_version(), "pandas": pd.__version__, "numpy": np.__version__},
        "data_quality": dq,
        "pipeline": {
            "input_rows": res.input_row_count,
            "windows": res.number_of_windows,
            "complete_windows": res.number_of_complete_windows,
            "entropy_columns": res.entropy_columns,
            "ewma_columns": res.ewma_columns,
            "windows_with_unevaluable_dport_entropy": dport_nan_windows,
            "windows_flagged_anomaly": int(out["window_anomaly"].sum()) if len(out) else 0,
            "windows_in_warmup": int(out["threshold_is_warmup"].sum()) if len(out) else 0,
        },
        "evaluation": metrics,
        "evaluation_rule": (
            f"window is attack if malicious flow fraction >= {args.attack_fraction}; "
            "prediction = window_anomaly; labels never used by the detector"
        ),
    }

    print(f"[4/5] Writing results to {args.output_dir}")
    os.makedirs(args.output_dir, exist_ok=True)
    out.to_csv(os.path.join(args.output_dir, "windows.csv"), index=False)
    with open(os.path.join(args.output_dir, "metrics.json"), "w") as fh:
        json.dump(summary, fh, indent=2, default=str)

    print("[5/5] Summary")
    print(f"      windows flagged anomalous: {summary['pipeline']['windows_flagged_anomaly']:,}")
    if metrics:
        m = metrics["all_windows"]
        print(f"      all windows:       TP={m['tp']} FP={m['fp']} FN={m['fn']} TN={m['tn']} "
              f"precision={m['precision']} recall={m['recall']} f1={m['f1']}")
        m = metrics["evaluable_windows"]
        print(f"      evaluable windows: TP={m['tp']} FP={m['fp']} FN={m['fn']} TN={m['tn']} "
              f"precision={m['precision']} recall={m['recall']} f1={m['f1']}")
    return summary


def main(argv=None) -> None:
    args = build_parser().parse_args(argv)
    run(args)


if __name__ == "__main__":
    main()
