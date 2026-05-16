from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MetadataPolicy:
    mode: str
    keep_icc: bool
    keep_exif: bool
    remove_gps: bool
    remove_private_camera_data: bool


def metadata_policy(mode: str) -> str:
    if mode not in {"strip", "keep-color", "keep-all"}:
        raise ValueError(f"Unsupported metadata mode: {mode}")
    return mode


def resolve_metadata_policy(mode: str) -> MetadataPolicy:
    metadata_policy(mode)
    if mode == "keep-all":
        return MetadataPolicy(mode=mode, keep_icc=True, keep_exif=True, remove_gps=False, remove_private_camera_data=False)
    if mode == "keep-color":
        return MetadataPolicy(mode=mode, keep_icc=True, keep_exif=False, remove_gps=True, remove_private_camera_data=True)
    return MetadataPolicy(mode=mode, keep_icc=True, keep_exif=False, remove_gps=True, remove_private_camera_data=True)
