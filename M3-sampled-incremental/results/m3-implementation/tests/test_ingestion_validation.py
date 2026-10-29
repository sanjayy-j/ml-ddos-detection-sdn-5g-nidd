"""Offline evidence checks for kernel-timestamped telemetry acceptance."""

import csv
import importlib.util
import json
import struct
from pathlib import Path

import dpkt
import pytest

from m3.analysis import comparison_key
from m3.research_metrics import (
    RATES,
    SCENARIOS,
    VALIDATION_GATES,
    comparison_signature,
    research_readiness,
)

SPEC = importlib.util.spec_from_file_location(
    "ingestion_validation_test", Path(__file__).parents[1] / "sdn/research_validation.py")
validation = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validation)


def _integers(*values):
    return struct.pack("!" + "I" * len(values), *values)


def _record(tag, body):
    return _integers(tag, len(body)) + body + bytes((-len(body)) % 4)


def _datagram(frame, sequence, rate=1):
    header = _integers(1, len(frame) + 4, 4, len(frame)) + frame
    sample = _integers(sequence, 1, rate, sequence, 0, 1, 2, 1) + _record(1, header)
    return (_integers(5, 1) + b"\x7f\x00\x00\x01"
            + _integers(1, sequence, 1000, 1) + _record(1, sample))


def _save(run, summary, events, payloads):
    (run / "run_summary.json").write_text(json.dumps(summary))
    (run / "ingestion.jsonl").write_text("\n".join(json.dumps(row) for row in events))
    with (run / "sflow.datagrams").open("wb") as raw:
        for event, payload in zip(events, payloads, strict=True):
            raw.write(struct.pack("!dI", event["kernel_epoch"], len(payload)))
            raw.write(payload)


def _save_sflow_capture(lab, events, payloads):
    with (lab / "sflow_rx.pcap").open("wb") as stream:
        writer = dpkt.pcap.Writer(stream)
        for event, payload in zip(events, payloads, strict=True):
            udp = dpkt.udp.UDP(sport=45000, dport=6343, data=payload)
            udp.ulen = len(udp)
            ip = dpkt.ip.IP(src=b"\x7f\x00\x00\x01", dst=b"\x7f\x00\x00\x01",
                            p=17, data=udp)
            ip.len = len(ip)
            ethernet = dpkt.ethernet.Ethernet(
                src=b"\x00" * 6, dst=b"\x00" * 6, type=0x800, data=ip)
            writer.writepkt(bytes(ethernet), event["kernel_epoch"])
    (lab / "sflow_rx.log").write_text("0 packets dropped by kernel\n")


