#!/usr/bin/env python3
"""Build favicon PNGs from the У-mark on page 1 of the Универмаг brand guide PDF."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
DEFAULT_SRC = ASSETS / "u-mark-green.png"


def crop_mark_from_pdf(pdf: Path) -> Path:
    import fitz
    from PIL import Image, ImageChops

    doc = fitz.open(pdf)
    page = doc[0]
    pix = page.get_pixmap(matrix=fitz.Matrix(5, 5), alpha=False)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    w, h = img.size
    mark = img.crop((int(w * 0.34), int(h * 0.10), int(w * 0.66), int(h * 0.50)))

    bg = Image.new("RGB", mark.size, (255, 255, 255))
    diff = ImageChops.difference(mark, bg)
    bbox = diff.getbbox()
    if bbox:
        mark = mark.crop(bbox)

    pad = int(max(mark.size) * 0.12)
    side = max(mark.size) + pad * 2
    square = Image.new("RGBA", (side, side), (255, 253, 248, 255))
    square.paste(mark.convert("RGBA"), ((side - mark.width) // 2, (side - mark.height) // 2))

    src = ASSETS / "u-mark-source.png"
    square.save(src)
    tmp = ASSETS / ".crest-src.png"
    square.save(tmp)
    return tmp


def sips_resize(src: Path, size: int, dest: Path) -> None:
    subprocess.run(
        ["sips", "-z", str(size), str(size), str(src), "--out", str(dest)],
        check=True,
        capture_output=True,
    )


def main() -> None:
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SRC
    if not src.is_file():
        sys.exit(f"Source not found: {src}")

    if src.suffix.lower() == ".pdf":
        tmp = crop_mark_from_pdf(src)
    else:
        from PIL import Image, ImageChops

        mark = Image.open(src).convert("RGBA")
        bg = Image.new("RGBA", mark.size, (255, 255, 255, 255))
        diff = ImageChops.difference(mark, bg)
        bbox = diff.getbbox()
        if bbox:
            mark = mark.crop(bbox)
        pad = int(max(mark.size) * 0.14)
        side = max(mark.size) + pad * 2
        square = Image.new("RGBA", (side, side), (255, 255, 255, 255))
        square.paste(mark, ((side - mark.width) // 2, (side - mark.height) // 2), mark)
        tmp = ASSETS / ".crest-src.png"
        square.save(tmp)

    sips_resize(tmp, 256, ASSETS / "rossiya-crest.png")
    sips_resize(tmp, 512, ASSETS / "favicon.png")
    sips_resize(tmp, 32, ASSETS / "favicon-32.png")
    sips_resize(tmp, 180, ASSETS / "apple-touch-icon.png")
    tmp.unlink(missing_ok=True)
    print("wrote favicon.png, favicon-32.png, apple-touch-icon.png, rossiya-crest.png")


if __name__ == "__main__":
    main()
