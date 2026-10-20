"""Recompute one-second quality from saved raw exports, never average features.

This is an explicitly offline window-size sensitivity check, not live timing.
Primary accepted run summaries and measurements are never rewritten.
"""

import argparse
import csv
import json
import math
import struct
from collections import defaultdict
from dataclasses import replace
from pathlib import Path

from m3.live_supervision import truth_payload
from m3.packets import WindowAccumulator
from m3.provenance import sha256
from m3.research_metrics import eligible, evaluate_ablations
from m3.sflow import decode_datagram
from m3.store import atomic_json


def compute(run_path):
    run_path = Path(run_path)
    summary = json.loads((run_path / "run_summary.json").read_text())
    if not eligible(summary):
        raise ValueError("Sensitivity requires accepted primary evidence")
    paths = {name: Path(summary["artifacts"][name]) for name in ("datagrams", "packet_events")}
    for name, path in paths.items():
        if sha256(path) != summary["raw_hashes"][name]:
            raise ValueError("Raw evidence changed after validation")
    origin, config = summary["origin_epoch"], summary["config"]
    truth = defaultdict(list)
    with paths["packet_events"].open() as stream:
        for row in csv.DictReader(stream):
            truth[math.floor(float(row["epoch"]) - origin)].append(row["attack_family"] or None)
    accumulator, records = WindowAccumulator(1.0), []
    with paths["datagrams"].open("rb") as stream:
        while header := stream.read(12):
            if len(header) != 12:
                raise ValueError("Truncated saved datagram header")
            epoch, size = struct.unpack("!dI", header)
            payload = stream.read(size)
            if len(payload) != size:
                raise ValueError("Truncated saved datagram payload")
            packets, _ = decode_datagram(payload, epoch)
            for packet in packets:
                if 0 <= epoch - origin < config["duration_seconds"]:
                    records.extend(accumulator.add(packet, origin))
    records.extend(accumulator.advance(math.floor(config["duration_seconds"])))
    rows = []
    for record, count in records:
        label = truth_payload(truth[record.index], origin + record.time, origin + record.time + 1)
        record = replace(record, label=label["label"], attack_family=label["attack_family"])
        rows.append({"features": record.features, "y_true": record.label,
                     "attack_family": record.attack_family,
                     "phase": "warmup" if record.time < config["warmup_seconds"] else "evaluation",
                     "observed_time": record.time + 1 + config["label_delay_seconds"],
                     "label_available_time": record.time + 1 + config["label_delay_seconds"],
                     "sampled_packets": count})
    models = evaluate_ablations(rows, seed=config["seed"], grace_period=config["grace_period"],
                               drift_delta=config["drift_delta"], threshold=config["threshold"])
    result = {"primary_run_id": summary["run_id"], "window_seconds": 1.0,
              "source": "posthoc_saved_raw_exports", "raw_hashes": summary["raw_hashes"],
              "models": models, "rows": len(rows),
              "scope": "Offline quality sensitivity only; no live CPU or latency comparison"}
    atomic_json(run_path / "sensitivity.json", result)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", default="output/runs")
    args = parser.parse_args()
    completed = 0
    for path in sorted(Path(args.runs).glob("*/run_summary.json")):
        if eligible(json.loads(path.read_text())):
            compute(path.parent)
            completed += 1
    print(json.dumps({"sensitivity_completed": completed}))
