"""Synthetic safety checks for the standalone project backup restorer."""

import copy
import hashlib
import importlib.util
import io
import json
import tarfile
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parents[1] / "scripts" / "restore_project_backup.py"
SPEC = importlib.util.spec_from_file_location("project_backup_restore", SCRIPT)
backup = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(backup)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def make_backup(tmp_path, members=None, expected=None, split=29):
    members = members or [("src/example.py", b"print('restored')\n", None)]
    expected = expected if expected is not None else [(n, d) for n, d, t in members]
    assets = tmp_path / "assets"
    assets.mkdir()
    payload = io.BytesIO()
    with tarfile.open(fileobj=payload, mode="w:gz") as archive:
        for name, data, kind in members:
            info = tarfile.TarInfo(name)
            info.size = len(data)
            if kind:
                info.type = kind
                info.linkname = "src/example.py"
            archive.addfile(info, io.BytesIO(data))
    parts = []
    stream = payload.getvalue()
    for index, start in enumerate(range(0, len(stream), split)):
        data = stream[start:start + split]
        name = f"project.tar.gz.part{index:04d}"
        (assets / name).write_bytes(data)
        parts.append({"name": name, "size_bytes": len(data), "sha256": digest(data)})
    files = [
        {"path": n, "size_bytes": len(d), "sha256": digest(d), "archive": "project"}
        for n, d in expected
    ]
    manifest = {
        "schema": "m3-project-backup-v1",
        "repository": "sanjayy-j/ml-ddos-detection-sdn-5g-nidd",
        "release_tag": "m3-backup-2026-10-29",
        "archives": [{"name": "project", "format": "tar.gz.parts", "parts": parts,
                      "files_count": len(files),
                      "uncompressed_bytes": sum(f["size_bytes"] for f in files)}],
        "files": files,
        "excluded": [],
    }
    return manifest, assets


def test_restore_stream_split_inside_gzip_and_tar_headers(tmp_path):
    manifest, assets = make_backup(tmp_path, members=[
        ("src/example.py", b"abc" * 1000, None), ("data/zero", b"", None),
    ], split=7)
    destination = tmp_path / "restored"
    result = backup.restore_backup(manifest, assets, destination)
    assert (destination / "src/example.py").read_bytes() == b"abc" * 1000
    assert (destination / "data/zero").read_bytes() == b""
    assert result["files_count"] == 2
    assert result["uncompressed_bytes"] == 3000
    receipt = json.loads((destination / backup.RECEIPT_NAME).read_text())
    assert receipt["files_count"] == 2


@pytest.mark.parametrize("failure", ["missing", "tampered", "size"])
def test_all_assets_verified_before_destination_created(tmp_path, failure):
    manifest, assets = make_backup(tmp_path)
    part = assets / manifest["archives"][0]["parts"][-1]["name"]
    if failure == "missing":
        part.unlink()
    elif failure == "tampered":
        data = part.read_bytes()
        part.write_bytes(bytes([data[0] ^ 1]) + data[1:])
    else:
        part.write_bytes(part.read_bytes() + b"x")
    destination = tmp_path / "restored"
    with pytest.raises(backup.BackupError):
        backup.restore_backup(manifest, assets, destination)
    assert not destination.exists()


@pytest.mark.parametrize("name", ["../escape", "/absolute", "C:/drive", "a\\b",
                                  "a/../escape", "a//b", "./file", "NUL", "a:stream"])
def test_reject_unsafe_manifest_paths(tmp_path, name):
    manifest, assets = make_backup(tmp_path, members=[(name, b"x", None)])
    with pytest.raises(backup.BackupError):
        backup.restore_backup(manifest, assets, tmp_path / "restored")


@pytest.mark.parametrize("kind", [tarfile.SYMTYPE, tarfile.LNKTYPE, tarfile.DIRTYPE,
                                  tarfile.FIFOTYPE])
def test_reject_non_regular_members(tmp_path, kind):
    manifest, assets = make_backup(tmp_path, members=[("src/example.py", b"", kind)])
    with pytest.raises(backup.BackupError, match="regular"):
        backup.restore_backup(manifest, assets, tmp_path / "restored")


