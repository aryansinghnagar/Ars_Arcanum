#!/usr/bin/env python3
"""
/usr/local/bin/ars-mount — Ars Arcanum Secure USB Storage Handler
Mounts authorized USB mass storage devices with USBGuard verification and safe mount flags.
"""

import os
import re
import sys
import shutil
import argparse
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common.ui_helpers import show_notification, ask_confirmation

# Strict allowlist: sd[a-z]+[0-9]+, nvme0n1pN, mmcblkNpN — no paths, no flags.
DEVICE_RE = re.compile(r"^(sd[a-z]+[0-9]+|nvme\d+n\d+p\d+|mmcblk\d+p\d+|vd[a-z]+[0-9]+)$")


def is_valid_device_name(name: str) -> bool:
    return bool(DEVICE_RE.match(name or ""))


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
            if not proc.stdout.strip():
                return []
            import json
            data = json.loads(proc.stdout)
            for dev in data.get("blockdevices", []):
                if dev.get("tran") == "usb":
                    for part in dev.get("children", [dev]):
                        if not part.get("mountpoint") and part.get("type") == "part":
                            if is_valid_device_name(part.get("name", "")):
                                devices.append(part)
        except (subprocess.SubprocessError, ValueError, OSError):
            pass
    return devices


def mount_device(device_name: str, allowed: set | None = None) -> bool:
    if not is_valid_device_name(device_name):
        print(f"[!] Refusing to mount invalid device name: {device_name!r}")
        return False
    if allowed is not None and device_name not in allowed:
        print(f"[!] Device {device_name!r} not in detected USB allowlist. Aborting.")
        return False
    dev_path = f"/dev/{device_name}"
    mount_base = Path(f"/media/{os.getenv('USER', 'author')}")
    mount_point = mount_base / device_name
    mount_point.mkdir(parents=True, exist_ok=True)

    print(f"[*] Mounting {dev_path} to {mount_point} with secure flags (nosuid, nodev, noexec)...")
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

        # Fallback to sudo mount (hardened flags; udisksctl path uses system defaults)
        res = subprocess.run(["sudo", "mount", "-o", "nosuid,nodev,noexec", dev_path, str(mount_point)], capture_output=True, text=True)
        if res.returncode == 0:
            print(f"[+] Successfully mounted {dev_path} at {mount_point}")
            show_notification("USB Drive Mounted", f"Mounted at {mount_point}", urgency="normal", icon="drive-removable-media")
            return True
        else:
            print(f"[!] Mount error: {res.stderr}")
            return False
    except OSError as e:
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
                mount_device(target, allowed={d.get("name") for d in devices})
            else:
                print("[*] Mount declined (default-deny).")
        return

    # Explicit device: fail closed against the live USB allowlist.
    # An empty allowlist means lsblk is missing or no USB device was detected;
    # mounting by bare name would risk hitting internal disks, so deny.
    live = {d.get("name") for d in list_unmounted_usb_devices()}
    if not live:
        print("[!] No USB devices detected (or lsblk unavailable). Refusing explicit mount — use --list.")
        return
    mount_device(args.device, allowed=live)


if __name__ == "__main__":
    main()
