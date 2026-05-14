from __future__ import annotations

import hashlib
import os
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Iterable
from urllib.parse import parse_qs, urlparse

from dropraw_web.constants import is_raw_file
from dropraw_web.models import RemoteFile
from dropraw_web.providers.base import StorageProvider

GOOGLE_FOLDER_MIME = "application/vnd.google-apps.folder"


class GoogleDriveProviderError(RuntimeError):
    pass


class GoogleDriveProvider(StorageProvider):
    name = "google-drive"

    def __init__(
        self,
        service: Any | None = None,
        list_retries: int = 8,
        download_retries: int = 8,
        retry_delay: float = 3.0,
        sleeper: Callable[[float], None] = time.sleep,
        event_callback: Callable[[str, str, dict[str, Any] | None], None] | None = None,
    ) -> None:
        self._provided_service = service
        self.list_retries = list_retries
        self.download_retries = download_retries
        self.retry_delay = retry_delay
        self.sleeper = sleeper
        self.event_callback = event_callback

    def validate_source(self, source: str) -> bool:
        return extract_folder_id(source) is not None

    def list_files(self, source: str) -> Iterable[RemoteFile]:
        folder_id = extract_folder_id(source)
        if not folder_id:
            raise GoogleDriveProviderError("Google Drive source must be a folder link.")
        service = self._service()
        queue: list[tuple[str, str]] = [(folder_id, "")]
        while queue:
            current_id, prefix = queue.pop(0)
            page_token: str | None = None
            while True:
                result = self._retry(
                    "Google Drive list folder",
                    self.list_retries,
                    lambda: service.files()
                    .list(
                        q=f"'{current_id}' in parents and trashed = false",
                        fields=(
                            "nextPageToken, files(id, name, mimeType, size, md5Checksum, "
                            "modifiedTime, trashed)"
                        ),
                        pageToken=page_token,
                        supportsAllDrives=True,
                        includeItemsFromAllDrives=True,
                    )
                    .execute(),
                    "listing_retry",
                )
                for item in result.get("files", []):
                    name = item.get("name") or item.get("id") or "drive-file"
                    rel_path = f"{prefix}/{name}".strip("/")
                    mime_type = item.get("mimeType")
                    if is_folder_metadata(item):
                        queue.append((item["id"], rel_path))
                    elif not _is_google_workspace_file(mime_type) and is_raw_file(name):
                        yield _remote_file_from_metadata(item, rel_path)
                page_token = result.get("nextPageToken")
                if not page_token:
                    break

    def download_file(self, file: RemoteFile, target_dir: Path) -> Path:
        target_dir.mkdir(parents=True, exist_ok=True)
        final_path = target_dir / _safe_temp_name(file.path)
        part_path = final_path.with_name(final_path.name + ".part")
        if part_path.exists():
            part_path.unlink()
        service = self._service()
        request = service.files().get_media(fileId=file.id, supportsAllDrives=True)
        last_error: BaseException | None = None
        for attempt in range(1, self.download_retries + 1):
            try:
                content = _execute_media_request(request)
                part_path.write_bytes(content)
                if file.size is not None and part_path.stat().st_size != file.size:
                    raise GoogleDriveProviderError(
                        f"Downloaded size mismatch for {file.path}: expected {file.size}, got {part_path.stat().st_size}"
                    )
                part_path.replace(final_path)
                return final_path
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                if part_path.exists():
                    part_path.unlink()
                if attempt >= self.download_retries:
                    raise GoogleDriveProviderError(
                        f"Download failed after {attempt} attempts for {file.path}: {exc}"
                    ) from exc
                delay = self.retry_delay * (2 ** (attempt - 1))
                self._emit(
                    "warning",
                    f"Google Drive download {file.path} retry {attempt}/{self.download_retries}: {exc}",
                    {"type": "download_retry", "attempt": attempt, "attempts": self.download_retries, "delay": delay},
                )
                self.sleeper(delay)
        raise GoogleDriveProviderError(f"Download failed for {file.path}: {last_error}")

    def fingerprint(self, file: RemoteFile) -> str:
        parts = [
            self.name,
            file.id,
            file.raw.get("md5Checksum", ""),
            file.raw.get("modifiedTime", ""),
            str(file.size or ""),
        ]
        return hashlib.sha256("\0".join(parts).encode("utf-8")).hexdigest()

    def _service(self) -> Any:
        if self._provided_service is not None:
            return self._provided_service
        try:
            from googleapiclient.discovery import build
        except ImportError as exc:
            raise GoogleDriveProviderError(
                "Google Drive support requires google-api-python-client. Install dropraw-web cloud dependencies."
            ) from exc

        api_key = os.getenv("GOOGLE_API_KEY")
        credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if credentials_path:
            try:
                from google.oauth2.service_account import Credentials
            except ImportError as exc:
                raise GoogleDriveProviderError(
                    "GOOGLE_APPLICATION_CREDENTIALS requires google-auth to be installed."
                ) from exc
            scopes = ["https://www.googleapis.com/auth/drive.readonly"]
            credentials = Credentials.from_service_account_file(credentials_path, scopes=scopes)
            return build("drive", "v3", credentials=credentials, cache_discovery=False)
        if api_key:
            return build("drive", "v3", developerKey=api_key, cache_discovery=False)
        raise GoogleDriveProviderError(
            "Google Drive credentials missing. Set GOOGLE_APPLICATION_CREDENTIALS or GOOGLE_API_KEY."
        )

    def _retry(self, label: str, attempts: int, operation: Callable[[], Any], event_type: str) -> Any:
        last_error: BaseException | None = None
        for attempt in range(1, attempts + 1):
            try:
                return operation()
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                if attempt >= attempts:
                    raise
                delay = self.retry_delay * (2 ** (attempt - 1))
                self._emit(
                    "warning",
                    f"{label} retry {attempt}/{attempts}: {exc}",
                    {"type": event_type, "attempt": attempt, "attempts": attempts, "delay": delay},
                )
                self.sleeper(delay)
        raise GoogleDriveProviderError(f"{label} failed: {last_error}")

    def _emit(self, level: str, message: str, payload: dict[str, Any] | None = None) -> None:
        if self.event_callback:
            self.event_callback(level, message, payload)


