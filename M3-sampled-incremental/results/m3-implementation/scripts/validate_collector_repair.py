"""Repeat affected collector configurations without selecting on detection scores.

This diagnostic batch is separate from the planned 54-trial primary matrix.
It reuses the first repaired pilot and preserves every new attempt on failure.
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "sdn"))

from finish_corrected_study import paper_snapshot, require_corrected_run
from run_official_capture_pilot import run

from m3.provenance import sha256
from m3.store import atomic_json, utc_now


def require_validation_run(summary):
    gates = ("telemetry_kernel_clock", "telemetry_ingestion_timing",
             "telemetry_tail_complete", "independent_sflow_capture")
    if (summary.get("status") != "completed"
            or summary.get("source") != "official_realtime_verified"
            or summary.get("config", {}).get("naive_bayes") != "log_space"
            or summary.get("config", {}).get("telemetry_clock") != "kernel_receive"
            or summary.get("validation", {}).get("accepted") is not True
            or any(summary.get("validation", {}).get(key) is not True for key in gates)):
        raise ValueError("Repair validation requires independently accepted kernel-ingestion evidence")


def validate(study):
    study = Path(study).resolve()
    destination = study / "repair_validation"
    destination.mkdir(parents=True, exist_ok=True)
    sources = sorted([*ROOT.glob("src/m3/*.py"), *ROOT.glob("sdn/*.py"),
                      Path(__file__).resolve(),
                      ROOT / "configs/research_protocol_kernel_ingestion.json"])
    fingerprint = {p.relative_to(ROOT).as_posix(): sha256(p) for p in sources}
    state_path = destination / "validation.json"
    if state_path.exists():
        state = json.loads(state_path.read_text())
        if state["source_sha256"] != fingerprint:
            raise ValueError("Source changed during collector-repair validation")
    else:
        pilot_path, = (study / "pilot/runs").glob("*/run_summary.json")
        pilot = json.loads(pilot_path.read_text())
        require_corrected_run(pilot, pilot=True, telemetry_clock="kernel_receive")
        if (pilot["scenario"], pilot["config"]["seed"]) != ("baseline", 43):
            raise ValueError("Expected the baseline seed43 repaired pilot")
        cells = []
        for scenario, sampling in [("baseline", 1), ("drift", 1), ("drift", 2)]:
            for trial_id, seed in enumerate([42, 43, 44], 1):
                reused = scenario == "baseline" and seed == 43
                cells.append({"scenario": scenario, "sampling": sampling, "seed": seed,
                              "trial_id": trial_id, "status": "completed" if reused else "pending",
                              "summary": str(pilot_path) if reused else None,
                              "origin": "initial_repaired_pilot" if reused else "new_validation"})
        state = {"created_at": utc_now(), "source_sha256": fingerprint, "cells": cells,
                 "purpose": "Targeted engineering regression, not the full primary study",
                 "selection": "Three configurations implicated by independent backlog diagnosis; all three fixed model seeds. Initial baseline43 pilot was seen before this batch was declared.",
                 "acceptance": "Existing raw-evidence and kernel-ingestion gates only; no F1 cutoff or outcome-based replacement"}
        atomic_json(state_path, state)
    paper_snapshot(study)
    for cell in state["cells"]:
        if cell["status"] == "completed":
            continue
        if cell["status"] != "pending":
            raise RuntimeError(f"Inspect retained failed/incomplete attempt before resuming: {cell}")
        cell.update(status="running", started_at=utc_now())
        atomic_json(state_path, state)
        try:
            report = run(
                ROOT / "data/prepared/research_20261019_equalrate_v1" / cell["scenario"] / "blocks.json",
                ROOT / "data/manifest.json", cell["sampling"], destination / "evidence",
                runs_root=destination / "runs",
                research={**{k: cell[k] for k in ("scenario", "seed", "trial_id")},
                          "study_role": "validation_pilot", "naive_bayes": "log_space",
                          "telemetry_clock": "kernel_receive"},
            )
            summary_path = destination / "runs" / report["collector_run_id"] / "run_summary.json"
            summary = json.loads(summary_path.read_text())
            require_validation_run(summary)
            cell.update(status="completed", summary=str(summary_path), finished_at=utc_now())
        except BaseException as error:
            cell.update(status="failed", error=str(error), finished_at=utc_now())
            atomic_json(state_path, state)
            raise
        atomic_json(state_path, state)
        print(json.dumps({"completed": sum(c["status"] == "completed" for c in state["cells"]),
                          "total": len(state["cells"]), "cell": cell}), flush=True)
    results = []
    for cell in state["cells"]:
        path = Path(cell["summary"])
        summary = json.loads(path.read_text())
        require_validation_run(summary)
        for name, checksum in summary["raw_hashes"].items():
            if sha256(summary["artifacts"][name]) != checksum:
                raise ValueError(f"Evidence changed: {path}/{name}")
        results.append({**cell, "summary_sha256": sha256(path), "run_id": summary["run_id"],
                        "metrics": summary["metrics"], "ingestion": summary["ingestion"],
                        "validation": summary["validation"]})
    if fingerprint != {p.relative_to(ROOT).as_posix(): sha256(p) for p in sources}:
        raise ValueError("Source changed during validation")
    paper_snapshot(study)
    atomic_json(destination / "results.json", {"completed_at": utc_now(), "runs": results})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--study", default="output/research/kernel_ingestion_v2_20261028")
    validate(parser.parse_args().study)
