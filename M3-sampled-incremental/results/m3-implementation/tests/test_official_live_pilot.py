"""Independent capture validation fixtures; not experimental evidence."""

import importlib.util
import json
from pathlib import Path

import dpkt
import pytest
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


def native_spool(tmp_path):
    spool = tmp_path / (pilot.SPOOL_PREFIX + "fixture")
    run = spool / "collector_runs" / ("a" * 32)
    run.mkdir(parents=True)
    raw = run / "sflow.datagrams"
    raw.write_bytes(b"\x00\xffraw evidence\x00")
    digest = pilot.sha256(raw)
    summary = {"config": {"output_root": str(spool / "collector_runs")},
               "artifacts": {"datagrams": str(raw), "raw_sha256": digest,
                             "external": str(tmp_path / "external.pcap")},
               "hashes": {"datagrams": digest}}
    (run / "run_summary.json").write_text(json.dumps(summary), encoding="utf-8")
    (spool / "replay_0.log").write_text("replay evidence", encoding="utf-8")
    (spool / "sflow_rx.pcap").write_bytes(b"independent UDP capture fixture")
    (spool / "sflow_rx.log").write_text("0 packets dropped by kernel", encoding="utf-8")
    (spool / "truth").mkdir()
    (spool / "truth/window.json").write_text('{"packets": 1}', encoding="utf-8")
    (spool / "truth/0.json").write_bytes(b'{ "packets": 2 }\r\n')
    (spool / "truth/1.json").write_bytes(b'{"packets":3}\n')
    (spool / "truth/ready.json").write_text('{"ready_epoch": 100}', encoding="utf-8")
    (spool / "truth/health.json").write_text('{"packets": 5}', encoding="utf-8")
    (spool / "truth/packet_events.csv").write_text("epoch,frame\n100,fixture\n", encoding="utf-8")
    return spool, run, summary


def test_native_spool_preserves_bytes_and_rebases_only_artifacts(tmp_path):
    spool, run, original = native_spool(tmp_path)
    output, runs = tmp_path / "evidence", tmp_path / "runs"
    metadata = pilot.preserve_native_spool(spool, output, runs)
    durable = runs / run.name
    summary = json.loads((durable / "run_summary.json").read_text(encoding="utf-8"))
    assert (durable / "sflow.datagrams").read_bytes() == (run / "sflow.datagrams").read_bytes()
    assert (output / "replay_0.log").read_text() == "replay evidence"
    assert (output / "sflow_rx.pcap").read_bytes() == (spool / "sflow_rx.pcap").read_bytes()
    assert (output / "sflow_rx.log").read_bytes() == (spool / "sflow_rx.log").read_bytes()
    assert (output / "truth/window.json").read_bytes() == (spool / "truth/window.json").read_bytes()
    for name in ("ready.json", "health.json", "packet_events.csv"):
        assert (output / "truth" / name).read_bytes() == (spool / "truth" / name).read_bytes()
    with pilot.zipfile.ZipFile(output / "truth/truth_windows.zip") as archive:
        for path in (spool / "truth").glob("*.json"):
            assert archive.read(path.name) == path.read_bytes()
    assert not (output / "truth/0.json").exists()
    assert not (output / "truth/1.json").exists()
    assert summary["artifacts"]["datagrams"] == str(durable / "sflow.datagrams")
    assert summary["artifacts"]["external"] == original["artifacts"]["external"]
    assert summary["artifacts"]["raw_sha256"] == original["artifacts"]["raw_sha256"]
    assert summary["hashes"] == original["hashes"]
    assert summary["config"] == original["config"]
    assert summary["storage"]["runtime_output_root"] == original["config"]["output_root"]
    assert summary["storage"]["durable_run_directory"] == str(durable)
    assert metadata["preservation"] == "byte_verified" and metadata["verified_files"] == 12
    assert metadata["archived_truth_windows"] == 2
    assert spool.exists()  # Preservation itself never destroys recovery evidence.
    pilot.cleanup_native_spool(spool, temp_root=tmp_path)
    assert not spool.exists() and (durable / "sflow.datagrams").exists()


@pytest.mark.parametrize("failure", ["corrupt", "io_error"])
def test_failed_native_copy_retains_complete_recovery_spool(tmp_path, monkeypatch, failure):
    spool, run, _ = native_spool(tmp_path)
    originals = {p.relative_to(spool): p.read_bytes() for p in spool.rglob("*") if p.is_file()}

    def failed_copy(source, destination):
        if failure == "io_error":
            raise OSError("fixture disk failure")
        Path(destination).write_bytes(b"corrupt")

    monkeypatch.setattr(pilot.shutil, "copyfile", failed_copy)
    with pytest.raises(OSError):
        pilot.preserve_native_spool(spool, tmp_path / "evidence", tmp_path / "runs")
    assert all((spool / path).read_bytes() == data for path, data in originals.items())
    assert run.is_dir()


def test_failed_oracle_zip_verification_retains_numbered_originals(tmp_path, monkeypatch):
    spool, _, _ = native_spool(tmp_path)
    numbered = {path.name: path.read_bytes() for path in (spool / "truth").glob("[01].json")}
    monkeypatch.setattr(pilot.zipfile.ZipFile, "read", lambda *args, **kwargs: b"corrupt")
    with pytest.raises(OSError, match="Oracle archive verification failed"):
        pilot.preserve_native_spool(spool, tmp_path / "evidence", tmp_path / "runs")
    assert all((spool / "truth" / name).read_bytes() == data for name, data in numbered.items())
    assert not (tmp_path / "runs").exists()


def test_native_cleanup_rejects_nonowned_or_outside_paths(tmp_path):
    unrelated = tmp_path / "unrelated"
    unrelated.mkdir()
    nested = unrelated / (pilot.SPOOL_PREFIX + "nested")
    nested.mkdir()
    for path in (tmp_path, unrelated, nested):
        with pytest.raises(ValueError, match="Refusing cleanup"):
            pilot.cleanup_native_spool(path, temp_root=tmp_path)
        assert path.exists()


def test_preservation_rejects_destination_inside_native_spool(tmp_path):
    spool, _, _ = native_spool(tmp_path)
    with pytest.raises(ValueError, match="outside the native spool"):
        pilot.preserve_native_spool(spool, spool / "recursive", tmp_path / "runs")
    assert not (spool / "recursive").exists()
