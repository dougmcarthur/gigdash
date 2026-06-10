#!/bin/bash
# Turn a fresh Raspberry Pi OS Lite (Bookworm or later) install into a GigDash
# kiosk. Run as root from the repo root:
#
#   sudo pi/setup.sh
#
# The same install steps are reused by the pi-gen stage in image/ when building
# a flashable image from scratch.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"

if [ "${GIGDASH_SKIP_APT:-0}" != "1" ]; then
    apt-get update
    apt-get install -y --no-install-recommends \
        cage chromium-browser qrencode seatd
fi

# Dedicated unprivileged user that owns the kiosk session.
if ! id gigdash >/dev/null 2>&1; then
    useradd --create-home --shell /usr/sbin/nologin gigdash
fi
# cage needs DRM/input access on the seat.
usermod -aG video,render,input gigdash

# Install the display app and kiosk launcher.
mkdir -p /opt/gigdash/bin
cp -r "$REPO_DIR/display" /opt/gigdash/
install -m 0755 "$REPO_DIR/pi/kiosk.sh" /opt/gigdash/bin/kiosk.sh

# Regenerate the QR code at install time so a URL change only needs an edit here.
qrencode -t SVG -o /opt/gigdash/display/assets/qr.svg -m 2 \
    "https://links.dougmcarthur.net"

chown -R gigdash:gigdash /opt/gigdash

# Boot straight into the kiosk on tty1.
install -m 0644 "$REPO_DIR/pi/gigdash-kiosk.service" \
    /etc/systemd/system/gigdash-kiosk.service
systemctl set-default graphical.target
systemctl enable gigdash-kiosk.service

# Quiet, fast boot: no rainbow splash, no console noise over the display.
BOOT_CONFIG=/boot/firmware/config.txt
CMDLINE=/boot/firmware/cmdline.txt
[ -f "$BOOT_CONFIG" ] || BOOT_CONFIG=/boot/config.txt
[ -f "$CMDLINE" ] || CMDLINE=/boot/cmdline.txt

grep -q '^disable_splash=1' "$BOOT_CONFIG" || echo 'disable_splash=1' >> "$BOOT_CONFIG"
if ! grep -q 'quiet' "$CMDLINE"; then
    sed -i 's/$/ quiet loglevel=3 vt.global_cursor_default=0/' "$CMDLINE"
fi

echo
echo "GigDash installed. Drop your photo at /opt/gigdash/display/assets/photo.jpg,"
echo "then reboot to start the kiosk."
