from __future__ import annotations

import json
import platform
import shutil
import sys
from pathlib import Path
from typing import Optional

import typer
from PIL import features
from rich.console import Console
from rich.table import Table

from dropraw_web import __version__
from dropraw_web.config import parse_csv_list, parse_int_csv, resolve_preset
from dropraw_web.logging import configure_logging
from dropraw_web.models import JobConfig
from dropraw_web.pipeline.converter import config_from_job_row, run_conversion
from dropraw_web.pipeline.manifest import Manifest
from dropraw_web.pipeline.scanner import detect_provider

app = typer.Typer(help="DropRaw Web: convert RAW folders into optimized web images.")
console = Console()


def _version_callback(value: bool) -> None:
    if value:
        console.print(f"dropraw-web {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(False, "--version", callback=_version_callback, is_eager=True, help="Show version and exit."),
) -> None:
    """DropRaw Web command line interface."""


@app.command()
def ui(
    host: str = typer.Option("127.0.0.1", "--host"),
    port: int = typer.Option(8787, "--port"),
    open_browser: bool = typer.Option(True, "--open-browser/--no-open-browser"),
) -> None:
    """Start the local DropRaw Web UI."""
    try:
        from dropraw_web.ui.server import run_ui
    except RuntimeError as exc:
        raise typer.BadParameter(str(exc)) from exc
    run_ui(host=host, port=port, open_browser=open_browser)


@app.command()
def doctor(out: Path = typer.Option(Path("."), "--out", help="Directory for writeability check.")) -> None:
    table = Table("Check", "Status", "Details")
    py = sys.version_info
    table.add_row("Python", "ok" if (3, 11) <= py[:2] <= (3, 12) else "warning", platform.python_version())
    if py[:2] >= (3, 13):
        table.add_row("Python version", "warning", "Use Python 3.11 or 3.12 for the v0.1.x release line.")
    for name in ("rawpy", "dropbox"):
        try:
            module = __import__(name)
            table.add_row(name, "ok", getattr(module, "__version__", "installed"))
        except Exception as exc:  # noqa: BLE001
            table.add_row(name, "missing", str(exc))
    table.add_row("Pillow", "ok", __import__("PIL").__version__)
    table.add_row("WebP", "ok" if features.check("webp") else "missing", str(features.check("webp")))
    table.add_row("AVIF", "ok" if features.check("avif") else "optional", str(features.check("avif")))
    try:
        out.mkdir(parents=True, exist_ok=True)
        probe = out / ".dropraw_write_test"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
        table.add_row("Output writable", "ok", str(out.resolve()))
    except Exception as exc:  # noqa: BLE001
        table.add_row("Output writable", "failed", str(exc))
    table.add_row("Dropbox token", "ok" if _has_dropbox_token() else "missing", "DROPBOX_ACCESS_TOKEN")
    console.print(table)


@app.command()
def scan(
    source: str,
    provider: str = typer.Option("auto", "--provider"),
    limit: int = typer.Option(20, "--limit"),
    list_retries: int = typer.Option(8, "--list-retries"),
    retry_delay: float = typer.Option(3.0, "--retry-delay"),
    dropbox_token: Optional[str] = typer.Option(None, "--dropbox-token"),
) -> None:
    storage = detect_provider(source, provider, token=dropbox_token, list_retries=list_retries, retry_delay=retry_delay)
    files = list(storage.list_files(source))
    table = Table("Path", "Size")
    for file in files[:limit]:
        table.add_row(file.path, str(file.size or ""))
    console.print(f"Provider: [bold]{storage.name}[/bold]")
    console.print(f"RAW count: {len(files)}")
    console.print(f"Estimated total size: {sum(file.size or 0 for file in files)} bytes")
    console.print(table)


