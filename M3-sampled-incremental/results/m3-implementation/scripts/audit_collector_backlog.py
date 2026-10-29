"""Read-only timing diagnosis of saved telemetry; no model replay or live traffic.

Independent victim RX timestamps are used ONLY to diagnose observation delay.
They must never replace deployable telemetry timestamps or supply model features.
"""

import argparse
import hashlib
import json
import math
import struct
import sys
from collections import Counter, defaultdict
from datetime import UTC, datetime
from itertools import pairwise
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from m3.packets import iter_pcap
from m3.sflow import decode_datagram

FOCUS_RUNS = (
    "50a9cfabd3c948409ba967f444f3081b",  # baseline N1 seed43, low F1
    "ef6b6262c44e4f88aeb14797f1607467",  # baseline N1 seed42, reference
    "4580fd2c59ef4fc0ac76377793004752",  # drift N1 seed44, low F1
    "7314798c3ae5416ca0d8032764b318f3",  # drift N1 seed42, low F1
    "4a96a47739da454ab97f558e6601ba77",  # drift N1 seed43, reference
    "92011ddcf7514e47a341679170bcc388",  # drift N2 seed43, low F1
    "31950a7004b54cc8a31b873e58314aef",  # drift N2 seed44, reference
)


def fingerprint(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return {"path": str(path.resolve()), "sha256": digest.hexdigest(),
            "size_bytes": path.stat().st_size}


def distribution(values):
    values = sorted(values)
    if not values:
        return {"n": 0, "min": None, "p50": None, "p95": None, "max": None}
    return {"n": len(values), "min": values[0],
            "p50": values[min(len(values) - 1, math.floor(len(values) * 0.5))],
            "p95": values[min(len(values) - 1, math.floor(len(values) * 0.95))],
            "max": values[-1]}


def read_datagrams(path):
    with path.open("rb") as stream:
        while header := stream.read(12):
            if len(header) != 12:
                raise ValueError(f"Truncated datagram header: {path}")
            epoch, size = struct.unpack("!dI", header)
            payload = stream.read(size)
            if not math.isfinite(epoch) or len(payload) != size:
                raise ValueError(f"Invalid datagram timestamp or truncated payload: {path}")
            packets, metadata = decode_datagram(payload, epoch, include_headers=True)
            yield epoch, packets, metadata


def audit_run(run_id, study_root, execution_path):
    run = study_root / "runs" / run_id
    evidence = execution_path.parent
    paths = {"summary": run / "run_summary.json", "features": run / "features.jsonl",
             "datagrams": run / "sflow.datagrams", "execution": execution_path,
             "rx": evidence / "rx.pcap", "oracle_health": evidence / "truth/health.json"}
    summary = json.loads(paths["summary"].read_text())
    execution = json.loads(execution_path.read_text())
    rows = [json.loads(line) for line in paths["features"].read_text().splitlines()]
    scored = [row for row in rows if row["phase"] == "evaluation"]
    warmup = [row for row in rows if row["phase"] == "warmup"]
    origin, duration = execution["origin_epoch"], summary["config"]["duration_seconds"]
    width = summary["config"]["window_seconds"]
    rx = list(iter_pcap(paths["rx"]))
    # Build one hash index per observed capture-header length. Each prefix lookup
    # is constant-time; repeated prefixes remain explicitly ambiguous.
    events = list(read_datagrams(paths["datagrams"]))
    prefix_indexes = defaultdict(dict)
    for _, _, metadata in events:
        for header in metadata["headers"]:
            if header["protocol"] == 1:
                prefix_indexes[len(header["raw"])][header["raw"]] = []
    for length, prefixes in prefix_indexes.items():
        for number, (_, frame) in enumerate(rx):
            prefix = frame[:length]
            if len(frame) >= length and prefix in prefixes:
                prefixes[prefix].append(number)
    sample_counts, bins = Counter(), Counter()
    delays, used_delays, bin_offsets = [], [], []
    datagrams, batch_sizes, sequences, uptimes, receipt_epochs = 0, [], [], [], []
    unmatched = ambiguous = non_ethernet = raw_samples = past_end = before_origin = 0
    wrong_bin = used_wrong_bin = used_matches = 0
    for epoch, packets, metadata in events:
        datagrams += 1
        batch_sizes.append(len(packets))
        sequences.append(metadata["sequence"])
        uptimes.append(metadata["uptime"])
        receipt_epochs.append(epoch)
        raw_samples += len(packets)
        used = origin <= epoch < origin + duration
        if used:
            bins[math.floor((epoch - origin) / width)] += len(packets)
        past_end += len(packets) if epoch >= origin + duration else 0
        before_origin += len(packets) if epoch < origin else 0
        for header in metadata["headers"]:
            if header["protocol"] != 1:
                non_ethernet += 1
                continue
            raw = header["raw"]
            length = len(raw)
            candidates = prefix_indexes[length].get(raw, [])
            if not candidates:
                unmatched += 1
                continue
            if len(candidates) != 1:
                ambiguous += 1
                continue
            number = candidates[0]
            sample_counts[number] += 1
            delay = epoch - rx[number][0]
            delays.append(delay)
            offset = math.floor((epoch - origin) / width) - math.floor((rx[number][0] - origin) / width)
            bin_offsets.append(offset)
            wrong_bin += offset != 0
            if used:
                used_delays.append(delay)
                used_matches += 1
                used_wrong_bin += offset != 0
    missing = [number for number in range(len(rx)) if number not in sample_counts]
    missing_epochs = sorted(rx[number][0] - origin for number in missing)
    rx_distinct = {frame for _, frame in rx}
    covered_distinct = {rx[number][1] for number in sample_counts}
    stages = [{"index": index, "family": stage["attack_family"],
               "scheduled_start": stage["start"], "requested_pps": stage["pps"],
               "actual_start": stage["actual_start_epoch"] - origin,
               "actual_end": stage["actual_end_epoch"] - origin,
               "wall_duration_ratio": (stage["actual_end_epoch"] - stage["actual_start_epoch"])
                                      / stage["duration"],
               "start_lateness_seconds": stage["actual_start_epoch"] - origin - stage["start"]}
              for index, stage in enumerate(execution["stages"])]
    offsets = [epoch - uptime / 1000 for epoch, uptime in zip(receipt_epochs, uptimes, strict=True)]
    minimum_offset = min(offsets) if offsets else None
    excess = [offset - minimum_offset for offset in offsets]
    uptime_steps = [b - a for a, b in pairwise(uptimes) if b > a]
    return {
        "run_id": run_id, "scenario": summary["scenario"], "sampling_rate": summary["sampling_rate"],
        "seed": summary["seed"], "saved_f1": summary["metrics"]["f1"],
        "source": summary["source"], "status": summary["status"],
        "accepted": summary.get("validation", {}).get("accepted"),
        "settings": {"origin_epoch": origin, "duration_seconds": duration, "window_seconds": width,
                     "warmup_seconds": summary["config"]["warmup_seconds"],
                     "telemetry_clock": summary["config"].get("telemetry_clock", "userspace"),
                     "naive_bayes": summary["config"].get("naive_bayes", "river")},
        "inputs": {name: fingerprint(path) for name, path in paths.items()},
        "saved_counts": summary["counts"],
        "windows": {"total": len(rows), "scored": len(scored),
                    "scored_empty": sum(row["sampled_packets"] == 0 for row in scored),
                    "wrong": sum(row["y_true"] != row["y_pred"] for row in scored),
                    "wrong_empty": sum(row["y_true"] != row["y_pred"] and row["sampled_packets"] == 0
                                       for row in scored),
                    "warmup_sample_pps": distribution([row["features"]["packets_per_second"] for row in warmup]),
                    "evaluation_sample_pps": distribution([row["features"]["packets_per_second"] for row in scored]),
                    "prediction_completion_lag_seconds": distribution(
                        [row["observed_time"] - row["window_end"] for row in rows]),
                    "feature_bins_disagreeing_with_raw_receive_time": sum(
                        row["sampled_packets"] != bins[row["index"]] for row in rows)},
        "observation": {"raw_samples": raw_samples, "datagrams": datagrams,
                        "samples_before_origin": before_origin, "samples_read_at_or_after_fixed_end": past_end,
                        "samples_per_datagram": distribution(batch_sizes),
                        "datagram_gap_seconds": distribution(
                            [b - a for a, b in pairwise(receipt_epochs)]),
                        "sequence_gaps": sum((b - a) % 2**32 != 1 for a, b in pairwise(sequences)),
                        "first_sequence": sequences[0] if sequences else None,
                        "last_sequence": sequences[-1] if sequences else None},
        "rx_prefix_diagnosis": {
            "unambiguous_sample_matches": len(delays), "unmatched_samples": unmatched,
            "ambiguous_samples": ambiguous, "unsupported_non_ethernet_samples": non_ethernet,
            "indexed_header_lengths": sorted(prefix_indexes),
            "rx_packets": len(rx), "rx_distinct_frames": len(rx_distinct),
            "covered_distinct_rx_frames": len(covered_distinct),
            "missing_distinct_rx_frames": len(rx_distinct - covered_distinct),
            "missing_rx_occurrences": len(missing),
            "missing_rx_relative_time_min": missing_epochs[0] if missing_epochs else None,
            "missing_rx_relative_time_max": missing_epochs[-1] if missing_epochs else None,
            "additional_duplicate_samples": sum(count - 1 for count in sample_counts.values()),
            "coverage_unambiguous": ambiguous == 0,
            "all_sample_delays_seconds": distribution(delays),
            "used_sample_delays_seconds": distribution(used_delays),
            "samples_delayed_over_half_second": sum(delay > 0.5 for delay in delays),
            "wrong_bin_samples": wrong_bin,
            "wrong_bin_fraction": wrong_bin / len(delays) if delays else None,
            "used_wrong_bin_samples": used_wrong_bin,
            "used_wrong_bin_fraction": used_wrong_bin / used_matches if used_matches else None,
            "receive_minus_rx_bin_offset": distribution(bin_offsets)},
        "exporter_clock_diagnosis": {
            "observed_uptime_step_gcd_ms": math.gcd(*uptime_steps) if uptime_steps else None,
            "uptime_remainders_mod_1000_ms": sorted({uptime % 1000 for uptime in uptimes}),
            "uptime_span_seconds": (uptimes[-1] - uptimes[0]) / 1000 if uptimes else None,
            "userspace_receive_span_seconds": receipt_epochs[-1] - receipt_epochs[0] if receipt_epochs else None,
            "receive_minus_uptime_excess_above_run_min_seconds": distribution(excess),
            "interpretation": "Variation after exporter uptime stamping, including uptime quantization; "
                              "does not isolate kernel queue versus loopback scheduling or infer packet event time."},
        "stages": stages,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT / "output/research/log_space_20261028")
    parser.add_argument("--output", type=Path,
                        default=ROOT / "output/experiments/collector_timing_diagnosis_v1/timing_audit.json")
    parser.add_argument("--run-id", action="append", help="Override the seven predeclared focus IDs")
    args = parser.parse_args()
    root, output = args.root.resolve(), args.output.resolve()
    if output.exists():
        raise SystemExit("Audit output already exists; select a fresh --output path")
    if output.is_relative_to(root) or output.is_relative_to(ROOT / "research"):
        raise SystemExit("Place diagnosis output outside captured study and research evidence directories")
    requested = args.run_id or FOCUS_RUNS
    executions = {}
    for path in (root / "matrix").glob("*/execution.json"):
        run_id = json.loads(path.read_text()).get("collector_run_id")
        if run_id in requested:
            if run_id in executions:
                raise ValueError(f"Duplicate execution evidence for {run_id}")
            executions[run_id] = path
    missing = set(requested) - executions.keys()
    if missing:
        raise SystemExit(f"Missing execution evidence for: {sorted(missing)}")
    result = {
        "created_utc": datetime.now(UTC).isoformat(), "study_root": str(root),
        "diagnostic_only": True, "model_replays": 0, "live_trials": 0,
        "method": {
            "purpose": "Reproduce timing/coverage observations without changing saved trials or scores",
            "prefix_matching": "Exact Ethernet captured-header prefix with a length-indexed RX mapping; "
                               "only one-candidate matches contribute delays, bins and coverage",
            "quantiles": "Sorted values at min(n-1,floor(n*p)); no interpolation",
            "window_comparison": "floor((userspace_receive-origin)/width) versus floor((RX-origin)/width)",
            "delay_population": "All decoded raw samples, including samples read after fixed measurement end; "
                                "used-sample results separately restrict raw receive time to measurement interval",
            "missing_coverage": "Unmatched RX occurrences/distinct frames using unambiguous raw prefix matches; "
                                "coverage is inconclusive when ambiguous_samples is nonzero",
            "limitations": "RX pcap timestamps have capture precision and small negative delay jitter can occur. "
                           "This diagnoses observation distortion; it does not prove the exact cause of each model error.",
            "prohibition": "Independent RX timestamps and labels are diagnostic only. Never deploy them as telemetry "
                           "timestamps, reconstruct deployable features from the oracle, or use these results to exclude low scores."},
        "audit_sources": {name: fingerprint(ROOT / name) for name in
                          ("scripts/audit_collector_backlog.py", "src/m3/packets.py", "src/m3/sflow.py")},
        "focus_run_ids": list(requested),
        "trials": [audit_run(run_id, root, executions[run_id]) for run_id in requested],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
        stream.write("\n")
    print(json.dumps({"audit": str(output), "trials": len(result["trials"]), "diagnostic_only": True}))


if __name__ == "__main__":
    main()
