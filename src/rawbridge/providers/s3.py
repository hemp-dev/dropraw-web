from __future__ import annotations

import hashlib
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable
from urllib.parse import urlparse

from rawbridge.constants import is_raw_file
from rawbridge.models import RemoteFile
from rawbridge.providers.base import StorageProvider


class S3ProviderError(RuntimeError):
    pass


@dataclass(frozen=True)
class S3Source:
    scheme: str
    bucket: str
    prefix: str


class S3Provider(StorageProvider):
    name = "s3"

    def __init__(
        self,
        client: Any | None = None,
        list_retries: int = 8,
        download_retries: int = 8,
        retry_delay: float = 3.0,
        sleeper: Callable[[float], None] = time.sleep,
        event_callback: Callable[[str, str, dict[str, Any] | None], None] | None = None,
    ) -> None:
        self._provided_client = client
        self.list_retries = list_retries
        self.download_retries = download_retries
        self.retry_delay = retry_delay
        self.sleeper = sleeper
        self.event_callback = event_callback

    def validate_source(self, source: str) -> bool:
        return parse_s3_url(source) is not None

    def list_files(self, source: str) -> Iterable[RemoteFile]:
        parsed = parse_s3_url(source)
        if parsed is None:
            raise S3ProviderError("Source must be s3://bucket/prefix, r2://bucket/prefix, or minio://bucket/prefix.")
        client = self._client(parsed.scheme)
        paginator = client.get_paginator("list_objects_v2")
        pages = self._retry(
            "S3 list prefix",
            self.list_retries,
            lambda: paginator.paginate(Bucket=parsed.bucket, Prefix=parsed.prefix),
            "listing_retry",
        )
        for page in pages:
            for obj in page.get("Contents", []):
                key = obj.get("Key", "")
                if key.endswith("/") or not is_raw_file(key):
                    continue
                rel_path = _relative_key(key, parsed.prefix)
                yield RemoteFile(
                    provider=self.name,
                    id=f"{parsed.scheme}://{parsed.bucket}/{key}",
                    name=Path(key).name,
                    path=rel_path,
                    size=obj.get("Size"),
                    modified_at=obj.get("LastModified"),
                    revision=obj.get("ETag"),
                    raw={
                        "scheme": parsed.scheme,
                        "bucket": parsed.bucket,
                        "key": key,
                        "etag": obj.get("ETag"),
                        "last_modified": str(obj.get("LastModified")) if obj.get("LastModified") else None,
                    },
                )

    def download_file(self, file: RemoteFile, target_dir: Path) -> Path:
        target_dir.mkdir(parents=True, exist_ok=True)
        final_path = target_dir / _safe_temp_name(file.path)
        part_path = final_path.with_name(final_path.name + ".part")
        if part_path.exists():
            part_path.unlink()
        scheme = file.raw.get("scheme") or "s3"
        client = self._client(str(scheme))
        bucket = file.raw.get("bucket")
        key = file.raw.get("key")
        if not bucket or not key:
            raise S3ProviderError("S3 RemoteFile is missing bucket/key metadata.")
        for attempt in range(1, self.download_retries + 1):
            try:
                client.download_file(Bucket=bucket, Key=key, Filename=str(part_path))
                if file.size is not None and part_path.stat().st_size != file.size:
                    raise S3ProviderError(
                        f"Downloaded size mismatch for {file.path}: expected {file.size}, got {part_path.stat().st_size}"
                    )
                part_path.replace(final_path)
                return final_path
            except Exception as exc:  # noqa: BLE001
                if part_path.exists():
                    part_path.unlink()
                if attempt >= self.download_retries:
                    raise S3ProviderError(f"Download failed after {attempt} attempts for {file.path}: {exc}") from exc
                delay = self.retry_delay * (2 ** (attempt - 1))
                self._emit(
                    "warning",
                    f"S3 download {file.path} retry {attempt}/{self.download_retries}: {exc}",
                    {"type": "download_retry", "attempt": attempt, "attempts": self.download_retries, "delay": delay},
                )
                self.sleeper(delay)
        raise S3ProviderError(f"Download failed for {file.path}")

    def fingerprint(self, file: RemoteFile) -> str:
        parts = [
            self.name,
            file.raw.get("bucket", ""),
            file.raw.get("key", ""),
            file.revision or "",
            str(file.size or ""),
            file.raw.get("last_modified", ""),
        ]
        return hashlib.sha256("\0".join(parts).encode("utf-8")).hexdigest()

    def _client(self, scheme: str) -> Any:
        if self._provided_client is not None:
            return self._provided_client
        try:
            import boto3
        except ImportError as exc:
            raise S3ProviderError("S3/R2 support requires boto3. Install rawbridge cloud dependencies.") from exc
        endpoint_url = os.getenv("AWS_ENDPOINT_URL") or os.getenv("S3_ENDPOINT_URL")
        region_name = os.getenv("AWS_REGION") or os.getenv("S3_REGION")
        if scheme in {"r2", "minio"} and not endpoint_url:
            raise S3ProviderError("R2/MinIO sources require AWS_ENDPOINT_URL or S3_ENDPOINT_URL.")
        return boto3.client("s3", endpoint_url=endpoint_url, region_name=region_name)

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
        raise S3ProviderError(f"{label} failed: {last_error}")

    def _emit(self, level: str, message: str, payload: dict[str, Any] | None = None) -> None:
        if self.event_callback:
            self.event_callback(level, message, payload)


def parse_s3_url(source: str) -> S3Source | None:
    parsed = urlparse(source)
    if parsed.scheme not in {"s3", "r2", "minio"} or not parsed.netloc:
        return None
    return S3Source(parsed.scheme, parsed.netloc, parsed.path.lstrip("/"))


def _relative_key(key: str, prefix: str) -> str:
    normalized_prefix = prefix.strip("/")
    normalized_key = key.lstrip("/")
    if normalized_prefix and normalized_key.startswith(normalized_prefix + "/"):
        return normalized_key[len(normalized_prefix) + 1 :]
    return normalized_key


def _safe_temp_name(path: str) -> str:
    clean = path.replace("\\", "/").strip("/")
    return clean.replace("/", "__")