@pytest.fixture
def kernel_evidence(tmp_path):
    run, lab = tmp_path / "run", tmp_path / "lab"
    run.mkdir()
    (lab / "truth").mkdir(parents=True)
    frames = []
    for index in range(2):
        udp = dpkt.udp.UDP(sport=100 + index, dport=200, data=b"fixture")
        udp.ulen = len(udp)
        ip = dpkt.ip.IP(src=b"\x0a\x00\x00\x01", dst=b"\x0a\x00\x00\x02",
                        p=17, data=udp)
        ip.len = len(ip)
        frames.append(bytes(dpkt.ethernet.Ethernet(
            src=b"\x00" * 6, dst=b"\x01" * 6, type=0x800, data=ip)))
    for name in ("tx", "rx"):
        with (lab / f"{name}.pcap").open("wb") as stream:
            writer = dpkt.pcap.Writer(stream)
            for index, frame in enumerate(frames):
                writer.writepkt(frame, 100.05 + index * 0.1)
    rows, packets, events, payloads = [], [], [], []
    for index, frame in enumerate(frames):
        rows.append({"index": index, "y_true": index, "y_pred": index,
                     "phase": "evaluation", "window_start": index * 0.1,
                     "window_end": (index + 1) * 0.1,
                     "completion_epoch": 100.7 + index * 0.1,
                     "observed_time": 0.7 + index * 0.1,
                     "label_read_epoch": 100.71 + index * 0.1,
                     "oracle_created_epoch": 100.3 + index * 0.1,
                     "sampled_packets": 1, "ground_truth_packets": 1})
        packets.append({"epoch": 100.05 + index * 0.1, "label": index,
                        "attack_family": "Benign" if index == 0 else "SYNFlood",
                        "frame_sha256": validation.sha256_frame(frame)})
        payload = _datagram(frame, index + 1)
        events.append({"kernel_epoch": 100.05 + index * 0.1,
                       "read_epoch": 100.055 + index * 0.1,
                       "processed_epoch": 100.06 + index * 0.1,
                       "payload_bytes": len(payload)})
        payloads.append(payload)
    (run / "features.jsonl").write_text("\n".join(json.dumps(row) for row in rows))
    for path, data in ((run / "predictions.csv", rows), (lab / "truth/packet_events.csv", packets)):
        with path.open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(data[0]))
            writer.writeheader()
            writer.writerows(data)
    (lab / "truth/health.json").write_text(json.dumps(
        {"packets": 2, "unknown": 0, "kernel_drops": 0, "late_packets": 0}))
    (run / "resources.csv").write_text("time,cpu_percent\n1,1\n")
    summary = {"status": "completed", "scenario": "baseline", "sampling_rate": 1,
               "config": {"warmup_seconds": 0, "window_seconds": 0.1,
                          "duration_seconds": 0.2, "telemetry_clock": "kernel_receive"},
               "metrics": {},
               "ingestion": {"timestamp_source": "kernel_receive_ns", "receiver_finished": True,
                             "drain_complete": True, "queue_overflows": 0, "kernel_drops": 0,
                             "missing_timestamps": 0, "lag_limit_seconds": 0.1,
                             "datagrams_received": 2,
                             "max_receive_lag_seconds": max(e["read_epoch"] - e["kernel_epoch"]
                                                            for e in events),
                             "max_processing_lag_seconds": max(e["processed_epoch"] - e["kernel_epoch"]
                                                               for e in events)}}
    _save(run, summary, events, payloads)
    _save_sflow_capture(lab, events, payloads)
    report = {"origin_epoch": 100, "sampling_rate": 1,
              "switch_sampling": {"before": 1, "after": 1},
              "dataplane_validation": {"status": "validated"}}
    return run, lab, report, summary, rows, events, payloads, frames


def test_kernel_promotion_recomputes_timing_and_tail_and_hashes_log(kernel_evidence):
    run, lab, report, *_ = kernel_evidence
    validation.accept_realtime(run, lab, report)
    result = json.loads((run / "run_summary.json").read_text())
    assert all(result["validation"][key] for key in
               ("telemetry_kernel_clock", "telemetry_ingestion_timing", "telemetry_tail_complete",
                "independent_sflow_capture"))
    assert result["ingestion_validation"]["n1_prefix_coverage"]["matched_rx_packets"] == 2
    assert result["raw_hashes"]["ingestion"] == validation.sha256(run / "ingestion.jsonl")
    assert result["raw_hashes"]["sflow_rx"] == validation.sha256(lab / "sflow_rx.pcap")


@pytest.mark.parametrize("rate", [1, 2])
def test_missing_independent_udp_datagram_rejects_any_sampling_rate(kernel_evidence, rate):
    run, lab, report, summary, _, events, _, frames = kernel_evidence
    summary["sampling_rate"] = rate
    report["switch_sampling"] = {"before": rate, "after": rate}
    payloads = [_datagram(frame, index + 1, rate) for index, frame in enumerate(frames)]
    _save(run, summary, events, payloads)
    _save_sflow_capture(lab, events[:1], payloads[:1])
    with pytest.raises(ValueError, match="Independent sFlow capture"):
        validation.accept_realtime(run, lab, report)


