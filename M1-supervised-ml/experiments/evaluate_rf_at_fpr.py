"""Authorised secondary RF evaluation at the locked FPR <= 1% operating point.

    python M1-supervised-ml/experiments/evaluate_rf_at_fpr.py

Context: the official Stage F RF result used the earlier F1-oriented
threshold rule (threshold 0.30, test FPR 54.4%). Stage G's SVM was
evaluated under the locked protocol (validation FPR <= 1%), so the two
were not comparable. This script produces the missing like-for-like RF
result.

Guarantees:
  * the RF is **not retrained** — the fitted model saved in Stage F is
    loaded from disk and reused unchanged
  * the threshold is chosen on VALIDATION scores only, by the locked rule
    (max recall subject to FPR <= 1%, ties -> highest threshold)
  * exactly one test pass is made at the frozen threshold
  * every output file is NEW; no Stage F artifact is overwritten
"""

from __future__ import annotations

import argparse
import json
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

M1_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = M1_ROOT.parent
if str(M1_ROOT) not in sys.path:
    sys.path.insert(0, str(M1_ROOT))

from evaluation.metrics import compute_metrics, group_breakdown  # noqa: E402
from evaluation.thresholds import (  # noqa: E402
    FPR_BUDGETS,
    PRIMARY_FPR_CAP,
    recall_at_fpr_budgets,
    select_threshold_at_fpr,
)
from preprocessing.data_loader import load_config_file  # noqa: E402
from preprocessing.pipeline import load_processed, resolve_path  # noqa: E402
from training.metadata import (  # noqa: E402
    load_split_metadata,
    verify_metadata_alignment,
)

