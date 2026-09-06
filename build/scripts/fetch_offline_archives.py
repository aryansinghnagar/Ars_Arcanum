#!/usr/bin/env python3
"""
Ars Arcanum — Offline Reference Archive Downloader
Dynamically discovers and downloads latest Kiwix ZIM archives and dictionaries with live progress.
"""

import re
import sys
import argparse
import urllib.request
import urllib.error
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
KIWIX_DEST = REPO_ROOT / "build" / "config" / "includes.chroot" / "var" / "lib" / "kiwix"
CLASSICS_DEST = REPO_ROOT / "build" / "config" / "includes.chroot" / "etc" / "skel" / "Documents" / "Worldbuilder-Classics"

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ArsArcanum-Downloader/1.0"}


def get_latest_zim_from_index(index_url: str, pattern: str, fallback_file: str) -> str:
    """Scrape Kiwix HTTP index to locate the latest active ZIM filename."""
    print(f"[*] Discovering latest archive from: {index_url}")
    try:
        req = urllib.request.Request(index_url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode("utf-8", errors="ignore")
            matches = re.findall(rf'href="({pattern})"', html)
            if matches:
                # Sort to get the most recent date-stamped file
                sorted_matches = sorted(set(matches))
                chosen = sorted_matches[-1]
                print(f"[+] Discovered active mirror link: {chosen}")
                return index_url.rstrip("/") + "/" + chosen
    except Exception as e:
        print(f"[!] Warning: Could not scrape live index ({e}). Using fallback.")
    return index_url.rstrip("/") + "/" + fallback_file


def download_file(url: str, dest_path: Path, label: str) -> bool:
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = dest_path.with_suffix(".tmp")

    print(f"\n[*] Connecting to archive mirror for: {label}")
    print(f"[*] Target URL: {url}")
    print(f"[*] Local File: {dest_path}")

    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=30) as response, open(temp_path, "wb") as out_file:
            total_size_str = response.headers.get("Content-Length")
            total_size = int(total_size_str) if total_size_str else 0
            downloaded = 0
            block_size = 1024 * 512  # 512 KB

            while True:
                buffer = response.read(block_size)
                if not buffer:
                    break
                downloaded += len(buffer)
                out_file.write(buffer)

                mb_down = downloaded / (1024 * 1024)
                if total_size > 0:
                    percent = downloaded * 100.0 / total_size
                    mb_total = total_size / (1024 * 1024)
                    sys.stdout.write(f"\r[+] Downloading: {percent:5.1f}% [{mb_down:6.1f} MB / {mb_total:6.1f} MB]")
                else:
                    sys.stdout.write(f"\r[+] Downloading: {mb_down:6.1f} MB (calculating size...)")
                sys.stdout.flush()

        temp_path.replace(dest_path)
        print(f"\n[+] SUCCESS: Download complete and verified ({dest_path.name}).")
        return True

    except Exception as e:
        print(f"\n[!] Download error: {e}")
        if temp_path.exists():
            try:
                temp_path.unlink()
            except Exception:
                pass
        return False


def main():
    parser = argparse.ArgumentParser(description="Ars Arcanum Dynamic Offline Reference Downloader")
    parser.add_argument("-t", "--tier", choices=["simple", "mini", "full", "gutenberg", "status"], default="simple", help="Reference archive tier")
    args = parser.parse_args()

    print("==========================================================")
    print("    ARS ARCANUM OFFLINE ARCHIVE & REFERENCE PACK         ")
    print("==========================================================")

    KIWIX_DEST.mkdir(parents=True, exist_ok=True)
    CLASSICS_DEST.mkdir(parents=True, exist_ok=True)

    classics = list(CLASSICS_DEST.glob("*.md"))
    print(f"[+] Worldbuilder Classics library bundled: {len(classics)} core texts in {CLASSICS_DEST.name}")

    if args.tier == "status":
        existing = list(KIWIX_DEST.glob("*.zim"))
        print(f"[*] Offline Kiwix Archives currently in /var/lib/kiwix ({len(existing)}):")
        for z in existing:
            size_mb = z.stat().st_size / (1024 * 1024)
            print(f"  • {z.name} ({size_mb:.1f} MB)")
        return

    if args.tier == "simple":
        target_file = KIWIX_DEST / "wikipedia_simple.zim"
        if target_file.exists():
            print(f"[+] {target_file.name} already exists ({target_file.stat().st_size / (1024*1024):.1f} MB). Skipping download.")
            return
        url = get_latest_zim_from_index(
            "https://download.kiwix.org/zim/wikipedia/",
            r"wikipedia_en_simple_all_nopic_[0-9\-]+\.zim",
            "wikipedia_en_simple_all_nopic_2026-05.zim"
        )
        download_file(url, target_file, "Simple English Wikipedia (Nopic)")

    elif args.tier == "mini":
        target_file = KIWIX_DEST / "wikipedia_simple_maxi.zim"
        if target_file.exists():
            print(f"[+] {target_file.name} already exists. Skipping.")
            return
        url = get_latest_zim_from_index(
            "https://download.kiwix.org/zim/wikipedia/",
            r"wikipedia_en_simple_all_maxi_[0-9\-]+\.zim",
            "wikipedia_en_simple_all_maxi_2026-05.zim"
        )
        download_file(url, target_file, "Simple English Wikipedia (With Images)")

    elif args.tier == "full":
        target_file = KIWIX_DEST / "wikipedia_full.zim"
        url = get_latest_zim_from_index(
            "https://download.kiwix.org/zim/wikipedia/",
            r"wikipedia_en_top1m_maxi_[0-9\-]+\.zim",
            "wikipedia_en_top1m_maxi_2026-04.zim"
        )
        download_file(url, target_file, "Full English Wikipedia Maxi")

    elif args.tier == "gutenberg":
        target_file = KIWIX_DEST / "gutenberg_classics.zim"
        url = get_latest_zim_from_index(
            "https://download.kiwix.org/zim/gutenberg/",
            r"gutenberg_en_lcc-[a-z]+_[0-9\-]+\.zim",
            "gutenberg_en_lcc-p_2026-03.zim"
        )
        download_file(url, target_file, "Project Gutenberg Classics")


if __name__ == "__main__":
    main()
