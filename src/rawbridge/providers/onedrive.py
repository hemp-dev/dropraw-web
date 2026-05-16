from __future__ import annotations

from pathlib import Path
from typing import Iterable

from rawbridge.models import RemoteFile
from rawbridge.providers.base import StorageProvider


class OneDriveProvider(StorageProvider):
    name = "onedrive"

    def validate_source(self, source: str) -> bool:
        lowered = source.lower()
        return "1drv.ms" in lowered or "onedrive.live.com" in lowered or "sharepoint.com" in lowered

    def list_files(self, source: str) -> Iterable[RemoteFile]:
        raise NotImplementedError(
            "OneDrive provider is on the roadmap. Use local, Dropbox, Google Drive, or S3/R2 for now."
        )

    def download_file(self, file: RemoteFile, target_dir: Path) -> Path:
        raise NotImplementedError("OneDrive downloads are not implemented yet.")
