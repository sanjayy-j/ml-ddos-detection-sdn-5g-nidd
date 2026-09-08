"""Stage L — train and evaluate RF / SVM / CNN under the unseen-capture holdout.

    python M1-supervised-ml/experiments/train_unseen_capture.py --model rf
    python M1-supervised-ml/experiments/train_unseen_capture.py --model svm
    python M1-supervised-ml/experiments/train_unseen_capture.py --model cnn

Protocol, enforced by the code path:
  1. load the Stage L development matrices (held-out never touched)
  2. hyperparameter search on dev-train, scored on dev-validation only
  3. freeze the threshold on dev-validation at FPR <= 1%
  4. evaluate the held-out blocks exactly once
  5. write metrics, per-block, per-attack and curve artifacts

The search grids and selection rules are **imported from the Stage F/G/H
scripts**, so the model-selection protocol is provably identical rather
than restated. Held-out data is not read until step 4.
"""

from __future__ import annotations

import argparse
import itertools
import json
import os
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")

import joblib  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

M1_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = M1_ROOT.parent
for path in (str(M1_ROOT), str(M1_ROOT / "experiments")):
    if path not in sys.path:
        sys.path.insert(0, path)

from evaluation.metrics import compute_metrics, group_breakdown  # noqa: E402
from evaluation.thresholds import (  # noqa: E402
    FPR_BUDGETS,
    PRIMARY_FPR_CAP,
    recall_at_fpr_budgets,
    select_threshold_at_fpr,
)
from preprocessing.block_holdout import DEV_TRAIN, DEV_VAL, HELD_OUT  # noqa: E402
from preprocessing.pipeline import resolve_path  # noqa: E402
from prepare_unseen_capture import load_config  # noqa: E402

# Protocols imported verbatim from the primary stages.
import train_random_forest as rf_stage  # noqa: E402
import train_svm as svm_stage  # noqa: E402

SELECTION_METRIC = "pr_auc"


def _load(processed_dir: Path, name: str):
    return (np.load(processed_dir / f"X_{name}.npy"),
            np.load(processed_dir / f"y_{name}.npy"))


# ---------------------------------------------------------------------------
# per-model search + refit, reusing the Stage F/G/H grids and tie-breaks
# ---------------------------------------------------------------------------

def run_random_forest(config, X_tr, y_tr, X_va, y_va):
    from models.random_forest import build_random_forest, describe_forest

    grid = rf_stage.SEARCH_GRID
    keys = list(grid)
    candidates = [dict(zip(keys, combo))
                  for combo in itertools.product(*(grid[k] for k in keys))]
    rows = []
    for i, overrides in enumerate(candidates, 1):
        model = build_random_forest(config, **overrides)
        t0 = time.perf_counter(); model.fit(X_tr, y_tr)
        fit_s = time.perf_counter() - t0
        scores = model.predict_proba(X_va)[:, 1]
        row = compute_metrics(y_va, (scores >= 0.5).astype(np.int8), scores)
        row.update({"candidate": i, "fit_seconds": round(fit_s, 2),
                    "max_depth": overrides.get("max_depth", "config"),
                    "min_samples_leaf": overrides.get("min_samples_leaf", "config"),
                    "max_features": overrides.get("max_features", "config")})
        rows.append(row)
        print("      [{:>2}/{}] depth={:<5} leaf={:<4} feat={:<5} PR-AUC={:.5f} "
              "fit={:.0f}s".format(i, len(candidates), str(row["max_depth"]),
                                   str(row["min_samples_leaf"]),
                                   str(row["max_features"]), row["pr_auc"], fit_s),
              flush=True)
        del model

    search = pd.DataFrame(rows)
    best_score = search[SELECTION_METRIC].max()
    close = search[search[SELECTION_METRIC] >= best_score
                   - rf_stage.TIE_TOLERANCE].copy()
    close["_feat_rank"] = close["max_features"].apply(
        lambda f: 0 if f == "sqrt" else 1)
    close["_leaf_rank"] = close["min_samples_leaf"].apply(
        lambda v: 0 if rf_stage._is_unlimited(v) else -int(v))
    close["_depth_rank"] = close["max_depth"].apply(
        lambda d: 10 ** 6 if rf_stage._is_unlimited(d) else int(d))
    chosen = close.sort_values(
        ["_feat_rank", "_leaf_rank", "_depth_rank", "fit_seconds"]).iloc[0]
    best = {}
    for key in ("max_depth", "min_samples_leaf", "max_features"):
        value = chosen[key]
        if key == "max_features":
            best[key] = value
        elif rf_stage._is_unlimited(value):
            best[key] = None if key == "max_depth" else 1
        else:
            best[key] = int(value)

    model = build_random_forest(config, **best)
    t0 = time.perf_counter(); model.fit(X_tr, y_tr)
    train_seconds = time.perf_counter() - t0
    structure = describe_forest(model)
    return model, search, best, best_score, train_seconds, structure, \
        (lambda m, X: m.predict_proba(X)[:, 1]), structure["total_nodes"], "tree nodes"


