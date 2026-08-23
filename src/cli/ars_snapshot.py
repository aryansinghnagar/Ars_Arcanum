#!/usr/bin/env python3
"""
/usr/local/bin/ars-snapshot — Ars Arcanum Git Auto-Snapshot Utility
Commits timestamped diffs across active world repositories without network communication.
"""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common.config import DEFAULT_WORLDS_DIR, list_worlds, get_active_world_path
from common.git_ops import create_snapshot
from common.ui_helpers import show_notification, show_info_dialog


def run_snapshots(target_world: str = None, all_worlds: bool = False) -> None:
    worlds_to_process = []

    if target_world:
        p = DEFAULT_WORLDS_DIR / target_world
        if p.is_dir():
            worlds_to_process.append(p)
        else:
            print(f"[!] Error: World '{target_world}' not found in {DEFAULT_WORLDS_DIR}")
            return
    elif all_worlds:
        for w in list_worlds():
            worlds_to_process.append(DEFAULT_WORLDS_DIR / w)
    else:
        active_p = get_active_world_path()
        if active_p:
            worlds_to_process.append(active_p)
        else:
            # Fallback to all found worlds
            for w in list_worlds():
                worlds_to_process.append(DEFAULT_WORLDS_DIR / w)

    if not worlds_to_process:
        print("[!] No world projects found to snapshot.")
        return

    total_committed = 0
    summaries = []

    for w_path in worlds_to_process:
        res = create_snapshot(w_path, message_prefix="Manual Snapshot")
        if res["committed"]:
            total_committed += 1
            summaries.append(f"• {w_path.name}: {res['hash']} ({res['files_changed']} files)")
            print(f"[+] Committed [{w_path.name}]: {res['hash']} — {res['files_changed']} files changed.")
        else:
            print(f"[-] [{w_path.name}]: {res['message']}")

    if total_committed > 0:
        summary_text = "\n".join(summaries)
        show_notification(
            title="World Snapshots Created",
            message=f"Committed changes in {total_committed} world project(s).",
            urgency="normal",
            icon="document-save",
        )
    else:
        print("[*] All world repositories are clean. Nothing to commit.")


def main():
    parser = argparse.ArgumentParser(description="Ars Arcanum Git Auto-Snapshot Utility")
    parser.add_argument("world", nargs="?", help="Specific world project name (optional)")
    parser.add_argument("-a", "--all", action="store_true", help="Snapshot all worlds in ~/Worlds")
    args = parser.parse_args()

    run_snapshots(target_world=args.world, all_worlds=args.all)


if __name__ == "__main__":
    main()
