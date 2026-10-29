"""Promote provisional results only after independent physical evidence checks."""

import csv
import json
import math
import re
import struct
from collections import Counter, defaultdict
from pathlib import Path

import dpkt

from m3.live_supervision import truth_payload
from m3.metrics import measurement
from m3.packets import iter_pcap
from m3.provenance import sha256
from m3.research_metrics import physical_detection_metrics, post_drift_recovery
from m3.sflow import decode_datagram
from m3.store import atomic_json


def _finite_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _prefix_coverage(headers, receive_frames):
    """Audit coverage only; independent RX timing/labels never supply features.

    Match longer prefixes first, retaining frame occurrence multiplicities.
    Additional samples of an already covered RX frame are reported separately.
    """
    remaining = Counter(receive_frames)
    groups = defaultdict(Counter)
    for header in headers:
        groups[len(header)][header] += 1
    matched = duplicate = unmatched = 0
    for length, samples in sorted(groups.items(), reverse=True):
        candidates = defaultdict(list)
        for frame in remaining:
            if len(frame) >= length:
                candidates[frame[:length]].append(frame)
        for prefix, count in samples.items():
            frames = candidates.get(prefix, [])
            if not frames:
                unmatched += count
                continue
            for frame in frames:
                covered = min(count, remaining[frame])
                remaining[frame] -= covered
                count -= covered
                matched += covered
                if not count:
                    break
            duplicate += count
    return {"expected_rx_packets": sum(remaining.values()) + matched,
            "matched_rx_packets": matched, "missing_rx_packets": sum(remaining.values()),
            "unmatched_samples": unmatched, "duplicate_samples": duplicate}


def _independent_sflow_capture(evidence, recorded, origin, duration):
    capture, capture_log = evidence / "sflow_rx.pcap", evidence / "sflow_rx.log"
    if not capture.is_file() or not capture_log.is_file():
        raise ValueError("Independent sFlow UDP capture/log missing")
    dropped = re.search(r"(\d+) packets dropped by kernel", capture_log.read_text())
    if not dropped or int(dropped[1]):
        raise ValueError("Independent sFlow capture drop count unavailable or nonzero")
    captured = defaultdict(list)
    try:
        with capture.open("rb") as stream:
            reader = dpkt.pcap.Reader(stream)
            if reader.datalink() != dpkt.pcap.DLT_EN10MB:
                raise ValueError("Independent sFlow capture must contain Ethernet frames")
            for epoch, frame in reader:
                epoch = float(epoch)
                if not math.isfinite(epoch):
                    raise ValueError("Nonfinite independent sFlow capture timestamp")
                packet = dpkt.ethernet.Ethernet(frame).data
                if (isinstance(packet, dpkt.ip.IP) and isinstance(packet.data, dpkt.udp.UDP)
                        and packet.data.dport == 6343 and origin <= epoch < origin + duration):
                    captured[bytes(packet.data.data)].append(epoch)
    except (dpkt.UnpackError, struct.error) as error:
        raise ValueError("Malformed independent sFlow UDP capture") from error
    if set(captured) != set(recorded) or any(
            len(captured[payload]) != len(recorded[payload])
            or any(abs(a - b) > 0.00001 for a, b in
                   zip(sorted(captured[payload]), sorted(recorded[payload]), strict=True))
            for payload in recorded):
        raise ValueError("Independent sFlow capture and raw kernel datagrams disagree")
    return {"datagrams": sum(map(len, captured.values())), "timestamp_tolerance_seconds": 0.00001}