def run_svm(config, X_tr, y_tr, X_va, y_va):
    from models.svm import build_svm, describe_svm, gamma_scale

    gamma = gamma_scale(X_tr)          # TRAIN-only statistic
    print("      gamma('scale') from development-train = {:.6f}".format(gamma),
          flush=True)
    grid = svm_stage.SEARCH_GRID
    keys = list(grid)
    candidates = [dict(zip(keys, combo))
                  for combo in itertools.product(*(grid[k] for k in keys))]
    rows = []
    for i, params in enumerate(candidates, 1):
        model = build_svm(config, gamma, **params)
        t0 = time.perf_counter(); model.fit(X_tr, y_tr)
        fit_s = time.perf_counter() - t0
        scores = model.decision_function(X_va)
        row = compute_metrics(y_va, (scores >= 0).astype(np.int8), scores)
        row.update({"candidate": i, "fit_seconds": round(fit_s, 2), **params})
        rows.append(row)
        print("      [{}/{}] n_components={:<5} C={:<6} PR-AUC={:.5f} "
              "fit={:.0f}s".format(i, len(candidates), params["n_components"],
                                   params["C"], row["pr_auc"], fit_s), flush=True)
        del model

    search = pd.DataFrame(rows)
    best_score = search[SELECTION_METRIC].max()
    close = search[search[SELECTION_METRIC] >= best_score
                   - svm_stage.TIE_TOLERANCE].copy()
    chosen = close.sort_values(["n_components", "C", "fit_seconds"]).iloc[0]
    best = {"n_components": int(chosen["n_components"]), "C": float(chosen["C"])}

    model = build_svm(config, gamma, **best)
    t0 = time.perf_counter(); model.fit(X_tr, y_tr)
    train_seconds = time.perf_counter() - t0
    structure = describe_svm(model)
    structure["gamma_source"] = "sklearn 'scale' computed on development-train"
    return model, search, best, best_score, train_seconds, structure, \
        (lambda m, X: m.decision_function(X)), \
        int(structure["n_components"]) + 1, "linear weights (+bias)"


def run_cnn(config, X_tr, y_tr, X_va, y_va):
    import keras
    import train_cnn as cnn_stage
    from models.cnn import (balanced_class_weight, describe_cnn,
                            reshape_for_conv1d)

    Z_tr, Z_va = reshape_for_conv1d(X_tr), reshape_for_conv1d(X_va)
    class_weight = balanced_class_weight(y_tr)   # development-train only
    print("      class_weight (dev-train) = {}".format(
        {k: round(v, 6) for k, v in class_weight.items()}), flush=True)
    seed = int(config.get("seed", 42))

    grid = cnn_stage.SEARCH_GRID
    keys = list(grid)
    candidates = [dict(zip(keys, combo))
                  for combo in itertools.product(*(grid[k] for k in keys))]
    rows = []
    for i, params in enumerate(candidates, 1):
        model, fit_s, epochs_run, best_epoch = cnn_stage._fit_candidate(
            Z_tr, y_tr, Z_va, y_va, params, class_weight, seed)
        scores = model.predict(Z_va, batch_size=cnn_stage.PREDICT_BATCH,
                               verbose=0).ravel()
        row = compute_metrics(y_va, (scores >= 0.5).astype(np.int8), scores)
        row.update({"candidate": i,
                    "filters": "x".join(str(f) for f in params["filters"]),
                    "kernel_size": params["kernel_size"],
                    "dropout": params["dropout"],
                    "learning_rate": params["learning_rate"],
                    "params": int(model.count_params()),
                    "epochs_run": epochs_run, "best_epoch": best_epoch,
                    "fit_seconds": round(fit_s, 1)})
        rows.append(row)
        print("      [{:>2}/{}] filters={:<7} k={} drop={} lr={:<7} "
              "PR-AUC={:.5f} epochs={:>2} fit={:.0f}s".format(
                  i, len(candidates), row["filters"], params["kernel_size"],
                  params["dropout"], params["learning_rate"], row["pr_auc"],
                  epochs_run, fit_s), flush=True)
        del model
        keras.backend.clear_session()

    search = pd.DataFrame(rows)
    best_score = search[SELECTION_METRIC].max()
    close = search[search[SELECTION_METRIC] >= best_score
                   - cnn_stage.TIE_TOLERANCE].copy()
    chosen = close.sort_values(["params", "kernel_size", "fit_seconds"]).iloc[0]
    best = {"filters": tuple(int(f) for f in str(chosen["filters"]).split("x")),
            "kernel_size": int(chosen["kernel_size"]),
            "dropout": float(chosen["dropout"]),
            "learning_rate": float(chosen["learning_rate"])}

    model, train_seconds, epochs_run, best_epoch = cnn_stage._fit_candidate(
        Z_tr, y_tr, Z_va, y_va, best, class_weight, seed)
    structure = describe_cnn(model, config)
    structure.update({"epochs_run": epochs_run, "best_epoch": best_epoch,
                      "class_weight": {str(k): v for k, v in class_weight.items()}})
    return model, search, best, best_score, train_seconds, structure, \
        (lambda m, X: m.predict(reshape_for_conv1d(X),
                                batch_size=cnn_stage.PREDICT_BATCH,
                                verbose=0).ravel()), \
        int(structure["total_parameters"]), "trainable parameters"


