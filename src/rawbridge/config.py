from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .constants import SUPPORTED_FORMATS, normalize_format
from .models import ConversionPreset, JobConfig


def _repo_config_path(name: str) -> Path:
    package_path = Path(__file__).resolve().parent / "configs" / name
    if package_path.exists():
        return package_path
    return Path(__file__).resolve().parents[2] / "configs" / name


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Config file must contain a mapping: {path}")
    return data


def load_presets(path: Path | None = None) -> dict[str, ConversionPreset]:
    raw = load_yaml(path or _repo_config_path("presets.yaml"))
    return {name: ConversionPreset(name=name, **values) for name, values in raw.items()}


def load_config(path: Path | None = None) -> dict[str, Any]:
    base = load_yaml(_repo_config_path("default.yaml"))
    if path:
        base.update(load_yaml(path))
    return base


def parse_csv_list(value: str | None) -> list[str] | None:
    if not value:
        return None
    return [part.strip() for part in value.split(",") if part.strip()]


def parse_int_csv(value: str | None) -> list[int] | None:
    if not value:
        return None
    return [int(part.strip()) for part in value.split(",") if part.strip()]


def validate_formats(formats: list[str]) -> list[str]:
    normalized = [normalize_format(fmt) for fmt in formats]
    unknown = sorted(set(normalized) - SUPPORTED_FORMATS)
    if unknown:
        raise ValueError(f"Unsupported output format(s): {', '.join(unknown)}")
    return normalized


def validate_quality(quality: int) -> int:
    if quality < 1 or quality > 100:
        raise ValueError("quality must be between 1 and 100")
    return quality


def validate_retry_settings(config: JobConfig) -> None:
    if config.list_retries < 1:
        raise ValueError("list_retries must be >= 1")
    if config.download_retries < 1:
        raise ValueError("download_retries must be >= 1")
    if config.retry_delay < 0:
        raise ValueError("retry_delay must be >= 0")
    if config.cooldown < 0:
        raise ValueError("cooldown must be >= 0")


def resolve_preset(config: JobConfig) -> ConversionPreset:
    presets = load_presets()
    if config.preset not in presets:
        raise ValueError(f"Unknown preset '{config.preset}'. Available: {', '.join(sorted(presets))}")
    preset = presets[config.preset].model_copy(deep=True)
    if config.formats is not None:
        preset.formats = validate_formats(config.formats)
    else:
        preset.formats = validate_formats(preset.formats)
    if config.max_size is not None:
        preset.max_size = config.max_size
    if config.responsive_sizes is not None:
        preset.responsive_sizes = config.responsive_sizes
    if config.quality is not None:
        preset.quality = validate_quality(config.quality)
    else:
        preset.quality = validate_quality(preset.quality)
    if config.metadata_mode is not None:
        preset.metadata_mode = config.metadata_mode
    return preset


def merge_cli_overrides(config: JobConfig, config_file: Path | None = None) -> JobConfig:
    values = load_config(config_file)
    raw = config.model_dump()
    for key, value in values.items():
        if key in raw and raw[key] in (None, JobConfig.model_fields[key].default):
            raw[key] = value
    merged = JobConfig(**raw)
    merged.output_dir = Path(merged.output_dir)
    if merged.temp_dir is not None:
        merged.temp_dir = Path(merged.temp_dir)
    if merged.only_failed is not None:
        merged.only_failed = Path(merged.only_failed)
    if not str(merged.output_dir):
        raise ValueError("output_dir is required")
    validate_retry_settings(merged)
    return merged
