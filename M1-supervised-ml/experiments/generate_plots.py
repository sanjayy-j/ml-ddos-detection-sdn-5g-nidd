"""Stage J CLI — generate the M1 figure set from saved artifacts.

    python M1-supervised-ml/experiments/generate_plots.py

Consumes saved evaluation artifacts only: no model is loaded, no
prediction generated, and no threshold selected. Figures are written to
results/plots/ alongside a provenance manifest.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

M1_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = M1_ROOT.parent
if str(M1_ROOT) not in sys.path:
    sys.path.insert(0, str(M1_ROOT))

from evaluation.plots import (  # noqa: E402
    MODEL_DIRS,
    MODEL_ORDER,
    build_manifest,
    load_budgets,
    load_confusion,
    load_curves,
    load_per_attack,
    load_summary,
    plot_confusion,
    plot_cost,
    plot_fpr_budget,
    plot_metric_comparison,
    plot_per_attack,
    plot_pr,
    plot_roc,
)
from preprocessing.data_loader import load_config_file  # noqa: E402
from preprocessing.pipeline import resolve_path  # noqa: E402

SCRIPT = "M1-supervised-ml/experiments/generate_plots.py"

PROTECTED = (
    "feature_order.json", "split_manifest.csv",
    "random_forest/test_metrics.json", "random_forest/rf_run_record.json",
    "random_forest/test_metrics_fpr_constrained.json",
    "random_forest/rf_fpr_constrained_record.json",
    "random_forest/test_roc_curve.csv", "random_forest/test_pr_curve.csv",
    "svm/test_metrics.json", "svm/svm_run_record.json",
    "svm/test_roc_curve.csv", "svm/test_pr_curve.csv",
    "cnn/test_metrics.json", "cnn/cnn_run_record.json",
    "cnn/test_roc_curve.csv", "cnn/test_pr_curve.csv",
    "evaluation/three_model_fpr1pct_summary.csv",
    "evaluation/three_model_fpr_budget.csv",
    "evaluation/three_model_per_attack_type.csv",
    "evaluation/three_model_confusion_matrices.csv",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate M1 Stage J figures.")
    parser.add_argument("--config", default=str(M1_ROOT / "config" / "m1_config.yaml"))
    args = parser.parse_args()

    config = load_config_file(args.config)
    results_root = resolve_path(
        REPO_ROOT,
        (config.get("output") or {}).get("results_dir", "M1-supervised-ml/results"))
    plots_dir = results_root / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)

    before = {n: _sha256(results_root / n) for n in PROTECTED
              if (results_root / n).is_file()}

    print("[1/4] loading saved evaluation artifacts (no models, no inference)",
          flush=True)
    curves = load_curves(results_root)
    summary = load_summary(results_root)
    budgets = load_budgets(results_root)
    per_attack = load_per_attack(results_root)
    confusion = load_confusion(results_root)
    for model in MODEL_ORDER:
        print("      {:<13} ROC pts={:>5,}  PR pts={:>5,}".format(
            model, len(curves[model]["roc"]), len(curves[model]["pr"])),
            flush=True)

    print("[2/4] rendering figures", flush=True)
    figures: list[dict] = []

    def record(filename, title, sources, split, operating):
        figures.append({
            "filename": filename, "title": title,
            "data_source": sources, "split": split,
            "operating_point": operating,
        })
        print("      wrote {}".format(filename), flush=True)

    plot_roc(curves, summary, plots_dir / "roc_curves_test.png")
    record("roc_curves_test.png", "Combined test ROC",
           [f"{MODEL_DIRS[m]}/test_roc_curve.csv" for m in MODEL_ORDER]
           + ["evaluation/three_model_fpr1pct_summary.csv"],
           "test", "threshold-independent")

    plot_pr(curves, summary, plots_dir / "precision_recall_curves_test.png")
    record("precision_recall_curves_test.png",
           "Combined test precision-recall",
           [f"{MODEL_DIRS[m]}/test_pr_curve.csv" for m in MODEL_ORDER]
           + ["evaluation/three_model_fpr1pct_summary.csv"],
           "test", "threshold-independent")

    plot_fpr_budget(budgets, plots_dir / "fpr_recall_validation.png")
    record("fpr_recall_validation.png", "Validation FPR budget vs recall",
           ["evaluation/three_model_fpr_budget.csv"], "validation",
           "budgets 0.1/1/5/10%; primary = 1%")

    plot_metric_comparison(summary,
                           plots_dir / "model_metrics_fpr1pct_test.png")
    record("model_metrics_fpr1pct_test.png",
           "Test metrics at the frozen operating point",
           ["evaluation/three_model_fpr1pct_summary.csv"], "test",
           "validation FPR <= 1% (frozen before test)")

    plot_per_attack(per_attack, plots_dir / "per_attack_recall_test.png")
    record("per_attack_recall_test.png", "Per-attack-type test recall",
           ["evaluation/three_model_per_attack_type.csv"], "test",
           "validation FPR <= 1% (frozen before test)")

    short = {"RandomForest": "rf", "SVM": "svm", "CNN_1D": "cnn"}
    for model in MODEL_ORDER:
        row = confusion[confusion["model"] == model].iloc[0]
        name = f"confusion_matrix_{short[model]}.png"
        plot_confusion(row, plots_dir / name, normalised=False)
        record(name, f"{model} test confusion matrix (absolute counts)",
               ["evaluation/three_model_confusion_matrices.csv"], "test",
               "validation FPR <= 1% (frozen before test)")

    plot_cost(summary, plots_dir / "computational_cost.png")
    record("computational_cost.png",
           "Approximate computational cost (batch throughput, not latency)",
           ["evaluation/three_model_fpr1pct_summary.csv",
            "evaluation/evaluation_metadata.json"], "test",
           "n/a — cost measurement")

    print("[3/4] writing plot manifest", flush=True)
    manifest = build_manifest(
        figures, SCRIPT,
        datetime.now(timezone.utc).isoformat(timespec="seconds"))
    (plots_dir / "plot_manifest.json").write_text(
        json.dumps(manifest, indent=2, default=str), encoding="utf-8")

    print("[4/4] verifying protected artifacts unchanged", flush=True)
    after = {n: _sha256(results_root / n) for n in PROTECTED
             if (results_root / n).is_file()}
    changed = [n for n in before if before[n] != after.get(n)]
    if changed:
        raise SystemExit("ERROR: protected artifacts modified: " + str(changed))
    print("      {} protected artifacts unchanged".format(len(before)), flush=True)
    print("      {} figures in {}".format(len(figures), plots_dir), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