@app.command()
def convert(
    source: str,
    provider: str = typer.Option("auto", "--provider"),
    out: Path = typer.Option(Path("web_export"), "--out"),
    preset: str = typer.Option("web", "--preset"),
    format: Optional[str] = typer.Option(None, "--format"),
    max_size: Optional[int] = typer.Option(None, "--max-size"),
    responsive_sizes: Optional[str] = typer.Option(None, "--responsive-sizes"),
    quality: Optional[int] = typer.Option(None, "--quality"),
    overwrite: bool = typer.Option(False, "--overwrite"),
    resume: bool = typer.Option(True, "--resume/--no-resume"),
    only_failed: Optional[Path] = typer.Option(None, "--only-failed"),
    list_retries: int = typer.Option(8, "--list-retries"),
    download_retries: int = typer.Option(8, "--download-retries"),
    retry_delay: float = typer.Option(3.0, "--retry-delay"),
    cooldown: float = typer.Option(0.3, "--cooldown"),
    download_workers: int = typer.Option(2, "--download-workers"),
    convert_workers: int = typer.Option(2, "--convert-workers"),
    metadata: Optional[str] = typer.Option(None, "--metadata"),
    config: Optional[Path] = typer.Option(None, "--config"),
    dry_run: bool = typer.Option(False, "--dry-run"),
    verbose: bool = typer.Option(False, "--verbose"),
    dropbox_token: Optional[str] = typer.Option(None, "--dropbox-token"),
) -> None:
    configure_logging(verbose)
    job_config = JobConfig(
        source=source,
        provider=provider,
        output_dir=out,
        preset=preset,
        formats=parse_csv_list(format),
        max_size=max_size,
        responsive_sizes=parse_int_csv(responsive_sizes),
        quality=quality,
        overwrite=overwrite,
        resume=resume,
        only_failed=only_failed,
        list_retries=list_retries,
        download_retries=download_retries,
        retry_delay=retry_delay,
        cooldown=cooldown,
        download_workers=download_workers,
        convert_workers=convert_workers,
        metadata_mode=metadata,
        dry_run=dry_run,
        verbose=verbose,
        dropbox_token=dropbox_token,
    )
    summary = run_conversion(job_config, config_file=config)
    _print_summary(summary)


@app.command()
def resume(job_id: str) -> None:
    manifest = _find_manifest_for_job(job_id)
    if manifest is None:
        raise typer.BadParameter(f"Job not found: {job_id}")
    with Manifest(manifest.parent) as db:
        row = db.get_job(job_id)
        if row is None:
            raise typer.BadParameter(f"Job not found: {job_id}")
        config = config_from_job_row(row)
    summary = run_conversion(config, job_id=job_id)
    _print_summary(summary)


@app.command()
def report(job_id: str) -> None:
    manifest = _find_manifest_for_job(job_id)
    if manifest is None:
        raise typer.BadParameter(f"Job not found: {job_id}")
    with Manifest(manifest.parent) as db:
        row = db.get_job(job_id)
        console.print(json.dumps(dict(row), indent=2, ensure_ascii=False))


@app.command()
def clean(out: Path = typer.Option(Path("web_export"), "--out")) -> None:
    tmp = out / ".dropraw_tmp"
    if tmp.exists():
        shutil.rmtree(tmp)
    for part in out.rglob("*.part"):
        part.unlink()
    console.print(f"Cleaned temp files under {out}")


def _print_summary(summary: object) -> None:
    table = Table("Metric", "Value")
    for key in ("job_id", "provider", "total_raw_files", "processed", "skipped", "failed", "output_files_count"):
        table.add_row(key, str(getattr(summary, key)))
    console.print(table)
    console.print(f"Reports: {summary.output_dir}")


def _find_manifest_for_job(job_id: str) -> Path | None:
    for path in Path.cwd().rglob(".dropraw_manifest.sqlite"):
        with Manifest(path.parent) as manifest:
            if manifest.get_job(job_id):
                return path
    return None


def _has_dropbox_token() -> bool:
    import os

    return bool(os.getenv("DROPBOX_ACCESS_TOKEN"))


if __name__ == "__main__":
    app()
