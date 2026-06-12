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
    "file:///opt/gigdash/display/index.html"
