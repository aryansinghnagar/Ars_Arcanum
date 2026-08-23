#!/usr/bin/env python3
"""
Ars Arcanum — Live-Build Chroot Overlay Synchronizer
Prepares includes.chroot filesystem tree from repository source before live-build compilation.
"""

import os
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
INCLUDES_CHROOT = REPO_ROOT / "build" / "config" / "includes.chroot"


def sync_tree(src: Path, dest: Path) -> None:
    if not src.exists():
        print(f"[!] Warning: Source directory {src} does not exist. Skipping.")
        return
    dest.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        if item.name.startswith((".", "__pycache__")):
            continue
        target = dest / item.name
        if item.is_dir():
            shutil.copytree(item, target, dirs_exist_ok=True)
        else:
            shutil.copy2(item, target)


def prepare_overlay():
    print("==========================================================")
    print("   PREPARING LIVE-BUILD CHROOT OVERLAY (INCLUDES.CHROOT)  ")
    print("==========================================================")

    # 1. Security configurations
    print("[*] Syncing security profiles (sysctl, nftables, apparmor, udev, usbguard)...")
    sync_tree(REPO_ROOT / "security" / "sysctl", INCLUDES_CHROOT / "etc" / "sysctl.d")
    sync_tree(REPO_ROOT / "security" / "nftables", INCLUDES_CHROOT / "etc" / "nftables")
    sync_tree(REPO_ROOT / "security" / "apparmor", INCLUDES_CHROOT / "etc" / "apparmor.d")
    sync_tree(REPO_ROOT / "security" / "udev", INCLUDES_CHROOT / "etc" / "udev" / "rules.d")
    sync_tree(REPO_ROOT / "security" / "usbguard", INCLUDES_CHROOT / "etc" / "usbguard")

    # 2. CLI Tools and Common Libs
    print("[*] Syncing CLI tool suite & Python library...")
    bin_dir = INCLUDES_CHROOT / "usr" / "local" / "bin"
    lib_dir = INCLUDES_CHROOT / "usr" / "local" / "lib" / "ars-arcanum"
    bin_dir.mkdir(parents=True, exist_ok=True)
    lib_dir.mkdir(parents=True, exist_ok=True)

    sync_tree(REPO_ROOT / "src" / "common", lib_dir / "common")
    sync_tree(REPO_ROOT / "src" / "gui", lib_dir / "gui")

    # Map python CLI scripts to standard unix commands (e.g. ars_focus.py -> ars-focus)
    cli_src = REPO_ROOT / "src" / "cli"
    for py_file in cli_src.glob("ars_*.py"):
        cmd_name = py_file.stem.replace("_", "-")
        target_bin = bin_dir / cmd_name
        shutil.copy2(py_file, target_bin)

    # Create launcher wrapper for ars-welcome and ars-wizard
    welcome_wrapper = bin_dir / "ars-welcome"
    welcome_wrapper.write_text("#!/bin/sh\nexec python3 /usr/local/lib/ars-arcanum/gui/ars_welcome/main.py \"$@\"\n", encoding="utf-8")
    
    wizard_wrapper = bin_dir / "ars-wizard"
    wizard_wrapper.write_text("#!/bin/sh\nexec python3 /usr/local/lib/ars-arcanum/gui/ars_wizard/main.py \"$@\"\n", encoding="utf-8")

    # 3. Themes & Wallpapers
    print("[*] Syncing visual theme packs & wallpapers...")
    themes_dest = INCLUDES_CHROOT / "usr" / "share" / "themes" / "ars-arcanum"
    sync_tree(REPO_ROOT / "themes", themes_dest)

    # 4. Template Packs
    print("[*] Syncing author methodology template packs...")
    templates_dest = INCLUDES_CHROOT / "usr" / "share" / "ars-arcanum" / "templates"
    sync_tree(REPO_ROOT / "templates", templates_dest)

    # 5. Pre-installed Reference World (World of Elaris)
    print("[*] Syncing reference project (/etc/skel/Worlds/Elaris)...")
    elaris_dest = INCLUDES_CHROOT / "etc" / "skel" / "Worlds" / "Elaris"
    sync_tree(REPO_ROOT / "sample_world", elaris_dest)

    # 6. Documentation & Help
    print("[*] Syncing offline help HTML & manual...")
    docs_dest = INCLUDES_CHROOT / "usr" / "share" / "doc" / "ars-arcanum" / "help"
    sync_tree(REPO_ROOT / "docs" / "help_html", docs_dest)
    skel_docs = INCLUDES_CHROOT / "etc" / "skel" / "Documents"
    skel_docs.mkdir(parents=True, exist_ok=True)
    if (REPO_ROOT / "docs" / "typst_manual" / "Ars-Arcanum-Manual.typ").exists():
        shutil.copy2(REPO_ROOT / "docs" / "typst_manual" / "Ars-Arcanum-Manual.typ", skel_docs / "Ars-Arcanum-Manual.typ")

    # 7. Calamares Installer configuration & branding
    print("[*] Syncing Calamares installer configuration & branding...")
    calamares_dest = INCLUDES_CHROOT / "etc" / "calamares"
    sync_tree(REPO_ROOT / "calamares", calamares_dest)

    print("[+] Chroot overlay prepared successfully.")


if __name__ == "__main__":
    prepare_overlay()
