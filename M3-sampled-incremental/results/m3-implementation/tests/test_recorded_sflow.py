"""Recorded-export parser/header checks use explicit synthetic fixtures only."""

import importlib.util
import struct
from pathlib import Path

import pytest
from test_ground_truth import udp_packet


@pytest.fixture
def scorer(monkeypatch):
    directory = Path(__file__).parents[1] / "sdn"
    monkeypatch.syspath_prepend(str(directory))
    spec = importlib.util.spec_from_file_location(
        "recorded_sflow_test", directory / "score_recorded_sflow.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_header_compatibility_does_not_invent_ambiguous_labels(scorer):
    frame = udp_packet()
    index = {frame[:42]: [(frame, "UDPFlood")]}
    assert scorer.header_family(frame, index) == "UDPFlood"
    assert scorer.header_family(frame[:48], index) == "UDPFlood"
    assert scorer.header_family(udp_packet(sport=999), index) is None
    index[frame[:42]].append((frame, "Benign"))
    assert scorer.header_family(frame, index) is None


def test_datagram_framing_and_bounds(scorer, tmp_path):
    path = tmp_path / "synthetic.datagrams"
    path.write_bytes(struct.pack("!dI", 100.0, 3) + b"abc")
    assert list(scorer.datagrams(path)) == [(100.0, b"abc")]
    for payload in (
        b"x",
        struct.pack("!dI", 100, 999999),
        struct.pack("!dI", float("nan"), 1),
        struct.pack("!dI", 100, 5) + b"x",
    ):
        path.write_bytes(payload)
        with pytest.raises(ValueError):
            list(scorer.datagrams(path))
