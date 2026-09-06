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
from common.ui_helpers import show_notification


def run_snapshots(target_world: str = None, all_worlds: bool = False) -> int:
    """Snapshot worlds. Returns number of worlds committed. Raises SystemExit codes via main."""
    worlds_to_process = []

    if target_world:
        if "/" in target_world or "\\" in target_world or ".." in target_world:
            print(f"[!] Error: Invalid world name '{target_world}'. Use a plain world name, not a path.")
            return -1
        p = (DEFAULT_WORLDS_DIR / target_world).resolve()
        # Containment: resolved path must stay inside ~/Worlds
        try:
            p.relative_to(DEFAULT_WORLDS_DIR.resolve())
        except ValueError:
            print(f"[!] Error: World '{target_world}' escapes {DEFAULT_WORLDS_DIR}")
            return -1
        if p.is_dir():
            worlds_to_process.append(p)
        else:
            print(f"[!] Error: World '{target_world}' not found in {DEFAULT_WORLDS_DIR}")
            return -1
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
        return 0

    total_committed = 0

    for w_path in worlds_to_process:
        res = create_snapshot(w_path, message_prefix="Manual Snapshot")
        if res["committed"]:
            total_committed += 1
            print(f"[+] Committed [{w_path.name}]: {res['hash']} — {res['files_changed']} files changed.")
        else:
            print(f"[-] [{w_path.name}]: {res['message']}")

    if total_committed > 0:
        show_notification(
            title="World Snapshots Created",
            message=f"Committed changes in {total_committed} world project(s).",
            urgency="normal",
            icon="document-save",
        )
    else:
        print("[*] All world repositories are clean. Nothing to commit.")
    return total_committed


def main():
    parser = argparse.ArgumentParser(description="Ars Arcanum Git Auto-Snapshot Utility")
    parser.add_argument("world", nargs="?", help="Specific world project name (optional)")
    parser.add_argument("-a", "--all", action="store_true", help="Snapshot all worlds in ~/Worlds")
    args = parser.parse_args()

    rc = run_snapshots(target_world=args.world, all_worlds=args.all)
    sys.exit(1 if rc == -1 else 0)


if __name__ == "__main__":
    main()
