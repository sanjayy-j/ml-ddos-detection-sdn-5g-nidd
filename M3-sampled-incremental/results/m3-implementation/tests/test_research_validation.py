"""Synthetic physical evidence exercises promotion gates, never research claims."""

import csv
import importlib.util
import json
from pathlib import Path

import dpkt
import pytest

SPEC = importlib.util.spec_from_file_location("research_validation_test",
    Path(__file__).parents[1] / "sdn/research_validation.py")
validation = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validation)


@pytest.fixture
def evidence(tmp_path):
    run, lab = tmp_path / "run", tmp_path / "lab"
    run.mkdir()
    (lab / "truth").mkdir(parents=True)
    frames = [b"a" * 60, b"b" * 60]
    for name in ("tx", "rx"):
        with (lab / f"{name}.pcap").open("wb") as stream:
            writer = dpkt.pcap.Writer(stream)
            for number, frame in enumerate(frames):
                writer.writepkt(frame, 100.05 + number * 0.1)
    rows, packets = [], []
    for index, frame in enumerate(frames):
        rows.append({"index": index, "y_true": index, "y_pred": index,
            "phase": "evaluation", "window_start": index * 0.1,
            "window_end": (index + 1) * 0.1, "completion_epoch": 100.7 + index * 0.1,
            "observed_time": 0.7 + index * 0.1, "label_read_epoch": 100.71 + index * 0.1,
            "oracle_created_epoch": 100.3 + index * 0.1, "ground_truth_packets": 1})
        packets.append({"epoch": 100.05 + index * 0.1, "label": index,
            "attack_family": "Benign" if index == 0 else "SYNFlood",
            "frame_sha256": validation.sha256_frame(frame)})
    (run / "features.jsonl").write_text("\n".join(json.dumps(r) for r in rows))
    for path, data in ((run / "predictions.csv", rows), (lab / "truth/packet_events.csv", packets)):
        with path.open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(data[0]))
            writer.writeheader()
            writer.writerows(data)
    (lab / "truth/health.json").write_text(json.dumps({"packets": 2, "unknown": 0,
        "kernel_drops": 0, "late_packets": 0}))
    (run / "resources.csv").write_text("time,cpu_percent\n1,1\n")
    (run / "sflow.datagrams").write_bytes(b"fixture")
    cost = {"value": 1, "unit": "kbit/s", "status": "measured", "reason": None}
    (run / "run_summary.json").write_text(json.dumps({"status": "completed",
        "scenario": "baseline", "sampling_rate": 1, "config": {"warmup_seconds": 0,
        "window_seconds": 0.1}, "metrics": {"telemetry_bandwidth_kbps": cost,
        "openflow_bandwidth_kbps": cost}}))
    report = {"origin_epoch": 100, "sampling_rate": 1, "switch_sampling": {"before": 1, "after": 1},
              "dataplane_validation": {"status": "validated"}}
    return run, lab, report


def test_provisional_promotion_requires_independent_truth(evidence):
    run, lab, report = evidence
    validation.accept_realtime(run, lab, report)
    result = json.loads((run / "run_summary.json").read_text())
    assert result["source"] == "official_realtime_verified"
    assert result["validation"]["accepted"]
    assert result["metrics"]["packets_to_detect"]["unit"] == "original IP packets"
    assert result["raw_hashes"]


def test_changed_label_cannot_be_promoted(evidence):
    run, lab, report = evidence
    rows = [json.loads(line) for line in (run / "features.jsonl").read_text().splitlines()]
    rows[0]["y_true"] = 1
    rows[1]["y_true"] = 0
    (run / "features.jsonl").write_text("\n".join(json.dumps(r) for r in rows))
    with pytest.raises(ValueError, match="truth"):
        validation.accept_realtime(run, lab, report)


def test_capture_gate_is_not_a_self_asserted_boolean(evidence):
    run, lab, report = evidence
    report["dataplane_validation"]["status"] = "failed"
    with pytest.raises(ValueError, match="TX/RX"):
        validation.accept_realtime(run, lab, report)
