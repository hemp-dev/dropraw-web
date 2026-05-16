from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field


class RemoteFile(BaseModel):
    provider: str
    id: str
    name: str
    path: str
    size: int | None = None
    modified_at: datetime | None = None
    revision: str | None = None
    mime_type: str | None = None
    is_folder: bool = False
    raw: dict[str, Any] = Field(default_factory=dict)


class ConversionPreset(BaseModel):
    name: str
    formats: list[str] = Field(default_factory=lambda: ["webp"])
    max_size: int = 0
    responsive_sizes: list[int] = Field(default_factory=list)
    quality: int = 88
    webp_lossless: bool = False
    png_compress_level: int = 9
    jpeg_quality: int | None = None
    metadata_mode: Literal["strip", "keep-color", "keep-all"] = "strip"
    half_size: bool = False


class JobConfig(BaseModel):
    source: str
    provider: str = "auto"
    output_dir: Path = Path("web_export")
    preset: str = "web"
    formats: list[str] | None = None
    max_size: int | None = None
    responsive_sizes: list[int] | None = None
    quality: int | None = None
    overwrite: bool = False
    resume: bool = True
    only_failed: Path | None = None
    list_retries: int = 8
    download_retries: int = 8
    retry_delay: float = 3.0
    cooldown: float = 0.3
    download_workers: int = 2
    convert_workers: int = 2
    metadata_mode: Literal["strip", "keep-color", "keep-all"] | None = None
    temp_dir: Path | None = None
    dropbox_token: str | None = None
    dry_run: bool = False
    verbose: bool = False


class AssetResult(BaseModel):
    source_path: str
    output_path: str
    format: str
    width: int = 0
    height: int = 0
    input_size: int | None = None
    output_size: int | None = None
    status: str
    error: str | None = None
    output_size_name: str = "full"


class FailedItem(BaseModel):
    rel_path: str
    error: str


class JobSummary(BaseModel):
    job_id: str
    source: str
    provider: str
    output_dir: Path
    preset: str
    started_at: str | None = None
    finished_at: str | None = None
    total_raw_files: int = 0
    processed: int = 0
    skipped: int = 0
    failed: int = 0
    output_files_count: int = 0
    total_input_bytes: int = 0
    total_output_bytes: int = 0
    formats: list[str] = Field(default_factory=list)
    sizes: list[str] = Field(default_factory=list)
    errors: list[FailedItem] = Field(default_factory=list)
