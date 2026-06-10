#!/usr/bin/env python3
"""Convert songs exported from the Setlists iOS app (RTF) to ChordPro (.cho).

The Setlists app wraps ChordPro-style content ({t:...}, {st:...}, [chords])
in RTF. This strips the RTF layer, normalizes Unicode line separators and
smart punctuation artifacts, and writes UTF-8 .cho files.

Usage: tools/rtf2chordpro.py <dir-with-rtf-files> [output-dir]
Requires: pip install striprtf
"""
import sys
import unicodedata
from pathlib import Path

from striprtf.striprtf import rtf_to_text


def convert(rtf_source: str) -> str:
    text = rtf_to_text(rtf_source, encoding="cp1252")
    # The app emits U+2028 LINE SEPARATOR for some line breaks.
    text = text.replace(" ", "\n")
    # Collapse runs of 3+ blank lines left over from RTF paragraph marks.
    lines = [ln.rstrip() for ln in text.split("\n")]
    out, blanks = [], 0
    for ln in lines:
        blanks = blanks + 1 if not ln else 0
        if blanks <= 2:
            out.append(ln)
    return "\n".join(out).strip() + "\n"


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    src = Path(sys.argv[1])
    dst = Path(sys.argv[2]) if len(sys.argv) > 2 else src
    dst.mkdir(parents=True, exist_ok=True)
    for rtf in sorted(src.glob("*.rtf")):
        cho = dst / (rtf.stem + ".cho")
        cho.write_text(convert(rtf.read_text(errors="replace")), encoding="utf-8")
        print(f"{rtf.name} -> {cho.name}")


if __name__ == "__main__":
    main()
