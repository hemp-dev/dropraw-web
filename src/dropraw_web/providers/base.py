from __future__ import annotations

import hashlib
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterable

from dropraw_web.models import RemoteFile


class StorageProvider(ABC):
    name: str

    @abstractmethod
    def validate_source(self, source: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def list_files(self, source: str) -> Iterable[RemoteFile]:
        raise NotImplementedError

    @abstractmethod
    def download_file(self, file: RemoteFile, target_dir: Path) -> Path:
        raise NotImplementedError

    def fingerprint(self, file: RemoteFile) -> str:
        parts = [
            file.provider,
            file.id,
            file.path,
            file.revision or "",
            file.modified_at.isoformat() if file.modified_at else "",
            str(file.size or ""),
        ]
        return hashlib.sha256("\0".join(parts).encode("utf-8")).hexdigest()

