#!/bin/bash
# Ars Arcanum QEMU Virtual Machine Test Runner
set -e

ISO_PATH="${1:-$(ls -t ../live-image-amd64.hybrid.iso 2>/dev/null | head -n 1)}"

if [ -z "$ISO_PATH" ] || [ ! -f "$ISO_PATH" ]; then
  echo "[!] Error: No ISO image found. Pass path to ISO as first argument."
  exit 1
fi

echo "[*] Booting Ars Arcanum ISO in QEMU: $ISO_PATH"

qemu-system-x86_64 \
  -enable-kvm \
  -m 4096 \
  -smp 4 \
  -cpu host \
  -vga virtio \
  -display gtk,gl=on \
  -cdrom "$ISO_PATH" \
  -boot d \
  -device intel-hda -device hda-duplex