@pytest.mark.parametrize("corruption", ["missing", "drops", "clock"])
def test_independent_sflow_evidence_is_required(kernel_evidence, corruption):
    run, lab, report, _summary, _rows, events, payloads, _frames = kernel_evidence
    if corruption == "missing":
        (lab / "sflow_rx.pcap").unlink()
    elif corruption == "drops":
        (lab / "sflow_rx.log").write_text("1 packets dropped by kernel\n")
    else:
        events[0]["kernel_epoch"] += 0.001
        _save_sflow_capture(lab, events, payloads)
    with pytest.raises(ValueError, match="sFlow"):
        validation.accept_realtime(run, lab, report)


def test_self_asserted_small_lag_cannot_hide_raw_backlog(kernel_evidence):
    run, lab, report, summary, _, events, payloads, _ = kernel_evidence
    events[-1]["processed_epoch"] += 1
    _save(run, summary, events, payloads)
    with pytest.raises(ValueError, match="backlog"):
        validation.accept_realtime(run, lab, report)


def test_n1_unread_tail_is_rejected_even_with_contiguous_received_datagrams(kernel_evidence):
    run, lab, report, summary, rows, events, payloads, _ = kernel_evidence
    summary["ingestion"]["datagrams_received"] = 1
    summary["ingestion"]["max_receive_lag_seconds"] = events[0]["read_epoch"] - events[0]["kernel_epoch"]
    summary["ingestion"]["max_processing_lag_seconds"] = events[0]["processed_epoch"] - events[0]["kernel_epoch"]
    rows[-1]["sampled_packets"] = 0
    (run / "features.jsonl").write_text("\n".join(json.dumps(row) for row in rows))
    _save(run, summary, events[:1], payloads[:1])
    with pytest.raises(ValueError, match="tail incomplete"):
        validation.accept_realtime(run, lab, report)


def test_missing_receive_timestamp_log_cannot_claim_kernel_validation(kernel_evidence):
    run, lab, report, *_ = kernel_evidence
    (run / "ingestion.jsonl").unlink()
    with pytest.raises(ValueError, match="timestamp log missing"):
        validation.accept_realtime(run, lab, report)


def test_legacy_promotion_does_not_claim_new_ingestion_gates(kernel_evidence):
    run, lab, report, summary, *_ = kernel_evidence
    summary["config"].pop("telemetry_clock")
    (run / "run_summary.json").write_text(json.dumps(summary))
    (run / "ingestion.jsonl").unlink()
    validation.accept_realtime(run, lab, report)
    result = json.loads((run / "run_summary.json").read_text())
    assert "telemetry_kernel_clock" not in result["validation"]
    assert "ingestion" not in result["raw_hashes"]


@pytest.mark.parametrize("key,value", [
    ("kernel_drops", 1), ("missing_timestamps", 1), ("receiver_finished", False),
    ("drain_complete", False), ("max_receive_lag_seconds", float("nan")),
])
def test_incomplete_or_nonfinite_ingestion_cannot_be_promoted(kernel_evidence, key, value):
    run, lab, report, summary, *_ = kernel_evidence
    summary["ingestion"][key] = value
    (run / "run_summary.json").write_text(json.dumps(summary))
    with pytest.raises(ValueError):
        validation.accept_realtime(run, lab, report)


@pytest.mark.parametrize("corruption", ["raw_timestamp", "missing_log_row", "summary_lag", "feature_bin"])
def test_kernel_evidence_is_cross_checked(kernel_evidence, corruption):
    run, lab, report, summary, rows, events, _payloads, _ = kernel_evidence
    if corruption == "raw_timestamp":
        events[0]["kernel_epoch"] += 0.001
        (run / "ingestion.jsonl").write_text("\n".join(json.dumps(row) for row in events))
    elif corruption == "missing_log_row":
        (run / "ingestion.jsonl").write_text(json.dumps(events[0]))
    elif corruption == "summary_lag":
        summary["ingestion"]["max_processing_lag_seconds"] = 0
        (run / "run_summary.json").write_text(json.dumps(summary))
    else:
        rows[0]["sampled_packets"] = 0
        (run / "features.jsonl").write_text("\n".join(json.dumps(row) for row in rows))
    with pytest.raises(ValueError):
        validation.accept_realtime(run, lab, report)


