"""Controlled trace preparation uses synthetic fixtures, never dataset evidence."""

import csv
import importlib.util
import json
from pathlib import Path

import pytest
from test_capture_audit import inputs

from m3.packets import iter_pcap

SPEC = importlib.util.spec_from_file_location(
    "prepare_blocks_test", Path(__file__).parents[1] / "sdn/prepare_replay_blocks.py"
)
prepare = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(prepare)


def setup_plan(tmp_path, monkeypatch, count=2):
    capture, labels, manifest = inputs(tmp_path)
    monkeypatch.setattr(prepare, "ROOT", tmp_path)
    segment = {
        "capture": str(capture),
        "flow_labels": str(labels),
        "family": "UDPFlood",
        "packet_count": count,
        "pps": 100,
    }
    return {"segments": [segment]}, manifest, tmp_path / "data/prepared/blocks"


def test_exact_selection_mac_only_and_constructed_timing(tmp_path, monkeypatch):
    plan, manifest, output = setup_plan(tmp_path, monkeypatch)
    result = prepare.prepare_blocks(plan, output, manifest)
    original = list(iter_pcap(plan["segments"][0]["capture"]))
    packets = list(iter_pcap(output / "block_00.pcap"))
    assert len(packets) == 2
    assert [time for time, _ in packets] == [0, 0.01]
    for (_, source), (_, rewritten) in zip(original, packets, strict=False):
        assert source[12:] == rewritten[12:]
        assert rewritten[:12] == prepare.MAC_PREFIX
    assert result["fixture"] and result["blocks"][0]["attack_family"] == "UDPFlood"
    rows = list(csv.DictReader((output / "block_00_mapping.csv").open()))
    assert [int(row["source_packet_index"]) for row in rows] == [0, 1]
    assert all(row["attack_family"] == "UDPFlood" for row in rows)
    assert any(
        entry["path"].endswith("blocks.json") for entry in json.loads(manifest.read_text())["files"]
    )


def test_insufficient_known_packets_never_registers_partial(tmp_path, monkeypatch):
    plan, manifest, output = setup_plan(tmp_path, monkeypatch, 4)
    original_manifest = manifest.read_bytes()
    with pytest.raises(ValueError, match="Insufficient"):
        prepare.prepare_blocks(plan, output, manifest)
    assert manifest.read_bytes() == original_manifest
    assert json.loads((output / "failed.json").read_text())["registered"] is False


@pytest.mark.parametrize(
    "field,value",
    [
        ("packet_count", 0),
        ("packet_count", True),
        ("pps", float("nan")),
        ("pps", 10001),
        ("family", "unknown"),
    ],
)
def test_invalid_plan_rejected_before_output(tmp_path, monkeypatch, field, value):
    plan, manifest, output = setup_plan(tmp_path, monkeypatch)
    plan["segments"][0][field] = value
    with pytest.raises(ValueError):
        prepare.prepare_blocks(plan, output, manifest)
    assert not output.exists()
