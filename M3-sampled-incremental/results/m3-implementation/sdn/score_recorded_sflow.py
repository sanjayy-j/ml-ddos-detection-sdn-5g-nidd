"""Post-hoc predict-before-learn scoring of independently validated live exports.

This is NOT real-time attack accuracy or a substitute for the final live study.
"""

import argparse
import json
import math
import struct
from collections import defaultdict
from dataclasses import replace
from pathlib import Path

from run_official_capture_pilot import ROOT, block_path, validate_dataplane

from m3.config import RunConfig
from m3.engine import Evaluation
from m3.metrics import measurement
from m3.packets import WindowAccumulator, iter_pcap
from m3.provenance import sha256, verify_input
from m3.sflow import decode_datagram
from m3.store import RunWriter


def header_family(raw, index):
    """Return a class only when all compatible prepared headers agree."""
    families = set()
    for frame, family in index.get(raw[:42], ()):
        prefix_length = min(len(raw), len(frame))
        if raw[:prefix_length] == frame[:prefix_length] and (
            len(raw) <= len(frame) or (len(raw) <= 60 and not any(raw[len(frame) :]))
        ):
            families.add(family)
    return next(iter(families)) if len(families) == 1 else None


def datagrams(path):
    with Path(path).open("rb") as source:
        while prefix := source.read(12):
            if len(prefix) != 12:
                raise ValueError("Truncated recorded datagram prefix")
            timestamp, length = struct.unpack("!dI", prefix)
            if not math.isfinite(timestamp) or not 1 <= length <= 65535:
                raise ValueError("Invalid recorded datagram bounds")
            payload = source.read(length)
            if len(payload) != length:
                raise ValueError("Truncated recorded datagram body")
            yield timestamp, payload


