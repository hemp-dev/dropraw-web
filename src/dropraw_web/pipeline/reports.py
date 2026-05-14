from __future__ import annotations

import csv
import html
import json
from pathlib import Path

from dropraw_web.models import AssetResult, JobSummary


def generate_reports(summary: JobSummary, assets: list[AssetResult]) -> None:
    out_dir = summary.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "job_id": summary.job_id,
        "source": summary.source,
        "provider": summary.provider,
        "output_dir": str(summary.output_dir),
        "preset": summary.preset,
        "started_at": summary.started_at,
        "finished_at": summary.finished_at,
        "total_raw_files": summary.total_raw_files,
        "processed": summary.processed,
        "skipped": summary.skipped,
        "failed": summary.failed,
        "output_files_count": summary.output_files_count,
        "total_input_bytes": summary.total_input_bytes,
        "total_output_bytes": summary.total_output_bytes,
        "estimated_saved_bytes": max(0, summary.total_input_bytes - summary.total_output_bytes),
        "formats": summary.formats,
        "sizes": summary.sizes,
        "errors": [item.model_dump() for item in summary.errors],
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    (out_dir / "assets.json").write_text(json.dumps(_assets_grouped(assets), indent=2, ensure_ascii=False), encoding="utf-8")

    with (out_dir / "report.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(report.keys()))
        writer.writeheader()
        writer.writerow({key: _csv_cell(json.dumps(value) if isinstance(value, list) else value) for key, value in report.items()})

    with (out_dir / "errors.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["rel_path", "error"])
        writer.writeheader()
        for item in summary.errors:
            writer.writerow({key: _csv_cell(value) for key, value in item.model_dump().items()})

    _write_picture_snippets(out_dir, assets)
    _write_report_html(out_dir, report, assets, summary)


def _write_picture_snippets(out_dir: Path, assets: list[AssetResult]) -> None:
    grouped: dict[str, list[AssetResult]] = {}
    for asset in assets:
        if asset.status == "done":
            grouped.setdefault(asset.source_path, []).append(asset)
    chunks = [
        "<!doctype html><html><head><meta charset=\"utf-8\"><title>DropRaw Picture Snippets</title></head><body>\n"
    ]
    for source_path, group in grouped.items():
        avif = sorted([a for a in group if a.format == "avif"], key=lambda a: a.output_size_name)
        webp = sorted([a for a in group if a.format == "webp"], key=lambda a: a.output_size_name)
        jpg = sorted([a for a in group if a.format == "jpg"], key=lambda a: a.output_size_name)
        fallback = (jpg or webp or avif or group)[-1]
        chunks.append(f"<!-- {html.escape(source_path)} -->\n<picture>\n")
        if avif:
            srcset = ", ".join(_srcset_item(out_dir, item) for item in avif)
            chunks.append(f'  <source type="image/avif" srcset="{srcset}">\n')
        if webp:
            srcset = ", ".join(_srcset_item(out_dir, item) for item in webp)
            chunks.append(f'  <source type="image/webp" srcset="{srcset}">\n')
        if jpg:
            srcset = ", ".join(_srcset_item(out_dir, item) for item in jpg)
            chunks.append(f'  <source type="image/jpeg" srcset="{srcset}">\n')
        src = html.escape(Path(fallback.output_path).relative_to(out_dir).as_posix(), quote=True)
        chunks.append(
            f'  <img src="{src}" alt="" '
            f'loading="lazy" width="{fallback.width}" height="{fallback.height}">\n'
        )
        chunks.append("</picture>\n")
    chunks.append("</body></html>\n")
    (out_dir / "picture-snippets.html").write_text("".join(chunks), encoding="utf-8")


def _srcset_item(out_dir: Path, asset: AssetResult) -> str:
    rel = html.escape(Path(asset.output_path).relative_to(out_dir).as_posix(), quote=True)
    if asset.output_size_name.isdigit():
        return f"{rel} {asset.output_size_name}w"
    return rel


def _csv_cell(value: object) -> object:
    if not isinstance(value, str) or not value:
        return value
    if value[0] in ("=", "+", "-", "@"):
        return "'" + value
    return value


def _assets_grouped(assets: list[AssetResult]) -> dict[str, dict[str, object]]:
    grouped: dict[str, dict[str, object]] = {}
    for asset in assets:
        source = grouped.setdefault(
            asset.source_path,
            {
                "source_path": asset.source_path,
                "input_size": asset.input_size,
                "outputs": [],
            },
        )
        source["outputs"].append(
            {
                "path": asset.output_path,
                "relative_path": Path(asset.output_path).name,
                "format": asset.format,
                "responsive_size": asset.output_size_name,
                "width": asset.width,
                "height": asset.height,
                "output_size": asset.output_size,
                "status": asset.status,
                "error": asset.error,
            }
        )
    return grouped


def _write_report_html(out_dir: Path, report: dict[str, object], assets: list[AssetResult], summary: JobSummary) -> None:
    rows = []
    for asset in assets:
        rows.append(
            "<tr>"
            f"<td>{html.escape(asset.source_path)}</td>"
            f"<td>{html.escape(asset.format)}</td>"
            f"<td>{html.escape(asset.output_size_name)}</td>"
            f"<td>{asset.width}x{asset.height}</td>"
            f"<td>{asset.output_size or 0}</td>"
            f"<td>{html.escape(asset.status)}</td>"
            "</tr>"
        )
    error_rows = [
        f"<tr><td>{html.escape(item.rel_path)}</td><td>{html.escape(item.error)}</td></tr>" for item in summary.errors
    ]
    retry_example = (
        f'dropraw convert "{summary.source}" --provider {summary.provider} --out "{summary.output_dir}" '
        f"--preset {summary.preset} --only-failed \"{summary.output_dir / 'dropraw_failed.tsv'}\""
    )
    doc = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>DropRaw Report {html.escape(summary.job_id)}</title>
  <style>
    body {{ font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 32px; color: #17202a; }}
    h1, h2 {{ margin-bottom: 8px; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin: 20px 0; }}
    .metric {{ border: 1px solid #d8dee9; border-radius: 8px; padding: 14px; background: #f9fafb; }}
    .metric strong {{ display: block; font-size: 24px; margin-top: 6px; }}
    table {{ border-collapse: collapse; width: 100%; margin: 12px 0 28px; }}
    th, td {{ border-bottom: 1px solid #e5e7eb; padding: 9px 10px; text-align: left; font-size: 14px; }}
    th {{ background: #f3f4f6; }}
    code {{ background: #f3f4f6; padding: 3px 5px; border-radius: 4px; }}
    .warning {{ background: #fff7ed; border: 1px solid #fed7aa; border-radius: 8px; padding: 12px; }}
  </style>
</head>
<body>
  <h1>DropRaw Report</h1>
  <p>Job <code>{html.escape(summary.job_id)}</code> finished with status: {html.escape('completed_with_errors' if summary.failed else 'completed')}.</p>
  <div class="grid">
    <div class="metric">RAW files<strong>{summary.total_raw_files}</strong></div>
    <div class="metric">Processed<strong>{summary.processed}</strong></div>
    <div class="metric">Skipped<strong>{summary.skipped}</strong></div>
    <div class="metric">Failed<strong>{summary.failed}</strong></div>
    <div class="metric">Output files<strong>{summary.output_files_count}</strong></div>
    <div class="metric">Estimated saved bytes<strong>{report["estimated_saved_bytes"]}</strong></div>
  </div>
  <h2>Outputs</h2>
  <table><thead><tr><th>Source</th><th>Format</th><th>Size</th><th>Dimensions</th><th>Bytes</th><th>Status</th></tr></thead><tbody>{''.join(rows)}</tbody></table>
  <h2>Errors and Failed Files</h2>
  <table><thead><tr><th>Source</th><th>Error</th></tr></thead><tbody>{''.join(error_rows) or '<tr><td colspan="2">No errors</td></tr>'}</tbody></table>
  <div class="warning">
    <strong>Retry command example</strong><br>
    <code>{html.escape(retry_example)}</code>
  </div>
</body>
</html>
"""
    (out_dir / "report.html").write_text(doc, encoding="utf-8")
