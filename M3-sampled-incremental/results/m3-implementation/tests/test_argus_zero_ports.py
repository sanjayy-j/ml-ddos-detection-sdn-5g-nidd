"""Fixture-only Argus export tests; these are not official-data measurements."""

import importlib.util
import subprocess
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location(
    "prepare_flow_labels", Path(__file__).resolve().parents[1] / "sdn/prepare_flow_labels.py"
)
prepare_labels = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(prepare_labels)


def fixture_row(offset="100", proto="udp", sport="123", dport=""):
    return {"Offset": offset, "Proto": proto, "Sport": sport, "Dport": dport}


def test_confirmed_zero_is_recovered_but_unconfirmed_blank_is_not():
    counts = prepare_labels.new_port_counts()
    proof = {"src": {}, "dst": {100: "udp"}}
    assert prepare_labels.resolve_ports(fixture_row(), proof, counts) == ("123", "0")
    assert prepare_labels.resolve_ports(fixture_row("200"), proof, counts) == ("123", "")
    assert counts["dst"]["recovered_zero"] == 1
    assert counts["dst"]["unconfirmed_blank"] == 1


def test_nonzero_ports_are_unchanged_and_nontransport_ports_are_not_invented():
    proof = {"src": {}, "dst": {}}
    counts = prepare_labels.new_port_counts()
    assert prepare_labels.resolve_ports(fixture_row(dport="80"), proof, counts) == ("123", "80")
    assert prepare_labels.resolve_ports(fixture_row(proto="icmp", sport="8"), proof, counts) == (
        "",
        "",
    )


@pytest.mark.parametrize(
    "row,proof,match",
    [
        (fixture_row(proto="tcp"), {"src": {}, "dst": {100: "udp"}}, "protocol"),
        (fixture_row(dport="53"), {"src": {}, "dst": {100: "udp"}}, "nonzero"),
        (fixture_row(proto="icmp"), {"src": {}, "dst": {100: "udp"}}, "protocol"),
    ],
)
def test_false_or_mismatched_zero_proof_is_rejected(row, proof, match):
    with pytest.raises(ValueError, match=match):
        prepare_labels.resolve_ports(row, proof, prepare_labels.new_port_counts())


def test_zero_filter_output_uses_exact_offsets_and_records_commands(monkeypatch):
    outputs = iter(
        [
            "Offset,Proto,Sport,Dport\n100,udp,,53\n",
            "Offset,Proto,Sport,Dport\n200,tcp,80,\n",
        ]
    )
    calls = []

    def fake_run(command, **kwargs):
        calls.append(command)
        return subprocess.CompletedProcess(command, 0, next(outputs), "")

    monkeypatch.setattr(prepare_labels.subprocess, "run", fake_run)
    proof, audit = prepare_labels.collect_zero_port_offsets(Path("fixture.argus"))
    assert proof == {"src": {100: "udp"}, "dst": {200: "tcp"}}
    assert audit["src"]["confirmed_offsets"] == 1
    assert audit["dst"]["command"] == calls[1]
    assert calls[0][-1] == "(tcp or udp) and src port 0"
    assert calls[1][-1] == "(tcp or udp) and dst port 0"
    prepare_labels.validate_zero_port_offsets(proof, {100, 200})
    with pytest.raises(ValueError, match="absent"):
        prepare_labels.validate_zero_port_offsets(proof, {100})


@pytest.mark.parametrize(
    "output",
    [
        "Offset,Proto,Sport,Dport\n100,icmp,,\n",
        "Offset,Proto,Sport,Dport\n100,udp,123,\n",
        "Offset,Proto,Sport,Dport\n100,udp,,\n100,udp,,\n",
        "Offset,Proto\n100,udp\n",
        "Offset,Proto,Sport,Dport\nnot-an-offset,udp,,\n",
    ],
)
def test_invalid_or_duplicate_filter_records_fail_closed(monkeypatch, output):
    monkeypatch.setattr(
        prepare_labels.subprocess,
        "run",
        lambda command, **kwargs: subprocess.CompletedProcess(command, 0, output, ""),
    )
    with pytest.raises(ValueError):
        prepare_labels.collect_zero_port_offsets(Path("fixture.argus"))


def test_backup_preserves_previous_verified_input_and_ancestry(tmp_path, monkeypatch):
    monkeypatch.setattr(prepare_labels, "ROOT", tmp_path)
    path = tmp_path / "labels.csv"
    path.write_text("fixture old label content\n")
    checksum = prepare_labels.sha(path)
    manifest = {
        "files": [
            {
                "path": "labels.csv",
                "sha256": checksum,
                "verification_status": "verified",
                "parent_sha256s": ["official-parent"],
                "transformations": ["fixture transform"],
            }
        ]
    }
    entry = prepare_labels.preserve_previous_labels(path, manifest, "different-sha")
    backup = tmp_path / entry["path"]
    assert backup.name == f"labels.{checksum}.csv"
    assert backup.read_bytes() == path.read_bytes()
    assert entry["sha256"] == checksum
    assert entry["parent_sha256s"] == ["official-parent"]
    assert entry["archived_from"] == "labels.csv"
    assert prepare_labels.preserve_previous_labels(path, manifest, checksum) is None
    backup.write_text("fixture corrupted archive")
    with pytest.raises(ValueError, match="backup"):
        prepare_labels.preserve_previous_labels(path, manifest, "different-sha")
