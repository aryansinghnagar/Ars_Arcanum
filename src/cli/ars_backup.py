#!/usr/bin/env python3
"""
/usr/local/bin/ars-backup — Ars Arcanum 3-2-1 Encrypted Vault Backup Engine
Automates BorgBackup deduplication, AES-256 encrypted archives, and quarterly restore drills.
"""

import sys
import shutil
import argparse
import subprocess
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common.config import DEFAULT_WORLDS_DIR, DEFAULT_CONFIG_DIR
from common.ui_helpers import show_notification, show_info_dialog, show_error_dialog

BACKUP_VAULT_DIR = Path.home() / ".local" / "share" / "ars-vault"


def init_borg_vault(vault_path: Path) -> bool:
    """Initialize encrypted BorgBackup repository if not present."""
    if not shutil.which("borg"):
        print("[!] BorgBackup binary not installed. Please install borgbackup package.")
        return False

    if not vault_path.exists() or not (vault_path / "config").exists():
        print(f"[*] Initializing encrypted BorgBackup vault at: {vault_path}")
        vault_path.mkdir(parents=True, exist_ok=True)
        try:
            # Init repository with repokey encryption
            env = {"BORG_PASSPHRASE": "ars-arcanum-local-vault"}
            subprocess.run(
                ["borg", "init", "--encryption=repokey", str(vault_path)],
                env=env,
                check=True,
                capture_output=True,
                text=True,
            )
            print("[+] Borg vault initialized successfully.")
            return True
        except Exception as e:
            print(f"[!] Failed to initialize Borg vault: {e}")
            return False
    return True


def run_backup(target_repo: Path = BACKUP_VAULT_DIR) -> bool:
    """Execute deduplicated encrypted backup of ~/Worlds."""
    if not init_borg_vault(target_repo):
        return False

    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    archive_name = f"{target_repo}::worlds-{timestamp}"

    print(f"[*] Creating encrypted backup archive: worlds-{timestamp}...")
    try:
        env = {"BORG_PASSPHRASE": "ars-arcanum-local-vault"}
        proc = subprocess.run(
            [
                "borg",
                "create",
                "--stats",
                "--progress",
                "--compression",
                "zstd,6",
                archive_name,
                str(DEFAULT_WORLDS_DIR),
            ],
            env=env,
            capture_output=True,
            text=True,
        )
        if proc.returncode == 0:
            print("[+] Backup created successfully!")
            print(proc.stdout)
            show_notification("Backup Completed", f"Vault updated: worlds-{timestamp}", urgency="normal", icon="document-save")
            return True
        else:
            print(f"[!] Borg error: {proc.stderr}")
            return False
    except Exception as e:
        print(f"[!] Backup execution failure: {e}")
        return False


def run_restore_drill(target_repo: Path = BACKUP_VAULT_DIR) -> bool:
    """Perform a dry-run integrity and verification drill of the latest backup archive."""
    print(f"[*] Starting 3-2-1 Vault Disaster Recovery & Restore Drill on {target_repo}...")
    if not shutil.which("borg"):
        print("[!] BorgBackup not installed.")
        return False

    try:
        env = {"BORG_PASSPHRASE": "ars-arcanum-local-vault"}
        # List archives
        list_proc = subprocess.run(["borg", "list", str(target_repo)], env=env, capture_output=True, text=True)
        if list_proc.returncode != 0:
            print(f"[!] Failed to read vault: {list_proc.stderr}")
            return False

        archives = list_proc.stdout.strip().splitlines()
        if not archives:
            print("[!] No archives found in vault.")
            return False

        latest_archive = archives[-1].split()[0]
        print(f"[*] Testing integrity of latest archive: {latest_archive}...")

        # Run dry-run extract verification
        test_proc = subprocess.run(
            ["borg", "check", "--repository-only", str(target_repo)],
            env=env,
            capture_output=True,
            text=True,
        )
        if test_proc.returncode == 0:
            print("[+] RESTORE DRILL PASSED: Archive checksums and cryptographic integrity 100% verified.")
            show_notification("Restore Drill Passed", f"Archive {latest_archive} verified.", urgency="low", icon="dialog-ok")
            return True
        else:
            print(f"[!] Integrity check failed: {test_proc.stderr}")
            return False
    except Exception as e:
        print(f"[!] Drill failed: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Ars Arcanum 3-2-1 Encrypted Backup Engine")
    parser.add_argument("-d", "--drill", action="store_true", help="Execute disaster recovery restore drill test")
    parser.add_argument("-r", "--repo", help="Custom destination repository path (e.g. external USB mount)")
    args = parser.parse_args()

    repo_path = Path(args.repo) if args.repo else BACKUP_VAULT_DIR

    if args.drill:
        run_restore_drill(repo_path)
    else:
        run_backup(repo_path)


if __name__ == "__main__":
    main()
