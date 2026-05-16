from __future__ import annotations

import hashlib
import shutil
from pathlib import Path
from typing import Iterable

from rawbridge.constants import is_raw_file
from rawbridge.models import RemoteFile
from rawbridge.providers.base import StorageProvider


class LocalProvider(StorageProvider):
    name = "local"

    def __init__(self, copy_to_temp: bool = False) -> None:
        self.copy_to_temp = copy_to_temp
        self._source_root: Path | None = None

    def validate_source(self, source: str) -> bool:
        return Path(source).expanduser().is_dir()

    def list_files(self, source: str) -> Iterable[RemoteFile]:
        root = Path(source).expanduser().resolve()
        self._source_root = root
        for path in sorted(root.rglob("*")):
            if not path.is_file() or not is_raw_file(path.name):
                continue
            rel = path.relative_to(root).as_posix()
            stat = path.stat()
            yield RemoteFile(
                provider=self.name,
                id=str(path.resolve()),
                name=path.name,
                path=rel,
                size=stat.st_size,
                modified_at=None,
                revision=str(stat.st_mtime_ns),
                raw={"local_path": str(path.resolve())},
            )

    def download_file(self, file: RemoteFile, target_dir: Path) -> Path:
        source = Path(file.raw.get("local_path") or file.id)
        if not self.copy_to_temp:
            return source
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / file.name
        shutil.copy2(source, target)
        return target

    def fingerprint(self, file: RemoteFile) -> str:
        parts = [self.name, file.path, file.revision or "", str(file.size or "")]
        return hashlib.sha256("\0".join(parts).encode("utf-8")).hexdigest()