# Files written by Stage F that this script must never touch.
PROTECTED = (
    "test_metrics.json",
    "rf_run_record.json",
    "per_attack_type.csv",
    "per_attack_tool.csv",
    "validation_search.csv",
    "threshold_analysis.csv",
    "feature_importance.csv",
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Secondary RF evaluation at validation FPR <= 1%.")
    parser.add_argument("--config", default=str(M1_ROOT / "config" / "m1_config.yaml"))
    args = parser.parse_args()

    config = load_config_file(args.config)
    results_root = resolve_path(
        REPO_ROOT,
        (config.get("output") or {}).get("results_dir", "M1-supervised-ml/results"),
    )
    results_dir = results_root / "random_forest"
    processed_dir = resolve_path(
        REPO_ROOT,
        (config.get("output") or {}).get("processed_dir",
                                         "M1-supervised-ml/data/processed"),
    )

    before = {name: (results_dir / name).stat().st_mtime
              for name in PROTECTED if (results_dir / name).is_file()}

    print("[1/5] loading the Stage F model (no retraining)", flush=True)
    model_path = processed_dir / "random_forest.joblib"
    model = joblib.load(model_path)
    data = load_processed(config, REPO_ROOT)
    X_va, y_va = data["X"]["val"], data["y"]["val"]
    X_te, y_te = data["X"]["test"], data["y"]["test"]
    print("      loaded {} ({} trees, max_depth={}, min_samples_leaf={})".format(
        model_path.name, model.n_estimators, model.max_depth,
        model.min_samples_leaf), flush=True)

    print("[2/5] scoring VALIDATION and freezing the threshold", flush=True)
    val_scores = model.predict_proba(X_va)[:, 1]
    budget_rows = recall_at_fpr_budgets(y_va, val_scores, FPR_BUDGETS)
    pd.DataFrame(budget_rows).to_csv(
        results_dir / "validation_fpr_budgets.csv", index=False)
    for row in budget_rows:
        print("        FPR<={:<7.2%} threshold={:>10.6f} recall={:.6f} "
              "achieved_FPR={:.6f} satisfiable={}".format(
                  row["max_fpr"], row["threshold"], row["recall"],
                  row["fpr"], row["satisfiable"]), flush=True)

    operating = select_threshold_at_fpr(y_va, val_scores, PRIMARY_FPR_CAP)
    threshold = operating["threshold"]
    print("      FROZEN threshold (validation FPR<=1%) = {:.6f}".format(threshold),
          flush=True)
    val_metrics = compute_metrics(
        y_va, (val_scores >= threshold).astype(np.int8), val_scores)

    print("[3/5] single TEST pass at the frozen threshold", flush=True)
    t0 = time.perf_counter()
    test_scores = model.predict_proba(X_te)[:, 1]
    test_seconds = time.perf_counter() - t0
    y_pred = (test_scores >= threshold).astype(np.int8)
    test_metrics = compute_metrics(y_te, y_pred, test_scores)
    test_metrics["per_flow_inference_ms"] = round(
        1000 * test_seconds / len(y_te), 6)
    for key in ("accuracy", "precision", "recall", "f1", "fpr", "tnr",
                "roc_auc", "pr_auc"):
        print("      {:<10} {:.6f}".format(key, test_metrics[key]), flush=True)
    print("      TP={:,} TN={:,} FP={:,} FN={:,}".format(
        test_metrics["TP"], test_metrics["TN"],
        test_metrics["FP"], test_metrics["FN"]), flush=True)

    print("[4/5] per-attack-type / per-tool breakdown", flush=True)
    meta = load_split_metadata(config, REPO_ROOT, "test")
    verify_metadata_alignment(meta, y_te)
    by_type = pd.DataFrame(group_breakdown(
        y_te, y_pred, meta["attack_type"].to_numpy()))
    by_tool = pd.DataFrame(group_breakdown(
        y_te, y_pred, meta["attack_tool"].to_numpy()))
    by_type.to_csv(results_dir / "per_attack_type_fpr_constrained.csv", index=False)
    by_tool.to_csv(results_dir / "per_attack_tool_fpr_constrained.csv", index=False)
    print(by_type.to_string(index=False), flush=True)

    print("[5/5] writing additive artifacts", flush=True)
    original = json.loads(
        (results_dir / "test_metrics.json").read_text(encoding="utf-8"))
    record = {
        "stage": "F-secondary (authorised re-evaluation)",
        "label": "RF @ FPR-constrained operating point (validation FPR <= 1%)",
        "model": "RandomForestClassifier (Stage F model, reused unchanged)",
        "retrained": False,
        "model_artifact": str(model_path),
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "python": platform.python_version(),
        "evaluation_scope": (
            "within-capture (within-session) generalisation; NOT unseen-capture, "
            "unseen-session, unseen-base-station or unseen-attack generalisation"
        ),
        "operating_point": {
            "rule": ("max validation recall subject to validation FPR <= 1%; "
                     "ties broken toward the highest threshold; frozen before "
                     "the test pass"),
            "primary_fpr_cap": PRIMARY_FPR_CAP,
            **operating,
        },
        "validation_fpr_budgets": budget_rows,
        "validation_metrics_at_frozen_threshold": val_metrics,
        "test_metrics_fpr_constrained": test_metrics,
        "original_stage_f_test_metrics_threshold_0_30": original,
        "note": (
            "The Stage F result at threshold 0.30 remains the original "
            "default-threshold characterisation and is preserved unchanged in "
            "test_metrics.json / rf_run_record.json. This record is additive."
        ),
    }
    (results_dir / "rf_fpr_constrained_record.json").write_text(
        json.dumps(record, indent=2, default=str), encoding="utf-8")
    (results_dir / "test_metrics_fpr_constrained.json").write_text(
        json.dumps(test_metrics, indent=2), encoding="utf-8")

    after = {name: (results_dir / name).stat().st_mtime
             for name in PROTECTED if (results_dir / name).is_file()}
    changed = [n for n in before if before[n] != after.get(n)]
    if changed:
        raise SystemExit("ERROR: Stage F artifacts were modified: " + str(changed))
    print("      Stage F artifacts verified unmodified: {}".format(
        ", ".join(sorted(before))), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
