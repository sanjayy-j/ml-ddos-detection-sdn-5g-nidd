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


def test_table_caption_stays_with_its_complete_table(tmp_path):
    pytest.importorskip("reportlab")
    pdf = pytest.importorskip("pypdf")
    markdown = "\n\n".join(["Pagination fixture paragraph."] * 30)
    markdown += "\n\n#### Results table\n\n| N column | Measurement |\n|---|---|\n"
    markdown += "\n".join(f"| Row {index} | Fixture |" for index in range(6))
    target = tmp_path / "pagination.pdf"
    report.render_pdf(markdown, tmp_path, target)
    pages = [page.extract_text() for page in pdf.PdfReader(target).pages]
    caption_page = next(text for text in pages if "Results table" in text)
    assert "N column" in caption_page
    assert "Row 5" in caption_page
