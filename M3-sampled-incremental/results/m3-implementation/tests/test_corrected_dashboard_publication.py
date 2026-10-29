import importlib.util
import json
from pathlib import Path

import pytest


def fixture_study(tmp_path, monkeypatch):
    spec = importlib.util.spec_from_file_location(
        "corrected_dashboard_test", Path(__file__).parents[1] / "scripts/publish_corrected_dashboard.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, "ROOT", tmp_path)
    study = tmp_path / "output/study"
    dashboard = tmp_path / "output/published-study"
    for directory in (study / "analysis", study / "matrix", dashboard, tmp_path / "research/results"):
        directory.mkdir(parents=True)
    (dashboard / "old-result.txt").write_text("retained original display")
    status = {"phase": "complete", "study_id": "test-only", "source_revision": "fixture"}
    (study / "study_status.json").write_text(json.dumps(status))
    (study / "analysis/research_readiness.json").write_text(json.dumps({"ready": True}))
    (study / "paper_snapshot.json").write_text("{}")
    (study / "source_sha256.json").write_text("{}")
    (study / "trial_index.json").write_text("[]")
    cells = []
    for number in range(54):
        run_id = f"{number:032x}"
        cells.append({"run_id": run_id, "status": "completed"})
        folder = study / "runs" / run_id
        folder.mkdir(parents=True)
        summary = {"run_id": run_id, "status": "completed", "source": "official_realtime_verified",
                   "config": {"naive_bayes": "log_space"}, "validation": {"accepted": True}}
        for name in module.DERIVED_FILES:
            (folder / name).write_text(json.dumps(summary) if name == "run_summary.json" else "fixture\n")
    (study / "matrix/matrix.json").write_text(json.dumps({"cells": cells, "protocol": {}}))
    return module, study, dashboard


def test_handoff_waits_for_complete_analysis_and_keeps_current_dashboard(tmp_path, monkeypatch):
    module, study, dashboard = fixture_study(tmp_path, monkeypatch)
    (study / "analysis/research_readiness.json").write_text('{"ready":false}')
    with pytest.raises(ValueError, match="passing analysis gates"):
        module.publish(study, dashboard)
    assert (dashboard / "old-result.txt").read_text() == "retained original display"
    assert not (study / "previous_dashboard").exists()


def test_handoff_preserves_previous_display_and_installs_matching_predictions(tmp_path, monkeypatch):
    module, study, dashboard = fixture_study(tmp_path, monkeypatch)
    module.publish(study, dashboard)
    assert len(list(dashboard.glob("*/run_summary.json"))) == 54
    assert (study / "previous_dashboard/old-result.txt").read_text() == "retained original display"
    for path in dashboard.glob("*/*"):
        assert path.read_bytes() == (study / "runs" / path.parent.name / path.name).read_bytes()
    assert json.loads((study / "publication_status.json").read_text())["phase"] == "complete"
    results = tmp_path / "research/results/corrected_log_space_20261028"
    for path in results.iterdir():
        if path.suffix in {".json", ".csv"}:
            assert b"\r\n" not in path.read_bytes()
    module.publish(study, dashboard)  # Repeating a successful handoff is safe.
