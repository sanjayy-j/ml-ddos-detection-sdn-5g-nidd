import importlib.util
from pathlib import Path

import pytest


def load_driver(monkeypatch):
    root = Path(__file__).parents[1]
    monkeypatch.syspath_prepend(str(root / "scripts"))
    spec = importlib.util.spec_from_file_location("corrected_study_test",
                                                root / "scripts/finish_corrected_study.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def pilot():
    return {"status": "completed", "source": "official_realtime_verified",
            "validation": {"accepted": True}, "config": {"naive_bayes": "log_space"},
            "sampling_rate": 1, "research": {"study_role": "validation_pilot"}}


def test_corrected_pipeline_rejects_legacy_and_unvalidated_pilots(monkeypatch):
    module = load_driver(monkeypatch)
    module.require_corrected_run(pilot(), pilot=True)
    for field, value in (("config", {"naive_bayes": "river"}),
                         ("validation", {"accepted": False}),
                         ("source", "provisional_realtime"),
                         ("sampling_rate", 2), ("research", {"study_role": "primary"})):
        candidate = {**pilot(), field: value}
        with pytest.raises(ValueError):
            module.require_corrected_run(candidate, pilot=True)


def test_new_clock_study_cannot_reuse_a_pilot_without_ingestion_proof(monkeypatch):
    module = load_driver(monkeypatch)
    with pytest.raises(ValueError, match="ingestion evidence"):
        module.require_corrected_run(pilot(), pilot=True, telemetry_clock="kernel_receive")


def test_paper_snapshot_detects_changes_without_rewriting_documents(tmp_path, monkeypatch):
    module = load_driver(monkeypatch)
    monkeypatch.setattr(module, "ROOT", tmp_path)
    research = tmp_path / "research"
    research.mkdir()
    paper = research / "M3_Research_Report.md"
    paper.write_text("original paper")
    study = tmp_path / "study"
    study.mkdir()
    assert module.paper_snapshot(study) == 1
    assert paper.read_text() == "original paper"
    paper.write_text("external edit")
    with pytest.raises(ValueError, match="Protected document changed"):
        module.paper_snapshot(study)
    assert paper.read_text() == "external edit"
