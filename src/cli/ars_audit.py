#!/usr/bin/env python3
"""
/usr/local/bin/ars-audit — Ars Arcanum Continuity & Lore Consistency Linter
Scans manuscripts against World Bible entities to identify attribute contradictions and broken links.
"""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common.config import resolve_world_path
from common.lore_parser import audit_manuscript_consistency, extract_world_entities
from common.ui_helpers import show_notification


def run_audit(world_dir: Path) -> int:
    print(f"[*] Auditing World Repository: {world_dir.name}")
    entities = extract_world_entities(world_dir)
    print(f"[*] Loaded {len(entities)} tracked lore entities from 00-World-Bible.")

    findings = audit_manuscript_consistency(world_dir)

    if not findings:
        print("\n[+] SUCCESS: Lore audit clean! Zero attribute contradictions or broken links found.")
        show_notification("Lore Audit Complete", "Zero lore contradictions found.", urgency="low", icon="dialog-ok")
        return 0

    print(f"\n[!] Found {len(findings)} continuity issue(s):")
    for f in findings:
        badge = "[ERROR]" if f["severity"] == "ERROR" else "[WARN]"
        print(f"  {badge} {f['file']}:{f['line']} — {f['category']}: {f['message']}")

    show_notification(
        title="Lore Audit Warnings",
        message=f"Found {len(findings)} continuity issues in {world_dir.name}.",
        urgency="critical",
        icon="dialog-warning",
    )
    return len(findings)


def main():
    parser = argparse.ArgumentParser(description="Ars Arcanum Continuity & Lore Linter")
    parser.add_argument("world", nargs="?", help="Specific world project name or path (optional)")
    args = parser.parse_args()

    world_path = resolve_world_path(args.world)
    if not world_path or not world_path.is_dir():
        print("[!] No active world found to audit.")
        sys.exit(1)

    exit_code = run_audit(world_path)
    sys.exit(0 if exit_code == 0 else 1)


if __name__ == "__main__":
    main()
