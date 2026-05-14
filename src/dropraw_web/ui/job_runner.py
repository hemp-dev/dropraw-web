from __future__ import annotations

import json
from concurrent.futures import Future, ThreadPoolExecutor
from pathlib import Path
from threading import Lock
from typing import Any

from dropraw_web.constants import DEFAULT_FAILED_LOG
from dropraw_web.models import JobConfig
from dropraw_web.pipeline.converter import config_from_job_row, run_conversion
from dropraw_web.pipeline.failed_log import read_failed_log
from dropraw_web.pipeline.jobs import new_job_id
from dropraw_web.pipeline.manifest import Manifest
from dropraw_web.ui.schemas import JobCreateRequest, JobEvent, JobStatus


class JobRunner:
    def __init__(self) -> None:
        self.executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="dropraw-ui")
        self._jobs: dict[str, dict[str, Any]] = {}
        self._lock = Lock()

    def create_job(self, request: JobCreateRequest) -> str:
        job_id = new_job_id()
        config = _request_to_config(request)
        with self._lock:
            self._jobs[job_id] = {
                "job_id": job_id,
                "status": "queued",
                "config": config,
                "output_dir": str(config.output_dir),
                "events": [],
            }
        future = self.executor.submit(self._run, job_id, config)
        with self._lock:
            self._jobs[job_id]["future"] = future
        return job_id

    def resume_job(self, job_id: str) -> bool:
        config = self._config_for_job(job_id)
        if config is None:
            return False
        config.resume = True
        future = self.executor.submit(self._run, job_id, config)
        with self._lock:
            self._jobs.setdefault(job_id, {"job_id": job_id, "events": []})
            self._jobs[job_id].update({"status": "queued", "config": config, "output_dir": str(config.output_dir), "future": future})
        return True

    def retry_failed(self, job_id: str) -> bool:
        config = self._config_for_job(job_id)
        if config is None:
            return False
        failed_log = config.output_dir / DEFAULT_FAILED_LOG
        if not failed_log.exists():
            return False
        config.only_failed = failed_log
        config.overwrite = False
        future = self.executor.submit(self._run, job_id, config)
        with self._lock:
            self._jobs[job_id]["status"] = "retry_queued"
            self._jobs[job_id]["future"] = future
        return True

    def cancel_job(self, job_id: str) -> bool:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return False
            future: Future | None = job.get("future")
            cancelled = bool(future and future.cancel())
            job["status"] = "cancelled" if cancelled else "cancel_requested"
            return True

    def list_jobs(self) -> list[JobStatus]:
        with self._lock:
            ids = list(self._jobs)
        return [self.get_status(job_id) for job_id in ids]

    def get_status(self, job_id: str) -> JobStatus:
        with self._lock:
            job = dict(self._jobs.get(job_id, {"job_id": job_id, "status": "unknown"}))
        output_dir = job.get("output_dir")
        if output_dir:
            row = _manifest_job(Path(output_dir), job_id)
            if row:
                return _row_to_status(row)
        return JobStatus(job_id=job_id, status=job.get("status", "unknown"), output_dir=output_dir)

    def get_events(self, job_id: str) -> list[JobEvent]:
        output_dir = self._output_dir_for_job(job_id)
        events: list[JobEvent] = []
        if output_dir:
            with Manifest(output_dir) as manifest:
                events.extend(_row_to_event(row) for row in manifest.list_events(job_id))
        with self._lock:
            for item in self._jobs.get(job_id, {}).get("events", []):
                events.append(JobEvent(**item))
        return events

    def get_failed(self, job_id: str) -> list[dict[str, str]]:
        output_dir = self._output_dir_for_job(job_id)
        if not output_dir:
            return []
        failed_path = output_dir / DEFAULT_FAILED_LOG
        if failed_path.exists():
            return [item.model_dump() for item in read_failed_log(failed_path)]
        with Manifest(output_dir) as manifest:
            return [{"rel_path": row["source_path"], "error": row["error"] or ""} for row in manifest.list_assets(job_id, "failed")]

    def get_report(self, job_id: str) -> dict[str, Any]:
        output_dir = self._output_dir_for_job(job_id)
        if not output_dir:
            return {"job_id": job_id, "status": "unknown"}
        report_path = output_dir / "report.json"
        report = json.loads(report_path.read_text(encoding="utf-8")) if report_path.exists() else {}
        report["paths"] = {
            "output_dir": str(output_dir),
            "report_html": str(output_dir / "report.html"),
            "report_json": str(output_dir / "report.json"),
            "report_csv": str(output_dir / "report.csv"),
            "errors_csv": str(output_dir / "errors.csv"),
            "failed_tsv": str(output_dir / DEFAULT_FAILED_LOG),
            "picture_snippets": str(output_dir / "picture-snippets.html"),
        }
        return report

    def _run(self, job_id: str, config: JobConfig) -> None:
        with self._lock:
            self._jobs[job_id]["status"] = "running"
        try:
            run_conversion(config, job_id=job_id, event_callback=lambda level, message, payload=None: self._event(job_id, level, message, payload))
            with self._lock:
                if self._jobs.get(job_id, {}).get("status") != "cancel_requested":
                    self._jobs[job_id]["status"] = "completed"
        except Exception as exc:  # noqa: BLE001
            self._event(job_id, "error", f"Job failed: {exc}", {"type": "job_failed", "error": str(exc)})
            with self._lock:
                self._jobs[job_id]["status"] = "failed"

    def _event(self, job_id: str, level: str, message: str, payload: dict[str, Any] | None = None) -> None:
        with self._lock:
            self._jobs.setdefault(job_id, {"job_id": job_id, "events": []})
            self._jobs[job_id].setdefault("events", []).append({"level": level, "message": message, "payload": payload or {}})

    def _config_for_job(self, job_id: str) -> JobConfig | None:
        with self._lock:
            job = self._jobs.get(job_id)
            if job and job.get("config"):
                return job["config"].model_copy(deep=True)
            output_dir = Path(job["output_dir"]) if job and job.get("output_dir") else None
        if output_dir:
            row = _manifest_job(output_dir, job_id)
            if row:
                return config_from_job_row(row)
        return None

    def _output_dir_for_job(self, job_id: str) -> Path | None:
        with self._lock:
            job = self._jobs.get(job_id)
            if job and job.get("output_dir"):
                return Path(job["output_dir"])
        return None


