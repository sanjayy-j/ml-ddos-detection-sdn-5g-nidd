"""Download recovery fixtures are protocol tests, never official dataset evidence."""

import hashlib
import io

import pytest

from scripts import fetch_dataset as downloader


class Response(io.BytesIO):
    def __init__(self, body, status=200, headers=None):
        super().__init__(body)
        self.status = status
        self.headers = headers or {}

    def geturl(self):
        return "https://download.fairdata.fi/fixture"


def setup_download(monkeypatch, payload, response):
    monkeypatch.setattr(
        downloader, "request_json", lambda *args: {"url": "https://download.fairdata.fi/fixture"}
    )
    requests = []

    def open_request(request, **kwargs):
        requests.append(request)
        return response

    monkeypatch.setattr(downloader.urllib.request, "urlopen", open_request)
    return {
        "pathname": "/fixture",
        "size": len(payload),
        "checksum": "sha256:" + hashlib.sha256(payload).hexdigest(),
    }, requests


def test_resume_exact_range_preserves_prefix(tmp_path, monkeypatch):
    payload = b"official-fixture"
    target = tmp_path / "input.zip"
    target.with_suffix(".zip.partial").write_bytes(payload[:5])
    record, requests = setup_download(
        monkeypatch,
        payload,
        Response(payload[5:], 206, {"Content-Range": f"bytes 5-{len(payload) - 1}/{len(payload)}"}),
    )
    downloader.fetch(record, target, resume=True)
    assert target.read_bytes() == payload
    assert requests[0].get_header("Range") == "bytes=5-"


@pytest.mark.parametrize("status,headers", [(200, {}), (206, {"Content-Range": "bytes 0-14/15"})])
def test_ignored_or_wrong_range_never_appends(tmp_path, monkeypatch, status, headers):
    payload = b"official-fixture"
    target = tmp_path / "input.zip"
    partial = target.with_suffix(".zip.partial")
    partial.write_bytes(payload[:5])
    record, _ = setup_download(monkeypatch, payload, Response(payload, status, headers))
    with pytest.raises(ValueError, match="byte range"):
        downloader.fetch(record, target, resume=True)
    assert partial.read_bytes() == payload[:5]
    assert not target.exists()


def test_restart_retains_old_partial(tmp_path, monkeypatch):
    payload = b"official-fixture"
    target = tmp_path / "input.zip"
    target.with_suffix(".zip.partial").write_bytes(b"previous")
    record, _ = setup_download(monkeypatch, payload, Response(payload))
    downloader.fetch(record, target, restart=True)
    assert target.read_bytes() == payload
    assert [p.read_bytes() for p in tmp_path.glob("*.saved-*")] == [b"previous"]


def test_bad_checksum_retains_unverified_partial(tmp_path, monkeypatch):
    payload = b"official-fixture"
    target = tmp_path / "input.zip"
    record, _ = setup_download(monkeypatch, payload, Response(b"x" * len(payload)))
    with pytest.raises(ValueError, match="checksum"):
        downloader.fetch(record, target)
    assert not target.exists()
    assert target.with_suffix(".zip.partial").exists()


def test_complete_partial_verified_without_network(tmp_path, monkeypatch):
    payload = b"official-fixture"
    target = tmp_path / "input.zip"
    target.with_suffix(".zip.partial").write_bytes(payload)
    record, requests = setup_download(monkeypatch, payload, Response(b""))
    downloader.fetch(record, target, resume=True)
    assert target.read_bytes() == payload and not requests
