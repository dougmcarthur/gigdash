# GigDash Roadmap

The MVP is a static page in a kiosk browser. Every feature below builds on one
architectural move: replace the static `file://` page with a **small local web
server on the Pi** (e.g. FastAPI or Node) that serves *views* to browser
windows and pushes live updates over WebSockets. Everything stays offline-first
— the Pi is its own network.

## 1. Dual-monitor performer / audience mode

- **Audience view** (today's MVP screen, outward-facing): photo, name, QR code,
  plus the *current song title* and an optional "about this song" blurb.
- **Performer view** (facing you): current setlist position, lyrics/chords,
  capo/tuning notes, next song preview, elapsed set time.
- Both views are just URLs (`/audience`, `/performer`) served by the local
  server, so they stay perfectly in sync via WebSocket events.
- Implementation note: `cage` is built for a single output. Dual-screen kiosk
  on the Pi means switching the compositor to **labwc** (Wayland) or X11 +
  Openbox, running one fullscreen Chromium window per HDMI output.

## 2. Setlists, lyrics, and chords

- Setlists as plain files (Markdown or ChordPro) in a `setlists/` folder —
  editable on a laptop, synced via USB stick, SSH, or a git pull.
- ChordPro parsing gives chords-over-lyrics for the performer view and clean
  song titles for the audience view.
- Auto-scroll with per-song tempo, or manual advance.
- Multiple setlists (solo set, full band, wedding set) selectable at boot or
  from the remote.

## 3. Remote control

- The Pi runs a **Wi-Fi hotspot**; your phone joins it and opens `/remote` —
  a control surface for next/previous song, jump-to-song, scroll, blackout,
  and "break mode" (audience screen shows "back at 9:30" + QR).
- **Foot pedal**: a USB/Bluetooth page-turner pedal (they present as
  keyboards) or a MIDI foot controller for hands-free next-song/scroll.
- Optional: a hardware GPIO button on the Pi case as a dumb "next" fallback.

## 4. Audience-screen content beyond the QR

- Rotating slides between songs: merch/tip-jar QR, social handles, mailing
  list signup, upcoming gig dates.
- Per-song context: title, writer credit, the album it's on, a one-liner story.
- "Now playing" with a subtle progress/visualizer so the screen feels alive.
- Song requests: the links page (or a dedicated form reachable from the QR)
  feeds requests back — viewable on the performer screen when there's venue
  internet, gracefully absent when offline.

## 5. Dynamic lighting control

The Pi is well suited to be the lighting brain. In rough order of effort:

- **WLED** (ESP32 LED strips/bars): the Pi sends UDP/E1.31 to WLED nodes over
  its own hotspot — cheapest entry into synced stage color.
- **DMX fixtures** via a USB-DMX interface or Art-Net/sACN node, driven from
  the Pi with [OLA](https://www.openlighting.org/) — real PAR cans, washes.
- **Scene-per-song**: each setlist entry names a lighting scene; advancing the
  song crossfades the lights. Manual override + blackout from the remote.
- **Audio-reactive**: a USB audio interface lets the Pi beat-detect from a
  line feed and pulse intensity/color live (e.g. via LedFx-style analysis).
- Stretch: tempo-synced cues from a click track or MIDI clock.

## 6. Appliance quality-of-life

- Read-only root filesystem (overlayfs) so yanking power never corrupts the
  SD card — important for a gig appliance.
- Settings file (`gigdash.toml`) for name, URL, theme colors — no HTML edits.
- Update path: `git pull` + restart from the remote UI, or a USB stick that
  auto-imports new setlists/photos when inserted.
- Status/diagnostics page on the remote: temperature, storage, display status.

## Suggested sequencing

1. Local server + WebSockets, keep single screen (foundation for everything).
2. Setlists + current-song on the audience screen.
3. Phone remote over Pi hotspot.
4. Second monitor with the performer view (compositor switch).
5. Foot pedal support.
6. WLED lighting, then DMX/OLA, then audio-reactive.
