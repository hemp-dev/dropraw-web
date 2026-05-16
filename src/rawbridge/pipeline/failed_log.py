from __future__ import annotations

from pathlib import Path
from typing import Iterable

from rawbridge.constants import DEFAULT_FAILED_LOG
from rawbridge.models import FailedItem, RemoteFile


def write_failed_log(out_dir: Path, failed_items: Iterable[FailedItem]) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / DEFAULT_FAILED_LOG
    lines = ["# rel_path\terror\n"]
    for item in failed_items:
        rel_path = _tsv_field(item.rel_path)
        error = item.error.replace("\n", " ").replace("\t", " ")
        lines.append(f"{rel_path}\t{error}\n")
    path.write_text("".join(lines), encoding="utf-8")
    return path


def read_failed_log(path: Path) -> list[FailedItem]:
    items: list[FailedItem] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        rel_path, _, error = line.partition("\t")
        items.append(FailedItem(rel_path=rel_path, error=error))
    return items


def filter_files_by_failed_log(files: Iterable[RemoteFile], failed_paths: Iterable[str]) -> list[RemoteFile]:
    wanted = {path.strip().replace("\\", "/").lstrip("/") for path in failed_paths}
    return [file for file in files if file.path.replace("\\", "/").lstrip("/") in wanted]


def _tsv_field(value: str) -> str:
    return value.replace("\n", " ").replace("\t", " ")
