from __future__ import annotations

from pathlib import Path

RAW_EXTENSIONS = {
    ".nef",
    ".nrw",
    ".cr2",
    ".cr3",
    ".arw",
    ".srf",
    ".sr2",
    ".raf",
    ".rw2",
    ".orf",
    ".dng",
    ".pef",
    ".raw",
    ".rwl",
    ".iiq",
    ".3fr",
    ".erf",
    ".mef",
    ".mos",
    ".mrw",
    ".srw",
    ".x3f",
}

SUPPORTED_FORMATS = {"webp", "jpg", "jpeg", "png", "avif"}
DEFAULT_FAILED_LOG = "dropraw_failed.tsv"
DEFAULT_MANIFEST = ".dropraw_manifest.sqlite"
DEFAULT_TEMP_DIR = ".dropraw_tmp"


def is_raw_file(path_or_name: str) -> bool:
    return Path(path_or_name).suffix.lower() in RAW_EXTENSIONS


def normalize_format(fmt: str) -> str:
    value = fmt.strip().lower()
    if value == "jpeg":
        return "jpg"
    return value

