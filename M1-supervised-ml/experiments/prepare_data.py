"""Stage D CLI — build the M1 processed dataset from the raw 5G-NIDD CSV.

    python M1-supervised-ml/experiments/prepare_data.py \
        --config M1-supervised-ml/config/m1_config.yaml

No models are trained here; this only produces the leakage-safe
representation and the accompanying audit artifacts.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

M1_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = M1_ROOT.parent
if str(M1_ROOT) not in sys.path:
    sys.path.insert(0, str(M1_ROOT))

from preprocessing.data_loader import load_config_file, load_raw_data  # noqa: E402
from preprocessing.pipeline import (  # noqa: E402
    prepare_m1_dataset,
    resolve_path,
    run_leakage_audit,
    save_artifacts,
)
from preprocessing.reporting import (  # noqa: E402
    build_feature_decision_report,
    report_to_markdown,
)
from preprocessing.validation import validate_dataset  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare the M1 dataset.")
    parser.add_argument(
        "--config",
        default=str(M1_ROOT / "config" / "m1_config.yaml"),
        help="Path to the M1 YAML configuration.",
    )
    parser.add_argument(
        "--dataset-path",
        default=None,
        help="Override dataset.raw_path from the config.",
    )
    parser.add_argument(
        "--nrows",
        type=int,
        default=None,
        help="Read only the first N rows (smoke testing only, not for results).",
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Run the pipeline without writing artifacts.",
    )
    args = parser.parse_args()

    config = load_config_file(args.config)
    if args.dataset_path:
        config["dataset"]["raw_path"] = args.dataset_path

    raw_path = config["dataset"]["raw_path"]
    config["dataset"]["raw_path"] = str(resolve_path(REPO_ROOT, raw_path))

    print(f"[1/6] loading {config['dataset']['raw_path']}", flush=True)
    started = time.perf_counter()
    if args.nrows:
        import pandas as pd

        df = pd.read_csv(config["dataset"]["raw_path"], nrows=args.nrows)
        print(f"      WARNING: --nrows={args.nrows} is a smoke test, "
              f"not a valid experimental run", flush=True)
    else:
        df = load_raw_data(config)
    print(f"      {df.shape[0]:,} rows x {df.shape[1]} cols "
          f"({time.perf_counter() - started:.1f}s)", flush=True)

    print("[2/6] validating dataset/schema", flush=True)
    result = validate_dataset(config, df)
    for warning in result.warnings:
        print(f"      WARN: {warning}", flush=True)
    if not result.is_valid:
        for error in result.errors:
            print(f"      ERROR: {error}", flush=True)
        return 1
    print(f"      label distribution: {result.label_distribution}", flush=True)

    print("[3/6] building feature decision report", flush=True)
    decisions = build_feature_decision_report(df, config)
    print(f"      KEEP={int((decisions.decision == 'KEEP').sum())} "
          f"DROP={int((decisions.decision == 'DROP').sum())}", flush=True)

    print("[4/6] preparing dataset (split + fit-on-train preprocessing)",
          flush=True)
    started = time.perf_counter()
    prepared = prepare_m1_dataset(df, config)
    print(f"      done in {time.perf_counter() - started:.1f}s", flush=True)
    for name, info in prepared.metadata["splits"].items():
        print(f"      {name:<5} rows={info['rows']:>9,} "
              f"malicious={info['malicious_pct']:>6.2f}% shape={info['shape']}",
              flush=True)
    print(f"      CNN input shape: {prepared.cnn_input_shape}", flush=True)

    print("[5/6] leakage audit", flush=True)
    audit = run_leakage_audit(prepared, config)
    for check in audit["checks"]:
        print(f"      [{check['status']}] {check['check']}: {check['detail']}",
              flush=True)

    if args.no_save:
        print("[6/6] --no-save: skipping artifact write", flush=True)
        return 0 if audit["all_passed"] else 1

    print("[6/6] writing artifacts", flush=True)
    written = save_artifacts(prepared, config, REPO_ROOT, audit=audit)

    results_dir = resolve_path(
        REPO_ROOT, (config.get("output") or {}).get("results_dir",
                                                    "M1-supervised-ml/results")
    )
    decisions.to_csv(results_dir / "feature_decisions.csv", index=False)
    (results_dir / "feature_decisions.md").write_text(
        report_to_markdown(decisions), encoding="utf-8"
    )
    written["feature_decisions"] = str(results_dir / "feature_decisions.csv")

    (results_dir / "dataset_validation.json").write_text(
        json.dumps(
            {
                "rows": int(len(df)),
                "columns": int(df.shape[1]),
                "warnings": result.warnings,
                "label_distribution": result.label_distribution,
                "missing_value_counts": result.missing_value_counts,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    for key, path in sorted(written.items()):
        print(f"      {key}: {path}", flush=True)

    return 0 if audit["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
