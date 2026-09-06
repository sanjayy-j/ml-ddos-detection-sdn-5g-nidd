"""Stage G CLI — M1 Support Vector Machine (Nystroem RBF + LinearSVC).

    python M1-supervised-ml/experiments/train_svm.py

Protocol, in enforced order:
  1. load the Stage D processed artifacts and verify integrity
  2. hyperparameter search on TRAIN, scored on VALIDATION only (PR-AUC)
  3. freeze the operating threshold on VALIDATION at FPR <= 1%
  4. evaluate TEST exactly once with the frozen threshold
  5. write metrics, per-attack breakdowns, run record

The test split is not read until step 4. Scores are SVM decision-function
margins; no probability calibration is applied.
"""

from __future__ import annotations

import argparse
import itertools
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

from evaluation.metrics import (  # noqa: E402
    compute_metrics,
    group_breakdown,
)
from evaluation.thresholds import (  # noqa: E402
    FPR_BUDGETS,
    PRIMARY_FPR_CAP,
    recall_at_fpr_budgets,
    select_threshold_at_fpr,
)
from models.svm import build_svm, describe_svm, gamma_scale  # noqa: E402
from preprocessing.data_loader import load_config_file  # noqa: E402
from preprocessing.pipeline import load_processed, resolve_path  # noqa: E402
from training.metadata import (  # noqa: E402
    load_split_metadata,
    verify_metadata_alignment,
)

# Small, bounded grid. `class_weight` is NOT searched: Stage D fixed class
# weighting as the imbalance strategy and it is held constant across
# RF/SVM/CNN so the model comparison is not confounded.
# n_components=1024 was excluded during probing: the transform needs ~7 GB
# and drove this 16 GB machine into swap.
SEARCH_GRID = {
    "n_components": [256, 512],
    "C": [0.01, 0.1, 1.0, 10.0],
}
SELECTION_METRIC = "pr_auc"
TIE_TOLERANCE = 1e-3

BASELINES = {
    "always_malicious_accuracy": 0.607077,
    "exact_vector_memorisation_accuracy": 0.735129,
    "empirical_feature_space_ceiling": 0.786258,
}


