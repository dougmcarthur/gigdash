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

ORIGINAL_ARTISTS = {"Doug McArthur", "Doug & Amber", "Broken Halo"}

# Covers performed solo; everything else is full-band-only (Radio Riders).
SOLO_COVER_TITLES = {
    "Across The Universe",
    "Ain't No Sunshine",
    "Baby One More Time",
    "Don't Dream It's Over",
    "Eleanor Rigby",
    "Fireworks",
    "I Will Survive",
    "Imagine",
    "It's All Been Done",
    "Love You Madly",
    "Mary Jane's Last Dance",
    "Mary Janes Last Dance",
    "Money",
    "Please Don't Let Me Be Misunderstood",
    "That's All Right",
    "The Way You Make Me Feel",
    "What I Got",
    "Wheat Kings",
}


# Solo covers that also appear in the Radio Riders (full band) set.
BOTH_COVER_TITLES = {
    "Fireworks",
    "I Will Survive",
    "It's All Been Done",
    "Mary Jane's Last Dance",
    "Mary Janes Last Dance",
    "What I Got",
}


def normalize_apostrophes(s):
    return s.replace("’", "'")

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
    songs = [s for s in songs if s["artist"] != "Ladywood"]
    originals = sorted((s for s in songs if s["artist"] in ORIGINAL_ARTISTS), key=lambda s: s["title"].lower())
    covers = [s for s in songs if s["artist"] not in ORIGINAL_ARTISTS]
    solo_covers = sorted((s for s in covers if normalize_apostrophes(s["title"]) in SOLO_COVER_TITLES), key=lambda s: s["title"].lower())
    band_covers = sorted((s for s in covers if normalize_apostrophes(s["title"]) not in SOLO_COVER_TITLES or normalize_apostrophes(s["title"]) in BOTH_COVER_TITLES), key=lambda s: s["title"].lower())

    data = {"originals": originals, "solo_covers": solo_covers, "band_covers": band_covers}
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(TEMPLATE.replace("__DATA__", json.dumps(data)), encoding="utf-8")
    print(f"Wrote {OUT_PATH} ({len(originals)} originals, {len(solo_covers)} solo covers, {len(band_covers)} band covers)")


TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Doug McArthur &mdash; Repertoire</title>
<style>
  :root {
    --bg: #0b0d12;
    --bg-raised: #11141b;
    --fg: #f5f2ea;
    --accent: #e8b44a;
    --muted: #9aa0ab;
    --border: #242933;
    --side-pad: 1.5rem;
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  * {
    scrollbar-width: thin;
    scrollbar-color: #3a4150 transparent;
  }
  *::-webkit-scrollbar { width: 10px; height: 10px; }
  *::-webkit-scrollbar-track { background: transparent; }
  *::-webkit-scrollbar-thumb {
    background: #3a4150;
    border-radius: 8px;
    border: 2px solid transparent;
    background-clip: content-box;
  }
  *::-webkit-scrollbar-thumb:hover { background: #4a5263; background-clip: content-box; }
  html, body {
    height: 100%;
    overflow: hidden;
    background: var(--bg);
    color: var(--fg);
    font-family: -apple-system, "Helvetica Neue", Helvetica, Arial, sans-serif;
    -webkit-text-size-adjust: 100%;
  }
  .layout {
    display: flex;
    flex-direction: column;
    height: 100%;
  }
  .sidebar {
    flex: 1;
    min-height: 0;
    padding: 1.75rem var(--side-pad) 2.5rem;
    background: var(--bg-raised);
    overflow-y: auto;
    scrollbar-gutter: stable;
  }
  .sidebar h1 {
    font-size: 1.5rem;
    font-weight: 700;
    letter-spacing: 0.01em;
    margin-bottom: 0.3rem;
  }
  .subtitle { color: var(--muted); margin-bottom: 2rem; font-size: 0.9rem; line-height: 1.5; }
  .category { border-bottom: 1px solid var(--border); }
  .category:last-child { border-bottom: none; }
  .category-toggle {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 0.6rem;
    width: 100%;
    text-align: left;
    background: none;
    border: none;
    border-radius: 8px;
    color: var(--accent);
    font-size: 0.8rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    padding: 1.1rem 0.6rem;
    margin: 0 -0.6rem;
    cursor: pointer;
    transition: background-color 0.15s ease;
  }
  .category-toggle:hover { background: rgba(245, 242, 234, 0.05); }
  .category-toggle:focus-visible {
    outline: 2px solid var(--accent);
    outline-offset: 2px;
  }
  .category-toggle .count {
    color: var(--muted);
    font-weight: normal;
    text-transform: none;
    letter-spacing: normal;
    margin-left: 0.5rem;
  }
  .category-toggle .arrow {
    flex-shrink: 0;
    font-size: 1.1rem;
    opacity: 0.7;
    transition: transform 0.15s ease;
  }
  .category.is-expanded .category-toggle .arrow { transform: rotate(90deg); }
  .song-list { display: none; padding-bottom: 0.5rem; }
  .category.is-expanded .song-list { display: block; }
  .song-item { border-bottom: 1px solid var(--border); }
  .song-item:last-child { border-bottom: none; }
  .song-toggle {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 0.6rem;
    width: 100%;
    text-align: left;
    background: none;
    border: none;
    border-radius: 8px;
    color: var(--fg);
    font-size: 1rem;
    line-height: 1.4;
    padding: 0.8rem 0.6rem;
    margin: 0 -0.6rem;
    cursor: pointer;
    transition: background-color 0.15s ease, color 0.15s ease;
  }
  .song-toggle:hover { background: rgba(245, 242, 234, 0.05); }
  .song-toggle:focus-visible {
    outline: 2px solid var(--accent);
    outline-offset: 2px;
  }
  .song-toggle .title { font-weight: 500; }
  .song-toggle .artist {
    display: block;
    color: var(--muted);
    font-size: 0.82rem;
    font-weight: normal;
    margin-top: 0.15rem;
  }
  .song-toggle .arrow {
    color: var(--muted);
    flex-shrink: 0;
    font-size: 1.1rem;
    opacity: 0.6;
    transition: transform 0.15s ease;
  }
  .song-item.is-active .song-toggle { background: rgba(232, 180, 74, 0.1); }
  .song-item.is-active .song-toggle .title { color: var(--accent); }
  .song-item.is-active .song-toggle .arrow { color: var(--accent); opacity: 1; transform: translateX(2px); }

  .content {
    display: none;
    flex: 1;
    min-height: 0;
    overflow-y: auto;
    overflow-x: auto;
    scrollbar-gutter: stable;
  }
  .content.is-open { display: block; }
  .content-inner {
    padding: 1.5rem var(--side-pad) 4rem;
    max-width: 70ch;
  }
  .back-button {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: none;
    border: 1px solid var(--border);
    color: var(--muted);
    border-radius: 999px;
    padding: 0.45rem 1rem;
    font-size: 0.9rem;
    margin-bottom: 1.5rem;
    cursor: pointer;
    transition: color 0.15s ease, border-color 0.15s ease;
  }
  .back-button:hover { color: var(--fg); border-color: #3a4150; }
  .content-title {
    font-size: 1.6rem;
    font-weight: 700;
    letter-spacing: 0.01em;
    margin-bottom: 0.25rem;
  }
  .content-artist {
    color: var(--muted);
    font-size: 0.95rem;
    margin-bottom: 2rem;
    padding-bottom: 1.5rem;
    border-bottom: 1px solid var(--border);
  }
  .content-body {
    font-family: "SF Mono", "Menlo", "Consolas", monospace;
    font-size: 0.95rem;
    line-height: 1.7;
    white-space: pre-wrap;
  }
  .chord { color: var(--accent); font-weight: 700; }
  .chord-line {
    color: var(--muted);
    font-style: italic;
    margin-bottom: 0.4rem;
  }

  /* Mobile drill-down: categories -> songs -> content, one screen at a time. */
  @media (max-width: 799px) {
    body[data-view="songs"] .sidebar-header,
    body[data-view="content"] .sidebar-header { display: none; }
    body[data-view="songs"] .category:not(.is-expanded),
    body[data-view="content"] .category:not(.is-expanded) { display: none; }
    body[data-view="content"] .sidebar { display: none; }
  }

  @media (min-width: 800px) {
    .layout { flex-direction: row; }
    .sidebar {
      width: 33%;
      min-width: 280px;
      max-width: 420px;
      flex-shrink: 0;
      border-right: 1px solid var(--border);
    }
    .content-inner {
      padding: 3rem 3.5rem 5rem;
    }
    .content-body {
      font-size: 1.15rem;
      line-height: 1.85;
    }
    .content:not(.is-open) {
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .content:not(.is-open)::after {
      content: "Select a song to view chords & lyrics";
      color: var(--muted);
      font-family: -apple-system, "Helvetica Neue", Helvetica, Arial, sans-serif;
      font-size: 1rem;
    }
    .back-button { display: none; }
    .content-title { font-size: 2.1rem; }
  }
</style>
</head>
<body>
<div class="layout">
  <nav class="sidebar">
    <div class="sidebar-header">
      <h1>Doug McArthur</h1>
      <p class="subtitle">Repertoire &mdash; select a category, then a song, for chords &amp; lyrics</p>
    </div>
    <div id="originals" class="category"></div>
    <div id="solo-covers" class="category"></div>
    <div id="band-covers" class="category"></div>
  </nav>
  <article class="content" id="content">
    <div class="content-inner">
      <button class="back-button" id="back-button">&larr; Back to list</button>
      <h2 class="content-title" id="content-title"></h2>
      <p class="content-artist" id="content-artist"></p>
      <div class="content-body" id="content-body"></div>
    </div>
  </article>
</div>
<script>
  const data = __DATA__;
  const content = document.getElementById('content');
  const contentTitle = document.getElementById('content-title');
  const contentArtist = document.getElementById('content-artist');
  const contentBody = document.getElementById('content-body');
  const categories = Array.from(document.querySelectorAll('.category'));
  const songMap = {};
  let activeItem = null;

  function isMobile() {
    return window.innerWidth < 800;
  }

  function applyState(state) {
    categories.forEach((c) => c.classList.remove('is-expanded'));
    if (activeItem) activeItem.classList.remove('is-active');
    content.classList.remove('is-open');
    document.body.dataset.view = state.view;

    if (state.categoryId) {
      const cat = document.getElementById(state.categoryId);
      if (cat) cat.classList.add('is-expanded');
    }
    if (state.view === 'content' && state.songId && songMap[state.songId]) {
      const entry = songMap[state.songId];
      activeItem = entry.item;
      activeItem.classList.add('is-active');
      contentTitle.textContent = entry.song.title;
      contentArtist.textContent = entry.song.artist;
      contentBody.innerHTML = entry.song.body;
      content.classList.add('is-open');
      content.scrollTop = 0;
    }
  }

  function navigateTo(state) {
    applyState(state);
    if (isMobile()) history.pushState(state, '');
  }

  window.addEventListener('popstate', (e) => {
    applyState(e.state || { view: 'categories' });
  });

  function showSong(song, item, songId) {
    if (isMobile()) {
      navigateTo({ view: 'content', categoryId: item.closest('.category').id, songId });
    } else {
      applyState({ view: 'content', categoryId: item.closest('.category').id, songId });
    }
  }

  document.getElementById('back-button').addEventListener('click', () => {
    if (isMobile()) {
      history.back();
    } else {
      content.classList.remove('is-open');
    }
  });

  function renderCategory(el, heading, songs) {
    const toggle = document.createElement('button');
    toggle.className = 'category-toggle';
    toggle.innerHTML = `<span>${heading}<span class="count">${songs.length}</span></span><span class="arrow">&#8250;</span>`;
    toggle.addEventListener('click', () => {
      if (isMobile()) {
        if (el.classList.contains('is-expanded')) {
          history.back();
        } else {
          navigateTo({ view: 'songs', categoryId: el.id });
        }
      } else {
        el.classList.toggle('is-expanded');
      }
    });
    el.appendChild(toggle);

    const list = document.createElement('div');
    list.className = 'song-list';
    songs.forEach((song, index) => {
      const wrap = document.createElement('div');
      wrap.className = 'song-item';
      const songId = `${el.id}-${index}`;
      songMap[songId] = { song, item: wrap };

      const songToggle = document.createElement('button');
      songToggle.className = 'song-toggle';
      songToggle.innerHTML = `<span><span class="title">${song.title}</span><span class="artist">${song.artist}</span></span><span class="arrow">&#8250;</span>`;
      songToggle.addEventListener('click', () => showSong(song, wrap, songId));

      wrap.appendChild(songToggle);
      list.appendChild(wrap);
    });
    el.appendChild(list);
  }

  renderCategory(document.getElementById('originals'), 'Originals', data.originals);
  renderCategory(document.getElementById('solo-covers'), 'Covers — Solo', data.solo_covers);
  renderCategory(document.getElementById('band-covers'), 'Covers — Radio Riders (Full Band)', data.band_covers);

  history.replaceState({ view: 'categories' }, '');
  document.body.dataset.view = 'categories';
</script>
</body>
</html>
"""

if __name__ == "__main__":
    main()
