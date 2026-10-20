"""Manifest lookup avoids unrelated filesystem traversal without skipping hashes."""

import hashlib
import json
from pathlib import Path

import pytest

from m3.provenance import OFFICIAL_DOI, verify_input


def test_direct_registered_path_does_not_resolve_unrelated_entries(tmp_path, monkeypatch):
    source, manifest = tmp_path / "input.bin", tmp_path / "manifest.json"
    source.write_bytes(b"fixture")
    unrelated = tmp_path / "unrelated.bin"
    manifest.write_text(json.dumps({"dataset": "5G-NIDD", "doi": OFFICIAL_DOI,
        "status": "verified", "files": [{"path": str(unrelated), "sha256": "unused"},
        {"path": str(source), "sha256": hashlib.sha256(b"fixture").hexdigest()}]}))
    original = Path.resolve

    def resolve(path, *args, **kwargs):
        if path == unrelated:
            raise AssertionError("Unrelated entry should not touch the filesystem")
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "resolve", resolve)
    assert verify_input(source, manifest)["sha256"] == hashlib.sha256(b"fixture").hexdigest()
    source.write_bytes(b"changed")
    with pytest.raises(ValueError, match="checksum"):
        verify_input(source, manifest)
