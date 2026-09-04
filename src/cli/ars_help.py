#!/usr/bin/env python3
"""
/usr/local/bin/ars-help — Ars Arcanum Offline Help & Documentation Launcher
Opens the built-in HTML documentation or prints CLI reference when invoked via F1 or terminal.
"""

import os
import sys
import shutil
import argparse
import subprocess
from pathlib import Path

# Help search locations
DOC_PATHS = [
    Path("/usr/share/doc/ars-arcanum/help_html/index.html"),
    Path(__file__).resolve().parent.parent.parent / "docs" / "help_html" / "index.html",
    Path.home() / "Documents" / "Ars-Arcanum-Manual.pdf",
]


def launch_help_gui() -> bool:
    """Launch offline help HTML in browser or document viewer."""
    for p in DOC_PATHS:
        try:
            if p.exists():
                print(f"[*] Opening Ars Arcanum Help System: {p}")
                if shutil.which("xdg-open"):
                    subprocess.Popen(["xdg-open", str(p)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    return True
                elif sys.platform == "win32":
                    os.startfile(str(p))  # noqa: S606 - local file path only
                    return True
        except OSError as e:
            print(f"[!] Could not open help file {p}: {e}")
            continue
    return False


def print_cli_help() -> None:
    print("""
========================================================================
            ARS ARCANUM — THE WRITER'S FORGE HELP REFERENCE
========================================================================

CORE KEYBOARD SHORTCUTS:
  Super+Space      : Open Rofi Workflow Launcher
  Super+W          : Open / Focus Obsidian (World Bible)
  Super+D          : Open / Focus FocusWriter (Distraction-free drafting)
  Super+N          : Open / Focus novelWriter (Structured manuscript)
  Super+M          : Open / Focus Manuskript (Snowflake planner)
  Super+K          : Open Krita (Digital concept painting)
  Super+I          : Open Inkscape (Heraldry & vector sigils)
  Super+T          : Open Timeline Project (Chronological tracking)
  Super+G          : GoldenDict-ng Instant Dictionary popup
  Ctrl+Alt+W       : Artha Instant Thesaurus lookup
  Super+F          : Engage Extreme Focus Mode (kiosk, timer, panel hide)
  Super+Shift+F    : Toggle Do Not Disturb (DND)
  Super+Escape     : Exit Focus Mode (Ceremony, word count, Git snapshot)
  Super+S          : Manual Git Snapshot of active worlds
  Super+B          : BorgBackup encrypted vault creation
  F1               : Open this Help System

CORE CLI COMMANDS:
  ars-focus [dnd|extreme|off|status] : Manage focus modes
  ars-snapshot [world] [-a]          : Git snapshot of world repositories
  ars-compile [world] [-f pdf|epub]  : Compile manuscript to Typst PDF / EPUB
  ars-audit [world]                  : Scan for lore & continuity contradictions
  ars-travel <miles> [-m mode]       : Transit time & supply calculator
  ars-loop [world] [--export-drawio] : Non-linear narrative state tracker
  ars-theme [name] [-l]              : Change system & editor color themes
  ars-backup [-d]                    : Encrypted 3-2-1 vault backup & drill test
  ars-mount                          : Secure USB storage mounting
  ars-update                         : Btrfs pre-snapshot & firewall-relay updater
  ars-extensions [list|install]      : Manage specialist tool tiers
========================================================================
""")


def main():
    parser = argparse.ArgumentParser(description="Ars Arcanum Help System")
    parser.add_argument("--cli", action="store_true", help="Print CLI help text in terminal")
    args = parser.parse_args()

    if args.cli or not launch_help_gui():
        print_cli_help()


if __name__ == "__main__":
    main()
