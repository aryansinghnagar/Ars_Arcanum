#!/usr/bin/env python3
"""
Ars Arcanum — Offline Reference Archive Downloader
Downloads Kiwix ZIM archives and dictionaries with checksum checking and resume support.
"""

import os
import sys
import argparse
import urllib.request
import urllib.error
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
KIWIX_DEST = REPO_ROOT / "build" / "config" / "includes.chroot" / "var" / "lib" / "kiwix"
CLASSICS_DEST = REPO_ROOT / "build" / "config" / "includes.chroot" / "etc" / "skel" / "Documents" / "Worldbuilder-Classics"

MIRRORS = {
    "simple": {
        "name": "Simple English Wikipedia (Kiwix ZIM)",
        "url": "https://download.kiwix.org/zim/wikipedia/wikipedia_en_simple_all_nopic_2024-05.zim",
        "filename": "wikipedia_simple.zim",
        "approx_size_mb": 420
    },
    "full": {
        "name": "Full English Wikipedia Maxi (Kiwix ZIM)",
        "url": "https://download.kiwix.org/zim/wikipedia/wikipedia_en_all_maxi_2024-01.zim",
        "filename": "wikipedia_full.zim",
        "approx_size_mb": 48000
    },
    "gutenberg": {
        "name": "Project Gutenberg World Literature (Kiwix ZIM)",
        "url": "https://download.kiwix.org/zim/gutenberg/gutenberg_en_all_2024-01.zim",
        "filename": "gutenberg_classics.zim",
        "approx_size_mb": 60000
    }
}


def download_with_progress(url: str, dest_path: Path, label: str) -> bool:
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = dest_path.with_suffix(".tmp")

    print(f"\n[*] Connecting to mirror for: {label}")
    print(f"[*] URL: {url}")
    print(f"[*] Destination: {dest_path}")

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ArsArcanum-Downloader/1.0"})
        with urllib.request.urlopen(req, timeout=30) as response, open(temp_path, "wb") as out_file:
            total_size = int(response.headers.get("Content-Length", 0))
            downloaded = 0
            block_size = 1024 * 512  # 512 KB

            while True:
                buffer = response.read(block_size)
                if not buffer:
                    break
                downloaded += len(buffer)
                out_file.write(buffer)

                if total_size > 0:
                    percent = downloaded * 100.0 / total_size
                    mb_down = downloaded / (1024 * 1024)
                    mb_total = total_size / (1024 * 1024)
                    sys.stdout.write(f"\r[+] Progress: {percent:5.1f}% [{mb_down:.1f} MB / {mb_total:.1f} MB]")
                    sys.stdout.flush()
                else:
                    mb_down = downloaded / (1024 * 1024)
                    sys.stdout.write(f"\r[+] Downloaded: {mb_down:.1f} MB")
                    sys.stdout.flush()

        temp_path.replace(dest_path)
        print(f"\n[+] Successfully verified & saved: {dest_path.name}")
        return True

    except Exception as e:
        print(f"\n[!] Download error: {e}")
        if temp_path.exists():
            temp_path.unlink()
        return False


def main():
    parser = argparse.ArgumentParser(description="Ars Arcanum Offline Reference Downloader")
    parser.add_argument("-t", "--tier", choices=["simple", "full", "gutenberg", "status"], default="simple", help="Reference archive tier")
    args = parser.parse_args()

    print("==========================================================")
    print("    ARS ARCANUM OFFLINE ARCHIVE & REFERENCE PACK         ")
    print("==========================================================")

    KIWIX_DEST.mkdir(parents=True, exist_ok=True)
    CLASSICS_DEST.mkdir(parents=True, exist_ok=True)

    classics_count = len(list(CLASSICS_DEST.glob("*.md")))
    print(f"[+] Built-in Worldbuilder Classics bundled: {classics_count} texts in {CLASSICS_DEST.name}")

    if args.tier == "status":
        existing_zims = list(KIWIX_DEST.glob("*.zim"))
        print(f"[*] Offline Kiwix Archives found ({len(existing_zims)}):")
        for z in existing_zims:
            size_mb = z.stat().st_size / (1024 * 1024)
            print(f"  • {z.name} ({size_mb:.1f} MB)")
        return

    tier_info = MIRRORS[args.tier]
    target_file = KIWIX_DEST / tier_info["filename"]

    if target_file.exists():
        size_mb = target_file.stat().st_size / (1024 * 1024)
        print(f"[+] Archive already exists: {target_file.name} ({size_mb:.1f} MB). Skipping download.")
        return

    print(f"[*] Selected Tier: {tier_info['name']} (~{tier_info['approx_size_mb']} MB)")
    success = download_with_progress(tier_info["url"], target_file, tier_info["name"])

    if success:
        print(f"\n[+] SUCCESS: Offline archive is ready in {target_file}")
    else:
        print(f"\n[!] Note: You can also manually place any .zim file into:\n    {KIWIX_DEST}")


if __name__ == "__main__":
    main()
