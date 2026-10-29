#!/usr/bin/env python3
"""Restore a manifest-verified M3 GitHub release backup using only Python's stdlib.

Example: python restore_project_backup.py --manifest backup_manifest.json
    --assets downloaded-assets --destination restored-project --download

Release assets are untrusted until their lengths and SHA256 values match the
manifest. Keep the manifest with the backup and obtain it from a trusted source.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import sys
import tarfile
import tempfile
import urllib.parse
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

SCHEMA = "m3-project-backup-v1"
RECEIPT_NAME = ".m3_restore_verification.json"
CHUNK_SIZE = 1024 * 1024
MAX_PART_SIZE = 1024 ** 3


class BackupError(ValueError):
    """A backup did not pass a required safety or integrity check."""


def safe_relative_path(value: str) -> str:
    """Accept only portable, non-ambiguous project-relative POSIX file paths."""
    if not isinstance(value, str) or not value or "\\" in value or ":" in value:
        raise BackupError(f"Unsafe file path: {value!r}")
    if value.startswith("/") or any(ord(c) < 32 for c in value):
        raise BackupError(f"Unsafe file path: {value!r}")
    reserved = {"CON", "PRN", "AUX", "NUL"}
    reserved.update(f"{prefix}{n}" for prefix in ("COM", "LPT") for n in range(1, 10))
    for component in value.split("/"):
        if (component in ("", ".", "..") or component.endswith((".", " "))
                or any(c in component for c in '<>"|?*')
                or component.split(".")[0].upper() in reserved):
            raise BackupError(f"Unsafe file path: {value!r}")
    return value


def _asset_name(value):
    value = safe_relative_path(value)
    if "/" in value:
        raise BackupError(f"Asset name must be a basename: {value!r}")
    return value


def _nonnegative_integer(value, label):
    if type(value) is not int or value < 0:
        raise BackupError(f"Invalid {label}: expected a nonnegative integer")


def _validate_asset(asset):
    if not isinstance(asset, dict):
        raise BackupError("Invalid asset record")
    _asset_name(asset.get("name"))
    _nonnegative_integer(asset.get("size_bytes"), "asset size")
    if not isinstance(asset.get("sha256"), str) or not re.fullmatch(
            r"[0-9a-fA-F]{64}", asset["sha256"]):
        raise BackupError(f"Invalid SHA256 for asset {asset['name']}")


def validate_manifest(manifest):
    """Validate the schema and all cross references before opening assets."""
    if not isinstance(manifest, dict) or manifest.get("schema") != SCHEMA:
        raise BackupError(f"Expected manifest schema {SCHEMA}")
    if not isinstance(manifest.get("repository"), str) or not re.fullmatch(
            r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", manifest["repository"]):
        raise BackupError("Invalid GitHub repository")
    tag = manifest.get("release_tag")
    if not isinstance(tag, str) or not tag or any(ord(c) < 32 for c in tag):
        raise BackupError("Invalid release tag")
    if not isinstance(manifest.get("archives"), list) or not manifest["archives"]:
        raise BackupError("Manifest must contain archives")
    if not isinstance(manifest.get("files"), list):
        raise BackupError("Manifest files must be a list")
    if not isinstance(manifest.get("excluded", []), list):
        raise BackupError("Manifest excluded must be a list")
    archives = {}
    asset_names = set()
    for archive in manifest["archives"]:
        if not isinstance(archive, dict):
            raise BackupError("Invalid archive record")
        name = _asset_name(archive.get("name"))
        if name.casefold() in archives:
            raise BackupError(f"Duplicate archive: {name}")
        archives[name.casefold()] = archive
        if archive.get("format") != "tar.gz.parts":
            raise BackupError(f"Unsupported archive format for {name}")
        _nonnegative_integer(archive.get("files_count"), "archive file count")
        _nonnegative_integer(archive.get("uncompressed_bytes"), "archive byte count")
        parts = archive.get("parts")
        if not isinstance(parts, list) or not parts:
            raise BackupError(f"Archive {name} has no parts")
        for part in parts:
            _validate_asset(part)
            if not 0 < part["size_bytes"] <= MAX_PART_SIZE:
                raise BackupError(f"Invalid part size: {part['name']}")
            if part["name"].casefold() in asset_names:
                raise BackupError(f"Duplicate asset: {part['name']}")
            asset_names.add(part["name"].casefold())
    file_names = set()
    counts = {a["name"]: [0, 0] for a in archives.values()}
    for record in manifest["files"]:
        if not isinstance(record, dict):
            raise BackupError("Invalid file record")
        name = safe_relative_path(record.get("path"))
        if name.casefold() == RECEIPT_NAME.casefold() or name.casefold() in file_names:
            raise BackupError(f"Duplicate or reserved file path: {name}")
        file_names.add(name.casefold())
        _validate_asset({"name": "file", "size_bytes": record.get("size_bytes"),
                         "sha256": record.get("sha256")})
        archive = record.get("archive")
        if not isinstance(archive, str) or archive not in counts:
            raise BackupError(f"Unknown archive for {name}")
        counts[archive][0] += 1
        counts[archive][1] += record["size_bytes"]
    # A path cannot be both a regular file and a parent of another file.
    for name in file_names:
        components = name.split("/")
        if any("/".join(components[:i]) in file_names for i in range(1, len(components))):
            raise BackupError(f"File/directory path collision: {name}")
    for archive in archives.values():
        if counts[archive["name"]] != [archive["files_count"], archive["uncompressed_bytes"]]:
            raise BackupError(f"Manifest counts disagree for {archive['name']}")
    bundle = manifest.get("git_bundle")
    if bundle is not None:
        _validate_asset(bundle)
        if bundle["name"].casefold() in asset_names:
            raise BackupError("Git bundle duplicates an archive asset")
    return manifest


def verify_asset(path, specification):
    """Read an entire regular asset and verify its declared size and SHA256."""
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise BackupError(f"Missing or non-regular asset: {path.name}")
    if path.stat().st_size != specification["size_bytes"]:
        raise BackupError(f"Size mismatch for asset {path.name}")
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(CHUNK_SIZE), b""):
            digest.update(block)
            size += len(block)
    if size != specification["size_bytes"]:
        raise BackupError(f"Size changed while reading asset {path.name}")
    if digest.hexdigest() != specification["sha256"].lower():
        raise BackupError(f"SHA256 mismatch for asset {path.name}")
    return size


def download_asset(manifest, specification, assets):
    """Download one missing public release asset; keep failed partials for diagnosis."""
    assets = Path(assets)
    assets.mkdir(parents=True, exist_ok=True)
    target = assets / specification["name"]
    if target.exists() or target.is_symlink():
        raise BackupError(f"Refusing to replace existing asset {target.name}")
    repository = manifest["repository"]
    tag = urllib.parse.quote(manifest["release_tag"], safe="")
    name = urllib.parse.quote(specification["name"], safe="")
    url = f"https://github.com/{repository}/releases/download/{tag}/{name}"
    with tempfile.NamedTemporaryFile(prefix=target.name + ".partial.", dir=assets,
                                     delete=False) as output:
        partial = Path(output.name)
        try:
            with urllib.request.urlopen(url) as response:
                while block := response.read(CHUNK_SIZE):
                    output.write(block)
        except Exception as error:
            raise BackupError(f"Download failed for {target.name}; partial: {partial.name}") from error
    verify_asset(partial, specification)
    if target.exists() or target.is_symlink():
        raise BackupError(f"Refusing to replace existing asset {target.name}; "
                          f"verified partial: {partial.name}")
    try:
        partial.rename(target)
    except OSError as error:
        raise BackupError(f"Cannot finalize {target.name}; verified partial: {partial.name}") from error
    return target


class ConcatenatedReader(io.RawIOBase):
    """Expose ordered local part files as one forward-only binary stream."""

    def __init__(self, paths):
        super().__init__()
        self.paths = iter(paths)
        self.current = None

    def readable(self):
        return True

    def readinto(self, buffer):
        view = memoryview(buffer)
        total = 0
        while total < len(view):
            if self.current is None:
                path = next(self.paths, None)
                if path is None:
                    break
                self.current = Path(path).open("rb")  # noqa: SIM115 - owned by reader.close()
            count = self.current.readinto(view[total:])
            if not count:
                self.current.close()
                self.current = None
            else:
                total += count
        return total

    def close(self):
        if self.current is not None:
            self.current.close()
            self.current = None
        super().close()


def verify_archive(archive, records, assets, destination=None):
    """Verify every tar member, optionally restoring regular file bytes."""
    expected = {r["path"]: r for r in records}
    seen = set()
    size_total = 0
    paths = [Path(assets) / p["name"] for p in archive["parts"]]
    try:
        with (
            io.BufferedReader(ConcatenatedReader(paths)) as combined,
            tarfile.open(fileobj=combined, mode="r|gz") as stream,
        ):
            for member in stream:
                name = safe_relative_path(member.name)
                if not member.isreg():
                    raise BackupError(f"Archive member is not a regular file: {name}")
                if name in seen:
                    raise BackupError(f"Duplicate archive member: {name}")
                if name not in expected:
                    raise BackupError(f"Unlisted archive member: {name}")
                record = expected[name]
                if member.size != record["size_bytes"]:
                    raise BackupError(f"Size mismatch for member {name}")
                digest = hashlib.sha256()
                count = 0
                output = None
                try:
                    if destination is not None:
                        target = Path(destination).joinpath(*name.split("/"))
                        target.parent.mkdir(parents=True, exist_ok=True)
                        if target.parent.resolve() != Path(destination).resolve() and not (
                                Path(destination).resolve() in target.parent.resolve().parents):
                            raise BackupError(f"Member escapes destination: {name}")
                        output = target.open("xb")
                    with stream.extractfile(member) as source:
                        while block := source.read(CHUNK_SIZE):
                            digest.update(block)
                            count += len(block)
                            if output is not None:
                                output.write(block)
                finally:
                    if output is not None:
                        output.close()
                if count != record["size_bytes"]:
                    raise BackupError(f"Size mismatch for member {name}")
                if digest.hexdigest() != record["sha256"].lower():
                    raise BackupError(f"SHA256 mismatch for member {name}")
                seen.add(name)
                size_total += count
    except (tarfile.TarError, EOFError, OSError) as error:
        raise BackupError(f"Cannot read/restore archive {archive['name']}: {error}") from error
    missing = expected.keys() - seen
    if missing:
        raise BackupError(f"Missing {len(missing)} archive members in {archive['name']}: "
                          f"{min(missing)}")
    return len(seen), size_total


def restore_backup(manifest, assets, destination=None, *, download=False, verify_only=False):
    """Verify all release assets, then verify or restore all declared archive files."""
    validate_manifest(manifest)
    assets = Path(assets)
    if not verify_only:
        if destination is None:
            raise BackupError("A destination is required for restoration")
        destination = Path(destination)
        if destination.is_symlink() or (destination.exists() and (
                not destination.is_dir() or any(destination.iterdir()))):
            raise BackupError("Restore destination must be new or empty")
    specifications = [p for a in manifest["archives"] for p in a["parts"]]
    if manifest.get("git_bundle") is not None:
        specifications.append(manifest["git_bundle"])
    asset_bytes = 0
    for specification in specifications:
        path = assets / specification["name"]
        if not path.exists() and not path.is_symlink() and download:
            download_asset(manifest, specification, assets)
        asset_bytes += verify_asset(path, specification)
    if not verify_only:
        destination.mkdir(parents=True, exist_ok=True)
        if any(destination.iterdir()):
            raise BackupError("Restore destination must remain empty before extraction")
    count = size = 0
    for archive in manifest["archives"]:
        records = [r for r in manifest["files"] if r["archive"] == archive["name"]]
        files_count, file_bytes = verify_archive(
            archive, records, assets, None if verify_only else destination)
        count += files_count
        size += file_bytes
    result = {"schema": "m3-project-restore-verification-v1", "backup_schema": SCHEMA,
              "repository": manifest["repository"], "release_tag": manifest["release_tag"],
              "verified_at_utc": datetime.now(UTC).isoformat(),
              "files_count": count, "uncompressed_bytes": size,
              "archives_count": len(manifest["archives"]),
              "assets_count": len(specifications), "asset_bytes": asset_bytes,
              "git_bundle_verified": manifest.get("git_bundle") is not None,
              "verify_only": verify_only}
    if not verify_only:
        with (destination / RECEIPT_NAME).open("x", encoding="utf-8") as receipt:
            json.dump(result, receipt, indent=2)
            receipt.write("\n")
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--assets", type=Path, required=True)
    parser.add_argument("--destination", type=Path)
    parser.add_argument("--download", action="store_true",
                        help="Download missing public GitHub release assets")
    parser.add_argument("--verify-only", action="store_true",
                        help="Verify asset and member bytes without extracting a project")
    args = parser.parse_args(argv)
    try:
        with args.manifest.open(encoding="utf-8") as source:
            manifest = json.load(source)
        result = restore_backup(manifest, args.assets, args.destination,
                                download=args.download, verify_only=args.verify_only)
    except (BackupError, OSError, ValueError) as error:
        print(f"Backup verification failed: {error}", file=sys.stderr)
        return 1
    operation = "Verified" if args.verify_only else "Restored and verified"
    print(f"{operation} {result['files_count']} files / {result['uncompressed_bytes']} bytes; "
          f"{result['assets_count']} assets / {result['asset_bytes']} bytes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
