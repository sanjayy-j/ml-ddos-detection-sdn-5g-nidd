"""Snapshot project-owned bytes into bounded release assets without deleting inputs."""
import argparse
import hashlib
import json
import os
import subprocess
import tarfile
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

SCHEMA = 'm3-project-backup-v1'
CACHE_NAMES = {'.git', 'node_modules', '__pycache__', '.pytest_cache', '.ruff_cache', '.npm-cache'}
METADATA = {'BACKUP_MANIFEST.json', 'BACKUP_VERIFICATION.json'}


def is_link(path):
    # Windows does not classify WSL's LX_SYMLINK reparse tag as a Path symlink.
    # Do not classify OneDrive's CLOUD placeholders as links: their bytes matter.
    tag = getattr(path.lstat(), 'st_reparse_tag', 0)
    return path.is_symlink() or path.is_junction() or tag in {0xA000000C, 0xA0000003, 0xA000001D}


def checksum(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


class SplitWriter:
    def __init__(self, directory, stem, limit):
        self.directory, self.stem, self.limit = directory, stem, limit
        self.parts, self.stream, self.size, self.total, self.digest = [], None, 0, 0, None

    def finish_part(self):
        if self.stream is not None:
            self.stream.close()
            self.parts.append({'name': self.name, 'size_bytes': self.size,
                               'sha256': self.digest.hexdigest()})
            self.stream = None

    def write(self, data):
        data = memoryview(data)
        size = len(data)
        while data:
            if self.stream is None:
                self.name = f'{self.stem}.tar.gz.part{len(self.parts) + 1:03d}'
                self.stream = (self.directory / self.name).open('xb')
                self.size, self.digest = 0, hashlib.sha256()
            length = min(len(data), self.limit - self.size)
            self.stream.write(data[:length])
            self.digest.update(data[:length])
            self.size += length
            self.total += length
            data = data[length:]
            if self.size == self.limit:
                self.finish_part()
        return size

    def flush(self):
        if self.stream is not None:
            self.stream.flush()

    def close(self):
        self.finish_part()


class HashingReader:
    def __init__(self, stream):
        self.stream, self.digest, self.count = stream, hashlib.sha256(), 0

    def read(self, size=-1):
        block = self.stream.read(size)
        self.digest.update(block)
        self.count += len(block)
        return block


def collect(root, output, excluded_root):
    groups, excluded = defaultdict(list), []
    for directory, dirs, files in os.walk(root, followlinks=False):
        base = Path(directory)
        for name in list(dirs):
            path = base / name
            relative = path.relative_to(root).as_posix()
            reason = None
            if is_link(path):
                reason = 'junction or symbolic link; target is outside the portable file snapshot'
            elif name in CACHE_NAMES or name.endswith('.egg-info'):
                reason = 'Git internals, installed dependencies or regenerable cache'
            elif base == root and (name.startswith('.venv') or name == '.tools'):
                reason = 'reinstallable Python environment or downloaded tool runtime'
            elif path.resolve() == output or relative == excluded_root:
                reason = 'backup self-reference and transfer working directory'
            if reason:
                dirs.remove(name)
                excluded.append({'path': relative, 'reason': reason})
        for name in files:
            path = base / name
            relative = path.relative_to(root).as_posix()
            if is_link(path) or (base == root and name in METADATA):
                excluded.append({'path': relative, 'reason': 'link or separately published backup metadata'})
                continue
            if name.endswith(('.pyc', '.pyo')) or name in {'.coverage', '.DS_Store'}:
                excluded.append({'path': relative, 'reason': 'regenerable cache'})
                continue
            if relative.startswith('data/raw/'):
                group = 'm3-original-data'
            elif relative.startswith('data/prepared/'):
                group = 'm3-prepared-data'
            elif relative.startswith('output/'):
                group = 'm3-experiment-evidence'
            elif relative.startswith('tmp/'):
                group = 'm3-authored-temporary-work'
            else:
                group = 'm3-project-files'
            groups[group].append(path)
    return groups, excluded


def create(root, output, manifest_path, *, repository, tag, bundle=None,
           exclude_root='tmp/github_backup_20261029', part_size=128 * 1024**2):
    root, output, manifest_path = root.resolve(), output.resolve(), manifest_path.resolve()
    if not 1 <= part_size < 2 * 1024**3:
        raise ValueError('Archive parts must be positive and smaller than 2 GiB')
    output.mkdir(parents=True, exist_ok=True)
    if list(output.glob('*.part*')):
        raise ValueError('Refusing to overwrite existing backup archive parts')
    groups, excluded = collect(root, output, exclude_root)
    manifest = {'schema': SCHEMA, 'repository': repository, 'release_tag': tag,
                'created_utc': datetime.now(UTC).isoformat(),
                'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip(),
                'scope': 'Project folder only; environments/dependencies are reinstalled separately',
                'archives': [], 'files': [], 'excluded': excluded}
    for group, paths in sorted(groups.items()):
        paths.sort(key=lambda p: p.relative_to(root).as_posix())
        writer = SplitWriter(output, group, part_size)
        total = 0
        print(json.dumps({'phase': 'archive', 'group': group, 'files': len(paths),
                          'input_bytes': sum(p.stat().st_size for p in paths)}), flush=True)
        try:
            with tarfile.open(fileobj=writer, mode='w|gz', compresslevel=1,
                              format=tarfile.PAX_FORMAT, bufsize=1024 * 1024) as archive:
                for number, path in enumerate(paths, 1):
                    before = path.stat()
                    relative = path.relative_to(root).as_posix()
                    info = archive.gettarinfo(str(path), arcname=relative)
                    if not info.isfile():
                        raise ValueError(f'Only regular project files may be backed up: {relative}')
                    info.uid = info.gid = 0
                    info.uname = info.gname = ''
                    with path.open('rb') as stream:
                        source = HashingReader(stream)
                        archive.addfile(info, source)
                    after = path.stat()
                    if (source.count != before.st_size or before.st_size != after.st_size
                            or before.st_mtime_ns != after.st_mtime_ns):
                        raise ValueError(f'File changed while archiving: {relative}')
                    manifest['files'].append({'path': relative, 'size_bytes': source.count,
                                              'sha256': source.digest.hexdigest(), 'archive': group})
                    total += source.count
                    if number % 1000 == 0:
                        print(json.dumps({'phase': 'archive', 'group': group,
                                          'files_completed': number, 'total_files': len(paths)}), flush=True)
        finally:
            writer.close()
        manifest['archives'].append({'name': group, 'format': 'tar.gz.parts',
                                     'parts': writer.parts, 'files_count': len(paths),
                                     'uncompressed_bytes': total})
    if bundle is not None:
        bundle = bundle.resolve()
        manifest['git_bundle'] = {'name': bundle.name, 'size_bytes': bundle.stat().st_size,
                                  'sha256': checksum(bundle)}
    manifest_path.write_bytes((json.dumps(manifest, indent=2) + '\n').encode('utf8'))
    print(json.dumps({'phase': 'complete', 'files': len(manifest['files']),
                      'bytes': sum(f['size_bytes'] for f in manifest['files']),
                      'parts': sum(len(a['parts']) for a in manifest['archives']),
                      'manifest': str(manifest_path)}), flush=True)
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path('.'))
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--manifest', type=Path, default=Path('BACKUP_MANIFEST.json'))
    parser.add_argument('--repository', default='sanjayy-j/ml-ddos-detection-sdn-5g-nidd')
    parser.add_argument('--tag', default='m3-backup-2026-10-29')
    parser.add_argument('--bundle', type=Path)
    args = parser.parse_args()
    create(args.root, args.output, args.manifest, repository=args.repository,
           tag=args.tag, bundle=args.bundle)
