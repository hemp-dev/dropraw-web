from __future__ import annotations

from pathlib import Path
from typing import Any

from PIL import Image


def decode_raw_to_pil(path: Path, settings: Any) -> Image.Image:
    try:
        import rawpy
    except ImportError as exc:
        raise RuntimeError("rawpy is required for RAW decoding. Install rawbridge dependencies.") from exc

    half_size = bool(getattr(settings, "half_size", False))
    no_auto_bright = bool(getattr(settings, "no_auto_bright", False))
    output_bps = int(getattr(settings, "output_bps", 8))
    white_balance = getattr(settings, "white_balance", "camera")
    use_camera_wb = white_balance != "auto"

    with rawpy.imread(str(path)) as raw:
        rgb = raw.postprocess(
            use_camera_wb=use_camera_wb,
            output_bps=output_bps,
            no_auto_bright=no_auto_bright,
            half_size=half_size,
            output_color=rawpy.ColorSpace.sRGB,
        )
    mode = "RGB" if output_bps == 8 else "RGB"
    return Image.fromarray(rgb, mode=mode)

