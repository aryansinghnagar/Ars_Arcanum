#!/bin/bash
# Ars Arcanum Hybrid ISO Build Orchestration Script
set -e

echo "========================================================"
echo "    ARS ARCANUM LINUX DISTRIBUTION — ISO BUILD RUNNER   "
echo "========================================================"

BUILD_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$BUILD_ROOT"

echo "[*] Checking build dependencies..."
for cmd in lb debootstrap xorriso git; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "[!] Missing required tool: $cmd"
    echo "    Install on Debian: sudo apt install -y live-build debootstrap xorriso git"
    exit 1
  fi
done

echo "[*] Cleaning previous build trees..."
lb clean --purge

echo "[*] Configuring live-build parameters..."
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

echo "[*] Building ISO image (this may take several minutes)..."
sudo lb build

echo "[+] BUILD COMPLETE: Ars Arcanum ISO generated successfully in $BUILD_ROOT"