def score(
    execution_path, manifest="data/manifest.json", warmup_seconds=24, output_root="output/runs"
):
    execution_path = Path(execution_path).resolve()
    execution = json.loads(execution_path.read_text())
    if execution["status"] != "validated_collection":
        raise ValueError("Only independently validated collections can be scored")
    blocks_path = Path(execution["blocks_provenance"]["path"])
    provenance = verify_input(blocks_path, manifest)
    if provenance.get("fixture"):
        raise ValueError("Synthetic fixture cannot become official experiment evidence")
    blocks = json.loads(blocks_path.read_text())["blocks"]
    index = defaultdict(list)
    for block in blocks:
        verify_input(block_path(block, blocks_path.parent), manifest)
        for _, frame in iter_pcap(block_path(block, blocks_path.parent)):
            index[frame[:42]].append((frame, block["attack_family"]))
    folder = execution_path.parent
    validation = validate_dataplane(
        blocks,
        blocks_path.parent,
        folder / "tx.pcap",
        folder / "rx.pcap",
        execution["origin_epoch"],
    )
    if validation["status"] != "validated":
        raise ValueError("Independent TX/RX revalidation failed")
    collection_id = execution["collector_run_id"]
    if len(collection_id) != 32 or any(c not in "0123456789abcdef" for c in collection_id):
        raise ValueError("Invalid collection run ID")
    collection_dir = ROOT / "output/runs" / collection_id
    collection = json.loads((collection_dir / "run_summary.json").read_text())
    health = collection.get("telemetry_health", {})
    if collection["status"] != "completed" or any(
        health.get(key, 0)
        for key in ("malformed_datagrams", "sampling_mismatches", "agent_reported_drops")
    ):
        raise ValueError("Collection telemetry health does not permit scoring")
    config = RunConfig(
        mode="live_sflow",
        input_path=str(blocks_path),
        manifest_path=str(manifest),
        output_root=str(output_root),
        sampling_rate=execution["sampling_rate"],
        seed=42,
        scenario="baseline",
        start_epoch=execution["origin_epoch"],
        duration_seconds=execution["duration_seconds"],
        window_seconds=1,
        warmup_seconds=warmup_seconds,
    )
    writer = RunWriter(config, "official_5g_nidd_recorded_sflow", provenance)
    evaluator = Evaluation(config, writer)
    writer.summary.update(
        evaluation_timing="post_hoc_recorded_live_exports",
        collection_run_id=collection_id,
        evidence={
            "execution_sha256": sha256(execution_path),
            "raw_datagrams_sha256": sha256(collection_dir / "sflow.datagrams"),
            "tx_sha256": validation["captures"]["tx"]["sha256"],
            "rx_sha256": validation["captures"]["rx"]["sha256"],
        },
        live_collection_metrics=collection["metrics"],
        notes=[
            "Genuine switch sampling and independently matched TX/RX packets; model evaluated after collection, not real-time inference",
            "Only nonempty, pure-class receive windows with compatible sampled headers are scored; transition/mixed/unknown windows remain unlabelled",
            "Packet-event-time detection delay and post-drift recovery are not established",
            "Controller and channel costs belong to live collection; classifier latency belongs to post-hoc scoring",
        ],
    )
    accumulator = WindowAccumulator(1)
    sample_families = defaultdict(set)
    error = None
    agent = None
    last_sequence = None
    previous_time = float("-inf")

    def observe(item):
        record, count = item
        families = validation["receive_windows"].get(str(record.index), {})
        family = next(iter(families)) if len(families) == 1 and "unknown" not in families else None
        observed = sample_families.pop(record.index, set())
        if family is None or any(value != family for value in observed):
            label, family = None, "unknown"
        else:
            label = int(family != "Benign")
        evaluator.observe(
            replace(record, label=label, attack_family=family),
            record.time < warmup_seconds,
            count,
            observed_time=record.time + 1,
            ground_truth_packets=sum(families.values()) if label is not None else None,
        )

    try:
        for timestamp, payload in datagrams(collection_dir / "sflow.datagrams"):
            if timestamp < previous_time:
                raise ValueError("Recorded arrival timestamps moved backwards")
            previous_time = timestamp
            packets, meta = decode_datagram(payload, timestamp, include_headers=True)
            identity = (meta["agent"], meta["subagent"])
            if agent is not None and (
                identity != agent or meta["sequence"] != (last_sequence + 1) % 2**32
            ):
                raise ValueError("Agent changed or a datagram sequence gap/reordering occurred")
            agent, last_sequence = identity, meta["sequence"]
            if meta["drops"]:
                raise ValueError("Exporter reports lost samples")
            for packet, header in zip(packets, meta["headers"], strict=True):
                relative = timestamp - config.start_epoch
                if not 0 <= relative < config.duration_seconds:
                    continue
                if packet.sample_rate != config.sampling_rate:
                    raise ValueError("Actual switch sampling differs from configuration")
                writer.summary["counts"]["input"] += 1
                writer.summary["counts"]["sampled"] += 1
                for item in accumulator.advance(relative):
                    observe(item)
                sample_families[math.floor(relative)].add(
                    header_family(header["raw"], index) if header["protocol"] == 1 else None
                )
                for item in accumulator.add(packet, config.start_epoch):
                    observe(item)
        for item in accumulator.advance(config.duration_seconds):
            observe(item)
        if not writer.summary["counts"]["evaluated"]:
            raise ValueError("No independently labelled evaluation windows")
    except Exception as exception:  # noqa: BLE001 - preserve third-party scoring failures
        error = exception
    metrics = evaluator.summary()
    for name in ("detection_time_seconds", "packets_to_detect", "post_drift_recovery_seconds"):
        metrics[name] = measurement(
            None,
            "seconds" if name != "packets_to_detect" else "packets",
            "Post-hoc collection pilot does not establish real-time detection timeliness",
        )
    writer.finish(metrics, error)
    if error:
        raise RuntimeError(
            f"Recorded-export scoring failed; evidence retained at {writer.path}: {error}"
        ) from error
    return writer.summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execution", required=True)
    parser.add_argument("--manifest", default="data/manifest.json")
    parser.add_argument("--warmup-seconds", type=float, default=24)
    parser.add_argument("--output-root", default="output/runs")
    args = parser.parse_args()
    result = score(args.execution, args.manifest, args.warmup_seconds, args.output_root)
    print(
        json.dumps(
            {
                "run_id": result["run_id"],
                "status": result["status"],
                "counts": result["counts"],
                "f1": result["metrics"]["f1"],
                "evaluation_timing": result["evaluation_timing"],
            }
        )
    )