def validate_kernel_ingestion(run_path, evidence, summary, features, origin):
    """Recompute the kernel-clock gates from raw datagrams and receive records."""
    state = summary.get("ingestion", {})
    width = summary["config"]["window_seconds"]
    duration = summary["config"]["duration_seconds"]
    if not (_finite_number(width) and width > 0 and _finite_number(duration) and duration > 0):
        raise ValueError("Invalid telemetry ingestion measurement interval")
    if (not isinstance(state, dict) or state.get("timestamp_source") != "kernel_receive_ns"
            or state.get("receiver_finished") is not True or state.get("drain_complete") is not True
            or any(type(state.get(key)) is not int or state[key] != 0 for key in
                   ("queue_overflows", "kernel_drops", "missing_timestamps"))):
        raise ValueError("Kernel telemetry ingestion incomplete or unhealthy")
    if state.get("lag_limit_seconds") != width:
        raise ValueError("Telemetry ingestion lag limit must equal the feature window")
    log_path = run_path / "ingestion.jsonl"
    if not log_path.is_file():
        raise ValueError("Kernel ingestion timestamp log missing")
    receive_lag = processing_lag = 0.0
    count = 0
    previous = (-math.inf, -math.inf, -math.inf)
    bins, headers, recorded = Counter(), [], defaultdict(list)
    with (run_path / "sflow.datagrams").open("rb") as raw, log_path.open() as log:
        for line in log:
            try:
                event = json.loads(line)
                epochs = tuple(event[key] for key in ("kernel_epoch", "read_epoch", "processed_epoch"))
                size = event["payload_bytes"]
            except (ValueError, KeyError, TypeError) as error:
                raise ValueError("Invalid kernel ingestion timestamp record") from error
            if (not all(_finite_number(epoch) and epoch >= 0 for epoch in epochs)
                    or not epochs[0] <= epochs[1] <= epochs[2]
                    or any(new < old for new, old in zip(epochs, previous))
                    or not isinstance(size, int) or isinstance(size, bool) or size <= 0):
                raise ValueError("Invalid or nonchronological kernel ingestion timestamps")
            header = raw.read(12)
            if len(header) != 12:
                raise ValueError("Kernel ingestion log and raw datagram counts disagree")
            epoch, raw_size = struct.unpack("!dI", header)
            payload = raw.read(raw_size)
            if epoch != epochs[0] or raw_size != size or len(payload) != size:
                raise ValueError("Kernel ingestion timestamps/payload disagree with raw datagrams")
            receive_lag = max(receive_lag, epochs[1] - epochs[0])
            processing_lag = max(processing_lag, epochs[2] - epochs[0])
            if receive_lag > width or processing_lag > width:
                raise ValueError("Telemetry ingestion backlog exceeds one feature window")
            packets, metadata = decode_datagram(payload, epoch, include_headers=True)
            if origin <= epoch < origin + duration:
                recorded[payload].append(epoch)
                if any(packet.sample_rate != summary["sampling_rate"] for packet in packets):
                    raise ValueError("Raw kernel telemetry sampling rate mismatch")
                bins[math.floor((epoch - origin) / width)] += len(packets)
                headers.extend(item["raw"] for item in metadata["headers"])
            previous = epochs
            count += 1
        if raw.read(1):
            raise ValueError("Kernel ingestion timestamp log omits raw datagrams")
    if not count or state.get("datagrams_received") != count:
        raise ValueError("Kernel ingestion datagram count missing or inconsistent")
    for key, actual in (("max_receive_lag_seconds", receive_lag),
                        ("max_processing_lag_seconds", processing_lag)):
        reported = state.get(key)
        if (not _finite_number(reported) or reported < 0 or reported > width
                or not math.isclose(reported, actual, rel_tol=0, abs_tol=1e-9)):
            raise ValueError("Telemetry ingestion lag summary disagrees with timestamp evidence")
    indices = [row["index"] for row in features]
    if indices != list(range(math.ceil(duration / width))):
        raise ValueError("Kernel telemetry feature windows incomplete")
    if any(row.get("sampled_packets") != bins[row["index"]] for row in features):
        raise ValueError("Feature counts disagree with raw kernel timestamp bins")
    coverage = None
    if summary["sampling_rate"] == 1:
        coverage = _prefix_coverage(headers, [frame for _, frame in iter_pcap(evidence / "rx.pcap")])
        if coverage["missing_rx_packets"] or coverage["unmatched_samples"]:
            raise ValueError(f"N=1 telemetry tail incomplete: {coverage}")
    independent_capture = _independent_sflow_capture(evidence, recorded, origin, duration)
    return {"datagrams_verified": count, "max_receive_lag_seconds": receive_lag,
            "max_processing_lag_seconds": processing_lag, "n1_prefix_coverage": coverage,
            "independent_sflow_capture": independent_capture}


