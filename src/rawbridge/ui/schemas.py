from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field


ProviderId = Literal["auto", "local", "dropbox", "google-drive", "s3", "onedrive", "yadisk", "box"]


class RetrySettings(BaseModel):
    list_retries: int = Field(8, ge=1)
    download_retries: int = Field(8, ge=1)
    retry_delay: float = Field(3.0, ge=0)
    cooldown: float = Field(0.3, ge=0)


class ScanRequest(RetrySettings):
    source: str
    provider: ProviderId = "auto"
    dropbox_token: str | None = None


class FilePreview(BaseModel):
    path: str
    name: str
    size: int | None = None
    provider: str


class ScanResponse(BaseModel):
    job_preview_id: str
    provider: str
    files_count: int
    total_size: int
    folders_count: int
    first_files: list[FilePreview]
    unsupported_files_count: int = 0
    warnings: list[str] = Field(default_factory=list)


class JobCreateRequest(RetrySettings):
    source: str
    provider: ProviderId = "auto"
    output_dir: Path
    preset: str = "web"
    formats: list[str] | None = None
    quality: int | None = Field(None, ge=1, le=100)
    max_size: int | None = None
    responsive_sizes: list[int] | None = None
    overwrite: bool = False
    resume: bool = True
    only_failed: Path | None = None
    metadata_mode: Literal["strip", "keep-color", "keep-all"] | None = "strip"
    dropbox_token: str | None = None


class JobCreateResponse(BaseModel):
    job_id: str
    status: str


class JobEvent(BaseModel):
    id: int | None = None
    level: str
    message: str
    payload: dict = Field(default_factory=dict)
    created_at: str | None = None


class JobStatus(BaseModel):
    job_id: str
    status: str
    source: str | None = None
    provider: str | None = None
    output_dir: str | None = None
    total_files: int = 0
    processed_files: int = 0
    skipped_files: int = 0
    failed_files: int = 0
    started_at: str | None = None
    finished_at: str | None = None
    current_file: str | None = None
    progress: float = 0


class Settings(BaseModel):
    default_output_dir: str = "web_export"
    default_preset: str = "web"
    temp_dir: str | None = None
    max_temp_size: str | None = None
    default_retry_settings: RetrySettings = Field(default_factory=RetrySettings)
