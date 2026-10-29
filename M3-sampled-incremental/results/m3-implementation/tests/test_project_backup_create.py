"""Backup producer/consumer interoperability using synthetic local file trees."""
import importlib.util
from pathlib import Path

import pytest


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).parents[1] / 'scripts' / filename)
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


def test_created_parts_restore_all_authored_files_and_exclude_runtime_caches(tmp_path, monkeypatch):
    producer = module('backup_producer_test', 'create_project_backup.py')
    consumer = module('backup_consumer_create_test', 'restore_project_backup.py')
    monkeypatch.setattr(producer.subprocess, 'check_output', lambda *a, **k: 'fixture-commit\n')
    source, assets = tmp_path / 'source', tmp_path / 'assets'
    authored = {'src/model.py': b'example model\n', 'tmp/build_report.py': b'authored helper\n',
                'data/raw/capture.bin': bytes(range(256)) * 5}
    for name, value in {**authored, 'node_modules/cache.txt': b'reinstallable',
                        '.venv/cache.txt': b'reinstallable', '.git/config': b'local metadata'}.items():
        file = source / name
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_bytes(value)
    manifest = producer.create(source, assets, tmp_path / 'manifest.json',
                               repository='example/research', tag='fixture', part_size=64)
    assert {r['path'] for r in manifest['files']} == set(authored)
    assert any(len(a['parts']) > 1 for a in manifest['archives'])
    restored = tmp_path / 'restored'
    receipt = consumer.restore_backup(manifest, assets, restored)
    assert receipt['files_count'] == len(authored)
    assert all((restored / name).read_bytes() == value for name, value in authored.items())


def test_backup_refuses_to_overwrite_existing_parts(tmp_path):
    producer = module('backup_producer_existing_test', 'create_project_backup.py')
    assets = tmp_path / 'assets'
    assets.mkdir()
    saved = assets / 'previous.tar.gz.part001'
    saved.write_bytes(b'prior backup')
    with pytest.raises(ValueError, match='overwrite'):
        producer.create(tmp_path, assets, tmp_path / 'manifest.json', repository='a/b', tag='fixture')
    assert saved.read_bytes() == b'prior backup'


def test_file_mutation_never_produces_a_complete_manifest(tmp_path, monkeypatch):
    producer = module('backup_producer_mutation_test', 'create_project_backup.py')
    source = tmp_path / 'source'
    source.mkdir()
    file = source / 'changing.txt'
    file.write_bytes(b'first version')
    monkeypatch.setattr(producer.subprocess, 'check_output', lambda *a, **k: 'fixture-commit\n')
    original_read = producer.HashingReader.read

    def mutate(reader, size=-1):
        data = original_read(reader, size)
        file.write_bytes(b'a different version, changed while snapshotting')
        return data

    monkeypatch.setattr(producer.HashingReader, 'read', mutate)
    manifest_path = tmp_path / 'manifest.json'
    with pytest.raises(ValueError, match='changed while archiving'):
        producer.create(source, tmp_path / 'assets', manifest_path, repository='a/b', tag='fixture')
    assert not manifest_path.exists()
