#!/bin/bash
# Build a flashable GigDash SD-card image with pi-gen (in Docker).
#
# Requirements: docker, git, ~20 GB free disk. Takes 30-60+ minutes.
# Usage:  image/build.sh
# Output: image/work/pi-gen/deploy/*.img.xz  -> flash with Raspberry Pi Imager.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORK_DIR="$REPO_DIR/image/work"
PIGEN_DIR="$WORK_DIR/pi-gen"

mkdir -p "$WORK_DIR"
if [ ! -d "$PIGEN_DIR" ]; then
    # arm64 branch targets Pi 3/4/5.
    git clone --branch arm64 --depth 1 https://github.com/RPi-Distro/pi-gen "$PIGEN_DIR"
fi

# Install our custom stage into the pi-gen tree, bundling the app files so the
# stage is self-contained.
rm -rf "$PIGEN_DIR/stage-gigdash"
cp -r "$REPO_DIR/image/stage-gigdash" "$PIGEN_DIR/stage-gigdash"
FILES_DIR="$PIGEN_DIR/stage-gigdash/00-gigdash/files"
mkdir -p "$FILES_DIR"
cp -r "$REPO_DIR/display" "$REPO_DIR/pi" "$FILES_DIR/"

cp "$REPO_DIR/image/config" "$PIGEN_DIR/config"

cd "$PIGEN_DIR"
./build-docker.sh -c config

echo
echo "Done. Image(s) in: $PIGEN_DIR/deploy/"
