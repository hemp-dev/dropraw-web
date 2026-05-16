from __future__ import annotations

from PIL import Image


def resize_long_edge(img: Image.Image, max_size: int) -> Image.Image:
    if max_size <= 0:
        return img.copy()
    width, height = img.size
    long_edge = max(width, height)
    if long_edge <= max_size:
        return img.copy()
    scale = max_size / long_edge
    size = (max(1, round(width * scale)), max(1, round(height * scale)))
    return img.resize(size, Image.Resampling.LANCZOS)


def generate_variants(img: Image.Image, responsive_sizes: list[int], max_size: int) -> list[tuple[str, Image.Image]]:
    if responsive_sizes:
        return [(str(size), resize_long_edge(img, size)) for size in responsive_sizes]
    return [("full", resize_long_edge(img, max_size))]

