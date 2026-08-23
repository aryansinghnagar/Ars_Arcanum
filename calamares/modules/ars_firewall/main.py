#!/usr/bin/env python3
"""
Calamares Python Job Module: ars_firewall
Applies selected nftables firewall policy (Paranoid vs. Standard) to target installation root.
"""

import os
import shutil
import subprocess

import libcalamares


def run():
    """
    Executes in the chroot environment or directly against root_mount_point.
    """
    root_mount_point = libcalamares.globalstorage.value("rootMountPoint")
    if not root_mount_point:
        return ("No root mount point found", "Failed to configure firewall.")

    # Check user selection or default to paranoid
    firewall_mode = libcalamares.globalstorage.value("ars_firewall_mode") or "paranoid"
    libcalamares.utils.debug(f"[Ars Arcanum] Setting up firewall mode: {firewall_mode}")

    target_ruleset = os.path.join(root_mount_point, "etc", "nftables", f"{firewall_mode}.nft")
    target_conf = os.path.join(root_mount_point, "etc", "nftables.conf")

    if os.path.exists(target_ruleset):
        shutil.copy2(target_ruleset, target_conf)
        libcalamares.utils.debug(f"[Ars Arcanum] Copied {target_ruleset} -> {target_conf}")
    else:
        libcalamares.utils.warning(f"[Ars Arcanum] Firewall template {target_ruleset} not found; keeping default.")

    # Enable systemd nftables service in target root
    try:
        libcalamares.utils.target_env_call(["systemctl", "enable", "nftables.service"])
    except Exception as e:
        libcalamares.utils.warning(f"[Ars Arcanum] Could not enable nftables service: {e}")

    return None
