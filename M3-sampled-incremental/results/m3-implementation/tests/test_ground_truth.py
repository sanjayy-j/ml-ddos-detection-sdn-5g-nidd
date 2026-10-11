import csv

import dpkt
import pytest

from m3.config import RunConfig
from m3.engine import run_replay
from m3.ground_truth import FlowLabels, IntervalIndex, WindowTruth, packet_key


def udp_packet(source=b"\x0a\x00\x00\x01", destination=b"\x0a\x00\x00\x02", sport=123, dport=456):
    udp = dpkt.udp.UDP(sport=sport, dport=dport, data=b"payload")
    udp.ulen = len(udp)
    ip = dpkt.ip.IP(src=source, dst=destination, p=17, data=udp)
    ip.len = len(ip)
    return bytes(dpkt.ethernet.Ethernet(src=b"\x00" * 6, dst=b"\x01" * 6, type=0x0800, data=ip))


def test_numeric_time_tuple_join_and_conflicts(tmp_path):
    path = tmp_path / "test_flow_labels.csv"
    columns = [
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
    with path.open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(columns)
        writer.writerow([100, 101, "10.0.0.1", "10.0.0.2", 123, 456, "udp", 1, "UDPFlood", 128])
        writer.writerow([100.5, 100.6, "10.0.0.1", "10.0.0.2", 123, 456, "udp", 0, "Benign", 256])
    labels = FlowLabels(path)
    assert labels.match(udp_packet(), 100.1) == (1, "UDPFlood")
    assert labels.match(udp_packet(b"\x0a\x00\x00\x02", b"\x0a\x00\x00\x01", 456, 123), 100.1) == (
        1,
        "UDPFlood",
    )
    assert labels.match(udp_packet(), 100.55) == (None, "unknown")
    assert labels.match(udp_packet(), 101.1) == (None, "unknown")
    assert labels.match(udp_packet(sport=999), 100.1) == (None, "unknown")
    assert packet_key(b"invalid") is None


def test_interval_index_matches_brute_force():
    rows = [(float(i), float(i + (20 if i % 5 == 0 else 1)), i % 2, "family") for i in range(200)]
    index = IntervalIndex(rows)
    for time in range(225):
        assert sorted(index.at(time + 0.2)) == sorted(
            row for row in rows if row[0] <= time + 0.2 <= row[1]
        )


def test_window_uses_all_ground_truth_not_sampled_labels():
    truth = WindowTruth()
    assert truth.label() == (0, "Benign")
    truth.add(0, "Benign")
    truth.add(None, "unknown")
    assert truth.label() == (None, "unknown")
    truth.add(1, "SYNFlood")
    assert truth.label() == (1, "SYNFlood")
    assert truth.packets == 3 and truth.unknown == 1


def test_service_names_are_not_guessed(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text(
        "start_epoch,end_epoch,src_ip,dst_ip,src_port,dst_port,protocol,label,attack_family,offset\n100,101,10.0.0.1,10.0.0.2,http,456,udp,1,UDPFlood,128\n"
    )
    with pytest.raises(ValueError, match="service-name"):
        FlowLabels(path)


def test_packet_pipeline_scores_full_ground_truth_before_sampling(tmp_path):
    path = tmp_path / "flow_labels.csv"
    path.write_text(
        "start_epoch,end_epoch,src_ip,dst_ip,src_port,dst_port,protocol,label,attack_family,offset\n100,100.5,10.0.0.1,10.0.0.2,123,456,udp,1,UDPFlood,128\n101,102,10.0.0.1,10.0.0.2,123,456,udp,0,Benign,256\n"
    )
    capture = tmp_path / "fixture.pcap"
    with capture.open("wb") as stream:
        writer = dpkt.pcap.Writer(stream)
        for timestamp, port in [(100, 123), (100.2, 123), (101.2, 123), (103.2, 999)]:
            writer.writepkt(udp_packet(sport=port), timestamp)

    class AlwaysAttack:
        def predict(self, features):
            return 1, 0.9, 0.1

        def learn(self, features, label, predicted, monitor=True):
            return False

    run = run_replay(
        RunConfig(
            mode="pcap_replay",
            input_path=str(capture),
            flow_labels_path=str(path),
            output_root=str(tmp_path / "runs"),
            warmup_seconds=0,
        ),
        fixture=True,
        model=AlwaysAttack(),
    )
    assert run["counts"]["evaluated"] == 3
    assert run["packet_label_coverage"] == {"matched": 3, "unknown": 1, "unjoinable_flow_rows": 0}
    assert run["metrics"]["packets_to_detect"]["value"] == 2
    assert run["metrics"]["detection_time_seconds"]["value"] == 1
    assert run["metrics"]["f1"]["value"] == 0.5
