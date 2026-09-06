#!/usr/bin/env python3
"""
/usr/local/bin/ars-update — Ars Arcanum Maintenance & OS Updater
Takes pre-transaction Btrfs snapshot, unlocks nftables relay, applies upgrades, and relocks.
"""

import sys
import shutil
import argparse
import subprocess
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common.ui_helpers import show_notification, show_error_dialog


def create_btrfs_snapshot() -> bool:
    """Create instant pre-update Btrfs snapshot for instant rollback.

    Returns True when a snapshot was created or when btrfs is absent
    (nothing to snapshot — not a failure). Returns False only when a
    snapshot was attempted but failed.
    """
    print("[*] Creating pre-update Btrfs system snapshot...")
    if not shutil.which("btrfs"):
        print("[-] Btrfs tools not installed; skipping snapshot (non-btrfs root).")
        return True
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        snap_target = f"/.snapshots/pre-update-{timestamp}"
        proc = subprocess.run(
            ["sudo", "btrfs", "subvolume", "snapshot", "/", snap_target],
            capture_output=True, text=True, check=False,
        )
        if proc.returncode == 0:
            print(f"[+] Btrfs snapshot created: {snap_target}")
            return True
        print(f"[!] Btrfs snapshot failed: {proc.stderr.strip()[:300]}")
        return False
    except OSError as e:
        print(f"[!] Btrfs snapshot failed: {e}")
        return False


def _set_firewall(mode: str) -> bool:
    """Switch nftables policy using ONLY the mode-specific ruleset.

    Never falls back to the generic /etc/nftables.conf, whose content is
    distro-controlled and may not match the requested mode. Returns True
    when the requested ruleset was applied.
    """
    if mode not in ("standard", "paranoid"):
        return False
    src = Path(f"/etc/nftables/{mode}.nft")
    if not src.exists():
        print(f"[!] Firewall ruleset missing: {src}; leaving current policy in place.")
        return False
    if not shutil.which("nft"):
        print("[!] nft binary not found; cannot switch firewall policy.")
        return False
    proc = subprocess.run(["sudo", "nft", "-f", str(src)], capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        print(f"[!] Failed to apply {src}: {proc.stderr.strip()[:300]}")
        return False
    return True


def run_system_update() -> bool:
    create_btrfs_snapshot()

    print("[*] Opening temporary firewall relay for Debian and Flathub package mirrors...")
    print("[*] (Paranoid mode blocks Flatpak user updates; switching to Standard for update window.)")
    if not _set_firewall("standard"):
        print("[!] Continuing update with current firewall policy.")
    # In Paranoid mode, apt UID _apt is permitted; standard updates can run
    show_notification("OS Update Started", "Refreshing package repositories...", urgency="normal", icon="system-software-update")

    try:
        if shutil.which("apt-get"):
            print("[*] Running APT update...")
            subprocess.run(["sudo", "apt-get", "update"], check=True)
            print("[*] Applying system package upgrades...")
            subprocess.run(["sudo", "apt-get", "upgrade", "-y"], check=True)

        if shutil.which("flatpak"):
            print("[*] Updating sandboxed Flatpaks...")
            subprocess.run(["flatpak", "update", "-y"], check=False)

        print("\n[+] SUCCESS: Ars Arcanum operating system updated successfully!")
        show_notification("OS Update Complete", "All system packages and creative tools up to date.", urgency="normal", icon="dialog-ok")
        return True

    except subprocess.CalledProcessError as e:
        print(f"\n[!] Update error occurred: {e}")
        show_error_dialog("Update Failed", f"OS update encountered an error: {e}")
        return False
    finally:
        print("[*] Verifying nftables firewall lockdown status...")
        # Relock to Paranoid after updates; report honestly if relock fails.
        if not _set_firewall("paranoid"):
            print("[!] WARNING: could not relock Paranoid firewall; check /etc/nftables/paranoid.nft.")
            show_error_dialog("Firewall Relock Failed", "Paranoid nftables policy could not be reapplied.")


def main():
    parser = argparse.ArgumentParser(description="Ars Arcanum Maintenance & OS Updater")
    parser.parse_args()

    run_system_update()


if __name__ == "__main__":
    main()
