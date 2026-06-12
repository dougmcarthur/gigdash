#!/bin/sh
# Launched by gigdash-kiosk.service inside the cage Wayland compositor.
set -eu

# Raspberry Pi OS ships the browser as chromium-browser (a wrapper) or chromium
# depending on release; use whichever exists.
if command -v chromium-browser >/dev/null 2>&1; then
    BROWSER=chromium-browser
else
    BROWSER=chromium
fi

# --allow-file-access-from-files: script.js fetches config.json, which
# Chromium otherwise blocks under file:// (each file is its own origin).
exec "$BROWSER" \
    --kiosk \
    --incognito \
    --noerrdialogs \
    --disable-infobars \
    --no-first-run \
    --disable-features=TranslateUI \
    --ozone-platform=wayland \
    --autoplay-policy=no-user-gesture-required \
    --password-store=basic \
    --allow-file-access-from-files \
    "file:///opt/gigdash/display/index.html"
