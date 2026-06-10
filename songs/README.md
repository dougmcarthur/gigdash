# Songs

Your repertoire in [ChordPro](https://www.chordpro.org/) format (`.cho`),
one file per song. These were exported from the Setlists iOS app as RTF and
converted with `tools/rtf2chordpro.py` (the RTF originals live in the
Dropbox export, not in this repo).

Format basics:

- `{t:Song Title}` — title
- `{st:Artist}` — artist/subtitle
- `[G]`, `[Am]` … inline chords above lyrics (none of the current exports
  have chords, but the format supports adding them)
- Blank lines separate verses/sections

To import new exports from the Setlists app, drop the `.rtf` files in a
folder and run:

```sh
pip install striprtf
tools/rtf2chordpro.py path/to/rtfs songs/
```

This folder is **not** published to the website — Cloudflare Pages only
serves `display/`.

The `.cho` files are also **encrypted at rest** in the repo with
[transcrypt](https://github.com/elasticdog/transcrypt); see `CLAUDE.md` for
how to unlock a fresh clone. Don't upload songs through the GitHub web UI —
that bypasses the encryption filter and stores plaintext.
