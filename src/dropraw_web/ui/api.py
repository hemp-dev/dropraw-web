from __future__ import annotations

import hmac
import os
import platform
import sys
from pathlib import Path
from urllib.parse import urlparse
from uuid import uuid4

from PIL import features

from dropraw_web import __version__
from dropraw_web.config import load_presets
from dropraw_web.pipeline.scanner import available_provider_metadata, detect_provider
from dropraw_web.ui.job_runner import runner
from dropraw_web.ui.schemas import JobCreateRequest, JobCreateResponse, ScanRequest, ScanResponse, Settings

_settings = Settings()


def create_app():
    try:
        from fastapi import FastAPI, HTTPException, Request
        from fastapi.middleware.cors import CORSMiddleware
        from fastapi.responses import JSONResponse
    except ImportError as exc:
        raise RuntimeError("DropRaw UI requires fastapi and uvicorn. Install with: pip install 'dropraw-web[ui]'") from exc

    app = FastAPI(title="DropRaw Web UI API", version=__version__)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://127.0.0.1:8787", "http://localhost:8787"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def ui_token_auth(request: Request, call_next):
        token = os.getenv("DROPRAW_UI_TOKEN")
        supplied = _request_token(request)
        if token and request.url.path.startswith("/api/") and not hmac.compare_digest(supplied or "", token):
            return JSONResponse({"detail": "DropRaw UI token required."}, status_code=401)
        response = await call_next(request)
        if token and supplied and hmac.compare_digest(supplied, token):
            response.set_cookie(
                "dropraw_ui_token",
                token,
                httponly=True,
                samesite="strict",
                secure=request.url.scheme == "https",
            )
        return response

    @app.get("/api/health")
    def health() -> dict:
        py = sys.version_info
        warning = None
        if py[:2] >= (3, 13):
            warning = "Python 3.11 or 3.12 is recommended for this release."
        return {
            "status": "ok",
            "version": __version__,
            "python_version": platform.python_version(),
            "python_version_warning": warning,
            "recommended_python": "3.11 or 3.12",
            "available_providers": available_provider_metadata(),
            "pillow_webp_support": bool(features.check("webp")),
            "pillow_avif_support": bool(features.check("avif")),
            "dropbox_sdk_version": _module_version("dropbox"),
            "credentials": {
                "dropbox": bool(os.getenv("DROPBOX_ACCESS_TOKEN")),
                "google": bool(os.getenv("GOOGLE_APPLICATION_CREDENTIALS") or os.getenv("GOOGLE_API_KEY")),
                "s3": bool(os.getenv("AWS_ACCESS_KEY_ID") or os.getenv("AWS_PROFILE")),
            },
        }

    @app.get("/api/providers")
    def providers() -> list[dict]:
        return available_provider_metadata()

    @app.get("/api/presets")
    def presets() -> dict:
        return {name: preset.model_dump() for name, preset in load_presets().items()}

    @app.post("/api/scan", response_model=ScanResponse)
    def scan(request: ScanRequest) -> ScanResponse:
        warnings = _provider_warnings(request.provider, request.source)
        try:
            _validate_scan_request(request)
            provider = detect_provider(
                request.source,
                request.provider,
                token=request.dropbox_token,
                list_retries=request.list_retries,
                retry_delay=request.retry_delay,
            )
            files = list(provider.list_files(request.source))
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        folders = {str(Path(file.path).parent) for file in files if str(Path(file.path).parent) != "."}
        return ScanResponse(
            job_preview_id=f"scan_{uuid4().hex[:12]}",
            provider=provider.name,
            files_count=len(files),
            total_size=sum(file.size or 0 for file in files),
            folders_count=len(folders),
            first_files=[
                {"path": file.path, "name": file.name, "size": file.size, "provider": file.provider} for file in files[:50]
            ],
            warnings=warnings,
        )

    @app.post("/api/jobs", response_model=JobCreateResponse, status_code=202)
    def create_job(request: JobCreateRequest) -> JobCreateResponse:
        try:
            _validate_job_request(request)
            job_id = runner.create_job(request)
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return JobCreateResponse(job_id=job_id, status="queued")

    @app.get("/api/jobs")
    def jobs() -> list[dict]:
        return [job.model_dump() for job in runner.list_jobs()]

    @app.get("/api/jobs/{job_id}")
    def job(job_id: str) -> dict:
        return runner.get_status(job_id).model_dump()

    @app.get("/api/jobs/{job_id}/events")
    def job_events(job_id: str) -> list[dict]:
        return [event.model_dump() for event in runner.get_events(job_id)]

    @app.post("/api/jobs/{job_id}/cancel")
    def cancel(job_id: str) -> dict:
        return {"job_id": job_id, "accepted": runner.cancel_job(job_id)}

    @app.post("/api/jobs/{job_id}/resume", status_code=202)
    def resume(job_id: str) -> dict:
        accepted = runner.resume_job(job_id)
        if not accepted:
            raise HTTPException(status_code=404, detail="Job not found")
        return {"job_id": job_id, "accepted": True}

    @app.post("/api/jobs/{job_id}/retry-failed", status_code=202)
    def retry_failed(job_id: str) -> dict:
        accepted = runner.retry_failed(job_id)
        if not accepted:
            raise HTTPException(status_code=404, detail="No failed log found for job")
        return {"job_id": job_id, "accepted": True}

    @app.get("/api/jobs/{job_id}/failed")
    def failed(job_id: str) -> list[dict]:
        return runner.get_failed(job_id)

    @app.get("/api/jobs/{job_id}/report")
    def report(job_id: str) -> dict:
        return runner.get_report(job_id)

    @app.get("/api/settings")
    def get_settings() -> dict:
        return _settings.model_dump()

    @app.post("/api/settings")
    def save_settings(settings: Settings) -> dict:
        global _settings
        _settings = settings
        return _settings.model_dump()

    @app.post("/api/auth/{provider}/login")
    def auth_login(provider: str) -> dict:
        return {"provider": provider, "status": "todo", "message": "OAuth login flow is planned for a future release."}

    @app.get("/api/auth/{provider}/status")
    def auth_status(provider: str) -> dict:
        return {"provider": provider, "authenticated": False, "configured": _credential_configured(provider)}

    return app


