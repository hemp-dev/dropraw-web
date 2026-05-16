from __future__ import annotations

from pathlib import Path
from typing import Iterable

from rawbridge.models import RemoteFile
from rawbridge.providers.base import StorageProvider


class BoxProvider(StorageProvider):
    name = "box"

    def validate_source(self, source: str) -> bool:
        lowered = source.lower()
        return "box.com" in lowered or "app.box.com" in lowered

    def list_files(self, source: str) -> Iterable[RemoteFile]:
        raise NotImplementedError("Box provider is on the roadmap. Use local, Dropbox, Google Drive, or S3/R2 for now.")

    def download_file(self, file: RemoteFile, target_dir: Path) -> Path:
        raise NotImplementedError("Box downloads are not implemented yet.")
