"""Stage J — authorised one-off ROC/PR curve export for RF and SVM.

    python M1-supervised-ml/experiments/export_curves.py

Stages F and G never persisted test-set curve points (only the scalar
AUCs), so the combined ROC/PR figures could not be drawn. This script
re-scores the test split with the **existing saved models** purely to
persist curve data.

Strictly bounded:
  * models are LOADED, never retrained or modified
  * the Stage D feature matrices and Stage E split are used unchanged
  * NO threshold is selected, optimised, or applied
  * NO existing result artifact is written to
  * scores are the frozen models' own outputs: RF `predict_proba`
    positive-class probability, SVM `decision_function` margin (higher
    = more Malicious)

As an integrity check the script recomputes ROC-AUC/PR-AUC from the
fresh scores and compares them against the values already recorded in
Stage F/G — they must match, proving these are the same frozen
predictions rather than anything new.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import (
    average_precision_score,
    precision_recall_curve,
    roc_auc_score,
    roc_curve,
)

M1_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = M1_ROOT.parent
if str(M1_ROOT) not in sys.path:
    sys.path.insert(0, str(M1_ROOT))

from preprocessing.data_loader import load_config_file  # noqa: E402
from preprocessing.pipeline import resolve_path  # noqa: E402

# Match the CNN export convention from Stage H.
MAX_CURVE_POINTS = 2000

EXPORTS = {
    "RandomForest": {
        "model_file": "random_forest.joblib",
        "results_dir": "random_forest",
        "score_type": "predict_proba positive-class probability",
        "record": "random_forest/rf_fpr_constrained_record.json",
        "metrics_key": "test_metrics_fpr_constrained",
    },
    "SVM": {
        "model_file": "svm_model.joblib",
        "results_dir": "svm",
        "score_type": "decision_function margin (higher = Malicious)",
        "record": "svm/svm_run_record.json",
        "metrics_key": "test_metrics",
    },
}

# Nothing in this list may change.
PROTECTED = (
    "feature_order.json", "split_manifest.csv",
    "random_forest/test_metrics.json", "random_forest/rf_run_record.json",
    "random_forest/test_metrics_fpr_constrained.json",
    "random_forest/rf_fpr_constrained_record.json",
    "svm/test_metrics.json", "svm/svm_run_record.json",
    "cnn/test_metrics.json", "cnn/cnn_run_record.json",
    "cnn/test_roc_curve.csv", "cnn/test_pr_curve.csv",
    "evaluation/three_model_fpr1pct_summary.csv",
    "evaluation/three_model_confusion_matrices.csv",
)

AUC_TOLERANCE = 1e-9


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _thin(array: np.ndarray, step: int) -> np.ndarray:
    return array[::step]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Export RF/SVM test ROC and PR curve points.")
    parser.add_argument("--config", default=str(M1_ROOT / "config" / "m1_config.yaml"))
    args = parser.parse_args()

    config = load_config_file(args.config)
    results_root = resolve_path(
        REPO_ROOT,
        (config.get("output") or {}).get("results_dir", "M1-supervised-ml/results"))
    processed_dir = resolve_path(
        REPO_ROOT,
        (config.get("output") or {}).get("processed_dir",
                                         "M1-supervised-ml/data/processed"))

    before = {n: _sha256(results_root / n) for n in PROTECTED
              if (results_root / n).is_file()}

    print("[1/4] loading Stage D test matrices (split unchanged)", flush=True)
    X_te = np.load(processed_dir / "X_test.npy")
    y_te = np.load(processed_dir / "y_test.npy")
    print("      X_test={} y_test={} malicious%={:.4f}".format(
        X_te.shape, y_te.shape, 100 * y_te.mean()), flush=True)

    exported = {}
    for model_name, spec in EXPORTS.items():
        print("[2/4] {}: loading saved model and scoring test split"
              .format(model_name), flush=True)
        model_path = processed_dir / spec["model_file"]
        model = joblib.load(model_path)

        if model_name == "RandomForest":
            scores = model.predict_proba(X_te)[:, 1]
        else:
            scores = model.decision_function(X_te)

        # integrity: these must reproduce the already-recorded AUCs
        roc_auc = float(roc_auc_score(y_te, scores))
        pr_auc = float(average_precision_score(y_te, scores))
        recorded = json.loads(
            (results_root / spec["record"]).read_text(encoding="utf-8")
        )[spec["metrics_key"]]
        roc_delta = abs(roc_auc - float(recorded["roc_auc"]))
        pr_delta = abs(pr_auc - float(recorded["pr_auc"]))
        ok = roc_delta <= AUC_TOLERANCE and pr_delta <= AUC_TOLERANCE
        print("      ROC-AUC {:.6f} (recorded {:.6f}, dev {:.2e}) | "
              "PR-AUC {:.6f} (recorded {:.6f}, dev {:.2e}) -> {}".format(
                  roc_auc, recorded["roc_auc"], roc_delta,
                  pr_auc, recorded["pr_auc"], pr_delta,
                  "MATCH" if ok else "MISMATCH"), flush=True)
        if not ok:
            raise SystemExit(
                "ERROR: re-scored AUC does not match the recorded value for "
                f"{model_name}; aborting rather than persisting inconsistent "
                "curve data.")

        fpr, tpr, _ = roc_curve(y_te, scores)
        precision, recall, _ = precision_recall_curve(y_te, scores)

        roc_step = max(1, len(fpr) // MAX_CURVE_POINTS)
        pr_step = max(1, len(precision) // MAX_CURVE_POINTS)
        roc_df = pd.DataFrame({"fpr": _thin(fpr, roc_step),
                               "tpr": _thin(tpr, roc_step)})
        pr_df = pd.DataFrame({"recall": _thin(recall, pr_step),
                              "precision": _thin(precision, pr_step)})

        out_dir = results_root / spec["results_dir"]
        roc_path = out_dir / "test_roc_curve.csv"
        pr_path = out_dir / "test_pr_curve.csv"
        for path in (roc_path, pr_path):
            if path.exists():
                raise SystemExit(f"ERROR: refusing to overwrite {path}")
        roc_df.to_csv(roc_path, index=False)
        pr_df.to_csv(pr_path, index=False)

        exported[model_name] = {
            "model": model_name,
            "split": "test",
            "positive_class": "Malicious (1)",
            "score_type": spec["score_type"],
            "source_model_artifact": str(model_path),
            "feature_representation": "Stage D canonical 67-feature matrix",
            "split_protocol": "block_label_contiguous (Stage E, unchanged)",
            "threshold_selection_performed": False,
            "model_retrained": False,
            "n_test_rows": int(len(y_te)),
            "roc_points_written": int(len(roc_df)),
            "pr_points_written": int(len(pr_df)),
            "roc_auc_recomputed": roc_auc,
            "roc_auc_recorded": float(recorded["roc_auc"]),
            "pr_auc_recomputed": pr_auc,
            "pr_auc_recorded": float(recorded["pr_auc"]),
            "auc_matches_recorded": bool(ok),
            "roc_curve_file": str(roc_path),
            "pr_curve_file": str(pr_path),
        }
        print("      wrote {} ROC points, {} PR points".format(
            len(roc_df), len(pr_df)), flush=True)
        del model

    print("[3/4] writing export metadata", flush=True)
    metadata = {
        "stage": "J",
        "purpose": ("authorised one-off curve export; evaluation-artifact "
                    "generation only"),
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "python": platform.python_version(),
        "models_retrained": False,
        "thresholds_selected": False,
        "test_set_tuning": False,
        "frozen_thresholds_unchanged": {
            "RandomForest": 0.478734, "SVM": -0.062874, "CNN_1D": 0.471731,
        },
        "max_curve_points": MAX_CURVE_POINTS,
        "cnn_curves": "reused from Stage H; not regenerated",
        "exports": exported,
    }
    (results_root / "evaluation" / "curve_export_metadata.json").write_text(
        json.dumps(metadata, indent=2, default=str), encoding="utf-8")

    print("[4/4] verifying protected artifacts unchanged", flush=True)
    after = {n: _sha256(results_root / n) for n in PROTECTED
             if (results_root / n).is_file()}
    changed = [n for n in before if before[n] != after.get(n)]
    if changed:
        raise SystemExit("ERROR: protected artifacts modified: " + str(changed))
    print("      {} protected artifacts unchanged".format(len(before)), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
