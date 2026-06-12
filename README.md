# GigDash

A self-contained Raspberry Pi appliance for showing gig info on a portable
monitor. Power it on and it boots straight into a fullscreen display with your
name, photo, and a QR code pointing to <https://links.dougmcarthur.net> — no
network needed at the venue.

## Layout

| Path | Purpose |
|---|---|
| `display/` | The fullscreen display app (static HTML/CSS, fully offline) |
| `pi/` | Kiosk plumbing: provisioning script, systemd unit, browser launcher |
| `steamdeck/` | (WIP) Steam Deck kiosk port — fallback/parallel target |
| `image/` | pi-gen stage + build script for a flashable SD-card image |
| `docs/ROADMAP.md` | Future feature ideas (dual screens, setlists, lighting) |

## Quick start (existing Raspberry Pi OS)

The fastest path — no image build required:

1. Flash **Raspberry Pi OS Lite (64-bit, Bookworm)** with Raspberry Pi Imager.
2. Boot the Pi, get the repo onto it, and run:

   ```sh
   sudo pi/setup.sh
   ```

3. Copy your photo to `/opt/gigdash/display/assets/photo.jpg`
   (square crop looks best — it's displayed in a circle).
4. Reboot. The Pi now boots directly into the display.

The kiosk runs as an unprivileged `gigdash` user under
[cage](https://github.com/cage-kiosk/cage) (a single-app Wayland compositor)
with Chromium in kiosk mode, restarted automatically if it ever crashes.

## Building a standalone bootable image

`image/build.sh` builds a complete flashable image with
[pi-gen](https://github.com/RPi-Distro/pi-gen) (the official Raspberry Pi OS
image builder) plus a custom `stage-gigdash` that bakes in everything above.

On a Linux machine with Docker and ~20 GB free:

```sh
# 1. Set a real password first
$EDITOR image/config        # change FIRST_USER_PASS

# 2. Build (30-60+ min)
image/build.sh

# 3. Flash the result
ls image/work/pi-gen/deploy/*.img.xz
```

Flash with Raspberry Pi Imager ("Use custom" image). After first boot, copy
your photo over SSH to `/opt/gigdash/display/assets/photo.jpg`.

## Changing the content

- **Name / layout** — edit `display/index.html` and `display/style.css`.
- **QR URL** — change the URL in `pi/setup.sh` (it regenerates the QR at
  install time with `qrencode`); `display/assets/qr.svg` is a pre-generated
  copy used for previewing in a desktop browser.
- **Preview on your laptop** — just open `display/index.html` in a browser.

## What's next

See [docs/ROADMAP.md](docs/ROADMAP.md) for the planned evolution: dual-monitor
performer/audience mode, setlists and lyrics, phone remote control, and stage
lighting.
