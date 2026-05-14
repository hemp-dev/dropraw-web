from __future__ import annotations

from pathlib import Path

from dropraw_web.models import RemoteFile
from dropraw_web.providers.base import StorageProvider


def download_to_temp(provider: StorageProvider, file: RemoteFile, temp_dir: Path) -> Path:
    return provider.download_file(file, temp_dir)

