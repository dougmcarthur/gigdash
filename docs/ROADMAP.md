# GigDash Roadmap

GigDash is scoped to the **audience-facing display**: offline, rock-solid,
low-friction, polished. It does not handle setlists, lyrics, performer views,
remote control, or lighting — those are separate concerns (e.g. the Setlists
app) and may become their own on-stage automation project later.

## 1. Rotating audience content

Between songs, rotate the static screen through a few slides instead of one
fixed view:

- Today's MVP: photo, name, QR code.
- Additional slides: merch/tip-jar QR, social handles, mailing list signup,
  upcoming gig dates.
- Pure client-side (CSS animation / JS interval) — no server, no state,
  still a single static page loaded once at boot.

## 2. Appliance quality-of-life

- Read-only root filesystem (overlayfs) so yanking power never corrupts the
  SD card.
- Settings file (e.g. `gigdash.toml` or a small JSON config) for name, URL,
  theme colors, and which slides are enabled — no HTML edits for routine
  changes.
- Update path: `git pull` + restart, or a USB stick that auto-imports a new
  photo/config when inserted.
- Status/diagnostics: a way to confirm on boot that the display came up
  correctly (e.g. brief on-screen version/health indicator).

## Out of scope (for now)

Dual-monitor performer/audience sync, setlists/lyrics/ChordPro, phone remote
control, foot pedal input, and lighting control (WLED/DMX/OLA) were explored
but explicitly dropped from GigDash. They may resurface later as a separate
on-stage automation project, decoupled from this display appliance.
