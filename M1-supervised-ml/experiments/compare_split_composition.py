"""Phase 3.3 analysis — why the rotated contiguous split scores differently.

Pooled recall on this dataset is almost entirely a function of how many
UDP-flood records a window contains, because UDP-flood recall is ~0.09
while the other seven attack types are detected at >=0.986. Any
old-vs-new comparison therefore has to be read per attack type, not
pooled.

This script retrains the Random Forest on one representation at the
published hyperparameters, freezes the threshold on validation under the
locked FPR <= 1% protocol, and writes the per-attack-type breakdown, so
the published and rotated windows can be compared type by type.

It trains nothing new in methodology terms: the configuration, the
protocol and the seed are those of the committed run, so the pooled row
it produces reproduces the corresponding seed_sweep row exactly.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

M1_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = M1_ROOT.parent
if str(M1_ROOT) not in sys.path:
    sys.path.insert(0, str(M1_ROOT))

from evaluation.metrics import compute_metrics, group_breakdown  # noqa: E402
from evaluation.thresholds import (  # noqa: E402
    PRIMARY_FPR_CAP,
    select_threshold_at_fpr,
)
from models.random_forest import build_random_forest  # noqa: E402
from preprocessing.data_loader import load_config_file  # noqa: E402
from preprocessing.pipeline import load_processed, resolve_path  # noqa: E402
from training.metadata import load_split_metadata  # noqa: E402

# The configuration the Stage F validation search selected.
CHOSEN = {"max_depth": 20, "min_samples_leaf": 20, "max_features": "sqrt"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--label", default="run",
                        help="short name used in the output filename")
    args = parser.parse_args()

    config = load_config_file(args.config)
    config["seed"] = args.seed
    config.setdefault("models", {}).setdefault("random_forest", {})
    config["models"]["random_forest"]["random_state"] = args.seed

    results_root = resolve_path(
        REPO_ROOT,
        (config.get("output") or {}).get("results_dir",
                                        "M1-supervised-ml/results"))
    out_dir = results_root / "split_composition"
    out_dir.mkdir(parents=True, exist_ok=True)

    print("[1/4] loading representation from " + str(results_root), flush=True)
    data = load_processed(config, REPO_ROOT)
    X_tr, y_tr = data["X"]["train"], data["y"]["train"]
    X_va, y_va = data["X"]["val"], data["y"]["val"]
    X_te, y_te = data["X"]["test"], data["y"]["test"]
    print("      train={:,} val={:,} test={:,} features={}".format(
        len(y_tr), len(y_va), len(y_te), X_tr.shape[1]), flush=True)

    print("[2/4] training Random Forest (published hyperparameters, seed {})"
          .format(args.seed), flush=True)
    model = build_random_forest(config, **CHOSEN)
    t0 = time.perf_counter()
    model.fit(X_tr, y_tr)
    print("      fitted in {:.0f}s".format(time.perf_counter() - t0), flush=True)

    print("[3/4] freezing the threshold on validation (FPR <= 1%)", flush=True)
    val_scores = model.predict_proba(X_va)[:, 1]
    operating = select_threshold_at_fpr(y_va, val_scores, PRIMARY_FPR_CAP)
    threshold = float(operating["threshold"])
    print("      threshold = {:.6f} (validation recall {:.6f}, FPR {:.6f})"
          .format(threshold, operating["recall"], operating["fpr"]), flush=True)

    test_scores = model.predict_proba(X_te)[:, 1]
    y_pred = (test_scores >= threshold).astype(np.int8)
    pooled = compute_metrics(y_te, y_pred, test_scores)
    print("      pooled test: accuracy {accuracy:.6f} recall {recall:.6f} "
          "fpr {fpr:.6f} roc_auc {roc_auc:.6f}".format(**pooled), flush=True)

    print("[4/4] per-attack-type breakdown", flush=True)
    meta = load_split_metadata(config, REPO_ROOT, "test")
    groups = meta["attack_type"].to_numpy()
    rows = group_breakdown(y_te, y_pred, groups)
    frame = pd.DataFrame(rows)
    path = out_dir / f"per_attack_type_{args.label}.csv"
    frame.to_csv(path, index=False)
    print(frame.to_string(index=False), flush=True)
    print("      wrote " + str(path), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