def verify_inputs(data: dict) -> dict:
    report = {}
    n_features = data["X"]["train"].shape[1]
    for split in ("train", "val", "test"):
        X, y = data["X"][split], data["y"][split]
        assert X.shape[0] == y.shape[0], f"{split}: X/y row mismatch"
        assert X.shape[1] == n_features, f"{split}: feature-count mismatch"
        assert np.isfinite(X).all(), f"{split}: non-finite values present"
        assert set(np.unique(y)) <= {0, 1}, f"{split}: target not binary"
        report[split] = {
            "rows": int(X.shape[0]),
            "features": int(X.shape[1]),
            "malicious_pct": round(100 * float(y.mean()), 4),
        }
    report["n_features"] = int(n_features)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Train the M1 SVM.")
    parser.add_argument("--config", default=str(M1_ROOT / "config" / "m1_config.yaml"))
    parser.add_argument("--rebuild-metadata", action="store_true")
    args = parser.parse_args()

    config = load_config_file(args.config)
    seed = int(config.get("seed", 42))
    results_root = resolve_path(
        REPO_ROOT,
        (config.get("output") or {}).get("results_dir", "M1-supervised-ml/results"),
    )
    results_dir = results_root / "svm"
    results_dir.mkdir(parents=True, exist_ok=True)
    processed_dir = resolve_path(
        REPO_ROOT,
        (config.get("output") or {}).get("processed_dir",
                                         "M1-supervised-ml/data/processed"),
    )

    # ---------------- 1. load + verify ----------------
    print("[1/6] loading Stage D artifacts", flush=True)
    data = load_processed(config, REPO_ROOT)
    integrity = verify_inputs(data)
    feature_names = json.loads(
        (results_root / "feature_order.json").read_text(encoding="utf-8")
    )["feature_order"]
    assert len(feature_names) == integrity["n_features"], "feature-name mismatch"
    for split in ("train", "val", "test"):
        info = integrity[split]
        print("      {:<5} rows={:>8,} features={} mal%={}".format(
            split, info["rows"], info["features"], info["malicious_pct"]), flush=True)

    X_tr, y_tr = data["X"]["train"], data["y"]["train"]
    X_va, y_va = data["X"]["val"], data["y"]["val"]

    # gamma is derived from TRAINING data only, then frozen
    gamma = gamma_scale(X_tr)
    print("      gamma('scale') from train only = {:.6f}".format(gamma), flush=True)

    # ---------------- 2. search (validation only) ----------------
    print("[2/6] hyperparameter search (criterion: validation {})".format(
        SELECTION_METRIC), flush=True)
    keys = list(SEARCH_GRID)
    candidates = [dict(zip(keys, combo))
                  for combo in itertools.product(*(SEARCH_GRID[k] for k in keys))]

    rows = []
    for i, overrides in enumerate(candidates, 1):
        model = build_svm(config, gamma, **overrides)
        t0 = time.perf_counter()
        model.fit(X_tr, y_tr)
        fit_s = time.perf_counter() - t0
        t0 = time.perf_counter()
        scores = model.decision_function(X_va)
        pred_s = time.perf_counter() - t0
        row = compute_metrics(y_va, (scores >= 0).astype(np.int8), scores)
        row["candidate"] = i
        row.update({k: overrides[k] for k in keys})
        row["fit_seconds"] = round(fit_s, 2)
        row["val_predict_seconds"] = round(pred_s, 3)
        rows.append(row)
        print("      [{}/{}] n_components={:<5} C={:<6} PR-AUC={:.5f} "
              "ROC-AUC={:.5f} F1@0={:.5f} FPR@0={:.5f} fit={:.0f}s".format(
                  i, len(candidates), overrides["n_components"], overrides["C"],
                  row["pr_auc"], row["roc_auc"], row["f1"], row["fpr"], fit_s),
              flush=True)
        del model

    search = pd.DataFrame(rows)
    search.to_csv(results_dir / "validation_search.csv", index=False)

    best_score = search[SELECTION_METRIC].max()
    close = search[search[SELECTION_METRIC] >= best_score - TIE_TOLERANCE].copy()
    # tie-break toward the cheaper model: fewer components, then smaller C
    chosen = close.sort_values(["n_components", "C", "fit_seconds"]).iloc[0]
    best = {"n_components": int(chosen["n_components"]), "C": float(chosen["C"])}
    print("      best {}={:.5f}; {} within {}; chosen -> {}".format(
        SELECTION_METRIC, best_score, len(close), TIE_TOLERANCE, best), flush=True)

    # ---------------- 3. refit + freeze threshold on VALIDATION ----------------
    print("[3/6] refitting chosen configuration", flush=True)
    model = build_svm(config, gamma, **best)
    t0 = time.perf_counter()
    model.fit(X_tr, y_tr)
    train_seconds = time.perf_counter() - t0
    t0 = time.perf_counter()
    val_scores = model.decision_function(X_va)
    val_seconds = time.perf_counter() - t0
    print("      trained in {:.1f}s; validation scored in {:.2f}s".format(
        train_seconds, val_seconds), flush=True)

    budget_rows = recall_at_fpr_budgets(y_va, val_scores, FPR_BUDGETS)
    budgets = pd.DataFrame(budget_rows)
    budgets.to_csv(results_dir / "validation_fpr_budgets.csv", index=False)
    print("      validation recall at each FPR budget:", flush=True)
    for row in budget_rows:
        print("        FPR<={:<7.2%} threshold={:>10.6f} recall={:.6f} "
              "achieved_FPR={:.6f} satisfiable={}".format(
                  row["max_fpr"], row["threshold"], row["recall"],
                  row["fpr"], row["satisfiable"]), flush=True)

    operating = select_threshold_at_fpr(y_va, val_scores, PRIMARY_FPR_CAP)
    threshold = operating["threshold"]
    print("      FROZEN threshold (validation FPR<=1%) = {:.6f}".format(threshold),
          flush=True)
    if not operating["satisfiable"]:
        print("      WARNING: {}".format(operating["reason"]), flush=True)

    val_metrics = compute_metrics(
        y_va, (val_scores >= threshold).astype(np.int8), val_scores)
    val_at_zero = compute_metrics(
        y_va, (val_scores >= 0).astype(np.int8), val_scores)

    # ---------------- 4. TEST: exactly once ----------------
    print("[4/6] final test evaluation (single pass, frozen threshold)", flush=True)
    X_te, y_te = data["X"]["test"], data["y"]["test"]
    t0 = time.perf_counter()
    test_scores = model.decision_function(X_te)
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

    # ---------------- 5. per-attack analysis ----------------
    print("[5/6] per-attack-type and per-tool analysis", flush=True)
    meta = load_split_metadata(config, REPO_ROOT, "test",
                               rebuild=args.rebuild_metadata)
    verify_metadata_alignment(meta, y_te)
    by_type = pd.DataFrame(group_breakdown(
        y_te, y_pred, meta["attack_type"].to_numpy()))
    by_tool = pd.DataFrame(group_breakdown(
        y_te, y_pred, meta["attack_tool"].to_numpy()))
    by_type.to_csv(results_dir / "per_attack_type.csv", index=False)
    by_tool.to_csv(results_dir / "per_attack_tool.csv", index=False)
    print(by_type.to_string(index=False), flush=True)

    # ---------------- 6. persist ----------------
    print("[6/6] writing artifacts", flush=True)
    model_path = processed_dir / "svm_model.joblib"
    joblib.dump(model, model_path, compress=3)

    record = {
        "stage": "G",
        "model": "SVM (Nystroem RBF approximation + LinearSVC)",
        "strategy_rationale": (
            "A full SVC(kernel='rbf') on 851,106 training rows is not "
            "tractable here: measured fit time is quadratic (0.4s/1.7s/7.3s "
            "at n=5k/10k/20k, extrapolating to ~3.7h) and ~55% of rows become "
            "support vectors, so a true SVC trained on the Stage D 50k "
            "stratified subsample needed 246.5s to score validation "
            "(1.35 ms/flow) for only val PR-AUC 0.86877. Nystroem+LinearSVC "
            "trains on all 851,106 rows and scores ~400x faster."
        ),
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "python": platform.python_version(),
        "seed": seed,
        "split_protocol": (config.get("split") or {}).get("strategy"),
        "evaluation_scope": (
            "within-capture (within-session) generalisation; NOT unseen-capture, "
            "unseen-session, unseen-base-station or unseen-attack generalisation"
        ),
        "feature_representation": {
            "n_features": integrity["n_features"],
            "source": "Stage D canonical 67-feature matrix (unchanged)",
        },
        "integrity": integrity,
        "training_rows_used": int(len(y_tr)),
        "validation_rows": int(len(y_va)),
        "test_rows": int(len(y_te)),
        "gamma_source": "sklearn 'scale' heuristic computed on TRAIN only",
        "gamma": gamma,
        "selection_metric": SELECTION_METRIC,
        "search_grid": {k: [str(x) for x in v] for k, v in SEARCH_GRID.items()},
        "n_candidates": len(candidates),
        "class_weight_note": (
            "fixed to Stage D's class-weighting decision, not searched, so "
            "RF/SVM/CNN share the same imbalance strategy"
        ),
        "chosen_hyperparameters": best,
        "model_structure": describe_svm(model),
        "operating_point": {
            "rule": ("max validation recall subject to validation FPR <= 1%; "
                     "ties broken toward the highest threshold; frozen before "
                     "test"),
            "primary_fpr_cap": PRIMARY_FPR_CAP,
            **operating,
        },
        "validation_fpr_budgets": budget_rows,
        "timings_seconds": {
            "train": round(train_seconds, 2),
            "val_inference": round(val_seconds, 3),
            "test_inference": round(test_seconds, 3),
            "search_total": round(float(search["fit_seconds"].sum()), 2),
        },
        "validation_metrics_at_frozen_threshold": val_metrics,
        "validation_metrics_at_zero_margin": val_at_zero,
        "test_metrics": test_metrics,
        "baselines_test": BASELINES,
        "comparison_test": {
            "beats_always_malicious": bool(
                test_metrics["accuracy"] > BASELINES["always_malicious_accuracy"]),
            "beats_memorisation_baseline": bool(
                test_metrics["accuracy"]
                > BASELINES["exact_vector_memorisation_accuracy"]),
            "gap_to_ceiling_pp": round(
                100 * (BASELINES["empirical_feature_space_ceiling"]
                       - test_metrics["accuracy"]), 4),
        },
    }
    (results_dir / "svm_run_record.json").write_text(
        json.dumps(record, indent=2, default=str), encoding="utf-8")
    (results_dir / "test_metrics.json").write_text(
        json.dumps(test_metrics, indent=2), encoding="utf-8")
    print("      wrote " + str(results_dir), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
