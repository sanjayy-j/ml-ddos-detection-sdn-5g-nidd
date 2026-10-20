"""Synthetic selection tests and declared-protocol checks, not research evidence."""

import csv
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from test_capture_audit import inputs, udp

ROOT = Path(__file__).parents[1]


def load_script(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "sdn" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


prepare = load_script("prepare_replay_blocks")


@pytest.fixture
def selection_inputs(tmp_path, monkeypatch):
    paths = inputs(tmp_path, [(100.01 + index / 100, udp()) for index in range(10)])
    monkeypatch.setattr(prepare, "ROOT", tmp_path)
    segment = {
        "capture": str(paths[0]),
        "flow_labels": str(paths[1]),
        "family": "UDPFlood",
        "packet_count": 3,
        "pps": 100,
    }
    return segment, paths[2], tmp_path / "data/prepared/test"


def test_skipping_matching_packets_makes_source_selections_disjoint(selection_inputs):
    segment, manifest, output = selection_inputs
    document = prepare.prepare_blocks(
        {
            "require_disjoint_source_packets": True,
            "segments": [segment, dict(segment, skip_matching=3)],
        },
        output,
        manifest,
    )
    selections = [
        list(csv.DictReader((output / f"block_{index:02d}_mapping.csv").open()))
        for index in range(2)
    ]
    assert [int(row["source_packet_index"]) for row in selections[0]] == [0, 1, 2]
    assert [int(row["source_packet_index"]) for row in selections[1]] == [3, 4, 5]
    assert document["blocks"][1]["skip_matching"] == 3
    assert document["source_packet_reuse_count"] == 0
    assert "skip_matching" in document["selection_policy"]


@pytest.mark.parametrize("value", [-1, True, 1.5, "3"])
def test_invalid_skip_rejected_before_writes(selection_inputs, value):
    segment, manifest, output = selection_inputs
    with pytest.raises(ValueError, match="skip_matching"):
        prepare.prepare_blocks({"segments": [dict(segment, skip_matching=value)]}, output, manifest)
    assert not output.exists()


def test_skip_insufficiency_preserves_failed_evidence_without_registration(selection_inputs):
    segment, manifest, output = selection_inputs
    before = manifest.read_bytes()
    with pytest.raises(ValueError, match="Insufficient"):
        prepare.prepare_blocks({"segments": [dict(segment, skip_matching=9)]}, output, manifest)
    assert manifest.read_bytes() == before
    assert json.loads((output / "failed.json").read_text())["registered"] is False


def test_disjoint_guard_rejects_overlapping_source_indices(selection_inputs):
    segment, manifest, output = selection_inputs
    with pytest.raises(ValueError, match="reused"):
        prepare.prepare_blocks(
            {"require_disjoint_source_packets": True, "segments": [segment, segment]},
            output,
            manifest,
        )


def test_legacy_reuse_is_counted_not_silently_claimed_independent(selection_inputs):
    segment, manifest, output = selection_inputs
    result = prepare.prepare_blocks({"segments": [segment, segment]}, output, manifest)
    assert result["source_packet_reuse_count"] == 3
    assert result["blocks"][0]["skip_matching"] == 0


def test_research_protocol_has_fixed_rates_disjoint_inputs_and_unseen_holdout():
    research = load_script("prepare_research_scenarios")
    protocol = json.loads((ROOT / "configs/research_protocol.json").read_text())
    plans = research.build_plans(protocol)
    assert set(plans) == {"baseline", "drift", "unseen"}
    assert protocol["sampling_rates"] == [1, 2, 5, 10, 20, 50]
    assert protocol["model_seeds"] == [42, 43, 44]
    assert protocol["planned_trials"] == 54
    positions = {}
    for name, plan in plans.items():
        segments = plan["segments"]
        assert all(segment["pps"] == 100 for segment in segments)
        assert plan["require_disjoint_source_packets"] is True
        warmup = segments[: plan["warmup_blocks"]]
        evaluation = segments[plan["warmup_blocks"] :]
        assert {segment["family"] for segment in evaluation} >= {"Benign"}
        if name == "unseen":
            assert "SYNFlood" not in {segment["family"] for segment in warmup}
            assert "SYNFlood" in {segment["family"] for segment in evaluation}
        for segment in segments:
            key = (segment["capture"], segment["family"])
            start = segment["skip_matching"]
            assert start == positions.get(key, 0)
            positions[key] = start + segment["packet_count"]
    assert positions[(plans["drift"]["segments"][-1]["capture"], "ICMPFlood")] == 800


def test_protocol_rejects_family_rate_confound_before_preparation():
    research = load_script("prepare_research_scenarios")
    protocol = json.loads((ROOT / "configs/research_protocol.json").read_text())
    protocol["scenarios"]["baseline"]["blocks"][0]["pps"] = 200
    with pytest.raises(ValueError, match="same primary rate"):
        research.build_plans(protocol)


@pytest.mark.parametrize("warmup", [0, True, 12])
def test_invalid_warmup_boundary_rejected(warmup):
    research = load_script("prepare_research_scenarios")
    protocol = json.loads((ROOT / "configs/research_protocol.json").read_text())
    protocol["scenarios"]["baseline"]["warmup_blocks"] = warmup
    with pytest.raises(ValueError, match="warm-up"):
        research.build_plans(protocol)


def test_unseen_holdout_cannot_be_violated():
    research = load_script("prepare_research_scenarios")
    protocol = json.loads((ROOT / "configs/research_protocol.json").read_text())
    protocol["scenarios"]["unseen"]["blocks"][0]["family"] = "SYNFlood"
    with pytest.raises(ValueError, match="absent"):
        research.build_plans(protocol)


def test_existing_preparation_verifies_frozen_plan_and_all_artifacts(tmp_path, monkeypatch):
    research = load_script("prepare_research_scenarios")
    protocol_path = ROOT / "configs/research_protocol.json"
    plans = research.build_plans(json.loads(protocol_path.read_text()))
    output = tmp_path / "data/prepared/research"
    output.mkdir(parents=True)
    monkeypatch.setattr(research, "ROOT", tmp_path)
    checked = []
    monkeypatch.setattr(research, "verify_input", lambda path, _: checked.append(str(path)) or {})
    saved = {"protocol_sha256": research.sha256(protocol_path), "scenarios": {}}
    for name, plan in plans.items():
        folder = output / name
        folder.mkdir()
        (folder / "blocks.json").write_text(
            json.dumps({"plan": plan, "blocks": [{"path": "a.pcap", "mapping": "a.csv"}]})
        )
        saved["scenarios"][name] = {"blocks": f"{name}/blocks.json"}
    (output / "scenarios.json").write_text(json.dumps(saved))
    assert research.prepare_scenarios(protocol_path, output, "unused.json") == saved
    assert len(checked) == 15  # Six unique sources and nine derived artifacts.
    blocks_path = output / "baseline/blocks.json"
    changed = json.loads(blocks_path.read_text())
    changed["plan"]["warmup_blocks"] = 1
    blocks_path.write_text(json.dumps(changed))
    with pytest.raises(ValueError, match="do not match"):
        research.prepare_scenarios(protocol_path, output, "unused.json")


def test_preparation_refuses_fixture_and_outside_output(tmp_path, monkeypatch):
    research = load_script("prepare_research_scenarios")
    protocol = ROOT / "configs/research_protocol.json"
    monkeypatch.setattr(research, "verify_input", lambda *_: {"fixture": True})
    with pytest.raises(ValueError, match="Synthetic fixtures"):
        research.prepare_scenarios(protocol, tmp_path / "bad", "unused.json")
    monkeypatch.setattr(research, "verify_input", lambda *_: {})
    with pytest.raises(ValueError, match="under data/prepared"):
        research.prepare_scenarios(protocol, tmp_path / "bad", "unused.json")


def test_new_preparation_orchestrates_three_scenarios_once(tmp_path, monkeypatch):
    research = load_script("prepare_research_scenarios")
    monkeypatch.setattr(research, "ROOT", tmp_path)
    monkeypatch.setattr(research, "verify_input", lambda *_: {})
    calls = []

    def fake_prepare(plan, folder, manifest):
        calls.append((plan["scenario"], folder, manifest))
        folder.mkdir()
        return {"blocks": plan["segments"]}

    fake = SimpleNamespace(prepare_blocks=fake_prepare)
    spec = SimpleNamespace(loader=SimpleNamespace(exec_module=lambda _: None))
    monkeypatch.setattr(research.importlib.util, "spec_from_file_location", lambda *_: spec)
    monkeypatch.setattr(research.importlib.util, "module_from_spec", lambda _: fake)
    output = tmp_path / "data/prepared/research"
    result = research.prepare_scenarios(
        ROOT / "configs/research_protocol.json", output, "unused.json"
    )
    assert [name for name, _, _ in calls] == ["baseline", "drift", "unseen"]
    assert result["scenarios"]["drift"]["packet_count"] == 8000
    assert result["scenarios"]["baseline"]["active_seconds"] == 96
    assert json.loads((output / "scenarios.json").read_text()) == result
