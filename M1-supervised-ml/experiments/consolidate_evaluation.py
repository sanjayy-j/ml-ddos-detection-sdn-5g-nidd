"""Stage I CLI — consolidate the frozen RF/SVM/CNN results.

    python M1-supervised-ml/experiments/consolidate_evaluation.py

Read-only with respect to every Stage F/G/H artifact. It re-derives each
metric from the saved confusion matrices, assembles comparable tables,
and writes them to results/evaluation/. No model is loaded, no score is
recomputed, and no threshold is re-selected.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

M1_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = M1_ROOT.parent
if str(M1_ROOT) not in sys.path:
    sys.path.insert(0, str(M1_ROOT))

from evaluation.consolidate import (  # noqa: E402
    METRIC_TOLERANCE,
    MODEL_ORDER,
    SOURCES,
    build_confusion_table,
    build_fpr_budget_table,
    build_per_attack_table,
    build_summary_table,
    load_model_results,
    verify_metric_consistency,
)
from preprocessing.data_loader import load_config_file  # noqa: E402
from preprocessing.pipeline import resolve_path  # noqa: E402

# Artifacts that Stage I must leave byte-identical.
PROTECTED = (
    "feature_order.json",
    "split_manifest.csv",
    "random_forest/test_metrics.json",
    "random_forest/rf_run_record.json",
    "random_forest/test_metrics_fpr_constrained.json",
    "random_forest/rf_fpr_constrained_record.json",
    "svm/test_metrics.json",
    "svm/svm_run_record.json",
    "cnn/test_metrics.json",
    "cnn/cnn_run_record.json",
)

TIMING_CAVEAT = (
    "Inference figures are AMORTISED BATCH THROUGHPUT — total wall-clock "
    "time to score the complete 182,402-row test split divided by the row "
    "count — not single-flow latency. Each is a single timed run on a "
    "machine with substantial run-to-run load variation (the identical RF "
    "scoring call produced 0.0011 and 0.0017 ms/flow on two runs), so the "
    "values indicate relative cost only and should be read approximately."
)

SPLIT_CONTEXT = {
    "train_rows": 851106,
    "validation_rows": 182382,
    "test_rows": 182402,
    "test_malicious_prevalence_pct": 60.7077,
    "split_protocol": "block_label_contiguous",
    "evaluation_scope": (
        "within-capture (within-session) generalisation"
    ),
    "does_not_measure": [
        "unseen-capture generalisation",
        "unseen-session generalisation",
        "unseen-base-station generalisation",
        "unseen-attack generalisation",
    ],
    "pr_auc_no_skill_reference": 0.607077,
}

UDPFLOOD_WORDING = (
    "Because all three classifiers consume the same 67-feature "
    "representation, their agreement provides corroboration across model "
    "families rather than three independent tests of the representation "
    "itself. The independent Stage D exact-vector ambiguity analysis "
    "remains the stronger representation-level evidence."
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Consolidate the frozen three-model evaluation.")
    parser.add_argument("--config", default=str(M1_ROOT / "config" / "m1_config.yaml"))
    args = parser.parse_args()

    config = load_config_file(args.config)
    results_root = resolve_path(
        REPO_ROOT,
        (config.get("output") or {}).get("results_dir", "M1-supervised-ml/results"),
    )
    out_dir = results_root / "evaluation"
    out_dir.mkdir(parents=True, exist_ok=True)

    before = {name: _sha256(results_root / name) for name in PROTECTED
              if (results_root / name).is_file()}

    print("[1/5] loading frozen model results (read-only)", flush=True)
    loaded = load_model_results(results_root)
    for model in MODEL_ORDER:
        print("      {:<13} <- {}".format(model, SOURCES[model]["record"]),
              flush=True)

    print("[2/5] metric consistency audit (re-derived from confusion counts)",
          flush=True)
    consistency_rows = []
    all_consistent = True
    for model in MODEL_ORDER:
        for row in verify_metric_consistency(loaded[model]["test_metrics"]):
            row["model"] = model
            consistency_rows.append(row)
            if not row["consistent"]:
                all_consistent = False
                print("      [INCONSISTENT] {} {}: stored={} recomputed={} "
                      "dev={}".format(model, row["metric"], row["stored"],
                                      row["recomputed"], row["abs_deviation"]),
                      flush=True)
    import pandas as pd

    consistency = pd.DataFrame(consistency_rows)[
        ["model", "metric", "stored", "recomputed", "abs_deviation", "consistent"]]
    worst = consistency["abs_deviation"].dropna().max()
    print("      {} checks; all consistent = {}; max deviation = {:.3e} "
          "(tolerance {:.0e})".format(len(consistency), all_consistent,
                                      float(worst), METRIC_TOLERANCE), flush=True)

    print("[3/5] building consolidated tables", flush=True)
    summary = build_summary_table(loaded)
    confusion = build_confusion_table(loaded)
    budgets = build_fpr_budget_table(loaded, results_root)
    per_attack = build_per_attack_table(loaded, results_root)

    print(summary[["model", "threshold", "test_accuracy", "test_recall",
                   "test_fpr", "roc_auc", "pr_auc"]].to_string(index=False),
          flush=True)
    print(confusion.to_string(index=False), flush=True)

    print("[4/5] writing evaluation artifacts", flush=True)
    summary.to_csv(out_dir / "three_model_fpr1pct_summary.csv", index=False)
    budgets.to_csv(out_dir / "three_model_fpr_budget.csv", index=False)
    per_attack.to_csv(out_dir / "three_model_per_attack_type.csv", index=False)
    confusion.to_csv(out_dir / "three_model_confusion_matrices.csv", index=False)
    consistency.to_csv(out_dir / "metric_consistency_audit.csv", index=False)

    metadata = {
        "stage": "I",
        "purpose": "consolidation and audit of frozen Stage F/G/H results",
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "python": platform.python_version(),
        "models_retrained": False,
        "scores_recomputed": False,
        "thresholds_reselected": False,
        "source_artifacts": {m: SOURCES[m]["record"] for m in MODEL_ORDER},
        "frozen_thresholds": {
            m: loaded[m]["operating_point"].get("threshold") for m in MODEL_ORDER
        },
        "operating_point_rule": (
            "max validation recall subject to validation FPR <= 1%; ties "
            "broken toward the highest threshold; frozen before test"
        ),
        "metric_consistency": {
            "all_consistent": bool(all_consistent),
            "tolerance": METRIC_TOLERANCE,
            "max_abs_deviation": float(worst),
            "n_checks": int(len(consistency)),
        },
        "timing_caveat": TIMING_CAVEAT,
        "split_context": SPLIT_CONTEXT,
        "udpflood_interpretation": UDPFLOOD_WORDING,
        "note_existing_comparison": (
            "results/model_comparison_fpr1pct.csv (Stage H) is a subset of "
            "three_model_fpr1pct_summary.csv, which adds the validation-side "
            "operating point and cost columns. The Stage H file is left "
            "unmodified."
        ),
    }
    (out_dir / "evaluation_metadata.json").write_text(
        json.dumps(metadata, indent=2, default=str), encoding="utf-8")

    print("[5/5] verifying protected artifacts are byte-identical", flush=True)
    after = {name: _sha256(results_root / name) for name in PROTECTED
             if (results_root / name).is_file()}
    changed = [n for n in before if before[n] != after.get(n)]
    if changed:
        raise SystemExit("ERROR: protected artifacts modified: " + str(changed))
    print("      {} protected artifacts unchanged".format(len(before)), flush=True)
    print("      wrote " + str(out_dir), flush=True)
    return 0 if all_consistent else 1


if __name__ == "__main__":
    raise SystemExit(main())
