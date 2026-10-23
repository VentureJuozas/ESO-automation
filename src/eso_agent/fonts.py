"""Bundled DejaVu for Lithuanian glyphs in HTML and PDF."""
from __future__ import annotations

from pathlib import Path

FONT_DIR = Path(__file__).resolve().parent / "static" / "fonts"
DEJAVU = FONT_DIR / "DejaVuSans.ttf"
DEJAVU_BOLD = FONT_DIR / "DejaVuSans-Bold.ttf"
GLYPHS = "ąčęėįšųūžĄČĘĖĮŠŲŪŽ"


def font_face_css() -> str:
    return (
        "@font-face{font-family:DejaVu;src:url('/api/fonts/DejaVuSans.ttf') format('truetype');font-weight:400;}"
        "@font-face{font-family:DejaVu;src:url('/api/fonts/DejaVuSans-Bold.ttf') format('truetype');font-weight:700;}"
    )