def accept_realtime(run_path, evidence, report):
    run_path, evidence = Path(run_path), Path(evidence)
    summary_path = run_path / "run_summary.json"
    summary = json.loads(summary_path.read_text())
    atomic_json(run_path / "provisional_summary.json", summary)
    if summary["status"] != "completed":
        raise ValueError("Collector did not complete")
    if report.get("dataplane_validation", {}).get("status") != "validated":
        raise ValueError("Independent full TX/RX validation missing")
    sampling = summary["sampling_rate"]
    if summary["config"].get("telemetry_clock", "userspace") not in {"userspace", "kernel_receive"}:
        raise ValueError("Unrecognized telemetry clock protocol")
    if report.get("switch_sampling") != {"before": sampling, "after": sampling}:
        raise ValueError("Actual switch sampling evidence missing or mismatched")
    health = json.loads((evidence / "truth/health.json").read_text())
    if any(health[key] for key in ("unknown", "kernel_drops", "late_packets")):
        raise ValueError(f"Independent oracle integrity failed: {health}")
    features = [json.loads(line) for line in (run_path / "features.jsonl").read_text().splitlines()]
    if not features or not all(row["completion_epoch"] <= row["label_read_epoch"]
                               and row["completion_epoch"] >= report["origin_epoch"] + row["window_end"]
                               and row["oracle_created_epoch"] <= row["label_read_epoch"] for row in features):
        raise ValueError("Causal chronology evidence incomplete")
    with (evidence / "truth/packet_events.csv").open() as stream:
        events = list(csv.DictReader(stream))
    window_families = defaultdict(list)
    origin = report["origin_epoch"]
    width = summary["config"]["window_seconds"]
    for event in events:
        window_families[math.floor((float(event["epoch"]) - origin) / width)].append(
            event["attack_family"] or None)
    for row in features:
        expected = truth_payload(window_families[row["index"]], 0, 1)
        if row["y_true"] != expected["label"] or row["ground_truth_packets"] != expected["packets"]:
            raise ValueError("Saved prediction labels/counts disagree with independent packet truth")
    frames = Counter(sha256_frame(frame) for _, frame in iter_pcap(evidence / "rx.pcap"))
    if frames != Counter(row["frame_sha256"] for row in events) or len(events) != health["packets"]:
        raise ValueError("Independent RX capture and teacher frame multiplicities disagree")
    receive_epochs = sorted(epoch for epoch, _ in iter_pcap(evidence / "rx.pcap"))
    teacher_epochs = sorted(float(row["epoch"]) for row in events)
    if any(abs(a - b) > 0.00001 for a, b in zip(receive_epochs, teacher_epochs, strict=True)):
        raise ValueError("Independent kernel RX timestamp evidence disagrees")
    labels = {row["y_true"] for row in features if row["phase"] == "evaluation"}
    if not {0, 1} <= labels:
        raise ValueError("Both classes must have scored support")
    telemetry_validation = {}
    if summary["config"].get("telemetry_clock", "userspace") == "kernel_receive":
        summary["ingestion_validation"] = validate_kernel_ingestion(
            run_path, evidence, summary, features, origin)
        telemetry_validation = {"telemetry_kernel_clock": True,
                                "telemetry_ingestion_timing": True,
                                "telemetry_tail_complete": True,
                                "independent_sflow_capture": True}
    physical = physical_detection_metrics(features, events, report["origin_epoch"], summary["config"]["warmup_seconds"])
    recovery = None
    if summary["scenario"] == "drift":
        boundary = report["stages"][8]["start"]
        recovery = post_drift_recovery(features, boundary)
        physical["post_drift_recovery_seconds"] = recovery["recovery_seconds"]
        physical["recovery"] = recovery
    for key, unit in (("detection_time_seconds", "seconds"), ("packets_to_detect", "original IP packets"),
                      ("post_drift_recovery_seconds", "seconds")):
        summary["metrics"][key] = measurement(physical.get(key), unit,
            "Censored or not applicable; inspect research_metrics for criterion and episodes")
    if (run_path / "openflow.pcap").is_file():
        capture_log = (run_path / "openflow_capture.log").read_text()
        dropped = re.search(r"(\d+) packets dropped by kernel", capture_log)
        if not dropped or int(dropped[1]):
            raise ValueError("OpenFlow cost capture drop count missing or nonzero")
        duration = summary["config"]["duration_seconds"]
        sflow_bytes = 0
        with (run_path / "sflow.datagrams").open("rb") as stream:
            while header := stream.read(12):
                if len(header) != 12:
                    raise ValueError("Truncated raw datagram evidence")
                epoch, size = struct.unpack("!dI", header)
                if len(stream.read(size)) != size:
                    raise ValueError("Truncated raw datagram payload")
                if origin <= epoch < origin + duration:
                    sflow_bytes += size + 28  # IPv4 + UDP, loopback IPv4 collector.
        with (run_path / "openflow.pcap").open("rb") as stream:
            openflow_bytes = sum(len(dpkt.ethernet.Ethernet(frame).data)
                                 for epoch, frame in dpkt.pcap.Reader(stream)
                                 if origin <= float(epoch) < origin + duration)
        summary["metrics"]["sflow_bandwidth_kbit_s"] = measurement(sflow_bytes * 8 / duration / 1000, "kbit/s")
        summary["metrics"]["openflow_bandwidth_kbit_s"] = measurement(openflow_bytes * 8 / duration / 1000, "kbit/s")
        summary["channel_cost_basis"] = "IP-layer bytes: sFlow IPv4+UDP+payload and captured OpenFlow IP packets; no Ethernet/FCS"
    paths = {"features": run_path / "features.jsonl", "predictions": run_path / "predictions.csv",
             "datagrams": run_path / "sflow.datagrams", "packet_events": evidence / "truth/packet_events.csv",
             "rx": evidence / "rx.pcap", "tx": evidence / "tx.pcap",
             "resources": run_path / "resources.csv", "teacher_health": evidence / "truth/health.json"}
    if (run_path / "openflow.pcap").is_file():
        paths["openflow"] = run_path / "openflow.pcap"
        paths["openflow_capture_log"] = run_path / "openflow_capture.log"
    if (evidence / "truth/truth_windows.zip").is_file():
        paths["oracle_windows"] = evidence / "truth/truth_windows.zip"
    if telemetry_validation:
        paths["ingestion"] = run_path / "ingestion.jsonl"
        paths["sflow_rx"] = evidence / "sflow_rx.pcap"
        paths["sflow_rx_log"] = evidence / "sflow_rx.log"
    summary.update(source="official_realtime_verified", research_metrics=physical,
                   implementation_sha256=report.get("implementation_sha256"),
                   environment=report.get("environment"),
                   artifacts={key: str(path) for key, path in paths.items()},
                   raw_hashes={key: sha256(path) for key, path in paths.items()},
                   validation={"accepted": True, "actual_switch_config_verified": True,
                               "independent_tx_rx_match": True, "zero_capture_drops": True,
                               "raw_hashes_verified": True, "chronological_prediction_before_label": True,
                               "both_classes_scored": True, **telemetry_validation},
                   research={"ablations_completed": False, "sensitivity_completed": False,
                             "study_role": report.get("research", {}).get("study_role", "primary")})
    atomic_json(summary_path, summary)


def sha256_frame(frame):
    import hashlib

    return hashlib.sha256(frame).hexdigest()
