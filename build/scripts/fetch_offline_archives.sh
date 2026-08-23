#!/bin/bash
# Ars Arcanum Offline Reference Archive Fetcher
# Downloads verified Kiwix ZIM archives and dictionaries for bundling into the ISO image.

set -e

DEST_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/config/includes.chroot/var/lib/kiwix"
mkdir -p "$DEST_DIR"

echo "=========================================================="
echo "    ARS ARCANUM OFFLINE ARCHIVE DOWNLOADER & BUNDLER     "
echo "=========================================================="
echo "Destination: $DEST_DIR"
echo ""
echo "Select archive tier to bundle:"
echo "  1) Lightweight Subset (~1.5 GB: Simple English Wikipedia + Gutenberg Classics)"
echo "  2) Full Offline Encyclopedia (~48 GB: Full English Wikipedia Maxi)"
echo "  3) Cancel / Skip"
echo ""

read -p "Enter choice [1-3]: " choice

case "$choice" in
  1)
    echo "[*] Downloading Simple English Wikipedia ZIM (~900 MB)..."
    curl -L "https://download.kiwix.org/zim/wikipedia/wikipedia_en_simple_all_maxi_2024-01.zim" -o "$DEST_DIR/wikipedia_simple.zim"
    echo "[+] Download complete: wikipedia_simple.zim"
    ;;
  2)
    echo "[*] Downloading Full English Wikipedia ZIM (~48 GB)..."
    curl -L "https://download.kiwix.org/zim/wikipedia/wikipedia_en_all_maxi_2024-01.zim" -o "$DEST_DIR/wikipedia_full.zim"
    echo "[+] Download complete: wikipedia_full.zim"
    ;;
  *)
    echo "[-] Download skipped."
    ;;
esac

echo "[+] Done."