def test_reject_duplicate_tar_member(tmp_path):
    manifest, assets = make_backup(tmp_path,
        members=[("one", b"x", None), ("one", b"x", None)], expected=[("one", b"x")])
    with pytest.raises(backup.BackupError, match="Duplicate"):
        backup.restore_backup(manifest, assets, tmp_path / "restored")


@pytest.mark.parametrize("name", ["../escape", "unlisted"])
def test_reject_unsafe_or_unlisted_tar_member(tmp_path, name):
    manifest, assets = make_backup(tmp_path, members=[(name, b"x", None)],
                                   expected=[("listed", b"x")])
    with pytest.raises(backup.BackupError):
        backup.restore_backup(manifest, assets, tmp_path / "restored")
    assert not (tmp_path / "escape").exists()


def test_reject_missing_member(tmp_path):
    manifest, assets = make_backup(tmp_path, members=[("one", b"x", None)],
                                   expected=[("one", b"x"), ("two", b"y")])
    with pytest.raises(backup.BackupError, match="Missing"):
        backup.restore_backup(manifest, assets, tmp_path / "restored")


def test_refuse_nonempty_destination(tmp_path):
    manifest, assets = make_backup(tmp_path)
    destination = tmp_path / "restored"
    destination.mkdir()
    (destination / "important").write_text("keep")
    with pytest.raises(backup.BackupError, match="empty"):
        backup.restore_backup(manifest, assets, destination)
    assert (destination / "important").read_text() == "keep"


def test_wrong_extracted_hash_does_not_write_success_receipt(tmp_path):
    manifest, assets = make_backup(tmp_path)
    manifest["files"][0]["sha256"] = "0" * 64
    destination = tmp_path / "restored"
    with pytest.raises(backup.BackupError, match="SHA256"):
        backup.restore_backup(manifest, assets, destination)
    assert not (destination / backup.RECEIPT_NAME).exists()


def test_verify_only_hashes_members_and_bundle_without_extracting(tmp_path):
    manifest, assets = make_backup(tmp_path)
    data = b"synthetic git bundle"
    (assets / "history.bundle").write_bytes(data)
    manifest["git_bundle"] = {"name": "history.bundle", "size_bytes": len(data),
                              "sha256": digest(data)}
    destination = tmp_path / "unused"
    result = backup.restore_backup(manifest, assets, destination, verify_only=True)
    assert result["files_count"] == 1
    assert result["assets_count"] == len(manifest["archives"][0]["parts"]) + 1
    assert not destination.exists()
    manifest["files"][0]["sha256"] = "0" * 64
    with pytest.raises(backup.BackupError, match="SHA256"):
        backup.restore_backup(manifest, assets, verify_only=True)


def test_reject_case_colliding_manifest_and_invalid_counts(tmp_path):
    manifest, _ = make_backup(tmp_path)
    duplicate = copy.deepcopy(manifest["files"][0])
    duplicate["path"] = duplicate["path"].upper()
    manifest["files"].append(duplicate)
    with pytest.raises(backup.BackupError):
        backup.validate_manifest(manifest)
    manifest["files"].pop()
    manifest["archives"][0]["files_count"] += 1
    with pytest.raises(backup.BackupError):
        backup.validate_manifest(manifest)


def test_download_verifies_before_rename_and_preserves_failed_partial(tmp_path, monkeypatch):
    manifest, assets = make_backup(tmp_path, split=100000)
    spec = manifest["archives"][0]["parts"][0]
    target = assets / spec["name"]
    data = target.read_bytes()
    target.unlink()
    urls = []
    def fetch(url):
        urls.append(url)
        return io.BytesIO(data)
    monkeypatch.setattr(backup.urllib.request, "urlopen", fetch)
    backup.restore_backup(manifest, assets, verify_only=True, download=True)
    assert target.read_bytes() == data
    assert urls[0].startswith("https://github.com/sanjayy-j/ml-ddos-detection-sdn-5g-nidd/")
    target.unlink()
    monkeypatch.setattr(backup.urllib.request, "urlopen", lambda url: io.BytesIO(b"wrong"))
    with pytest.raises(backup.BackupError):
        backup.restore_backup(manifest, assets, verify_only=True, download=True)
    assert not target.exists()
    assert list(assets.glob("*.partial*"))
