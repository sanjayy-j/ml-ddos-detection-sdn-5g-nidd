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
from preprocessing.features import build_target  # noqa: E402
from preprocessing.splitting import (  # noqa: E402
    detect_capture_blocks,
    make_split,
)
from training.metadata import load_split_metadata  # noqa: E402

# The configuration the Stage F validation search selected.
CHOSEN = {"max_depth": 20, "min_samples_leaf": 20, "max_features": "sqrt"}

# The dominant conflicting feature vector documented in the paper: it occurs
# 271,476 times as 159,875 UDP-flood and 111,601 benign records, so rows
# carrying it are irreducibly ambiguous. Conditioning on it separates the
# effect of ambiguity density from everything else that changes with the
# window.
CARRIER_COLUMNS = ["Proto", "Dur", "TotPkts", "TotBytes", "State", "sTtl",
                   "Rate", "Cause"]


def carrier_mask_for_test_split(config: dict, raw_path: Path) -> np.ndarray:
    """Per-test-row flag: does this row carry the dominant ambiguous vector?

    The split assignment is recomputed with the same config that produced
    the processed matrices, and rows are selected in original order, which
    is the order `load_processed` and `load_split_metadata` both use.
    """
    needed = sorted(set(CARRIER_COLUMNS + ["Unnamed: 0", "Offset", "Label"]))
    df = pd.read_csv(raw_path, usecols=needed, low_memory=False)
    y = build_target(df, config).to_numpy()
    blocks = detect_capture_blocks(df, config)
    assignment = make_split(y, blocks, config)

    carrier = ((df["Proto"].astype(str).str.lower() == "udp")
               & (df["Dur"] == 0)
               & (df["TotPkts"] == 1)
               & (df["TotBytes"] == 42)
               & (df["State"].astype(str) == "REQ")
               & (df["sTtl"] == 63)
               & (df["Rate"] == 0)
               & (df["Cause"].astype(str) == "Status")).to_numpy()
    return carrier[assignment == "test"]


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

    print("[5/5] UDP-flood recall conditioned on the dominant ambiguous vector",
          flush=True)
    raw_path = resolve_path(
        REPO_ROOT, (config.get("dataset") or {}).get("raw_path",
                                                     "data/raw/Combined.csv"))
    carrier = carrier_mask_for_test_split(config, raw_path)
    if len(carrier) != len(y_te):
        raise SystemExit("carrier mask length {} != test rows {}".format(
            len(carrier), len(y_te)))
    udp = groups == "UDPFlood"
    cond_rows = []
    for name, sel in (("carrier", udp & carrier), ("non_carrier", udp & ~carrier)):
        support = int(sel.sum())
        detected = int(y_pred[sel].sum())
        recall = detected / support if support else float("nan")
        cond_rows.append({"window": args.label, "subset": name,
                          "support": support, "detected": detected,
                          "recall": round(recall, 6)})
        print("      {:<12} support {:>7,}  detected {:>7,}  recall {:.6f}"
              .format(name, support, detected, recall), flush=True)
    all_udp = int((udp).sum())
    cond_rows.append({"window": args.label, "subset": "all_udpflood",
                      "support": all_udp,
                      "detected": int(y_pred[udp].sum()),
                      "recall": round(float(y_pred[udp].sum()) / all_udp, 6)})
    cond_rows.append({"window": args.label, "subset": "carrier_share_of_udpflood",
                      "support": all_udp,
                      "detected": int((udp & carrier).sum()),
                      "recall": round(float((udp & carrier).sum()) / all_udp, 6)})
    cond_path = out_dir / f"udpflood_by_ambiguity_{args.label}.csv"
    pd.DataFrame(cond_rows).to_csv(cond_path, index=False)
    print("      wrote " + str(cond_path), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
