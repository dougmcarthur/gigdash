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

## 3. Public release

Make GigDash easy for other local artists to set up for themselves, with
minimal manual configuration:

- **Promo image fetcher**: pull the background image from a Manitoba Music
  profile URL, Google Drive/Dropbox link, or direct image URL. No uploads —
  fetch at setup/build time only.
- **Instagram QR generator**: supply a handle, generate the QR code locally
  (no IG login/API needed if just encoding `instagram.com/<handle>`).
- **Brand colors**: derive accent/highlight colors from a website's CSS or
  from a supplied image (e.g. album art), and apply them to the existing
  `--accent` / carousel theme variables.
- **One-shot "smart setup" scan**: given a single starting point (e.g.
  Instagram handle or website), discover available assets (bio links,
  cover art, profile photo) and present the artist with choices to build
  their page — rather than configuring each source separately. Needs more
  thought on scope/privacy before committing to this (see open questions
  below).

Open questions to revisit before building:
- How much of this needs to run as a hosted service (fetch-time, e.g. on
  Cloudflare) vs. a one-time local setup script the artist runs themselves?
- The "smart scan" idea (Maigret-style discovery) is powerful but raises
  privacy/scope concerns — likely start with explicit, source-by-source
  configuration first, and revisit auto-discovery later if there's demand.

## Out of scope (for now)

Dual-monitor performer/audience sync, setlists/lyrics/ChordPro, phone remote
control, foot pedal input, and lighting control (WLED/DMX/OLA) were explored
but explicitly dropped from GigDash. They may resurface later as a separate
on-stage automation project, decoupled from this display appliance.
