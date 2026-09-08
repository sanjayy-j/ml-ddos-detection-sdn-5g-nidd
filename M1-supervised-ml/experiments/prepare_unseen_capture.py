"""Stage L — prepare the unseen-capture development / held-out matrices.

    python M1-supervised-ml/experiments/prepare_unseen_capture.py

Builds a completely fresh representation for the secondary experiment:
eight capture blocks are held out entirely, and preprocessing is fitted on
**development-train only**. Nothing from the primary Stage D/E pipeline is
reused except the *schema* (the 67-feature definition and its exclusions),
which is inherited unchanged.

No primary artifact is read for its values or written to.
"""

from __future__ import annotations

import argparse
import hashlib
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

from evaluation.novelty import novelty_report  # noqa: E402
from preprocessing.block_holdout import (  # noqa: E402
    ASSIGNMENT_NAMES,
    DEV_TRAIN,
    DEV_VAL,
    HELD_OUT,
    assign_blocks,
    build_manifest,
    get_block_sets,
    verify_isolation,
)
from preprocessing.data_loader import load_config_file, load_raw_data  # noqa: E402
from preprocessing.features import build_feature_frame, build_target  # noqa: E402
from preprocessing.pipeline import resolve_path  # noqa: E402
from preprocessing.splitting import (  # noqa: E402
    detect_base_station,
    detect_capture_blocks,
)
from preprocessing.transformers import (  # noqa: E402
    build_preprocessor,
    get_output_feature_names,
)


