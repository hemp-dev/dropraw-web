from __future__ import annotations

from pathlib import Path

from rawbridge.models import RemoteFile
from rawbridge.providers.base import StorageProvider


def download_to_temp(provider: StorageProvider, file: RemoteFile, temp_dir: Path) -> Path:
    return provider.download_file(file, temp_dir)

