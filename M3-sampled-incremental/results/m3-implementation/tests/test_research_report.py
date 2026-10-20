import importlib.util
import json
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location("research_report_test",
    Path(__file__).parents[1] / "scripts/build_research_report.py")
report = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(report)


def test_paper_generation_refuses_incomplete_evidence_before_creating_output(tmp_path):
    analysis = tmp_path / "analysis"
    analysis.mkdir()
    (analysis / "research_readiness.json").write_text(json.dumps({"ready": False, "accepted_trials": 1}))
    output, pdf = tmp_path / "publication", tmp_path / "report.pdf"
    with pytest.raises(ValueError, match="all 54"):
        report.build(analysis, tmp_path / "runs", output, pdf)
    assert not output.exists() and not pdf.exists()


def test_statistical_missing_values_remain_explicit():
    assert report.number(None) == "NA"
    assert report.number(0) == "0.000"