def _module_version(name: str) -> str | None:
    try:
        module = __import__(name)
        return str(getattr(module, "__version__", "installed"))
    except Exception:  # noqa: BLE001
        return None


def _request_token(request: object) -> str | None:
    headers = getattr(request, "headers", {})
    cookies = getattr(request, "cookies", {})
    return (
        headers.get("x-dropraw-ui-token")
        or cookies.get("dropraw_ui_token")
    )


def _validate_scan_request(request: ScanRequest) -> None:
    if _source_looks_local(request.source, request.provider):
        _require_under_roots(Path(request.source), _allowed_roots("DROPRAW_UI_ALLOWED_SOURCE_ROOTS"), "source")


def _validate_job_request(request: JobCreateRequest) -> None:
    if _source_looks_local(request.source, request.provider):
        _require_under_roots(Path(request.source), _allowed_roots("DROPRAW_UI_ALLOWED_SOURCE_ROOTS"), "source")
    _require_under_roots(request.output_dir, _allowed_roots("DROPRAW_UI_ALLOWED_OUTPUT_ROOTS"), "output_dir")
    if request.only_failed is not None:
        _require_under_roots(request.only_failed, _allowed_roots("DROPRAW_UI_ALLOWED_OUTPUT_ROOTS"), "only_failed")


def _source_looks_local(source: str, provider: str) -> bool:
    if provider == "local":
        return True
    if provider != "auto":
        return False
    parsed = urlparse(source)
    if parsed.scheme and parsed.scheme not in {"file"}:
        return False
    return True


def _allowed_roots(env_name: str) -> list[Path]:
    combined = os.getenv(env_name) or os.getenv("DROPRAW_UI_ALLOWED_ROOTS")
    if combined:
        raw_roots = [part for part in combined.split(os.pathsep) if part.strip()]
    else:
        raw_roots = [str(Path.cwd()), str(Path.home())]
    roots: list[Path] = []
    for raw_root in raw_roots:
        roots.append(Path(raw_root).expanduser().resolve(strict=False))
    return roots


def _require_under_roots(path: Path, roots: list[Path], label: str) -> None:
    resolved = path.expanduser().resolve(strict=False)
    for root in roots:
        if resolved == root or root in resolved.parents:
            return
    allowed = ", ".join(str(root) for root in roots)
    raise ValueError(f"{label} must be under an allowed UI root: {allowed}")


def _credential_configured(provider: str) -> bool:
    if provider == "dropbox":
        return bool(os.getenv("DROPBOX_ACCESS_TOKEN"))
    if provider in {"google", "google-drive"}:
        return bool(os.getenv("GOOGLE_APPLICATION_CREDENTIALS") or os.getenv("GOOGLE_API_KEY"))
    if provider == "s3":
        return bool(os.getenv("AWS_ACCESS_KEY_ID") or os.getenv("AWS_PROFILE"))
    return False


def _provider_warnings(provider: str, source: str) -> list[str]:
    warnings: list[str] = []
    if provider == "dropbox" or "dropbox.com" in source:
        warnings.append("DropRaw scans Dropbox folders through the API and does not download the whole folder as ZIP.")
    return warnings
