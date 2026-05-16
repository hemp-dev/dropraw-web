from __future__ import annotations

from pathlib import Path

from PIL import Image, features


def _rgb(img: Image.Image) -> Image.Image:
    if img.mode in {"RGB", "L"}:
        return img
    return img.convert("RGB")


def save_webp(img: Image.Image, path: Path, quality: int = 88, lossless: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, format="WEBP", quality=quality, method=6, lossless=lossless)


def save_jpeg(img: Image.Image, path: Path, quality: int = 88) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    _rgb(img).save(path, format="JPEG", quality=quality, optimize=True, progressive=True)


def save_png(img: Image.Image, path: Path, compress_level: int = 9) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, format="PNG", optimize=True, compress_level=compress_level)


def save_avif_optional(img: Image.Image, path: Path, quality: int = 88) -> None:
    if not features.check("avif"):
        raise RuntimeError("Pillow AVIF support is not available in this environment.")
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, format="AVIF", quality=quality)


def save_image(img: Image.Image, path: Path, fmt: str, quality: int, *, webp_lossless: bool, png_compress_level: int) -> None:
    if fmt == "webp":
        save_webp(img, path, quality=quality, lossless=webp_lossless)
    elif fmt == "jpg":
        save_jpeg(img, path, quality=quality)
    elif fmt == "png":
        save_png(img, path, compress_level=png_compress_level)
    elif fmt == "avif":
        save_avif_optional(img, path, quality=quality)
    else:
        raise ValueError(f"Unsupported format: {fmt}")