def load_config(path: str) -> dict:
    """Load the Stage L config and inherit the primary schema verbatim."""
    config = load_config_file(path)
    parent = config.get("inherit_schema_from")
    if parent:
        primary = load_config_file(resolve_path(REPO_ROOT, parent))
        config["schema"] = primary["schema"]
        config.setdefault("models", {})
        for key, value in (primary.get("models") or {}).items():
            config["models"].setdefault(key, value)
    return config


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Prepare the Stage L unseen-capture matrices.")
    parser.add_argument("--config",
                        default=str(M1_ROOT / "config"
                                    / "m1_config_unseen_capture.yaml"))
    args = parser.parse_args()

    config = load_config(args.config)
    dev_blocks, held_blocks = get_block_sets(config)
    results_dir = resolve_path(REPO_ROOT, config["output"]["results_dir"])
    processed_dir = resolve_path(REPO_ROOT, config["output"]["processed_dir"])
    results_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    print("[1/6] loading raw dataset", flush=True)
    config["dataset"]["raw_path"] = str(
        resolve_path(REPO_ROOT, config["dataset"]["raw_path"]))
    started = time.perf_counter()
    df = load_raw_data(config)
    print("      {:,} rows x {} cols ({:.1f}s)".format(
        df.shape[0], df.shape[1], time.perf_counter() - started), flush=True)

    y = build_target(df, config).to_numpy()
    features = build_feature_frame(df, config)
    block_ids = detect_capture_blocks(df, config)
    base_station_ids = detect_base_station(df, config)
    attack_types = df[config["schema"]["metadata_columns"][0]].to_numpy()
    attack_tools = df[config["schema"]["metadata_columns"][1]].to_numpy()

    print("[2/6] partitioning by whole capture block", flush=True)
    print("      held-out blocks:    {}".format(held_blocks), flush=True)
    print("      development blocks: {}".format(dev_blocks), flush=True)
    assignment = assign_blocks(block_ids, y, config)
    isolation = verify_isolation(assignment, block_ids, config)
    for name in ASSIGNMENT_NAMES:
        n = isolation["rows"][name]
        mask = assignment == name
        print("      {:<10} rows={:>9,}  malicious={:>7.3f}%".format(
            name, n, 100 * float(y[mask].mean())), flush=True)

    manifest = build_manifest(assignment, block_ids, base_station_ids, y,
                              attack_types)
    manifest.to_csv(results_dir / "unseen_capture_manifest.csv", index=False)

    # --- preprocessing fitted on DEVELOPMENT-TRAIN ONLY ------------------
    print("[3/6] fitting preprocessing on development-train only", flush=True)
    train_mask = assignment == DEV_TRAIN
    preprocessor = build_preprocessor(config)
    preprocessor.fit(features.loc[train_mask])
    feature_names = get_output_feature_names(preprocessor)
    print("      fitted on {:,} rows -> {} output features".format(
        int(train_mask.sum()), len(feature_names)), flush=True)

    scaler = preprocessor.named_transformers_["numeric"].named_steps["scale"]
    seen = scaler.n_samples_seen_
    seen = int(np.max(seen)) if np.ndim(seen) else int(seen)
    if seen != int(train_mask.sum()):
        raise SystemExit(
            "ERROR: preprocessing saw {:,} rows but development-train has "
            "{:,}".format(seen, int(train_mask.sum())))
    print("      provenance verified: scaler saw exactly the "
          "development-train rows (no held-out row contributed)", flush=True)

    print("[4/6] transforming all three partitions", flush=True)
    matrices, targets = {}, {}
    for name in ASSIGNMENT_NAMES:
        mask = assignment == name
        matrices[name] = preprocessor.transform(
            features.loc[mask]).astype(np.float32)
        targets[name] = y[mask].astype(np.int8)
        np.save(processed_dir / f"X_{name}.npy", matrices[name])
        np.save(processed_dir / f"y_{name}.npy", targets[name])
        meta = pd.DataFrame({
            "attack_type": attack_types[mask], "attack_tool": attack_tools[mask],
            "block": block_ids[mask], "base_station": base_station_ids[mask],
            "target": targets[name],
        })
        meta.to_csv(processed_dir / f"metadata_{name}.csv", index=False)
        print("      {:<10} {}".format(name, matrices[name].shape), flush=True)
    joblib.dump(preprocessor, processed_dir / "preprocessor.joblib")

    # --- novelty analysis -------------------------------------------------
    print("[5/6] novelty analysis (data only; no model involved)", flush=True)
    dev_mask = (assignment == DEV_TRAIN) | (assignment == DEV_VAL)
    X_dev = np.vstack([matrices[DEV_TRAIN], matrices[DEV_VAL]])
    y_dev = np.concatenate([targets[DEV_TRAIN], targets[DEV_VAL]])
    stage_l = novelty_report(X_dev, y_dev, matrices[HELD_OUT],
                             targets[HELD_OUT],
                             "Stage L held-out blocks vs development")
    for key, value in stage_l.items():
        if key != "scope":
            print("      {:<44} {}".format(key, value), flush=True)

    # primary comparison, using the primary artifacts READ-ONLY
    primary_dir = resolve_path(REPO_ROOT, "M1-supervised-ml/data/processed")
    primary = None
    if (primary_dir / "X_train.npy").is_file():
        Xp_ref = np.vstack([np.load(primary_dir / "X_train.npy"),
                            np.load(primary_dir / "X_val.npy")])
        yp_ref = np.concatenate([np.load(primary_dir / "y_train.npy"),
                                 np.load(primary_dir / "y_val.npy")])
        primary = novelty_report(
            Xp_ref, yp_ref, np.load(primary_dir / "X_test.npy"),
            np.load(primary_dir / "y_test.npy"),
            "Primary Stage E test vs its development")
        print("      -- primary comparison --", flush=True)
        for key in ("pct_rows_vector_seen_in_reference",
                    "pct_rows_in_conflicting_vectors"):
            print("      {:<44} {}".format(key, primary[key]), flush=True)

    print("[6/6] writing provenance", flush=True)
    record = {
        "stage": "L",
        "experiment": "secondary unseen-capture generalisation",
        "is_primary": False,
        "primary_protocol_unchanged": True,
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "python": platform.python_version(),
        "seed": int(config.get("seed", 42)),
        "held_out_blocks": held_blocks,
        "development_blocks": dev_blocks,
        "block_isolation": isolation,
        "split_strategy": config["split"]["strategy"],
        "train_ratio": config["split"]["train_ratio"],
        "rows": {name: int((assignment == name).sum())
                 for name in ASSIGNMENT_NAMES},
        "malicious_pct": {name: round(100 * float(y[assignment == name].mean()), 4)
                          for name in ASSIGNMENT_NAMES},
        "n_output_features": len(feature_names),
        "feature_order": feature_names,
        "preprocessing_provenance": {
            "fitted_on": "development-train only",
            "fit_rows": int(train_mask.sum()),
            "scaler_rows_seen": seen,
            "held_out_rows_used_for_fitting": 0,
            "reused_primary_preprocessor": False,
        },
        "novelty_stage_l": stage_l,
        "novelty_primary": primary,
        "limitations": {
            "udpflood_absent_from_holdout": True,
            "note": (
                "UDPFlood cannot be held out: every feasible whole-block "
                "subset containing block 4 or 14 carries a 42.9-43.5 pp "
                "class-prior shift. Stage L therefore CANNOT measure "
                "unseen-capture generalisation for UDP flood. The held-out "
                "population is also far less ambiguous than the primary test "
                "population, so Stage L results must NOT be read as a "
                "straight improvement over the primary test."
            ),
        },
    }
    (results_dir / "unseen_capture_preparation.json").write_text(
        json.dumps(record, indent=2, default=str), encoding="utf-8")
    print("      wrote {}".format(results_dir), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
