#!/bin/bash -e
# files/ is populated by image/build.sh with the repo's display/ and pi/ dirs.
rm -rf "${ROOTFS_DIR}/tmp/gigdash"
cp -r files "${ROOTFS_DIR}/tmp/gigdash"

# Packages were installed by 00-packages, so skip apt inside the chroot.
on_chroot <<EOF
GIGDASH_SKIP_APT=1 bash /tmp/gigdash/pi/setup.sh
rm -rf /tmp/gigdash
EOF
