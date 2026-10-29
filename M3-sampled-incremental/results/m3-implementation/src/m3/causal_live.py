"""Real-time sampled-window prediction with independently revealed RX labels."""

import json
import math
import socket
import struct
import time
from collections import deque
from dataclasses import replace
from pathlib import Path

from m3.engine import Evaluation
from m3.ingestion import KernelDatagramReceiver
from m3.live_supervision import reveal_truth
from m3.packets import WindowAccumulator
from m3.provenance import verify_input
from m3.resources import ResourceMonitor
from m3.sflow import DecodeError, decode_datagram
from m3.store import RunWriter


def run_causal(config, truth_directory):
    if config.mode != "live_sflow" or config.start_epoch is None:
        raise ValueError("Causal collector requires live mode and explicit physical origin")
    if config.telemetry_clock != "kernel_receive":
        raise ValueError("Legacy userspace-clock reproduction requires its pinned code revision")
    provenance = verify_input(config.input_path, config.manifest_path)
    writer = RunWriter(config, "provisional_realtime", provenance)
    evaluator, accumulator = Evaluation(config, writer), WindowAccumulator(config.window_seconds)
    resources = ResourceMonitor(writer, config.controller_pid)
    resources.measurement_epoch = config.start_epoch
    resources.measurement_duration = config.duration_seconds
    truth_directory = Path(truth_directory)
    start, pending = config.start_epoch, deque()
    health = {"malformed_datagrams": 0, "sampling_mismatches": 0,
              "agent_reported_drops": 0, "sequence_gaps": 0, "late_windows": 0}
    previous = None
    receiver = None
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 4 * 1024 * 1024)
    error = None
    try:
        sock.bind((config.bind, config.port))
        receiver = KernelDatagramReceiver(
            sock, start + config.duration_seconds + config.label_delay_seconds + 0.3,
            lag_limit_seconds=config.window_seconds)
        resources.start()
        receiver.start()
        print(f"Collector ready on {config.bind}:{config.port}; run={writer.run_id}", flush=True)
        with (writer.path / "sflow.datagrams").open("wb") as raw, \
                (writer.path / "features.jsonl").open("w") as features, \
                (writer.path / "ingestion.jsonl").open("w") as ingestion:
            def observe_ready():
                while pending and time.time() >= start + pending[0][0].time + config.window_seconds + config.label_delay_seconds:
                    record, count = pending.popleft()
                    # Neither the label file nor packet oracle is accessed before predict.
                    prediction = evaluator.detector.predict(record.features)
                    completion = time.time()
                    path = truth_directory / f"{record.index}.json"
                    if not path.is_file():
                        raise RuntimeError(f"Independent truth window {record.index} unavailable")
                    revealed = time.time()
                    truth = reveal_truth(path, prediction_epoch=completion, read_epoch=revealed)
                    warmup = record.time < config.warmup_seconds
                    record = replace(record, label=truth["label"], attack_family=truth["attack_family"])
                    evaluator.observe(record, warmup, count, completion - start, truth["packets"], prediction=prediction)
                    features.write(json.dumps({"index": record.index, "time": record.time,
                        "window_start": record.time, "window_end": record.time + config.window_seconds,
                        "features": record.features, "y_true": record.label, "y_pred": prediction[0],
                        "score": prediction[1], "attack_family": record.attack_family,
                        "phase": "unlabeled" if record.label is None else "warmup" if warmup else "evaluation",
                        "warmup": warmup, "sampled_packets": count, "ground_truth_packets": truth["packets"],
                        "completion_epoch": completion, "observed_time": completion - start,
                        "label_read_epoch": revealed, "label_available_time": revealed - start,
                        "oracle_created_epoch": truth["available_epoch"]}) + "\n")

            for event in receiver.events():
                if event.payload is None:
                    elapsed = min(max(0, event.kernel_epoch - start), config.duration_seconds)
                    pending.extend(accumulator.advance(elapsed))
                    observe_ready()
                    continue
                received, payload = event.kernel_epoch, event.payload
                processed = time.time()
                receiver.processed(event, processed)
                raw.write(struct.pack("!dI", received, len(payload)))
                raw.write(payload)
                ingestion.write(json.dumps({"kernel_epoch": received, "read_epoch": event.read_epoch,
                                            "processed_epoch": processed,
                                            "payload_bytes": len(payload)}) + "\n")
                if received < start:
                    continue
                if received < start + config.duration_seconds:
                    resources.telemetry_bytes += len(payload)
                try:
                    packets, meta = decode_datagram(payload, received)
                except DecodeError:
                    health["malformed_datagrams"] += 1
                    continue
                if previous is not None and (meta["sequence"] - previous) % 2**32 != 1:
                    health["sequence_gaps"] += 1
                previous = meta["sequence"]
                health["agent_reported_drops"] = max(health["agent_reported_drops"], meta["drops"])
                for packet in packets:
                    writer.summary["counts"]["input"] += 1
                    if packet.sample_rate != config.sampling_rate:
                        health["sampling_mismatches"] += 1
                        continue
                    if packet.time - start >= config.duration_seconds:
                        continue
                    if (accumulator.index is not None
                            and math.floor((packet.time - start) / config.window_seconds) < accumulator.index):
                        health["late_windows"] += 1
                        raise RuntimeError("Telemetry arrived behind a closed kernel-time window")
                    writer.summary["counts"]["sampled"] += 1
                    pending.extend(accumulator.add(packet, start))
                observe_ready()
            pending.extend(accumulator.advance(config.duration_seconds))
            observe_ready()
            receiver.validate()
            if pending or any(health.values()) or not writer.summary["counts"]["sampled"]:
                raise RuntimeError(f"Causal collection integrity gate failed: {health}; pending={len(pending)}")
    except BaseException as exc:  # noqa: BLE001
        error = exc
    finally:
        if receiver is not None:
            try:
                receiver.stop()
            except RuntimeError as exc:
                error = error or exc
            writer.summary["ingestion"] = dict(receiver.stats)
        sock.close()
        cost = resources.finish(live=True) if resources.thread.is_alive() else {}
        writer.summary.update(telemetry_health=health, origin_epoch=start,
                              evaluation_timing="realtime_predict_then_independent_oracle_reveal",
                              validation={"accepted": False})
        writer.finish({**evaluator.summary(), **cost}, error)
    if error:
        raise RuntimeError(f"Causal run {writer.run_id} failed; evidence preserved: {error}") from error
    return writer.summary


if __name__ == "__main__":
    import argparse

    from m3.config import RunConfig

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument("--truth", required=True)
    args = parser.parse_args()
    run_causal(RunConfig.load(args.config), args.truth)
