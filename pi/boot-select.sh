#!/bin/bash
# Runs under cage on tty1 in place of the kiosk browser. If a keyboard is
# attached, offers a 10-second choice between GigDash and the desktop;
# otherwise (no keyboard plugged in) goes straight into GigDash.
set -eu

BINDIR="$(cd "$(dirname "$0")" && pwd)"

if ! ls /dev/input/by-path/ 2>/dev/null | grep -q -- '-event-kbd$'; then
    exec "$BINDIR/kiosk.sh"
fi

echo
echo "  GigDash"
echo
echo "  [1] GigDash kiosk (default)"
echo "  [2] Desktop"
echo
choice=""
for i in 10 9 8 7 6 5 4 3 2 1; do
    printf '\r  Starting GigDash in %2ds — press 1 or 2 to choose ' "$i"
    if read -r -t 1 -n 1 key; then
        choice="$key"
        break
    fi
done
echo

case "$choice" in
    2)
        # Hand off to the normal desktop session for this boot only.
        exec systemctl --no-block isolate graphical-desktop.target
        ;;
    *)
        exec "$BINDIR/kiosk.sh"
        ;;
esac
