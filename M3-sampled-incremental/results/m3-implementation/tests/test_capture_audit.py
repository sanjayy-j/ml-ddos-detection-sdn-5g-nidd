"""Explicit synthetic unit fixtures only; never official 5G-NIDD evidence."""

import csv
import importlib.util
import json
from pathlib import Path

import dpkt
import pytest

from m3.provenance import OFFICIAL_DOI, sha256

SPEC = importlib.util.spec_from_file_location(
    "audit_packet_labels", Path(__file__).parents[1] / "sdn/audit_packet_labels.py"
)
audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)


def udp(reverse=False, sport=123):
    source, destination = b"\x0a\x00\x00\x01", b"\x0a\x00\x00\x02"
    dport = 456
    if reverse:
        source, destination, sport, dport = destination, source, dport, sport
    transport = dpkt.udp.UDP(sport=sport, dport=dport, data=b"fixture")
    transport.ulen = len(transport)
    ip = dpkt.ip.IP(src=source, dst=destination, p=17, data=transport)
    ip.len = len(ip)
    return bytes(dpkt.ethernet.Ethernet(src=b"\x00" * 6, dst=b"\x01" * 6, type=0x0800, data=ip))


def inputs(tmp_path, packets=None):
    capture, labels, manifest = [
        tmp_path / name
        for name in ("synthetic_fixture.pcap", "synthetic_labels.csv", "synthetic_manifest.json")
    ]
    rows = [
        [100, 101, "10.0.0.1", "10.0.0.2", 123, 456, "udp", 1, "UDPFlood", 1],
        [100.5, 100.6, "10.0.0.1", "10.0.0.2", 123, 456, "udp", 0, "Benign", 2],
        [102, 103, "10.0.0.1", "10.0.0.2", 123, 456, "udp", 0, "Benign", 3],
        [104, 105, "10.0.0.1", "10.0.0.2", 123, 456, "udp", 1, "UDPFlood", 4],
        [104, 105, "10.0.0.1", "10.0.0.2", 123, 456, "udp", 1, "SYNFlood", 5],
        [100, 101, "10.0.0.1", "10.0.0.2", "", "", "arp", 0, "Benign", 6],
    ]
    with labels.open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(
            [
                "start_epoch",
                "end_epoch",
                "src_ip",
                "dst_ip",
                "src_port",
                "dst_port",
                "protocol",
                "label",
                "attack_family",
                "offset",
            ]
        )
        writer.writerows(rows)
    with capture.open("wb") as stream:
        writer = dpkt.pcap.Writer(stream)
        for timestamp, header in packets or [
            (100.1, udp()),
            (100.2, udp(reverse=True)),
            (100.55, udp()),
            (101.5, udp()),
            (102.1, udp()),
            (102.2, udp(sport=999)),
            (102.3, b"invalid"),
            (104.1, udp()),
        ]:
            writer.writepkt(header, timestamp)
    manifest.write_text(
        json.dumps(
            {
                "dataset": "5G-NIDD",
                "doi": OFFICIAL_DOI,
                "status": "verified",
                "notes": ["SYNTHETIC TEST FIXTURE ONLY: not official data or evidence"],
                "files": [
                    {
                        "path": str(path),
                        "sha256": sha256(path),
                        "fixture": True,
                        "source": "synthetic unit fixture, not official release",
                    }
                    for path in (capture, labels)
                ],
            }
        )
    )
    return capture, labels, manifest


def test_complete_counts_reverse_tuple_conflicts_and_unknowns(tmp_path):
    report = audit.audit_capture(*inputs(tmp_path))
    assert report["status"] == "complete" and report["complete"]
    assert report["counts"] == {
        "matched_benign": 1,
        "matched_flood": 3,
        "unmatched_key": 1,
        "unmatched_time": 1,
        "conflicting_label_overlap": 1,
        "invalid_or_nonjoinable_header": 1,
    }
    assert report["total_packets"] == 8
    assert report["matched_packets"] + report["unknown_packets"] == 8
    assert report["match_coverage"] == 0.5
    assert report["counts_reconcile"]
    assert report["matched_packets_by_family"] == {"Benign": 1, "UDPFlood": 2, "mixed_flood": 1}
    assert report["mixed_flood_family_sets"] == {"SYNFlood + UDPFlood": 1}
    assert report["label_rows"] == 6 and report["unjoinable_label_rows"] == 1
    assert report["min_timestamp_epoch"] == pytest.approx(100.1)
    assert report["max_timestamp_epoch"] == pytest.approx(104.1)
    assert report["provenance"]["capture"]["fixture"] is True
    assert report["evidence_scope"] == "synthetic_test_fixture_only_not_official_evidence"