def _request_to_config(request: JobCreateRequest) -> JobConfig:
    return JobConfig(
        source=request.source,
        provider=request.provider,
        output_dir=request.output_dir,
        preset=request.preset,
        formats=request.formats,
        max_size=request.max_size,
        responsive_sizes=request.responsive_sizes,
        quality=request.quality,
        overwrite=request.overwrite,
        resume=request.resume,
        only_failed=request.only_failed,
        list_retries=request.list_retries,
        download_retries=request.download_retries,
        retry_delay=request.retry_delay,
        cooldown=request.cooldown,
        metadata_mode=request.metadata_mode,
        dropbox_token=request.dropbox_token,
    )


def _manifest_job(output_dir: Path, job_id: str) -> Any | None:
    manifest_path = output_dir / ".dropraw_manifest.sqlite"
    if not manifest_path.exists():
        return None
    with Manifest(output_dir) as manifest:
        return manifest.get_job(job_id)


def _row_to_status(row: Any) -> JobStatus:
    total = row["total_files"] or 0
    done = (row["processed_files"] or 0) + (row["skipped_files"] or 0) + (row["failed_files"] or 0)
    progress = done / total if total else 0
    return JobStatus(
        job_id=row["id"],
        status=row["status"],
        source=row["source"],
        provider=row["provider"],
        output_dir=row["output_dir"],
        total_files=total,
        processed_files=row["processed_files"] or 0,
        skipped_files=row["skipped_files"] or 0,
        failed_files=row["failed_files"] or 0,
        started_at=row["started_at"],
        finished_at=row["finished_at"],
        progress=progress,
    )


def _row_to_event(row: Any) -> JobEvent:
    return JobEvent(
        id=row["id"],
        level=row["level"],
        message=row["message"],
        payload=json.loads(row["payload_json"] or "{}"),
        created_at=row["created_at"],
    )


runner = JobRunner()
