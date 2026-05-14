from __future__ import annotations

import logging
import os
import time
from pathlib import Path
from typing import Any, Callable, Iterable

from requests import ConnectionError as RequestsConnectionError

from dropraw_web.auth.token_store import get_dropbox_link_password, get_dropbox_token, token_presence_hint
from dropraw_web.constants import is_raw_file
from dropraw_web.models import RemoteFile
from dropraw_web.providers.base import StorageProvider

logger = logging.getLogger(__name__)


class DropboxProviderError(RuntimeError):
    pass


class DropboxDownloadSizeError(DropboxProviderError):
    pass


class DropboxSharedProvider(StorageProvider):
    name = "dropbox"

    def __init__(
        self,
        token: str | None = None,
        list_retries: int = 8,
        download_retries: int = 8,
        retry_delay: float = 3.0,
        cooldown: float = 0.0,
        api_factory: Callable[[], Any] | None = None,
        sleeper: Callable[[float], None] = time.sleep,
        link_password: str | None = None,
        event_callback: Callable[[str, str, dict[str, Any] | None], None] | None = None,
    ) -> None:
        self.token = get_dropbox_token(token)
        self.list_retries = list_retries
        self.download_retries = download_retries
        self.retry_delay = retry_delay
        self.cooldown = cooldown
        self.api_factory = api_factory
        self.sleeper = sleeper
        self.link_password = link_password or get_dropbox_link_password()
        self.source_url: str | None = None
        self.event_callback = event_callback

    def validate_source(self, source: str) -> bool:
        lowered = source.lower()
        return source.startswith("https://") and ("dropbox.com" in lowered or "db.tt" in lowered)

    def _client(self) -> Any:
        if self.api_factory:
            return self.api_factory()
        if not self.token:
            raise DropboxProviderError(f"Dropbox token missing. {token_presence_hint()}")
        try:
            import dropbox
        except ImportError as exc:
            raise DropboxProviderError("Dropbox SDK is not installed. Install dropbox>=12.0.2.") from exc
        return dropbox.Dropbox(self.token)

    def _shared_link(self, source: str) -> Any:
        try:
            import dropbox
        except ImportError as exc:
            raise DropboxProviderError("Dropbox SDK is not installed. Install dropbox>=12.0.2.") from exc
        return dropbox.files.SharedLink(url=source, password=self.link_password)

    def _retry(self, label: str, attempts: int, operation: Callable[[Any], Any]) -> Any:
        last_error: BaseException | None = None
        for attempt in range(1, attempts + 1):
            client = self._client()
            try:
                return operation(client)
            except Exception as exc:  # noqa: BLE001 - SDK wraps many transport errors.
                last_error = exc
                if attempt >= attempts or not self._is_retryable(exc):
                    raise
                delay = self.retry_delay * (2 ** (attempt - 1))
                logger.warning("%s failed on attempt %s/%s: %s", label, attempt, attempts, _safe_error(exc))
                self._emit_retry_event("listing_retry", label, attempt, attempts, delay, exc)
                self.sleeper(delay)
        raise DropboxProviderError(f"{label} failed after {attempts} attempts: {_safe_error(last_error)}")

    @staticmethod
    def _is_retryable(exc: Exception) -> bool:
        name = exc.__class__.__name__.lower()
        text = str(exc).lower()
        transient_tokens = (
            "connection",
            "timeout",
            "temporarily",
            "too_many",
            "internal",
            "rate",
            "reset",
            "invalid argument",
            "oserror",
        )
        permanent_tokens = ("auth", "permission", "not_found", "malformed", "validationerror")
        if any(token in name or token in text for token in permanent_tokens):
            return False
        return isinstance(exc, (RequestsConnectionError, OSError)) or any(
            token in name or token in text for token in transient_tokens
        )

    def list_folder_with_retries(self, source: str, path: str) -> Any:
        shared_link = self._shared_link(source) if self.api_factory is None else source
        api_path = _folder_api_path(path)
        return self._retry(
            f"Dropbox list folder {api_path or '/'}",
            self.list_retries,
            lambda client: client.files_list_folder(path=api_path, recursive=False, shared_link=shared_link),
        )

    def list_folder_continue_with_retries(self, cursor: str) -> Any:
        return self._retry(
            "Dropbox list folder continue",
            self.list_retries,
            lambda client: client.files_list_folder_continue(cursor),
        )

    def list_files(self, source: str) -> Iterable[RemoteFile]:
        if not self.validate_source(source):
            raise DropboxProviderError("Source is not a Dropbox shared-folder link.")
        self.source_url = source
        queue = [""]
        seen_folders = set()
        while queue:
            folder = queue.pop(0)
            if folder in seen_folders:
                continue
            seen_folders.add(folder)
            result = self.list_folder_with_retries(source, folder)
            while True:
                for entry in getattr(result, "entries", []):
                    rel_path = _entry_rel_path(entry, folder)
                    if _is_folder_entry(entry):
                        queue.append(rel_path)
                    elif is_raw_file(getattr(entry, "name", rel_path)):
                        yield _remote_file_from_entry(entry, rel_path)
                if not getattr(result, "has_more", False):
                    break
                result = self.list_folder_continue_with_retries(result.cursor)

    def _download_once(self, client: Any, file: RemoteFile, part_path: Path) -> None:
        if self.source_url is None and self.api_factory is None:
            raise DropboxProviderError("Dropbox source URL is unknown; call list_files first or set source_url.")
        source = self.source_url or file.raw.get("source_url") or ""
        shared_link = self._shared_link(source) if self.api_factory is None else source
        api_path = ensure_leading_slash(file.path)
        response = client.files_download(path=api_path, shared_link=shared_link)
        if isinstance(response, tuple) and len(response) == 2:
            _, response = response
        with part_path.open("wb") as handle:
            if hasattr(response, "iter_content"):
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        handle.write(chunk)
            elif hasattr(response, "content"):
                handle.write(response.content)
            elif isinstance(response, (bytes, bytearray)):
                handle.write(response)
            else:
                raise DropboxProviderError("Dropbox download response does not expose bytes.")

    def download_file_with_retries(self, file: RemoteFile, target_dir: Path) -> Path:
        target_dir.mkdir(parents=True, exist_ok=True)
        final_path = target_dir / _safe_temp_name(file.path)
        part_path = final_path.with_name(final_path.name + ".part")
        if part_path.exists():
            part_path.unlink()

        last_error: BaseException | None = None
        for attempt in range(1, self.download_retries + 1):
            client = self._client()
            try:
                self._download_once(client, file, part_path)
                if file.size is not None and part_path.stat().st_size != file.size:
                    raise DropboxDownloadSizeError(
                        f"Downloaded size mismatch for {file.path}: expected {file.size}, got {part_path.stat().st_size}"
                    )
                part_path.replace(final_path)
                return final_path
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                if part_path.exists():
                    part_path.unlink()
                if attempt >= self.download_retries or not self._is_retryable(exc):
                    raise DropboxProviderError(
                        f"Download failed after {attempt} attempts for {file.path}: {_safe_error(exc)}"
                    ) from exc
                delay = self.retry_delay * (2 ** (attempt - 1))
                logger.warning(
                    "Dropbox download failed for %s on attempt %s/%s: %s",
                    file.path,
                    attempt,
                    self.download_retries,
                    _safe_error(exc),
                )
                self._emit_retry_event(
                    "download_retry",
                    f"Dropbox download {file.path}",
                    attempt,
                    self.download_retries,
                    delay,
                    exc,
                )
                self.sleeper(delay)
        raise DropboxProviderError(f"Download failed after {self.download_retries} attempts: {_safe_error(last_error)}")

    def download_file(self, file: RemoteFile, target_dir: Path) -> Path:
        return self.download_file_with_retries(file, target_dir)

    def _emit_retry_event(
        self,
        event_type: str,
        label: str,
        attempt: int,
        attempts: int,
        delay: float,
        exc: BaseException,
    ) -> None:
        if self.event_callback is None:
            return
        self.event_callback(
            "warning",
            f"{label} retry {attempt}/{attempts}: {_safe_error(exc)}",
            {"type": event_type, "attempt": attempt, "attempts": attempts, "delay": delay},
        )


