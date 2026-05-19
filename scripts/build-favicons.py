#!/usr/bin/env python3
"""Build favicon PNGs from the client crest in the brand book (PDF page 7)."""

from __future__ import annotations

import io
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
DEFAULT_PDF = Path.home() / "Downloads" / "Брендбук НЦ Россия_removed.pdf"


def crop_crest(pdf: Path) -> "object":
    import fitz
    from PIL import Image

    doc = fitz.open(pdf)
    page = doc[6]
    pix = page.get_pixmap(matrix=fitz.Matrix(5, 5), alpha=False)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    w, h = img.size
    crop = img.crop((int(w * 0.54), int(h * 0.30), int(w * 0.74), int(h * 0.82)))
    side = max(crop.size) + 40
    square = Image.new("RGBA", (side, side), (255, 253, 248, 255))
    square.paste(crop, ((side - crop.width) // 2, (side - crop.height) // 2))
    return square


def sips_resize(src: Path, size: int, dest: Path) -> None:
    subprocess.run(
        ["sips", "-z", str(size), str(size), str(src), "--out", str(dest)],
        check=True,
        capture_output=True,
    )


def main() -> None:
    pdf = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PDF
    if not pdf.is_file():
        sys.exit(f"Brand book not found: {pdf}")

    buf = io.BytesIO()
    crop_crest(pdf).save(buf, format="PNG")
    tmp = ASSETS / ".crest-src.png"
    tmp.write_bytes(buf.getvalue())

    sips_resize(tmp, 256, ASSETS / "rossiya-crest.png")
    sips_resize(tmp, 512, ASSETS / "favicon.png")
    sips_resize(tmp, 32, ASSETS / "favicon-32.png")
    sips_resize(tmp, 180, ASSETS / "apple-touch-icon.png")
    tmp.unlink(missing_ok=True)
    print("wrote favicon.png, favicon-32.png, apple-touch-icon.png, rossiya-crest.png")


if __name__ == "__main__":
    main()
