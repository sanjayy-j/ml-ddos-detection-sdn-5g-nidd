"""Resumable sequential official-data experiment matrix; no outcome-based retries."""

import argparse
import json
import random
from pathlib import Path

from run_official_capture_pilot import run

from m3.store import atomic_json, utc_now


def retry_failed(matrix, reason):
    if not reason or not reason.strip():
        raise ValueError("A retry needs a documented technical reason")
    for cell in matrix["cells"]:
        if cell["status"] == "failed":
            history = cell.setdefault("attempts", [])
            history.append({key: value for key, value in cell.items() if key != "attempts"})
            cell.update(status="pending", retry_explanation=reason, retry_at=utc_now())
            cell.pop("error", None)


def execute(protocol, prepared, output, *, limit=None, retry_reason=None):
    protocol = json.loads(Path(protocol).read_text())
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    matrix_path = output / "matrix.json"
    if matrix_path.exists():
        matrix = json.loads(matrix_path.read_text())
    else:
        cells = [{"scenario": scenario, "sampling": rate, "seed": seed, "trial_id": number + 1,
                  "status": "pending"}
                 for scenario in protocol["scenarios"] for rate in protocol["sampling_rates"]
                 for number, seed in enumerate(protocol["model_seeds"])]
        random.Random(protocol["ordering_seed"]).shuffle(cells)
        matrix = {"protocol": protocol, "cells": cells}
        atomic_json(matrix_path, matrix)
    if retry_reason:
        retry_failed(matrix, retry_reason)
        atomic_json(matrix_path, matrix)
    done = 0
    for cell in matrix["cells"]:
        if cell["status"] == "completed":
            continue
        # A failure is retained and stops the batch; it is never silently replaced.
        if cell["status"] in {"failed", "running"}:
            raise RuntimeError(f"Resolve and document prior incomplete cell before resuming: {cell}")
        cell["status"] = "running"
        atomic_json(matrix_path, matrix)
        try:
            report = run(Path(prepared) / cell["scenario"] / "blocks.json", "data/manifest.json",
                         cell["sampling"], output, research={key: cell[key]
                         for key in ("scenario", "seed", "trial_id")})
            cell.update(status="completed", run_id=report["collector_run_id"])
        except Exception as error:
            cell.update(status="failed", error=str(error))
            atomic_json(matrix_path, matrix)
            raise
        atomic_json(matrix_path, matrix)
        print(json.dumps({"completed": sum(c["status"] == "completed" for c in matrix["cells"]),
                          "total": len(matrix["cells"]), "cell": cell}), flush=True)
        done += 1
        if limit is not None and done >= limit:
            break


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", default="configs/research_protocol.json")
    parser.add_argument("--prepared", default="data/prepared/research_20261019_equalrate_v1")
    parser.add_argument("--output", default="output/research/equalrate_v1")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--retry-failed", help="Documented technical reason; failed attempts remain saved")
    args = parser.parse_args()
    execute(args.protocol, args.prepared, args.output, limit=args.limit, retry_reason=args.retry_failed)
