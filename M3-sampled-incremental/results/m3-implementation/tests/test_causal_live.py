"""Deterministic collector orchestration checks; no network or experiment data."""

import csv
import json
from types import SimpleNamespace

import pytest

from m3 import causal_live
from m3.config import RunConfig
from m3.engine import Evaluation
from m3.packets import Packet
from m3.sflow import DecodeError


@pytest.fixture
def causal_lab(tmp_path, monkeypatch):
    """Keep the real writer/evaluator; replace only physical I/O and the model."""
    clock = SimpleNamespace(now=100.0)
    trace = []
    truth_dir = tmp_path / "truth"
    truth_dir.mkdir()
    for index in range(4):
        (truth_dir / f"{index}.json").write_text(json.dumps({
            "label": 1, "attack_family": "UDPFlood", "packets": 10,
            "start_epoch": 100 + index / 10,
            "end_epoch": 100 + (index + 1) / 10,
            "available_epoch": 100 + (index + 1) / 10,
        }))

    class Detector:
        def predict(self, features):
            trace.append(("predict", dict(features)))
            return 0, 0.1, 0.01

        def learn(self, features, label, predicted, monitor=True):
            trace.append(("learn", label))
            return False

    class Resources:
        def __init__(self, *_):
            self.telemetry_bytes = 0
            self.thread = SimpleNamespace(is_alive=lambda: True)

        def start(self):
            trace.append(("resources_start", None))

        def finish(self, **_):
            trace.append(("resources_finish", None))
            return {}

    class Socket:
        def __init__(self):
            self.payloads = [b"good"]
            self.closed = False
            self.bind_error = None

        def setsockopt(self, *_):
            pass

        def bind(self, _):
            if self.bind_error:
                raise self.bind_error

        def settimeout(self, _):
            pass

        def recvfrom(self, _):
            clock.now += 0.025
            if self.payloads:
                return self.payloads.pop(0), ("127.0.0.1", 9999)
            raise TimeoutError

        def close(self):
            self.closed = True

    sock = Socket()
    sequence = 0

    def decode(payload, received):
        nonlocal sequence
        sequence += 1
        if payload == b"malformed":
            raise DecodeError("deliberately malformed fixture")
        return [Packet(received, 64, 17, False, 2 if payload == b"mismatch" else 1)], {
            "sequence": sequence + (2 if payload == b"gap" else 0),
            "drops": int(payload == b"drops"),
        }

    original_reveal = causal_live.reveal_truth

    def reveal(path, **kwargs):
        trace.append(("reveal", int(path.stem)))
        return original_reveal(path, **kwargs)

    monkeypatch.setattr(causal_live, "time", SimpleNamespace(time=lambda: clock.now))
    monkeypatch.setattr(causal_live.socket, "socket", lambda *_: sock)
    monkeypatch.setattr(causal_live, "verify_input", lambda *_: {"verified": True})
    monkeypatch.setattr(causal_live, "ResourceMonitor", Resources)
    monkeypatch.setattr(causal_live, "decode_datagram", decode)
    monkeypatch.setattr(causal_live, "reveal_truth", reveal)
    monkeypatch.setattr(causal_live, "Evaluation", lambda c, w: Evaluation(c, w, Detector()))
    config = RunConfig(mode="live_sflow", input_path="fixture-blocks.json", start_epoch=100,
                       output_root=str(tmp_path / "runs"), duration_seconds=0.4,
                       window_seconds=0.1, warmup_seconds=0, label_delay_seconds=0.05)
    return SimpleNamespace(config=config, truth=truth_dir, sock=sock, trace=trace,
                           output=tmp_path / "runs")


def saved_run(lab):
    directory, = lab.output.iterdir()
    return directory, json.loads((directory / "run_summary.json").read_text())


def test_predict_precedes_each_independent_label_read_and_learning(causal_lab):
    result = causal_live.run_causal(causal_lab.config, causal_lab.truth)
    causal_steps = [event for event, _ in causal_lab.trace
                    if event in {"predict", "reveal", "learn"}]
    assert causal_steps == ["predict", "reveal", "learn"] * 4
    assert result["status"] == "completed"
    # Collection completion alone never promotes a run to validated research evidence.
    assert result["source"] == "provisional_realtime"
    assert result["validation"]["accepted"] is False
    assert causal_lab.sock.closed


def test_empty_sample_windows_are_scored_from_independent_positive_truth(causal_lab):
    result = causal_live.run_causal(causal_lab.config, causal_lab.truth)
    directory, _ = saved_run(causal_lab)
    rows = [json.loads(line) for line in (directory / "features.jsonl").read_text().splitlines()]
    assert result["counts"]["evaluated"] == 4
    assert result["counts"]["sampled"] == 1
    assert len(rows) == 4
    assert [row["sampled_packets"] for row in rows] == [1, 0, 0, 0]
    assert all(row["y_true"] == 1 and row["ground_truth_packets"] == 10 for row in rows)
    assert rows[1]["features"]["empty_window"] == 1
    assert all(row["completion_epoch"] <= row["label_read_epoch"] for row in rows)


@pytest.mark.parametrize("payload,health_key", [
    (b"malformed", "malformed_datagrams"),
    (b"mismatch", "sampling_mismatches"),
    (b"gap", "sequence_gaps"),
    (b"drops", "agent_reported_drops"),
])
def test_datagram_integrity_failure_preserves_unaccepted_evidence(causal_lab, payload, health_key):
    causal_lab.sock.payloads.append(payload)
    with pytest.raises(RuntimeError, match="evidence preserved"):
        causal_live.run_causal(causal_lab.config, causal_lab.truth)
    directory, summary = saved_run(causal_lab)
    assert summary["status"] == "failed"
    assert summary["validation"]["accepted"] is False
    assert summary["telemetry_health"][health_key] > 0
    assert summary["error"]
    assert (directory / "sflow.datagrams").stat().st_size > 0
    assert (directory / "features.jsonl").stat().st_size > 0
    assert causal_lab.sock.closed
    assert ("resources_finish", None) in causal_lab.trace


def test_missing_truth_stops_without_learning_and_keeps_prior_predictions(causal_lab):
    (causal_lab.truth / "1.json").unlink()
    with pytest.raises(RuntimeError, match="truth window 1 unavailable"):
        causal_live.run_causal(causal_lab.config, causal_lab.truth)
    directory, summary = saved_run(causal_lab)
    assert summary["status"] == "failed"
    with (directory / "predictions.csv").open() as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 1
    assert rows[0]["index"] == "0"
    assert len([event for event, _ in causal_lab.trace if event == "predict"]) == 2
    assert len([event for event, _ in causal_lab.trace if event == "learn"]) == 1


def test_socket_bind_failure_is_saved_and_socket_closed(causal_lab):
    causal_lab.sock.bind_error = OSError("port already in use")
    with pytest.raises(RuntimeError, match="port already in use"):
        causal_live.run_causal(causal_lab.config, causal_lab.truth)
    _, summary = saved_run(causal_lab)
    assert summary["status"] == "failed"
    assert summary["counts"]["input"] == 0
    assert summary["validation"]["accepted"] is False
    assert causal_lab.sock.closed
