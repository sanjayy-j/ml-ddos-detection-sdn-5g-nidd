import importlib.util
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
