import csv
import json
import struct
from dataclasses import replace

import pytest
from fastapi.testclient import TestClient

from m3.analysis import aggregate, pareto
from m3.api import create_app
from m3.config import RunConfig
from m3.data import binary_label, extract_flow_features
from m3.engine import run_replay
from m3.labels import LabelTimeline
from m3.metrics import QualityMetrics, measurement, roc_auc
from m3.model import OnlineDetector
from m3.packets import Packet, WindowAccumulator, parse_header
from m3.provenance import OFFICIAL_DOI, sha256, verify_input
from m3.sflow import DecodeError, decode_datagram
from m3.store import RunRepository


@pytest.mark.parametrize("rate", [1, 2, 5, 10, 20, 50])
def test_valid_config(rate):
    assert RunConfig(input_path="x", sampling_rate=rate).sampling_rate == rate


@pytest.mark.parametrize(
    "kwargs",
    [
        {"sampling_rate": 3},
        {"sampling_rate": True},
        {"threshold": float("nan")},
        {"window_seconds": 0},
        {"max_records": 0},
        {"mode": "bad"},
    ],
)
def test_invalid_config(kwargs):
    with pytest.raises(ValueError):
        RunConfig(input_path="x", **kwargs)


def test_labels_and_leakage():
    assert binary_label("SYNFlood", "Malicious") == 1
    assert binary_label("UDPFlood", "UDPFlood") == 1
    assert binary_label("Benign", "Benign") == 0
    assert binary_label("UDPScan", "Malicious") is None
    with pytest.raises(ValueError):
        binary_label("SYNFlood", "Benign")
    with pytest.raises(ValueError):
        binary_label("SYNTH_UDPFlood", "Malicious")
    row = {
        "Dur": "nan",
        "Proto": "UDP",
        "Label": "Malicious",
        "Attack Tool": "hping",
        "SrcAddr": "10.0.0.1",
        "Seq": "99",
        "Offset": "123",
    }
    features = extract_flow_features(row)
    assert features["missing_Dur"] == 1 and features["Dur"] == 0
    assert features["Proto"] == "udp"
    assert not {"Label", "Attack Tool", "SrcAddr", "Seq", "Offset"} & features.keys()


def test_metrics_missing_zero_and_auc():
    assert measurement(None)["status"] == "unavailable"
    assert measurement(0)["value"] == 0
    assert roc_auc([0, 1], [0.5, 0.5]) == 0.5
    assert roc_auc([0, 1, 0, 1], [0.1, 0.8, 0.2, 0.9]) == 1
    assert roc_auc([1, 1], [0.1, 0.2]) is None
    quality = QualityMetrics()
    for actual, predicted in [(1, 1), (1, 0), (0, 1), (0, 0)]:
        quality.update(actual, predicted, predicted, 1, "SYNFlood")
    metrics = quality.summary(True)
    for name in ("precision", "recall", "f1", "false_positive_rate", "unseen_attack_recall"):
        assert metrics[name]["value"] == 0.5


def test_provenance_rejects_mutation(tmp_path):
    source = tmp_path / "source.csv"
    source.write_text("official bytes", encoding="utf-8")
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "dataset": "5G-NIDD",
                "doi": OFFICIAL_DOI,
                "status": "partial",
                "files": [
                    {
                        "path": str(source),
                        "sha256": sha256(source),
                        "verification_status": "verified",
                    }
                ],
            }
        )
    )
    assert verify_input(source, manifest)["sha256"] == sha256(source)
    source.write_text("changed", encoding="utf-8")
    with pytest.raises(ValueError, match="checksum"):
        verify_input(source, manifest)


def test_window_sampling_and_empty_windows():
    accumulator = WindowAccumulator(1)
    assert list(accumulator.add(Packet(100.1, 80, 6, True, 10), 100)) == []
    windows = list(accumulator.advance(3.1))
    assert len(windows) == 3
    first, count = windows[0]
    assert count == 1 and first.features["packets_per_second"] == 10
    assert first.features["bytes_per_second"] == 800
    assert first.features["syn_fraction"] == 1
    assert windows[1][0].features["empty_window"] == 1
    with pytest.raises(ValueError, match="backwards"):
        list(accumulator.advance(1))


def udp_header():
    ethernet = b"\x00" * 12 + b"\x08\x00"
    ip = bytearray(20)
    ip[0], ip[9] = 0x45, 17
    return ethernet + ip + b"\x00" * 8


def sflow_datagram(rate=10, expanded=False):
    def ints(*values):
        return struct.pack("!" + "I" * len(values), *values)

    def record(tag, body):
        return ints(tag, len(body)) + body + b"\x00" * ((-len(body)) % 4)

    header = udp_header()
    raw = ints(1, len(header), 0, len(header)) + header
    sample = (
        ints(1, 0, 1, rate, 100, 0, 0, 1, 0, 2, 1)
        if expanded
        else ints(1, 0, rate, 100, 0, 1, 2, 1)
    )
    return (
        ints(5, 1)
        + b"\x7f\x00\x00\x01"
        + ints(0, 1, 1000, 1)
        + record(3 if expanded else 1, sample + record(1, raw))
    )


