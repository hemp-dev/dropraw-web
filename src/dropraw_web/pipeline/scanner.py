from __future__ import annotations

from pathlib import Path
from typing import Iterable

from dropraw_web.models import RemoteFile
from dropraw_web.providers import (
    BoxProvider,
    DropboxSharedProvider,
    GoogleDriveProvider,
    LocalProvider,
    OneDriveProvider,
    S3Provider,
    StorageProvider,
    YandexDiskProvider,
)


def detect_provider(source: str, provider: str = "auto", **kwargs) -> StorageProvider:
    normalized = provider.replace("_", "-").lower()
    if normalized == "local":
        return LocalProvider()
    if normalized == "dropbox":
        return DropboxSharedProvider(**_cloud_kwargs(kwargs, "dropbox"))
    if normalized in {"google-drive", "gdrive", "google"}:
        return GoogleDriveProvider(**_cloud_kwargs(kwargs, "google-drive"))
    if normalized in {"s3", "r2", "minio"}:
        return S3Provider(**_cloud_kwargs(kwargs, "s3"))
    if normalized == "onedrive":
        return OneDriveProvider()
    if normalized in {"yadisk", "yandex-disk"}:
        return YandexDiskProvider()
    if normalized == "box":
        return BoxProvider()
    local = LocalProvider()
    if local.validate_source(source):
        return local
    candidates: list[StorageProvider] = [
        DropboxSharedProvider(**_cloud_kwargs(kwargs, "dropbox")),
        GoogleDriveProvider(**_cloud_kwargs(kwargs, "google-drive")),
        S3Provider(**_cloud_kwargs(kwargs, "s3")),
        OneDriveProvider(),
        YandexDiskProvider(),
        BoxProvider(),
    ]
    for candidate in candidates:
        if candidate.validate_source(source):
            return candidate
    raise ValueError(
        "Could not detect provider. Use --provider local, dropbox, google-drive, s3, onedrive, yadisk, or box."
    )


def available_provider_metadata() -> list[dict[str, str | bool]]:
    return [
        {"id": "local", "label": "Local folder", "status": "stable", "implemented": True},
        {"id": "dropbox", "label": "Dropbox shared link", "status": "stable", "implemented": True},
        {"id": "google-drive", "label": "Google Drive folder", "status": "experimental", "implemented": True},
        {"id": "s3", "label": "S3 / R2 / MinIO", "status": "experimental", "implemented": True},
        {"id": "onedrive", "label": "OneDrive", "status": "coming soon", "implemented": False},
        {"id": "yadisk", "label": "Yandex Disk", "status": "coming soon", "implemented": False},
        {"id": "box", "label": "Box", "status": "coming soon", "implemented": False},
    ]


def _cloud_kwargs(kwargs: dict, provider: str) -> dict:
    allowed = {"list_retries", "download_retries", "retry_delay", "sleeper", "event_callback"}
    if provider == "dropbox":
        allowed |= {"token", "api_factory", "cooldown", "link_password"}
    return {key: value for key, value in kwargs.items() if key in allowed}


def scan_files(provider: StorageProvider, source: str) -> list[RemoteFile]:
    return list(provider.list_files(source))


def safe_relative_path(rel_path: str) -> Path:
    clean_parts: list[str] = []
    normalized = rel_path.replace("\\", "/")
    candidate = Path(normalized)
    if candidate.is_absolute():
        normalized = normalized.lstrip("/")
    for part in normalized.split("/"):
        if not part or part == "." or part == "..":
            continue
        clean_parts.append(part)
    if not clean_parts:
        raise ValueError(f"Unsafe empty relative path: {rel_path!r}")
    return Path(*clean_parts)


def output_paths_for_file(
    file: RemoteFile,
    output_dir: Path,
    formats: Iterable[str],
    responsive_sizes: Iterable[int],
) -> list[tuple[Path, str, str]]:
    rel = safe_relative_path(file.path)
    stem_path = output_dir / rel.with_suffix("")
    paths: list[tuple[Path, str, str]] = []
    sizes = list(responsive_sizes)
    if sizes:
        for size in sizes:
            for fmt in formats:
                ext = ".jpg" if fmt == "jpg" else f".{fmt}"
                paths.append((stem_path.with_name(f"{stem_path.name}@{size}").with_suffix(ext), fmt, str(size)))
    else:
        for fmt in formats:
            ext = ".jpg" if fmt == "jpg" else f".{fmt}"
            paths.append((stem_path.with_suffix(ext), fmt, "full"))
    output_root = output_dir.resolve()
    for path, _, _ in paths:
        resolved_parent = path.parent.resolve()
        if output_root != resolved_parent and output_root not in resolved_parent.parents:
            raise ValueError(f"Output path escapes output directory: {path}")
    return paths
