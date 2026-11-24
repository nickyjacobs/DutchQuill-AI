"""Beelden klaarmaken voor gebruik in een document: oriëntatie goed, EXIF eruit, formaat dat Word en pdf
aankunnen (png of jpg), en niet groter dan nodig. Het origineel blijft onaangeroerd.

  dq beeld <bestand> [<bestand> ...] --uit <map> [--max 2400]
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

NAAR_PNG = {".png", ".gif", ".bmp", ".tif", ".tiff", ".webp", ".heic", ".heif"}
JPG = {".jpg", ".jpeg"}


def _open(pad: Path):
    from PIL import Image
    try:
        return Image.open(pad), None
    except Exception:
        # HEIC zonder pillow-heif: op macOS kan sips het omzetten
        if shutil.which("sips"):
            tmp = Path(tempfile.mkdtemp()) / (pad.stem + ".png")
            subprocess.run(["sips", "-s", "format", "png", str(pad), "--out", str(tmp)], capture_output=True)
            if tmp.is_file():
                return Image.open(tmp), "omgezet met sips"
        raise


def normaliseer(pad: Path, uit: Path, max_zijde: int = 2400) -> dict:
    from PIL import ImageOps
    ext = pad.suffix.lower()
    r: dict = {"bron": str(pad)}
    uit.mkdir(parents=True, exist_ok=True)
    naam = re.sub(r"[^\w\-. ]", "_", pad.stem).strip() or "beeld"
    if ext == ".svg":
        doel = uit / f"{naam}.svg"
        shutil.copy2(pad, doel)
        return {**r, "pad": str(doel), "formaat": "svg",
                "waarschuwingen": ["SVG kan niet in .docx; zet hem om naar png als hij in een document moet."]}
    try:
        img, noot = _open(pad)
    except Exception as e:
        return {**r, "fout": f"Kan beeld niet openen ({type(e).__name__}). Sla het op als png of jpg."}
    with img:
        if getattr(img, "is_animated", False):
            img.seek(0)
        img = ImageOps.exif_transpose(img)
        verkleind = max(img.size) > max_zijde
        if verkleind:
            img.thumbnail((max_zijde, max_zijde))
        if ext in JPG:
            doel = uit / f"{naam}.jpg"
            img.convert("RGB").save(doel, "JPEG", quality=90, optimize=True)  # zonder exif=: metadata weg
        else:
            doel = uit / f"{naam}.png"
            if img.mode not in ("RGB", "RGBA", "L", "LA"):
                img = img.convert("RGBA")
            img.save(doel, "PNG", optimize=True)
        b, h = img.size
    uitkomst = {**r, "pad": str(doel), "formaat": doel.suffix[1:], "breedte": b, "hoogte": h,
                "orientatie": "liggend" if b > h * 1.15 else "staand" if h > b * 1.15 else "vierkant",
                "verkleind": verkleind}
    if noot:
        uitkomst["noot"] = noot
    return uitkomst


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(prog="dq beeld", description="Beelden klaarmaken voor documenten")
    p.add_argument("bestanden", nargs="+")
    p.add_argument("--uit", required=True)
    p.add_argument("--max", type=int, default=2400, help="Langste zijde in pixels (standaard 2400)")
    a = p.parse_args(argv)
    uitkomst = []
    for b in a.bestanden:
        pad = Path(b).expanduser()
        uitkomst.append(normaliseer(pad, Path(a.uit), a.max) if pad.is_file() else {"bron": b, "fout": "niet gevonden"})
    print(json.dumps(uitkomst, ensure_ascii=False, indent=2))
    if any("fout" in u for u in uitkomst):
        sys.exit(1)
