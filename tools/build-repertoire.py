#!/usr/bin/env python3
"""Generate display/repertoire/index.html from songs/*.cho.

Requires songs/*.cho to be decrypted (transcrypt) in the working tree.
Output is gitignored-by-convention-only-in-spirit: it embeds full lyrics
and chords, so it must never be referenced from public navigation and
should be treated as an unlisted page.
"""
import html
import json
import re
from pathlib import Path

SONGS_DIR = Path(__file__).resolve().parent.parent / "songs"
OUT_PATH = Path(__file__).resolve().parent.parent / "display" / "repertoire" / "index.html"

ORIGINAL_ARTISTS = {"Doug McArthur", "Doug & Amber"}

CHORD_RE = re.compile(r"\[([^\]]+)\]")


def render_line(line):
    if line.startswith("{c:"):
        text = line[3:].rstrip("}")
        return f'<div class="chord-line">{html.escape(text)}</div>'
    if line.startswith("{") and line.endswith("}"):
        return ""
    escaped = html.escape(line)
    rendered = CHORD_RE.sub(lambda m: f'<span class="chord">{html.escape(m.group(1))}</span>', escaped)
    return f"<div>{rendered or '&nbsp;'}</div>"


def parse_song(path):
    lines = path.read_text(encoding="utf-8").splitlines()
    title = path.stem
    artist = ""
    body_lines = []
    for line in lines:
        m = re.match(r"\{t:(.*)\}$", line)
        if m:
            title = m.group(1)
            continue
        m = re.match(r"\{st:(.*)\}$", line)
        if m:
            artist = m.group(1)
            continue
        body_lines.append(render_line(line))
    body_html = "\n".join(body_lines)
    return {"title": title, "artist": artist, "body": body_html}


def main():
    songs = [parse_song(p) for p in sorted(SONGS_DIR.glob("*.cho"))]
    covers = sorted((s for s in songs if s["artist"] not in ORIGINAL_ARTISTS), key=lambda s: s["title"].lower())
    originals = sorted((s for s in songs if s["artist"] in ORIGINAL_ARTISTS), key=lambda s: s["title"].lower())

    data = {"covers": covers, "originals": originals}
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(TEMPLATE.replace("__DATA__", json.dumps(data)), encoding="utf-8")
    print(f"Wrote {OUT_PATH} ({len(covers)} covers, {len(originals)} originals)")


TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Doug McArthur &mdash; Repertoire</title>
<style>
  :root {
    --bg: #0b0d12;
    --fg: #f5f2ea;
    --accent: #e8b44a;
    --muted: #9aa0ab;
    --card: #161a22;
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  html, body {
    background: var(--bg);
    color: var(--fg);
    font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
    -webkit-text-size-adjust: 100%;
  }
  main { max-width: 640px; margin: 0 auto; padding: 1.2rem 1rem 4rem; }
  h1 { font-size: 1.6rem; margin-bottom: 0.2rem; }
  .subtitle { color: var(--muted); margin-bottom: 1.5rem; font-size: 0.95rem; }
  h2 {
    font-size: 1.1rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--accent);
    margin: 1.8rem 0 0.6rem;
  }
  .song { border-bottom: 1px solid #2a2f3a; }
  .song-toggle {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
    text-align: left;
    background: none;
    border: none;
    color: var(--fg);
    font-size: 1.05rem;
    padding: 0.85rem 0.2rem;
    cursor: pointer;
  }
  .song-toggle .artist {
    color: var(--muted);
    font-size: 0.85rem;
    font-weight: normal;
  }
  .song-toggle .arrow {
    transition: transform 0.2s ease;
    color: var(--muted);
    flex-shrink: 0;
    margin-left: 0.6rem;
  }
  .song.is-open .song-toggle .arrow { transform: rotate(90deg); }
  .song-body {
    display: none;
    padding: 0 0.2rem 1.2rem;
    font-family: "SF Mono", "Menlo", "Consolas", monospace;
    font-size: 0.9rem;
    line-height: 1.5;
    white-space: pre-wrap;
    overflow-x: auto;
  }
  .song.is-open .song-body { display: block; }
  .chord { color: var(--accent); font-weight: 700; }
  .chord-line { color: var(--muted); font-style: italic; margin-bottom: 0.3rem; }
</style>
</head>
<body>
<main>
  <h1>Doug McArthur</h1>
  <p class="subtitle">Repertoire &mdash; tap a song for chords &amp; lyrics</p>
  <section id="originals"></section>
  <section id="covers"></section>
</main>
<script>
  const data = __DATA__;

  function renderSection(el, heading, songs) {
    const h2 = document.createElement('h2');
    h2.textContent = heading;
    el.appendChild(h2);
    for (const song of songs) {
      const wrap = document.createElement('div');
      wrap.className = 'song';

      const toggle = document.createElement('button');
      toggle.className = 'song-toggle';
      toggle.innerHTML = `<span>${song.title}<br><span class="artist">${song.artist}</span></span><span class="arrow">&#9656;</span>`;
      toggle.addEventListener('click', () => wrap.classList.toggle('is-open'));

      const body = document.createElement('div');
      body.className = 'song-body';
      body.innerHTML = song.body;

      wrap.appendChild(toggle);
      wrap.appendChild(body);
      el.appendChild(wrap);
    }
  }

  renderSection(document.getElementById('originals'), 'Originals', data.originals);
  renderSection(document.getElementById('covers'), 'Covers', data.covers);
</script>
</body>
</html>
"""

if __name__ == "__main__":
    main()
