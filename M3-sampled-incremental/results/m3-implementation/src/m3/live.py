import socket
import time
from dataclasses import replace

from m3.engine import Evaluation
from m3.labels import LabelTimeline
from m3.packets import WindowAccumulator
from m3.provenance import verify_input
from m3.resources import ResourceMonitor
from m3.sflow import DecodeError, decode_datagram
from m3.store import RunWriter


def run_live(config):
    if config.mode != "live_sflow":
        raise ValueError("Live collector requires mode=live_sflow")
    provenance = (
        verify_input(config.input_path, config.manifest_path) if config.input_path else None
    )
    labels = LabelTimeline(config.labels_path)
    writer = RunWriter(
        config, "official_5g_nidd" if provenance and labels.verified else "live_sflow", provenance
    )
    evaluator = Evaluation(config, writer)
    resources = ResourceMonitor(writer, config.controller_pid)
    accumulator = WindowAccumulator(config.window_seconds)
    start = config.start_epoch or time.time()
    issues = {"malformed_datagrams": 0, "sampling_mismatches": 0, "agent_reported_drops": 0}
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    error = None
    try:
        sock.bind((config.bind, config.port))
        sock.settimeout(0.2)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 4 * 1024 * 1024)
        resources.start()
        print(f"Collector ready on {config.bind}:{config.port}; run={writer.run_id}", flush=True)

        def observe(item):
            record, count = item
            label, family = labels.label(record.time, record.time + config.window_seconds, start)
            evaluator.observe(
                replace(record, label=label, attack_family=family),
                record.time < config.warmup_seconds,
                count,
                time.time() - start,
            )

        with (writer.path / "sflow.datagrams").open("wb") as raw:
            while time.time() - start < config.duration_seconds:
                now = time.time()
                if now < start:
                    time.sleep(min(0.1, start - now))
                    continue
                for item in accumulator.advance(min(now - start, config.duration_seconds)):
                    observe(item)
                try:
                    payload, _peer = sock.recvfrom(65535)
                except TimeoutError:
                    continue
                received = time.time()
                resources.telemetry_bytes += len(payload)
                # Length-prefixed datagrams preserve raw export evidence without pickle.
                import struct

                raw.write(struct.pack("!dI", received, len(payload)))
                raw.write(payload)
                raw.flush()
                try:
                    packets, metadata = decode_datagram(payload, received)
                except DecodeError:
                    issues["malformed_datagrams"] += 1
                    continue
                issues["agent_reported_drops"] = max(
                    issues["agent_reported_drops"], metadata["drops"]
                )
                for packet in packets:
                    writer.summary["counts"]["input"] += 1
                    if packet.sample_rate != config.sampling_rate:
                        issues["sampling_mismatches"] += 1
                        continue
                    if packet.time - start >= config.duration_seconds:
                        continue
                    writer.summary["counts"]["sampled"] += 1
                    for item in accumulator.add(packet, start):
                        observe(item)
            for item in accumulator.advance(config.duration_seconds):
                observe(item)
            writer.summary["telemetry_health"] = issues
            writer.summary["notes"] = [
                "Input count is received sample headers, not unsampled data-plane packets",
                "Bandwidth measures received sFlow UDP payload, excluding IP/UDP overhead",
                "Ground truth is scored only for fully covered, verified label intervals",
            ]
            if not writer.summary["counts"]["sampled"]:
                raise ValueError("No matching decoded sFlow packet samples received")
            if issues["sampling_mismatches"]:
                raise ValueError("Switch sampling rate changed/mismatched during the run")
    except BaseException as exc:  # noqa: BLE001 - interrupts must close files and mark the run failed
        error = exc
    finally:
        sock.close()
        if resources.thread.is_alive():
            cost = resources.finish(live=True)
        else:
            cost = {}
        writer.summary["telemetry_health"] = issues
        writer.finish({**evaluator.summary(), **cost}, error)
    if error:
        raise RuntimeError(
            f"Live run {writer.run_id} failed; evidence retained: {error}"
        ) from error
    return writer.summary
