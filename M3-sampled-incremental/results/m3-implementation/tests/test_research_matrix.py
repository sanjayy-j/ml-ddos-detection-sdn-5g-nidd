import importlib.util
import json
from pathlib import Path

import pytest


def load_matrix(monkeypatch):
    folder = Path(__file__).parents[1] / "sdn"
    monkeypatch.syspath_prepend(str(folder))
    spec = importlib.util.spec_from_file_location("research_matrix_test", folder / "run_research_matrix.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_retry_retains_failure_and_never_replaces_completed_cells(monkeypatch):
    module = load_matrix(monkeypatch)
    matrix = {"cells": [{"status": "completed", "run_id": "accepted"},
                        {"status": "failed", "error": "startup deadline", "trial_id": 2}]}
    module.retry_failed(matrix, "Verified manifest lookup optimization; no scored outcome existed")
    assert matrix["cells"][0] == {"status": "completed", "run_id": "accepted"}
    retry = matrix["cells"][1]
    assert retry["status"] == "pending"
    assert retry["attempts"][0]["error"] == "startup deadline"
    assert retry["retry_explanation"]
    with pytest.raises(ValueError):
        module.retry_failed(matrix, " ")


@pytest.mark.parametrize('vote, expected', [(None, 'river'), ('log_space', 'log_space')])
def test_matrix_preserves_frozen_vote_and_propagates_explicit_revision(tmp_path, monkeypatch, vote, expected):
    module = load_matrix(monkeypatch)
    protocol = {'scenarios': ['baseline'], 'sampling_rates': [1], 'model_seeds': [42],
                'ordering_seed': 1, 'model': {} if vote is None else {'naive_bayes': vote}}
    path = tmp_path / 'protocol.json'
    path.write_text(json.dumps(protocol))
    seen = []

    def fake_run(*args, **kwargs):
        seen.append(kwargs['research'])
        return {'collector_run_id': 'a' * 32}

    monkeypatch.setattr(module, 'run', fake_run)
    module.execute(path, tmp_path / 'prepared', tmp_path / 'matrix')
    assert seen[0]['naive_bayes'] == expected


def test_matrix_cannot_resume_under_a_different_vote(tmp_path, monkeypatch):
    module = load_matrix(monkeypatch)
    protocol = {'scenarios': ['baseline'], 'sampling_rates': [1], 'model_seeds': [42],
                'ordering_seed': 1, 'model': {}}
    path = tmp_path / 'protocol.json'
    path.write_text(json.dumps(protocol))
    monkeypatch.setattr(module, 'run', lambda *a, **k: {'collector_run_id': 'a' * 32})
    module.execute(path, tmp_path / 'prepared', tmp_path / 'matrix')
    protocol['model']['naive_bayes'] = 'log_space'
    path.write_text(json.dumps(protocol))
    with pytest.raises(ValueError, match='vote'):
        module.execute(path, tmp_path / 'prepared', tmp_path / 'matrix')


def test_matrix_isolates_collector_results_and_pins_the_directory(tmp_path, monkeypatch):
    module = load_matrix(monkeypatch)
    protocol = {'scenarios': ['baseline'], 'sampling_rates': [1], 'model_seeds': [42],
                'ordering_seed': 1, 'model': {'naive_bayes': 'log_space'}}
    path = tmp_path / 'protocol.json'
    path.write_text(json.dumps(protocol))
    seen = []

    def fake_run(*args, **kwargs):
        seen.append(kwargs)
        return {'collector_run_id': 'b' * 32}

    monkeypatch.setattr(module, 'run', fake_run)
    selected = tmp_path / 'corrected-runs'
    module.execute(path, tmp_path / 'prepared', tmp_path / 'matrix', runs_output=selected)
    assert seen[0]['runs_root'] == str(selected.resolve())
    matrix = json.loads((tmp_path / 'matrix/matrix.json').read_text())
    assert matrix['runs_output'] == str(selected.resolve())
    with pytest.raises(ValueError, match='collector results directory'):
        module.execute(path, tmp_path / 'prepared', tmp_path / 'matrix',
                       runs_output=tmp_path / 'old-runs')
