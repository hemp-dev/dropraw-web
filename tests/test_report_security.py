from pathlib import Path

from dropraw_web.models import AssetResult, FailedItem, JobSummary
from dropraw_web.pipeline.reports import generate_reports


def test_picture_snippets_escape_attribute_values(tmp_path):
    dangerous_name = 'bad" onerror="alert(1).webp'
    asset = AssetResult(
        source_path="source.NEF",
        output_path=str(tmp_path / dangerous_name),
        format="webp",
        width=10,
        height=10,
        output_size=12,
        status="done",
    )
    summary = JobSummary(job_id="job1", source="local", provider="local", output_dir=tmp_path, preset="web")

    generate_reports(summary, [asset])

    snippets = (tmp_path / "picture-snippets.html").read_text(encoding="utf-8")
    assert '&quot; onerror=&quot;alert(1).webp' in snippets
    assert 'src="bad" onerror=' not in snippets


def test_csv_reports_escape_formula_like_cells(tmp_path):
    summary = JobSummary(
        job_id="job1",
        source="=HYPERLINK(\"https://example.invalid\")",
        provider="local",
        output_dir=tmp_path,
        preset="web",
        errors=[FailedItem(rel_path="@bad.NEF", error="+cmd")],
    )

    generate_reports(summary, [])

    report_csv = (tmp_path / "report.csv").read_text(encoding="utf-8")
    errors_csv = (tmp_path / "errors.csv").read_text(encoding="utf-8")
    assert "'=HYPERLINK" in report_csv
    assert "'@bad.NEF" in errors_csv
    assert "'+cmd" in errors_csv