RUNNERS = {"rf": ("RandomForest", run_random_forest),
           "svm": ("SVM", run_svm),
           "cnn": ("CNN_1D", run_cnn)}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Stage L unseen-capture training and evaluation.")
    parser.add_argument("--model", required=True, choices=sorted(RUNNERS))
    parser.add_argument("--config",
                        default=str(M1_ROOT / "config"
                                    / "m1_config_unseen_capture.yaml"))
    args = parser.parse_args()

    config = load_config(args.config)
    name, runner = RUNNERS[args.model]
    results_dir = resolve_path(REPO_ROOT, config["output"]["results_dir"])
    processed_dir = resolve_path(REPO_ROOT, config["output"]["processed_dir"])
    model_dir = results_dir / args.model
    model_dir.mkdir(parents=True, exist_ok=True)

    print("[1/5] loading Stage L development matrices", flush=True)
    X_tr, y_tr = _load(processed_dir, DEV_TRAIN)
    X_va, y_va = _load(processed_dir, DEV_VAL)
    for split, X, y in ((DEV_TRAIN, X_tr, y_tr), (DEV_VAL, X_va, y_va)):
        assert np.isfinite(X).all() and set(np.unique(y)) <= {0, 1}
        print("      {:<10} {}  malicious={:.3f}%".format(
            split, X.shape, 100 * y.mean()), flush=True)

    print("[2/5] {} search on dev-train, scored on dev-validation".format(name),
          flush=True)
    (model, search, best, best_score, train_seconds, structure,
     score_fn, size, size_kind) = runner(config, X_tr, y_tr, X_va, y_va)
    search.to_csv(model_dir / "validation_search.csv", index=False)
    print("      best {}={:.5f}; chosen -> {}".format(
        SELECTION_METRIC, best_score, best), flush=True)
    print("      refit on dev-train in {:.1f}s".format(train_seconds), flush=True)

    print("[3/5] freezing threshold on dev-validation (FPR <= 1%)", flush=True)
    val_scores = score_fn(model, X_va)
    budgets = recall_at_fpr_budgets(y_va, val_scores, FPR_BUDGETS)
    pd.DataFrame(budgets).to_csv(model_dir / "validation_fpr_budgets.csv",
                                 index=False)
    for row in budgets:
        print("        FPR<={:<7.2%} threshold={:>10.6f} recall={:.6f} "
              "achieved={:.6f}".format(row["max_fpr"], row["threshold"],
                                       row["recall"], row["fpr"]), flush=True)
    operating = select_threshold_at_fpr(y_va, val_scores, PRIMARY_FPR_CAP)
    threshold = operating["threshold"]
    print("      FROZEN threshold = {:.6f}".format(threshold), flush=True)
    val_metrics = compute_metrics(
        y_va, (val_scores >= threshold).astype(np.int8), val_scores)

    # ---- 4. HELD-OUT: read for the first time, evaluated exactly once ----
    print("[4/5] held-out evaluation (single pass, frozen threshold)", flush=True)
    X_ho, y_ho = _load(processed_dir, HELD_OUT)
    t0 = time.perf_counter()
    held_scores = score_fn(model, X_ho)
    infer_seconds = time.perf_counter() - t0
    y_pred = (held_scores >= threshold).astype(np.int8)
    held_metrics = compute_metrics(y_ho, y_pred, held_scores)
    held_metrics["batch_throughput_ms_per_flow"] = round(
        1000 * infer_seconds / len(y_ho), 6)
    for key in ("accuracy", "precision", "recall", "f1", "fpr", "tnr",
                "roc_auc", "pr_auc"):
        print("      {:<10} {:.6f}".format(key, held_metrics[key]), flush=True)
    print("      TP={:,} TN={:,} FP={:,} FN={:,}".format(
        held_metrics["TP"], held_metrics["TN"],
        held_metrics["FP"], held_metrics["FN"]), flush=True)

    print("[5/5] per-block / per-attack breakdown and artifacts", flush=True)
    meta = pd.read_csv(processed_dir / f"metadata_{HELD_OUT}.csv")
    assert len(meta) == len(y_ho) and np.array_equal(
        meta["target"].to_numpy().astype(np.int8), y_ho)

    per_block = []
    for block, group in meta.groupby("block", sort=True):
        idx = group.index.to_numpy()
        bm = compute_metrics(y_ho[idx], y_pred[idx])
        per_block.append({
            "block": int(block),
            "base_station": int(group["base_station"].iloc[0]),
            "attack_types": "|".join(
                sorted(set(group["attack_type"]) - {"Benign"})) or "Benign",
            "rows": int(len(idx)),
            "benign": int((y_ho[idx] == 0).sum()),
            "malicious": int((y_ho[idx] == 1).sum()),
            "malicious_pct": round(100 * float(y_ho[idx].mean()), 4),
            **{k: bm[k] for k in ("accuracy", "precision", "recall", "f1",
                                  "fpr", "tnr", "TP", "TN", "FP", "FN")},
        })
    pd.DataFrame(per_block).to_csv(model_dir / "per_block_metrics.csv",
                                   index=False)
    print(pd.DataFrame(per_block)[
        ["block", "attack_types", "rows", "malicious_pct", "recall", "fpr"]
    ].to_string(index=False), flush=True)

    by_type = pd.DataFrame(group_breakdown(y_ho, y_pred,
                                           meta["attack_type"].to_numpy()))
    by_tool = pd.DataFrame(group_breakdown(y_ho, y_pred,
                                           meta["attack_tool"].to_numpy()))
    by_type.to_csv(model_dir / "per_attack_type.csv", index=False)
    by_tool.to_csv(model_dir / "per_attack_tool.csv", index=False)

    from sklearn.metrics import precision_recall_curve, roc_curve
    fpr_c, tpr_c, _ = roc_curve(y_ho, held_scores)
    prec_c, rec_c, _ = precision_recall_curve(y_ho, held_scores)
    step = max(1, len(fpr_c) // 2000)
    pd.DataFrame({"fpr": fpr_c[::step], "tpr": tpr_c[::step]}).to_csv(
        model_dir / "heldout_roc_curve.csv", index=False)
    step = max(1, len(prec_c) // 2000)
    pd.DataFrame({"recall": rec_c[::step], "precision": prec_c[::step]}).to_csv(
        model_dir / "heldout_pr_curve.csv", index=False)

    suffix = ".keras" if args.model == "cnn" else ".joblib"
    model_path = processed_dir / f"{args.model}_model{suffix}"
    if args.model == "cnn":
        model.save(model_path)
    else:
        joblib.dump(model, model_path, compress=3)

    record = {
        "stage": "L",
        "experiment": "secondary unseen-capture generalisation",
        "is_primary": False,
        "model": name,
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "python": platform.python_version(),
        "seed": int(config.get("seed", 42)),
        "held_out_blocks": config["unseen_capture"]["held_out_blocks"],
        "development_blocks": config["unseen_capture"]["development_blocks"],
        "rows": {"dev_train": int(len(y_tr)), "dev_val": int(len(y_va)),
                 "held_out": int(len(y_ho))},
        "search_grid_source": (
            "imported verbatim from the Stage F/G/H experiment scripts"),
        "n_candidates": int(len(search)),
        "selection_metric": SELECTION_METRIC,
        "best_validation_score": float(best_score),
        "chosen_hyperparameters": {k: (list(v) if isinstance(v, tuple) else v)
                                   for k, v in best.items()},
        "model_structure": structure,
        "model_size": size, "model_size_kind": size_kind,
        "operating_point": {"rule": ("max dev-validation recall subject to "
                                     "dev-validation FPR <= 1%; ties -> highest "
                                     "threshold; frozen before held-out"),
                            "primary_fpr_cap": PRIMARY_FPR_CAP, **operating},
        "validation_fpr_budgets": budgets,
        "validation_metrics_at_frozen_threshold": val_metrics,
        "held_out_metrics": held_metrics,
        "timings_seconds": {"train": round(train_seconds, 2),
                            "held_out_inference": round(infer_seconds, 3),
                            "search_total": round(
                                float(search["fit_seconds"].sum()), 1)},
        "held_out_evaluations_performed": 1,
        "test_based_tuning": False,
        "udpflood_in_holdout": False,
        "note": ("UDPFlood is absent from the held-out blocks and is NOT "
                 "evaluable under this holdout; the held-out population is "
                 "also far less ambiguous than the primary test population."),
    }
    (model_dir / "unseen_capture_record.json").write_text(
        json.dumps(record, indent=2, default=str), encoding="utf-8")
    (model_dir / "heldout_metrics.json").write_text(
        json.dumps(held_metrics, indent=2), encoding="utf-8")
    print("      wrote {}".format(model_dir), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
