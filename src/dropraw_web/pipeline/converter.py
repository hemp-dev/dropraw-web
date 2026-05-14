from __future__ import annotations

import json
import shutil
import time
from pathlib import Path
from typing import Any, Callable

from dropraw_web.config import merge_cli_overrides, resolve_preset
from dropraw_web.constants import DEFAULT_TEMP_DIR
from dropraw_web.imaging.encoders import save_image
from dropraw_web.imaging.raw_decode import decode_raw_to_pil
from dropraw_web.imaging.resize import generate_variants
from dropraw_web.models import AssetResult, FailedItem, JobConfig, JobSummary, RemoteFile
from dropraw_web.pipeline.failed_log import filter_files_by_failed_log, read_failed_log, write_failed_log
from dropraw_web.pipeline.jobs import new_job_id
from dropraw_web.pipeline.manifest import Manifest, utc_now
from dropraw_web.pipeline.reports import generate_reports
from dropraw_web.pipeline.scanner import detect_provider, output_paths_for_file


def run_conversion(
    job_config: JobConfig,
    *,
    job_id: str | None = None,
    config_file: Path | None = None,
    event_callback: Callable[[str, str, dict[str, Any] | None], None] | None = None,
) -> JobSummary:
    config = merge_cli_overrides(job_config, config_file)
    preset = resolve_preset(config)
    output_dir = config.output_dir.resolve()
    temp_root = (config.temp_dir or output_dir / DEFAULT_TEMP_DIR).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    temp_root.mkdir(parents=True, exist_ok=True)
    actual_job_id = job_id or new_job_id()
    assets: list[AssetResult] = []
    failed: list[FailedItem] = []

    with Manifest(output_dir) as manifest:
        def emit(level: str, message: str, payload: dict[str, Any] | None = None) -> None:
            manifest.record_event(actual_job_id, level, message, payload)
            if event_callback is not None:
                event_callback(level, message, payload)

        provider = detect_provider(
            config.source,
            config.provider,
            token=config.dropbox_token,
            list_retries=config.list_retries,
            download_retries=config.download_retries,
            retry_delay=config.retry_delay,
            cooldown=config.cooldown,
            event_callback=emit,
        )
        manifest.create_job(actual_job_id, config, preset, provider.name)
        try:
            emit("info", f"Scanning source with {provider.name}", {"type": "scan_started"})
            files = list(provider.list_files(config.source))
            emit("info", f"Found {len(files)} RAW files", {"type": "scan_completed", "count": len(files)})
            if config.only_failed:
                failed_paths = [item.rel_path for item in read_failed_log(config.only_failed)]
                files = filter_files_by_failed_log(files, failed_paths)
                emit(
                    "info",
                    f"Retry failed only selected {len(files)} files from {config.only_failed}",
                    {"type": "retry_failed_filter", "failed_log": str(config.only_failed), "count": len(files)},
                )
            summary = JobSummary(
                job_id=actual_job_id,
                source=config.source,
                provider=provider.name,
                output_dir=output_dir,
                preset=preset.name,
                started_at=utc_now(),
                total_raw_files=len(files),
                total_input_bytes=sum(file.size or 0 for file in files),
                formats=preset.formats,
                sizes=[str(size) for size in preset.responsive_sizes] or ["full"],
            )
            manifest.update_job(actual_job_id, total_files=len(files))

            for index, file in enumerate(files, start=1):
                fingerprint = provider.fingerprint(file)
                outputs = output_paths_for_file(file, output_dir, preset.formats, preset.responsive_sizes)
                if manifest.should_skip(fingerprint, preset, outputs, config.overwrite):
                    summary.skipped += 1
                    emit("info", f"Skipped existing {file.path}", {"type": "file_skipped", "path": file.path})
                    manifest.update_job(actual_job_id, skipped_files=summary.skipped)
                    continue
                if config.dry_run:
                    continue
                try:
                    file_assets = _process_file(provider, file, fingerprint, preset, outputs, temp_root, output_dir)
                    for asset in file_assets:
                        manifest.mark_done(actual_job_id, file, fingerprint, preset.name, asset)
                    assets.extend(file_assets)
                    summary.processed += 1
                    summary.output_files_count += len(file_assets)
                    summary.total_output_bytes += sum(asset.output_size or 0 for asset in file_assets)
                    emit(
                        "info",
                        f"Converted {file.path}",
                        {"type": "file_converted", "path": file.path, "outputs": len(file_assets), "index": index},
                    )
                    manifest.update_job(actual_job_id, processed_files=summary.processed)
                except Exception as exc:  # noqa: BLE001
                    item = FailedItem(rel_path=file.path, error=str(exc))
                    failed.append(item)
                    summary.errors.append(item)
                    summary.failed += 1
                    manifest.mark_failed(actual_job_id, file, fingerprint, preset.name, str(exc))
                    emit("error", f"Failed {file.path}", {"type": "file_failed", "path": file.path, "error": str(exc)})
                    manifest.update_job(actual_job_id, failed_files=summary.failed)
                finally:
                    if config.cooldown > 0 and provider.name == "dropbox":
                        time.sleep(config.cooldown)

            summary.finished_at = utc_now()
            write_failed_log(output_dir, failed)
            generate_reports(summary, assets)
            manifest.update_job(
                actual_job_id,
                status="completed" if not failed else "completed_with_errors",
                finished_at=summary.finished_at,
                processed_files=summary.processed,
                skipped_files=summary.skipped,
                failed_files=summary.failed,
            )
            return summary
        except Exception:
            manifest.update_job(actual_job_id, status="failed", finished_at=utc_now())
            raise


def _process_file(
    provider: object,
    file: RemoteFile,
    fingerprint: str,
    preset: object,
    outputs: list[tuple[Path, str, str]],
    temp_root: Path,
    output_dir: Path,
) -> list[AssetResult]:
    file_temp_dir = temp_root / fingerprint[:12]
    file_temp_dir.mkdir(parents=True, exist_ok=True)
    downloaded: Path | None = None
    try:
        downloaded = provider.download_file(file, file_temp_dir)  # type: ignore[attr-defined]
        image = decode_raw_to_pil(downloaded, preset)
        variants = {name: img for name, img in generate_variants(image, preset.responsive_sizes, preset.max_size)}
        results: list[AssetResult] = []
        for output_path, fmt, size_name in outputs:
            variant = variants[size_name]
            if output_path.exists():
                output_path.unlink()
            save_image(
                variant,
                output_path,
                fmt,
                preset.jpeg_quality or preset.quality,
                webp_lossless=preset.webp_lossless,
                png_compress_level=preset.png_compress_level,
            )
            results.append(
                AssetResult(
                    source_path=file.path,
                    output_path=str(output_path),
                    format=fmt,
                    width=variant.width,
                    height=variant.height,
                    input_size=file.size,
                    output_size=output_path.stat().st_size,
                    status="done",
                    output_size_name=size_name,
                )
            )
        return results
    finally:
        if downloaded and file_temp_dir in downloaded.resolve().parents and downloaded.exists():
            downloaded.unlink()
        if file_temp_dir.exists():
            shutil.rmtree(file_temp_dir, ignore_errors=True)


def config_from_job_row(row: object) -> JobConfig:
    data = json.loads(row["config_json"])
    return JobConfig(**data)