def ensure_leading_slash(path: str) -> str:
    normalized = path.replace("\\", "/").lstrip("/")
    return f"/{normalized}" if normalized else ""


def _folder_api_path(path: str) -> str:
    return ensure_leading_slash(path)


def _entry_rel_path(entry: Any, current_folder: str) -> str:
    path = getattr(entry, "path_display", None) or getattr(entry, "path_lower", None)
    name = getattr(entry, "name", "")
    if path:
        path = path.replace("\\", "/").lstrip("/")
        return path
    prefix = current_folder.replace("\\", "/").strip("/")
    return f"{prefix}/{name}".strip("/")


def _is_folder_entry(entry: Any) -> bool:
    if getattr(entry, "is_folder", False):
        return True
    cls_name = entry.__class__.__name__.lower()
    return "folder" in cls_name and "file" not in cls_name


def _remote_file_from_entry(entry: Any, rel_path: str) -> RemoteFile:
    modified = getattr(entry, "server_modified", None) or getattr(entry, "client_modified", None)
    return RemoteFile(
        provider=DropboxSharedProvider.name,
        id=getattr(entry, "id", rel_path),
        name=getattr(entry, "name", Path(rel_path).name),
        path=rel_path.lstrip("/"),
        size=getattr(entry, "size", None),
        modified_at=modified,
        revision=getattr(entry, "rev", None),
        raw={"dropbox_path": ensure_leading_slash(rel_path)},
    )


def _safe_temp_name(path: str) -> str:
    clean = path.replace("\\", "/").strip("/")
    return clean.replace("/", "__")


def _safe_error(exc: BaseException | None) -> str:
    if exc is None:
        return "unknown error"
    text = str(exc)
    token = os.getenv("DROPBOX_ACCESS_TOKEN")
    if token:
        text = text.replace(token, "***")
    return text
