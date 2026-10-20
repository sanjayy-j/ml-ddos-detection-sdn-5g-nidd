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
from m3.store import atomic_json


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
    summary.update(source="official_realtime_verified", research_metrics=physical,
                   artifacts={key: str(path) for key, path in paths.items()},
                   raw_hashes={key: sha256(path) for key, path in paths.items()},
                   validation={"accepted": True, "actual_switch_config_verified": True,
                               "independent_tx_rx_match": True, "zero_capture_drops": True,
                               "raw_hashes_verified": True, "chronological_prediction_before_label": True,
                               "both_classes_scored": True},
                   research={"ablations_completed": False, "sensitivity_completed": False,
                             "study_role": report.get("research", {}).get("study_role", "primary")})
    atomic_json(summary_path, summary)


def sha256_frame(frame):
    import hashlib

    return hashlib.sha256(frame).hexdigest()
