#!/usr/bin/env python3
"""Pre-fetch the upcoming Bandsintown show(s) and bake them into the display
so the "Next Show" card works offline (e.g. on the Raspberry Pi kiosk).

Run this while you have internet, then commit the results:

    python3 tools/bake-next-show.py            # uses display/config.json
    python3 tools/bake-next-show.py --artist "Doug McArthur" --app-id XXXX
    python3 tools/bake-next-show.py --from-file events.json   # offline, from a saved response

It writes:
  * display/assets/next-show.json           — the show data the display reads
  * display/assets/next-show-poster-N.<ext> — the downloaded poster image(s)

The display prefers this baked data (offline-safe) and only falls back to a
live Bandsintown fetch when the baked file is missing. Re-run before each gig
to refresh. The "skip today's gig" filter is applied at display time, so it's
fine to bake a day or two ahead.
"""
import argparse
import datetime
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DISPLAY = REPO / "display"
ASSETS = DISPLAY / "assets"
CONFIG = DISPLAY / "config.json"

# How many upcoming shows to bake. A small list lets the display skip a show
# happening *today* and fall through to the next real one.
MAX_SHOWS = 3

# Keys whose string values are worth treating as a poster/flyer image, most
# preferred first. We don't know the exact Bandsintown field ahead of time,
# so we discover candidates and rank them.
POSTER_KEY_PRIORITY = ["flyer", "poster", "image", "photo", "thumb"]
IMAGE_EXT_RE = re.compile(r"\.(jpe?g|png|webp|gif)(\?|$)", re.IGNORECASE)


def load_config_artist():
    """Return (artistName, appId) from the first next-gig slide in config.json."""
    try:
        cfg = json.loads(CONFIG.read_text())
    except Exception as err:  # noqa: BLE001
        return None, None, f"Could not read {CONFIG}: {err}"
    for slide in cfg.get("slides", []):
        if slide.get("type") == "next-gig":
            bit = slide.get("bandsintown", {})
            return bit.get("artistName"), bit.get("appId"), None
    return None, None, "No next-gig slide found in config.json"


def fetch_events(artist, app_id):
    url = (
        f"https://rest.bandsintown.com/artists/"
        f"{urllib.parse.quote(artist)}/events?app_id={urllib.parse.quote(app_id)}"
    )
    print(f"Fetching {url}")
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def discover_images(obj, path=""):
    """Recursively collect (keypath, url) pairs that look like image URLs."""
    found = []
    if isinstance(obj, dict):
        for key, val in obj.items():
            here = f"{path}.{key}" if path else key
            if isinstance(val, str) and val.startswith("http") and (
                IMAGE_EXT_RE.search(val)
                or any(k in key.lower() for k in POSTER_KEY_PRIORITY)
            ):
                found.append((here, val))
            else:
                found.extend(discover_images(val, here))
    elif isinstance(obj, list):
        for i, val in enumerate(obj):
            found.extend(discover_images(val, f"{path}[{i}]"))
    return found


def choose_poster(candidates):
    """Pick the best image URL from discovered (keypath, url) candidates."""
    def rank(item):
        key = item[0].lower()
        for i, pref in enumerate(POSTER_KEY_PRIORITY):
            if pref in key:
                return i
        return len(POSTER_KEY_PRIORITY)
    ordered = sorted(candidates, key=rank)
    return ordered[0][1] if ordered else None


def ext_for(url, content_type):
    ct = (content_type or "").lower()
    if "png" in ct:
        return "png"
    if "webp" in ct:
        return "webp"
    if "gif" in ct:
        return "gif"
    if "jpeg" in ct or "jpg" in ct:
        return "jpg"
    m = IMAGE_EXT_RE.search(url or "")
    if m:
        return m.group(1).lower().replace("jpeg", "jpg")
    return "jpg"


def download_image(url, dest_stem):
    req = urllib.request.Request(url, headers={"User-Agent": "gigdash-bake"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = resp.read()
        ext = ext_for(url, resp.headers.get("Content-Type"))
    dest = ASSETS / f"{dest_stem}.{ext}"
    dest.write_bytes(data)
    return f"assets/{dest.name}"


def extract_show(event):
    venue = event.get("venue", {}) or {}
    location = ", ".join(
        p for p in [venue.get("city"), venue.get("region")] if p
    )
    return {
        "datetime": event.get("datetime"),
        "venue": venue.get("name", ""),
        "location": location,
        "url": event.get("url", ""),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--artist", help="Bandsintown artist name (overrides config.json)")
    ap.add_argument("--app-id", help="Bandsintown app id (overrides config.json)")
    ap.add_argument("--from-file", help="Read the events JSON from a local file instead of the network")
    args = ap.parse_args()

    if args.from_file:
        events = json.loads(Path(args.from_file).read_text())
    else:
        artist, app_id = args.artist, args.app_id
        if not (artist and app_id):
            c_artist, c_app, err = load_config_artist()
            artist = artist or c_artist
            app_id = app_id or c_app
            if err and not (artist and app_id):
                sys.exit(f"error: {err}")
        if not (artist and app_id):
            sys.exit("error: need an artist name and app id (via args or config.json)")
        events = fetch_events(artist, app_id)

    if not isinstance(events, list):
        sys.exit(f"error: unexpected Bandsintown response: {events!r}")

    print(f"Found {len(events)} upcoming event(s); baking up to {MAX_SHOWS}.")
    shows = []
    poster_by_url = {}
    for i, event in enumerate(events[:MAX_SHOWS]):
        show = extract_show(event)
        candidates = discover_images(event)
        if candidates:
            print(f"  event {i}: image fields found: " +
                  ", ".join(f"{k}" for k, _ in candidates))
        else:
            print(f"  event {i}: no image fields in this event")
        poster_url = choose_poster(candidates)
        if poster_url:
            if poster_url not in poster_by_url:
                try:
                    poster_by_url[poster_url] = download_image(poster_url, f"next-show-poster-{i}")
                    print(f"           downloaded poster -> {poster_by_url[poster_url]}")
                except Exception as err:  # noqa: BLE001
                    print(f"           poster download failed ({err}); skipping image")
                    poster_by_url[poster_url] = None
            if poster_by_url[poster_url]:
                show["poster"] = poster_by_url[poster_url]
        shows.append(show)

    out = {"fetchedAt": datetime.datetime.now().isoformat(timespec="seconds"),
           "shows": shows}
    (ASSETS / "next-show.json").write_text(json.dumps(out, indent=2) + "\n")
    print(f"Wrote {ASSETS / 'next-show.json'} with {len(shows)} show(s).")
    if not any(s.get("poster") for s in shows):
        print("NOTE: no poster image was baked. If you expected a per-show flyer, "
              "check the 'image fields found' lines above — the public API may only "
              "expose the artist photo.")


if __name__ == "__main__":
    main()
