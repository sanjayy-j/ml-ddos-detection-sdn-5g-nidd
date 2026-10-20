import hashlib
import importlib.util
import json
import zipfile
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location("frozen_annotation_test",
    Path(__file__).parents[1] / "scripts/restore_frozen_labels.py")
annotations = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(annotations)


def test_restore_checks_all_files_before_writing_and_preserves_different_existing(tmp_path):
    names = [f"BS2_{family}_flow_labels.csv" for family in ("SYNFlood", "ICMPFlood", "UDPFlood")]
    archive, manifest, target = tmp_path / "labels.zip", tmp_path / "manifest.json", tmp_path / "prepared"
    with zipfile.ZipFile(archive, "w") as stream:
        for name in names:
            stream.writestr(name, b"fixture")
        stream.writestr("../not_extracted.txt", b"must not be extracted")
    manifest.write_text(json.dumps({"files": [{"path": "data/prepared/" + name,
        "sha256": hashlib.sha256(b"fixture").hexdigest()} for name in names]}))
    assert annotations.restore(archive, manifest, target) == names
    assert not (tmp_path / "not_extracted.txt").exists()
    (target / names[1]).write_bytes(b"different existing input")
    with pytest.raises(ValueError, match="retained"):
        annotations.restore(archive, manifest, target)
    assert (target / names[1]).read_bytes() == b"different existing input"


def test_prepared_verification_rejects_unsafe_and_changed_paths(tmp_path):
    archive, target = tmp_path / "expected.zip", tmp_path / "prepared"
    target.mkdir()
    (target / "file.pcap").write_bytes(b"fixture")
    with zipfile.ZipFile(archive, "w") as stream:
        stream.writestr("expected_prepared_sha256.json", json.dumps({
            "file.pcap": hashlib.sha256(b"fixture").hexdigest()}))
    assert annotations.verify_prepared(archive, target) == 1
    (target / "file.pcap").write_bytes(b"changed")
    with pytest.raises(ValueError, match="differs"):
        annotations.verify_prepared(archive, target)
    with zipfile.ZipFile(archive, "w") as stream:
        stream.writestr("expected_prepared_sha256.json", json.dumps({"../outside": "bad"}))
    with pytest.raises(ValueError, match="unsafe"):
        annotations.verify_prepared(archive, target)