def extract_folder_id(source: str) -> str | None:
    parsed = urlparse(source)
    if parsed.netloc and "drive.google.com" not in parsed.netloc:
        return None
    query_id = parse_qs(parsed.query).get("id")
    if query_id and query_id[0]:
        return query_id[0]
    match = re.search(r"/folders/([^/?#]+)", parsed.path)
    if match:
        return match.group(1)
    return None


def is_folder_metadata(item: dict[str, Any]) -> bool:
    return item.get("mimeType") == GOOGLE_FOLDER_MIME


def _is_google_workspace_file(mime_type: str | None) -> bool:
    return bool(mime_type and mime_type.startswith("application/vnd.google-apps.") and mime_type != GOOGLE_FOLDER_MIME)


def _remote_file_from_metadata(item: dict[str, Any], rel_path: str) -> RemoteFile:
    modified = _parse_datetime(item.get("modifiedTime"))
    size = int(item["size"]) if item.get("size") else None
    return RemoteFile(
        provider=GoogleDriveProvider.name,
        id=item["id"],
        name=item.get("name") or Path(rel_path).name,
        path=rel_path,
        size=size,
        modified_at=modified,
        revision=item.get("md5Checksum"),
        mime_type=item.get("mimeType"),
        raw={
            "md5Checksum": item.get("md5Checksum"),
            "modifiedTime": item.get("modifiedTime"),
            "size": item.get("size"),
        },
    )


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _execute_media_request(request: Any) -> bytes:
    result = request.execute()
    if isinstance(result, bytes):
        return result
    if isinstance(result, bytearray):
        return bytes(result)
    if hasattr(result, "content"):
        return result.content
    raise GoogleDriveProviderError("Google Drive media response did not return bytes.")


def _safe_temp_name(path: str) -> str:
    clean = path.replace("\\", "/").strip("/")
    return clean.replace("/", "__")
