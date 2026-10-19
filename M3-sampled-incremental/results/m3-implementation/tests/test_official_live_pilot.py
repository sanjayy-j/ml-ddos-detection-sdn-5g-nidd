"""Independent capture validation fixtures; not experimental evidence."""

import importlib.util
from pathlib import Path

import dpkt
from test_core import sflow_datagram
from test_ground_truth import udp_packet

from m3.sflow import decode_datagram

SPEC = importlib.util.spec_from_file_location(
    "official_capture_pilot", Path(__file__).parents[1] / "sdn/run_official_capture_pilot.py"
)
pilot = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pilot)


def write_capture(path, frames):
    with path.open("wb") as output:
        writer = dpkt.pcap.Writer(output)
        for time, frame in frames:
            writer.writepkt(frame, time)


def test_independent_tx_rx_multiplicity_and_unknowns(tmp_path):
    frame = udp_packet()
    prepared, tx, rx = [tmp_path / name for name in ("block.pcap", "tx.pcap", "rx.pcap")]
    write_capture(prepared, [(0, frame), (0.01, frame)])
    write_capture(tx, [(100, frame), (100.01, frame)])
    write_capture(rx, [(100.001, frame), (100.011, frame)])
    blocks = [{"path": "block.pcap", "attack_family": "UDPFlood"}]
    report = pilot.validate_dataplane(blocks, tmp_path, tx, rx, 100)
    assert report["status"] == "validated" and report["expected_packets"] == 2
    assert report["receive_windows"] == {"0": {"UDPFlood": 2}}
    write_capture(rx, [(100, frame), (100.01, udp_packet(sport=999))])
    report = pilot.validate_dataplane(blocks, tmp_path, tx, rx, 100)
    assert report["status"] == "failed"
    assert report["captures"]["rx"]["unknown_packets"] == 1


def test_raw_sflow_headers_are_opt_in_and_align_with_packets():
    datagram = sflow_datagram(1)
    ordinary, normal = decode_datagram(datagram, 100)
    detailed, metadata = decode_datagram(datagram, 100, include_headers=True)
    assert ordinary == detailed
    assert "headers" not in normal
    assert len(metadata["headers"]) == len(detailed)
    assert metadata["headers"][0]["protocol"] == 1
    assert metadata["headers"][0]["raw"]
