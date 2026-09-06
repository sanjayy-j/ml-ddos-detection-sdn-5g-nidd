"""Stage F CLI — M1 Random Forest.

    python M1-supervised-ml/experiments/train_random_forest.py

Protocol (order matters and is enforced by the code path):
  1. load the Stage D processed artifacts and verify integrity
  2. hyperparameter search on TRAIN, scored on VALIDATION only
  3. decision-threshold selection on VALIDATION only
  4. lock the configuration, then evaluate on TEST exactly once
  5. write metrics, per-attack breakdowns, feature importance, run record

The test split is not read until step 4.
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
    threshold_sweep,
)
from models.random_forest import build_random_forest, describe_forest  # noqa: E402
from preprocessing.data_loader import load_config_file  # noqa: E402
from preprocessing.pipeline import load_processed, resolve_path  # noqa: E402
from training.metadata import (  # noqa: E402
    load_split_metadata,
    verify_metadata_alignment,
)

# Modest, fully-enumerated search grid (documented in the M1 README).
SEARCH_GRID = {
    "max_depth": [None, 20, 30],
    "min_samples_leaf": [1, 5, 20],
    "max_features": ["sqrt", 0.5],
}
# Primary selection criterion: validation PR-AUC. It is threshold-free, so
# model choice stays independent of threshold choice, and it is sensitive to
# the precision/recall trade-off that matters for DDoS detection.
SELECTION_METRIC = "pr_auc"
TIE_TOLERANCE = 1e-3

# Reference points established in Stages D/E (test split).
BASELINES = {
    "always_malicious_accuracy": 0.607077,
    "exact_vector_memorisation_accuracy": 0.735129,
    "empirical_feature_space_ceiling": 0.786258,
}

CATEGORICAL_SOURCES = ("Proto", "sDSb", "dDSb", "Cause", "State")


def verify_inputs(data: dict) -> dict:
    """Integrity checks on the Stage D artifacts before any training."""
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


def _source_column(feature: str) -> str:
    for column in CATEGORICAL_SOURCES:
        if feature.startswith(column + "_"):
            return column
    return feature


def _is_unlimited(value) -> bool:
    """True when a grid value means "no limit".

    `max_depth=None` survives a DataFrame round-trip as float NaN (the
    column holds both None and ints, so pandas casts it to float64), and
    `NaN in (None, ...)` is False — so NaN must be tested explicitly.
    """
    if value is None or value == "config":
        return True
    return isinstance(value, float) and np.isnan(value)


def main() -> int:
    parser = argparse.ArgumentParser(description="Train the M1 Random Forest.")
    parser.add_argument("--config", default=str(M1_ROOT / "config" / "m1_config.yaml"))
    parser.add_argument("--skip-search", action="store_true",
                        help="Use the configured hyperparameters unchanged.")
    parser.add_argument("--rebuild-metadata", action="store_true")
    parser.add_argument(
        "--reuse-search", action="store_true",
        help="Reuse an existing validation_search.csv instead of refitting the "
             "grid. The search is deterministic, so this reproduces the same "
             "selection; it exists so a failure after the grid does not force "
             "a full re-fit.")
    args = parser.parse_args()

    config = load_config_file(args.config)
    seed = int(config.get("seed", 42))
    results_root = resolve_path(
        REPO_ROOT,
        (config.get("output") or {}).get("results_dir", "M1-supervised-ml/results"),
    )
    results_dir = results_root / "random_forest"
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
    feature_order = json.loads(
        (results_root / "feature_order.json").read_text(encoding="utf-8")
    )
    feature_names = feature_order["feature_order"]
    assert len(feature_names) == integrity["n_features"], "feature-name mismatch"
    for split in ("train", "val", "test"):
        info = integrity[split]
        print("      {:<5} rows={:>8,} features={} mal%={}".format(
            split, info["rows"], info["features"], info["malicious_pct"]), flush=True)

    X_tr, y_tr = data["X"]["train"], data["y"]["train"]
    X_va, y_va = data["X"]["val"], data["y"]["val"]

    # ---------------- 2. hyperparameter search (validation only) ----------------
    print("[2/6] hyperparameter search (criterion: validation " + SELECTION_METRIC + ")",
          flush=True)
    if args.skip_search:
        candidates = [{}]
    else:
        keys = list(SEARCH_GRID)
        candidates = [dict(zip(keys, combo))
                      for combo in itertools.product(*(SEARCH_GRID[k] for k in keys))]

    search_path = results_dir / "validation_search.csv"
    if args.reuse_search and search_path.is_file():
        search = pd.read_csv(search_path)
        print("      reusing {} deterministic candidates from {}".format(
            len(search), search_path.name), flush=True)
        candidates = [None] * len(search)
        search_rows = None
    else:
        search_rows = []
    for i, overrides in enumerate(candidates if search_rows is not None else [], 1):
        model = build_random_forest(config, **overrides)
        t0 = time.perf_counter()
        model.fit(X_tr, y_tr)
        fit_s = time.perf_counter() - t0
        t0 = time.perf_counter()
        scores = model.predict_proba(X_va)[:, 1]
        pred_s = time.perf_counter() - t0
        row = compute_metrics(y_va, (scores >= 0.5).astype(np.int8), scores)
        row["candidate"] = i
        row["max_depth"] = overrides.get("max_depth", "config")
        row["min_samples_leaf"] = overrides.get("min_samples_leaf", "config")
        row["max_features"] = overrides.get("max_features", "config")
        row["fit_seconds"] = round(fit_s, 2)
        row["val_predict_seconds"] = round(pred_s, 2)
        for k, v in describe_forest(model).items():
            row["forest_" + k] = v
        search_rows.append(row)
        print("      [{:>2}/{}] depth={:<5} leaf={:<4} feat={:<5} PR-AUC={:.5f} "
              "ROC-AUC={:.5f} F1={:.5f} FPR={:.5f} fit={:.0f}s".format(
                  i, len(candidates), str(row["max_depth"]),
                  str(row["min_samples_leaf"]), str(row["max_features"]),
                  row["pr_auc"], row["roc_auc"], row["f1"], row["fpr"], fit_s),
              flush=True)
        del model

    if search_rows is not None:
        search = pd.DataFrame(search_rows)
        search.to_csv(search_path, index=False)

    # tie-break toward the simpler / cheaper model
    best_score = search[SELECTION_METRIC].max()
    close = search[search[SELECTION_METRIC] >= best_score - TIE_TOLERANCE].copy()
    close["_feat_rank"] = close["max_features"].apply(
        lambda f: 0 if f == "sqrt" else 1)
    close["_leaf_rank"] = close["min_samples_leaf"].apply(
        lambda v: 0 if _is_unlimited(v) else -int(v))
    # unlimited depth ranks last, so a bounded (simpler) tree wins a tie
    close["_depth_rank"] = close["max_depth"].apply(
        lambda d: 10 ** 6 if _is_unlimited(d) else int(d))
    chosen = close.sort_values(
        ["_feat_rank", "_leaf_rank", "_depth_rank", "fit_seconds"]).iloc[0]

    best = {}
    for key in ("max_depth", "min_samples_leaf", "max_features"):
        value = chosen[key]
        if key == "max_features":
            best[key] = value
        elif _is_unlimited(value):
            # max_depth=None is meaningful; min_samples_leaf must stay >= 1
            best[key] = None if key == "max_depth" else 1
        else:
            best[key] = int(value)
    print("      best {}={:.5f}; {} within {}; chosen -> {}".format(
        SELECTION_METRIC, best_score, len(close), TIE_TOLERANCE, best), flush=True)

    # ---------------- 3. refit chosen config; threshold on validation ----------
    print("[3/6] refitting chosen configuration", flush=True)
    model = build_random_forest(config, **best)
    t0 = time.perf_counter()
    model.fit(X_tr, y_tr)
    train_seconds = time.perf_counter() - t0
    t0 = time.perf_counter()
    val_scores = model.predict_proba(X_va)[:, 1]
    val_seconds = time.perf_counter() - t0
    print("      trained in {:.1f}s; validation scored in {:.1f}s".format(
        train_seconds, val_seconds), flush=True)

    sweep = pd.DataFrame(threshold_sweep(
        y_va, val_scores, np.round(np.arange(0.05, 0.96, 0.01), 2)))
    sweep.to_csv(results_dir / "threshold_analysis.csv", index=False)
    at_default = sweep[sweep["threshold"] == 0.50].iloc[0]
    best_f1_row = sweep.loc[sweep["f1"].idxmax()]
    gain = float(best_f1_row["f1"]) - float(at_default["f1"])
    # Keep 0.5 unless validation F1 improves materially (>= 0.005).
    threshold = 0.5 if gain < 0.005 else float(best_f1_row["threshold"])
    print("      val F1@0.50={:.5f} (FPR={:.5f}); best F1={:.5f} @ {} "
          "(gain {:+.5f}) -> threshold locked at {}".format(
              at_default["f1"], at_default["fpr"], best_f1_row["f1"],
              best_f1_row["threshold"], gain, threshold), flush=True)
    val_metrics = compute_metrics(
        y_va, (val_scores >= threshold).astype(np.int8), val_scores)

    # ---------------- 4. TEST: evaluated exactly once ----------------
    print("[4/6] final test evaluation (single pass)", flush=True)
    X_te, y_te = data["X"]["test"], data["y"]["test"]
    t0 = time.perf_counter()
    test_scores = model.predict_proba(X_te)[:, 1]
    test_seconds = time.perf_counter() - t0
    y_pred = (test_scores >= threshold).astype(np.int8)
    test_metrics = compute_metrics(y_te, y_pred, test_scores)
    test_metrics["per_flow_inference_ms"] = round(1000 * test_seconds / len(y_te), 6)
    for key in ("accuracy", "precision", "recall", "f1", "fpr", "tnr",
                "roc_auc", "pr_auc"):
        print("      {:<10} {:.6f}".format(key, test_metrics[key]), flush=True)
    print("      TP={:,} TN={:,} FP={:,} FN={:,}".format(
        test_metrics["TP"], test_metrics["TN"],
        test_metrics["FP"], test_metrics["FN"]), flush=True)

    # ---------------- 5. per-attack / per-tool analysis ----------------
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

    importance = pd.DataFrame({
        "feature": feature_names,
        "importance": model.feature_importances_,
    }).sort_values("importance", ascending=False).reset_index(drop=True)
    importance["source_column"] = importance["feature"].apply(_source_column)
    importance.to_csv(results_dir / "feature_importance.csv", index=False)
    print("\n      top 15 features:", flush=True)
    print(importance.head(15).to_string(index=False), flush=True)

    # ---------------- 6. persist ----------------
    print("[6/6] writing artifacts", flush=True)
    model_path = processed_dir / "random_forest.joblib"
    joblib.dump(model, model_path, compress=3)

    chosen_hyperparameters = {
        "n_estimators": int(model.n_estimators),
        "max_depth": model.max_depth,
        "min_samples_leaf": int(model.min_samples_leaf),
        "max_features": model.max_features,
        "class_weight": str(model.class_weight),
        "random_state": int(model.random_state),
        "n_jobs": model.n_jobs,
    }
    record = {
        "stage": "F",
        "model": "RandomForestClassifier",
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "python": platform.python_version(),
        "seed": seed,
        "split_protocol": (config.get("split") or {}).get("strategy"),
        "evaluation_scope": (
            "within-capture (within-session) generalisation; NOT unseen-capture, "
            "unseen-session, unseen-base-station or unseen-attack generalisation"
        ),
        "n_features": integrity["n_features"],
        "integrity": integrity,
        "selection_metric": SELECTION_METRIC,
        "search_grid": {k: [str(x) for x in v] for k, v in SEARCH_GRID.items()},
        "n_candidates": len(candidates),
        "chosen_hyperparameters": chosen_hyperparameters,
        "forest_structure": describe_forest(model),
        "decision_threshold": threshold,
        "threshold_rule": (
            "0.5 retained unless validation F1 improves by >= 0.005; "
            "selected on validation only"
        ),
        "timings_seconds": {
            "train": round(train_seconds, 2),
            "val_inference": round(val_seconds, 2),
            "test_inference": round(test_seconds, 2),
            "search_total": round(float(search["fit_seconds"].sum()), 2),
        },
        "validation_metrics": val_metrics,
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
    (results_dir / "rf_run_record.json").write_text(
        json.dumps(record, indent=2, default=str), encoding="utf-8")
    (results_dir / "test_metrics.json").write_text(
        json.dumps(test_metrics, indent=2), encoding="utf-8")
    print("      wrote " + str(results_dir), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
