import argparse
import sys
from pathlib import Path

import pandas as pd

M2_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(M2_DIR))

from pipeline import PipelineConfig, run_entropy_pipeline
from features import FeatureConfig
from thresholds import ThresholdConfig
from evaluate import evaluate_window_results

parser = argparse.ArgumentParser(
    description="Run M2 entropy detector sensitivity experiments."
)
parser.add_argument(
    "--input",
    required=True,
    help="Path to the 5G-NIDD CSV file or ZIP archive.",
)
parser.add_argument(
    "--nrows",
    type=int,
    default=50000,
    help="Number of input rows to evaluate (default: 50000).",
)
args = parser.parse_args()

OUTPUT_DIR = M2_DIR / "results"
OUTPUT_DIR.mkdir(exist_ok=True)

df = pd.read_csv(args.input, nrows=args.nrows)

feature_config = FeatureConfig(
    categorical_cols=["Proto", "State", "sTtl", "sDSb", "SrcAddr", "Dport"],
    numerical_cols=["TotPkts", "TotBytes", "Rate", "Dur"],
)

experiments = [
    ("baseline_k3_vote2", 3.0, 2),
    ("sensitive_k2_vote2", 2.0, 2),
    ("vote1_k3", 3.0, 1),
]

rows = []

for name, k, vote in experiments:
    output_path = OUTPUT_DIR / f"sensitivity_{name}.csv"

    config = PipelineConfig(
        df=df,
        nrows=None,
        window_size=100,
        step_size=50,
        alpha=0.2,
        feature_config=feature_config,
        threshold_config=ThresholdConfig(
            history_len=50,
            min_history=10,
            k_sensitivity=k,
            voting_threshold=vote,
        ),
        output_path=str(output_path),
    )

    result = run_entropy_pipeline(config)
    metrics, details = evaluate_window_results(
        source_df=df,
        predictions_df=result.output_df,
    )

    row = {"experiment": name, **metrics}
    rows.append(row)

    print(f"\n=== {name} ===")
    for key, value in metrics.items():
        print(f"{key}: {value}")

summary = pd.DataFrame(rows)
summary_path = OUTPUT_DIR / "sensitivity_summary.csv"
summary.to_csv(summary_path, index=False)

print("\n=== COMPARISON ===")
print(summary.to_string(index=False))
print(f"\nSaved summary: {summary_path}")
