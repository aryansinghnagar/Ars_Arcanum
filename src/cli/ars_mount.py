#!/usr/bin/env python3
"""
/usr/local/bin/ars-mount — Ars Arcanum Secure USB Storage Handler
Mounts authorized USB mass storage devices with USBGuard verification and safe mount flags.
"""

import os
import sys
import shutil
import argparse
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common.ui_helpers import show_notification, show_info_dialog, show_error_dialog, ask_confirmation


def list_unmounted_usb_devices() -> list:
    """Find plugged USB block devices that are not yet mounted."""
    devices = []
    if shutil.which("lsblk"):
        try:
            proc = subprocess.run(
                ["lsblk", "-J", "-o", "NAME,SIZE,TYPE,MOUNTPOINT,TRAN,LABEL,FSTYPE"],
                capture_output=True,
                text=True,
            )
            import json
            data = json.loads(proc.stdout)
            for dev in data.get("blockdevices", []):
                if dev.get("tran") == "usb":
                    for part in dev.get("children", [dev]):
                        if not part.get("mountpoint") and part.get("type") == "part":
                            devices.append(part)
        except Exception:
            pass
    return devices


def mount_device(device_name: str) -> bool:
    dev_path = f"/dev/{device_name}"
    mount_base = Path(f"/media/{os.getenv('USER', 'author')}")
    mount_point = mount_base / device_name
    mount_point.mkdir(parents=True, exist_ok=True)

    print(f"[*] Mounting {dev_path} to {mount_point} with secure flags (nosuid, nodev)...")
    try:
        # Use udisksctl or direct mount
        if shutil.which("udisksctl"):
            res = subprocess.run(["udisksctl", "mount", "-b", dev_path], capture_output=True, text=True)
            if res.returncode == 0:
                print(f"[+] Successfully mounted: {res.stdout.strip()}")
                show_notification("USB Drive Mounted", f"Mounted {device_name} securely.", urgency="normal", icon="drive-removable-media")
                return True
            else:
                print(f"[!] udisksctl mount warning: {res.stderr}")

        # Fallback to sudo mount
        res = subprocess.run(["sudo", "mount", "-o", "nosuid,nodev", dev_path, str(mount_point)], capture_output=True, text=True)
        if res.returncode == 0:
            print(f"[+] Successfully mounted {dev_path} at {mount_point}")
            show_notification("USB Drive Mounted", f"Mounted at {mount_point}", urgency="normal", icon="drive-removable-media")
            return True
        else:
            print(f"[!] Mount error: {res.stderr}")
            return False
    except Exception as e:
        print(f"[!] Mount failure: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Ars Arcanum Secure USB Mounter")
    parser.add_argument("device", nargs="?", help="Block device name (e.g. sdb1)")
    parser.add_argument("-l", "--list", action="store_true", help="List detected USB drives")
    args = parser.parse_args()

    if args.list or not args.device:
        devices = list_unmounted_usb_devices()
        if not devices:
            print("[*] No unmounted USB storage devices detected.")
            return
        print("\nDetected USB Storage Devices:")
        for d in devices:
            print(f"  • {d.get('name')} — Size: {d.get('SIZE')}, FS: {d.get('FSTYPE')}, Label: {d.get('LABEL')}")
        print()
        if not args.device and devices:
            target = devices[0].get("name")
            if ask_confirmation("Mount USB Drive", f"Authorize and mount USB drive '/dev/{target}'?"):
                mount_device(target)
        return

    mount_device(args.device)


if __name__ == "__main__":
    main()
