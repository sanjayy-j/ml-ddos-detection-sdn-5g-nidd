import json
import struct

import pytest

from m3.live_supervision import FrameLabels, restore_vlan, reveal_truth, truth_payload


def test_conflicting_full_frame_labels_rejected():
    with pytest.raises(ValueError, match="conflict"):
        FrameLabels([(b"same", "Benign"), (b"same", "SYNFlood")])


def test_truth_unknown_is_not_benign():
    assert truth_payload([], 0, 1)["label"] is None
    assert truth_payload([None, "Benign"], 0, 1)["label"] is None
    assert truth_payload(["Benign"], 0, 1)["label"] == 0
    assert truth_payload(["SYNFlood"], 0, 1)["label"] == 1
    assert truth_payload(["SYNFlood", "Benign"], 0, 1)["label"] is None


def test_label_must_be_available_only_after_prediction(tmp_path):
    path = tmp_path / "0.json"
    path.write_text(json.dumps({"label": 1, "available_epoch": 9, "end_epoch": 8}))
    with pytest.raises(ValueError, match="prediction"):
        reveal_truth(path, prediction_epoch=7, read_epoch=10)
    assert reveal_truth(path, prediction_epoch=9.5, read_epoch=10)["label"] == 1
    with pytest.raises(ValueError, match="clock"):
        reveal_truth(path, prediction_epoch=11, read_epoch=10)


def test_source_prefix_matching_requires_unique_family():
    labels = FrameLabels([(b"a" * 60, "Benign"), (b"b" * 60, "UDPFlood")])
    assert labels.match(b"a" * 60) == "Benign"
    assert labels.match(b"unknown") is None


def test_vlan_offload_restored_from_authoritative_kernel_auxdata():
    frame = b"m" * 12 + b"\x08\x00" + b"payload"
    auxiliary = struct.pack("=IIIHHHH", 16 | 64, len(frame), len(frame), 0, 14, 610, 0x8100)
    assert restore_vlan(frame, auxiliary) == frame[:12] + b"\x81\x00\x02\x62" + frame[12:]
    assert restore_vlan(frame, struct.pack("=IIIHHHH", 0, 0, 0, 0, 0, 0, 0)) == frame
    with pytest.raises(ValueError, match="auxdata"):
        restore_vlan(frame, b"short")