def test_prefix_coverage_retains_multiplicity_and_reports_extra_samples():
    assert validation._prefix_coverage([b"aaa", b"aaa", b"bbb", b"bbb"],
                                       [b"aaaa", b"aaaa", b"bbbb"]) == {
        "expected_rx_packets": 3, "matched_rx_packets": 3, "missing_rx_packets": 0,
        "unmatched_samples": 0, "duplicate_samples": 1}
    assert validation._prefix_coverage([b"aaa"], [b"aaaa", b"aaaa"])["missing_rx_packets"] == 1


def test_clock_protocols_are_separate_and_absent_clock_is_legacy():
    legacy = {"source": "official_realtime_verified", "mode": "live_sflow", "unit": "window",
              "scenario": "baseline", "config": {"window_seconds": 0.1}}
    explicit = {**legacy, "config": {**legacy["config"], "telemetry_clock": "userspace"}}
    kernel = {**legacy, "config": {**legacy["config"], "telemetry_clock": "kernel_receive"}}
    for signature in (comparison_signature, comparison_key):
        assert signature(legacy) == signature(explicit)
        assert signature(legacy) != signature(kernel)
        assert "telemetry_clock" not in json.loads(signature(legacy))["settings"]
        assert "telemetry_clock" not in json.loads(signature(explicit))["settings"]


def test_kernel_readiness_requires_new_evidence_without_changing_legacy_gates():
    metrics = {key: {"value": 0.3, "status": "measured",
                     "unit": "kbit/s" if "bandwidth" in key else "ratio"}
               for key in ("f1", "recall", "roc_auc", "false_positive_rate", "cpu_percent_mean",
                           "cpu_percent_p95", "controller_cpu_percent_mean", "controller_cpu_percent_p95",
                           "sflow_bandwidth_kbit_s", "openflow_bandwidth_kbit_s", "inference_latency_ms",
                           "inference_latency_p95_ms", "flow_table_entries")}
    runs = [{"source": "official_realtime_verified", "status": "completed", "scenario": scenario,
             "sampling_rate": rate, "config": {"trial_id": trial, "window_seconds": 0.1},
             "validation": {"accepted": True, "both_classes_scored": True,
                            **{gate: True for gate in VALIDATION_GATES}},
             "raw_hashes": {"rx": "a" * 64}, "metrics": metrics,
             "research": {"ablations_completed": True, "sensitivity_completed": True}}
            for scenario in SCENARIOS for rate in RATES for trial in (1, 2, 3)]
    new_gates = {"telemetry_kernel_clock", "telemetry_ingestion_timing",
                 "telemetry_tail_complete", "independent_sflow_capture"}
    legacy = research_readiness(runs)
    assert legacy["ready"]
    assert not (new_gates | {"consistent_telemetry_clock"}) & legacy["evidence_gates"].keys()
    runs[0]["config"]["telemetry_clock"] = "kernel_receive"
    mixed = research_readiness(runs)
    assert not mixed["ready"]
    assert mixed["evidence_gates"]["consistent_telemetry_clock"] is False
    for run in runs:
        run["config"]["telemetry_clock"] = "kernel_receive"
    missing = research_readiness(runs)
    assert not missing["ready"]
    assert missing["evidence_gates"]["consistent_telemetry_clock"] is True
    assert all(missing["evidence_gates"][gate] is False for gate in new_gates)
    for run in runs:
        run["validation"].update({gate: True for gate in new_gates})
    assert research_readiness(runs)["ready"]
    runs[0]["validation"].pop("independent_sflow_capture")
    assert research_readiness(runs)["ready"] is False