@pytest.mark.parametrize("expanded", [False, True])
def test_sflow_decode_and_truncation(expanded):
    datagram = sflow_datagram(expanded=expanded)
    packets, metadata = decode_datagram(datagram, 100)
    assert len(packets) == 1 and packets[0].sample_rate == 10 and packets[0].protocol == 17
    assert metadata["sequence"] == 1
    for size in range(len(datagram)):
        with pytest.raises((DecodeError, ValueError)):
            decode_datagram(datagram[:size], 100)
    assert parse_header(b"short", 0, 5) is None


def test_label_intervals(tmp_path):
    path = tmp_path / "labels.json"
    data = {
        "verified": True,
        "source": "test fixture only",
        "intervals": [
            {"start": 0, "end": 2, "label": 0, "attack_family": "Benign"},
            {"start": 2, "end": 4, "label": 1, "attack_family": "SYNFlood"},
        ],
    }
    path.write_text(json.dumps(data))
    labels = LabelTimeline(path)
    assert labels.label(0, 1, 100) == (0, "Benign")
    assert labels.label(1.5, 2.5, 100) == (None, "unknown")
    data["intervals"][1]["start"] = 1
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="overlap"):
        LabelTimeline(path)


class SpyModel:
    def __init__(self):
        self.events = []

    def predict(self, features):
        self.events.append("predict")
        return 0, 0.25, 0.1

    def learn(self, features, label, predicted, monitor=True):
        self.events.append("learn")
        return False


def fixture_csv(path):
    with path.open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["Label", "Attack Type", "Proto", "Dur", "TotPkts", "TotBytes"])
        for i in range(30):
            family = "Benign" if i % 2 == 0 else "SYNFlood"
            writer.writerow(
                ["Benign" if family == "Benign" else "Malicious", family, "udp", 1, 10, 100]
            )


def test_pipeline_api_and_fixture_separation(tmp_path):
    path = tmp_path / "fixture.csv"
    fixture_csv(path)
    config = RunConfig(input_path=str(path), output_root=str(tmp_path / "runs"), warmup_records=2)
    model = SpyModel()
    run = run_replay(config, fixture=True, model=model)
    assert run["counts"]["evaluated"] == 28
    assert model.events == ["predict", "learn"] * 30
    assert run["metrics"]["detection_time_seconds"]["value"] is None
    assert run["metrics"]["telemetry_bandwidth_kbps"]["status"] == "estimated"
    assert aggregate([run]) == []
    repository = RunRepository(config.output_root)
    assert len(repository.series(run["run_id"], 3)["predictions"]) == 3
    with TestClient(create_app(config.output_root)) as client:
        assert client.get("/api/health").status_code == 200
        assert client.get("/api/runs").json()["runs"][0]["feature_schema"] == "flow-v1"
        assert client.get("/api/runs/invalid").status_code == 404
        assert client.get(f"/api/runs/{run['run_id']}/series?limit=1").status_code == 422
    with pytest.raises(FileNotFoundError):
        repository.directory("..")
    other = run_replay(replace(config, sampling_rate=10), fixture=True, model=SpyModel())
    assert other["counts"]["sampled"] < run["counts"]["sampled"]


def test_failed_run_keeps_evidence(tmp_path):
    source = tmp_path / "bad.csv"
    source.write_text("bad,columns\n1,2\n")
    config = RunConfig(input_path=str(source), output_root=str(tmp_path / "runs"))
    with pytest.raises(RuntimeError, match="raw logs preserved"):
        run_replay(config, fixture=True, model=SpyModel())
    run = RunRepository(config.output_root).list()[0]
    assert run["status"] == "failed" and run["error"]


def test_pareto_strict_dominance():
    points = [{"f1": 0.8, "cost": 10}, {"f1": 0.7, "cost": 20}, {"f1": 0.9, "cost": 30}]
    assert pareto(points) == [points[0], points[2]]
    assert len(pareto([points[0], points[0]])) == 2


def test_aggregate_variation_and_status():
    base = {
        "source": "official_5g_nidd",
        "status": "completed",
        "mode": "live_sflow",
        "unit": "window",
        "scenario": "baseline",
        "config": {},
        "feature_schema": "packet-window-v1",
        "sampling_rate": 1,
        "provenance": {"sha256": "a"},
    }
    runs = [
        {**base, "run_id": str(i), "seed": i, "metrics": {"f1": measurement(value)}}
        for i, value in enumerate([0.5, 0.6, 0.7])
    ]
    row = aggregate(runs)[0]
    assert row["metrics"]["f1"]["mean"] == pytest.approx(0.6)
    assert row["metrics"]["f1"]["std"] == pytest.approx(0.1)
    assert row["distinct_seeds"] == 3
    runs[0]["provenance"] = {"sha256": "different"}
    assert len(aggregate(runs)) == 2


def test_real_hat_and_adwin():
    detector = OnlineDetector(RunConfig(input_path="fixture"))
    for i in range(5000):
        label = i % 2
        features = {"Dur": float(label * 100), "TotPkts": float(1 + label * 100), "Proto": "udp"}
        predicted, score, latency = detector.predict(features)
        assert 0 <= score <= 1 and latency >= 0
        detector.learn(features, label, predicted)
    assert detector.predict({"Dur": 100.0, "TotPkts": 101.0, "Proto": "udp"})[0] == 1
    detector.monitor.reset() if hasattr(detector.monitor, "reset") else None
    alarms = []
    for error in [0] * 500 + [1] * 500:
        detector.monitor.update(error)
        alarms.append(detector.monitor.drift_detected)
    assert any(alarms)
