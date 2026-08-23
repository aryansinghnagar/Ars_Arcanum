#!/bin/bash
# Ars Arcanum Hybrid ISO Build Orchestration Script
set -e

echo "========================================================"
echo "    ARS ARCANUM LINUX DISTRIBUTION — ISO BUILD RUNNER   "
echo "========================================================"

WORKSPACE="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BUILD_DIR="$WORKSPACE/build"
OUTPUT_DIR="$BUILD_DIR/output"
mkdir -p "$OUTPUT_DIR"

echo "[*] Preparing chroot overlay from repository sources..."
if command -v python3 >/dev/null 2>&1; then
    python3 "$BUILD_DIR/scripts/prepare_overlay.py"
fi

# Use native Linux tmpfs/filesystem for live-build rootfs
CONTAINER_WORK_DIR="/tmp/ars-live-build"
rm -rf "$CONTAINER_WORK_DIR"
mkdir -p "$CONTAINER_WORK_DIR"

echo "[*] Copying configuration tree to native Linux workspace ($CONTAINER_WORK_DIR)..."
cp -a "$BUILD_DIR"/* "$CONTAINER_WORK_DIR/"
cd "$CONTAINER_WORK_DIR"

echo "[*] Initializing live-build configuration..."
lb clean --purge || true

lb config \
  --distribution trixie \
  --archive-areas "main contrib non-free non-free-firmware" \
  --binary-images iso-hybrid \
  --iso-application "Ars Arcanum" \
  --iso-publisher "Ars Arcanum Project" \
  --iso-volume "ARS_ARCANUM" \
  --memtest none \
  --bootappend-live "boot=live components quiet splash security=apparmor apparmor=1 lsm=landlock,lockdown,yama,apparmor,bpf" \
  --apt-recommends false

echo "[*] Commencing live-build compilation (this downloads Debian 13 packages and builds rootfs)..."
lb build

echo "[*] Copying compiled ISO image to output directory ($OUTPUT_DIR)..."
cp -f *.iso "$OUTPUT_DIR/live-image-amd64.hybrid.iso" 2>/dev/null || cp -f live-image-*.iso "$OUTPUT_DIR/" 2>/dev/null || true

cd "$OUTPUT_DIR"
if ls *.iso >/dev/null 2>&1; then
    sha256sum *.iso > "ars-arcanum-x86_64.iso.sha256"
    echo "========================================================"
    echo "[+] SUCCESS: Ars Arcanum ISO compiled successfully!"
    echo "========================================================"
    ls -lh "$OUTPUT_DIR"
else
    echo "[!] Warning: No .iso file detected in build output."
fi