@pytest.mark.parametrize("cap", [1, 8])
def test_cap_never_claims_complete_without_eof(tmp_path, cap):
    report = audit.audit_capture(*inputs(tmp_path), max_packets=cap)
    assert report["status"] == "diagnostic_capped"
    assert report["complete"] is False and report["cap_reached"]
    assert report["total_packets"] == cap
    assert sum(report["counts"].values()) == cap


def test_cap_above_actual_size_observes_eof(tmp_path):
    report = audit.audit_capture(*inputs(tmp_path), max_packets=9)
    assert report["complete"] and not report["cap_reached"]


def test_timestamp_order_failure_is_not_completed(tmp_path):
    report = audit.audit_capture(*inputs(tmp_path, [(100.2, udp()), (100.1, udp())]))
    assert report["status"] == "failed" and not report["complete"]
    assert report["timestamp_order_errors"] == 1
    assert report["total_packets"] == 1 and report["counts_reconcile"]


def test_nonfinite_timestamp_fails_closed(tmp_path, monkeypatch):
    paths = inputs(tmp_path)
    monkeypatch.setattr(audit, "iter_pcap", lambda path: iter([(float("nan"), udp())]))
    report = audit.audit_capture(*paths)
    assert report["status"] == "failed" and not report["complete"]
    assert report["total_packets"] == 0 and report["counts_reconcile"]
    assert report["match_coverage"] is None


def test_empty_capture_has_no_fabricated_coverage(tmp_path):
    paths = inputs(tmp_path)
    with paths[0].open("wb") as stream:
        dpkt.pcap.Writer(stream)
    value = json.loads(paths[2].read_text())
    value["files"][0]["sha256"] = sha256(paths[0])
    paths[2].write_text(json.dumps(value))
    report = audit.audit_capture(*paths)
    assert report["complete"] and report["total_packets"] == 0
    assert report["match_coverage"] is None and report["counts_reconcile"]


@pytest.mark.parametrize("input_index", [0, 1])
def test_rejects_unverified_capture_or_labels(tmp_path, input_index):
    paths = inputs(tmp_path)
    with paths[input_index].open("ab") as stream:
        stream.write(b"corrupt")
    with pytest.raises(ValueError, match="checksum mismatch"):
        audit.audit_capture(*paths)


def test_cli_failed_capture_writes_failed_atomic_report(tmp_path):
    paths = inputs(tmp_path, [(100.2, udp()), (100.1, udp())])
    output = tmp_path / "audit.json"
    assert (
        audit.main(
            [
                "--capture",
                str(paths[0]),
                "--labels",
                str(paths[1]),
                "--manifest",
                str(paths[2]),
                "--output",
                str(output),
            ]
        )
        == 1
    )
    assert json.loads(output.read_text())["status"] == "failed"
    assert not output.with_suffix(".json.tmp").exists()


def test_cli_protects_original_inputs(tmp_path):
    paths = inputs(tmp_path)
    with pytest.raises(SystemExit) as error:
        audit.main(
            [
                "--capture",
                str(paths[0]),
                "--labels",
                str(paths[1]),
                "--manifest",
                str(paths[2]),
                "--output",
                str(paths[0]),
            ]
        )
    assert error.value.code == 2


@pytest.mark.parametrize("cap", [0, -1, 1.5, True, "1"])
def test_invalid_caps(tmp_path, cap):
    with pytest.raises(ValueError, match="positive integer"):
        audit.audit_capture(*inputs(tmp_path), max_packets=cap)
