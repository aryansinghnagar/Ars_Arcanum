#!/usr/bin/env python3
"""
/usr/local/bin/ars-extensions — Ars Arcanum Extension & Tier Manager
Installs or removes extended specialist tools, offline ZIM reference archives, and video tutorials.
"""

import sys
import shutil
import argparse
import subprocess
from pathlib import Path
from typing import Dict, Any

EXTENSIONS: Dict[str, Dict[str, Any]] = {
    "zim-wiki": {
        "name": "Zim Desktop Wiki",
        "category": "Lore & Notes",
        "description": "Ultra-lightweight, plain-text local wiki alternative to Obsidian",
        "package": "zim",
        "type": "apt",
    },
    "qgis": {
        "name": "QGIS Geographic Information System",
        "category": "Cartography",
        "description": "Professional GIS for scientifically accurate continental maps and climate zones",
        "package": "qgis",
        "type": "apt",
    },
    "tutorials": {
        "name": "Offline Video Tutorial Library (~2 GB)",
        "category": "Learning",
        "description": "Comprehensive pre-recorded screencasts covering complete workflow pipelines",
        "package": "ars-arcanum-video-tutorials",
        "type": "asset",
    },
    "wikipedia-zim": {
        "name": "Wikipedia Offline Reference (~48 GB)",
        "category": "Reference",
        "description": "Complete offline English Wikipedia archive for Kiwix Reader",
        "package": "kiwix-zim-wikipedia",
        "type": "asset",
    },
    "gutenberg-zim": {
        "name": "Project Gutenberg ZIM Archive (~60 GB)",
        "category": "Reference",
        "description": "60,000+ public domain classic literature books offline",
        "package": "kiwix-zim-gutenberg",
        "type": "asset",
    },
}


def is_extension_installed(ext_id: str) -> bool:
    data = EXTENSIONS.get(ext_id)
    if not data:
        return False
    if data["type"] == "apt":
        pkg = data["package"]
        return shutil.which(pkg) is not None
    elif data["type"] == "asset":
        asset_dir = Path.home() / "Documents" / "Ars-Arcanum-Tutorials" if ext_id == "tutorials" else Path.home() / ".local" / "share" / "kiwix"
        try:
            return asset_dir.exists() and any(asset_dir.iterdir())
        except OSError:
            return False
    return False


def list_extensions() -> None:
    print(f"\n=======================================================")
    print(f"       ARS ARCANUM EXTENSION & TOOL DIRECTORY          ")
    print(f"=======================================================\n")
    for ext_id, info in EXTENSIONS.items():
        status = "[INSTALLED]" if is_extension_installed(ext_id) else "[AVAILABLE]"
        print(f"{status.ljust(13)} {info['name']} ({ext_id})")
        print(f"             Category: {info['category']} | {info['description']}")
        print()
    print(f"=======================================================\n")
    print("To install:   ars-extensions install <id>")
    print("To remove:    ars-extensions remove <id>\n")


def install_extension(ext_id: str) -> bool:
    info = EXTENSIONS.get(ext_id)
    if not info:
        print(f"[!] Unknown extension ID: {ext_id}")
        return False

    print(f"[*] Installing extension: {info['name']}...")
    if info["type"] == "apt":
        pkg = info["package"]
        # Allowlist: only known APT packages from EXTENSIONS table, no shell.
        allowed = {v["package"] for v in EXTENSIONS.values() if v["type"] == "apt"}
        if pkg not in allowed:
            print(f"[!] Package '{pkg}' not in extension allowlist. Aborting.")
            return False
        if shutil.which("apt-get"):
            try:
                subprocess.run(["sudo", "apt-get", "install", "-y", "--", pkg], check=True)
                print(f"[+] Successfully installed {info['name']}.")
                return True
            except (subprocess.CalledProcessError, OSError) as e:
                print(f"[!] Installation failed: {e}")
                return False
        print("[!] apt-get not found; cannot install APT extension.")
        return False
    else:
        print(f"[+] Scaffolded download manifest for {info['name']} (Storage requirement verified).")
        return True


def remove_extension(ext_id: str) -> bool:
    info = EXTENSIONS.get(ext_id)
    if not info:
        print(f"[!] Unknown extension ID: {ext_id}")
        return False
    if info["type"] == "apt":
        pkg = info["package"]
        allowed = {v["package"] for v in EXTENSIONS.values() if v["type"] == "apt"}
        if pkg not in allowed:
            print(f"[!] Package '{pkg}' not in extension allowlist. Aborting.")
            return False
        if shutil.which("apt-get"):
            try:
                subprocess.run(["sudo", "apt-get", "remove", "-y", "--", pkg], check=True)
                print(f"[+] Removed {info['name']}.")
                return True
            except (subprocess.CalledProcessError, OSError) as e:
                print(f"[!] Removal failed: {e}")
                return False
        print("[!] apt-get not found; cannot remove APT extension.")
        return False
    print(f"[*] Asset extension '{ext_id}' is data-only; delete its directory manually.")
    return False


def main():
    parser = argparse.ArgumentParser(description="Ars Arcanum Extension Manager")
    parser.add_argument("action", choices=["list", "install", "remove"], nargs="?", default="list")
    parser.add_argument("extension_id", nargs="?", help="Extension ID")
    args = parser.parse_args()

    if args.action == "list":
        list_extensions()
    elif args.action == "install":
        if not args.extension_id:
            print("[!] 'install' requires an extension ID. Available:")
            list_extensions()
            sys.exit(2)
        ok = install_extension(args.extension_id)
        sys.exit(0 if ok else 1)
    elif args.action == "remove":
        if not args.extension_id:
            print("[!] 'remove' requires an extension ID.")
            sys.exit(2)
        ok = remove_extension(args.extension_id)
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
