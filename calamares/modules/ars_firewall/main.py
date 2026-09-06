#!/usr/bin/env python3
"""
Calamares Python Job Module: ars_firewall
Applies selected nftables firewall policy (Paranoid vs. Standard) to target installation root.
"""

import os
import shutil

import libcalamares


def run():
    """
    Executes in the chroot environment or directly against root_mount_point.
    Expects globalstorage key 'ars_firewall_mode' in {paranoid, standard, airplane}.
    Defaults to 'paranoid' when unset (set by welcome page or settings.conf).
    """
    root_mount_point = libcalamares.globalstorage.value("rootMountPoint")
    if not root_mount_point:
        return ("No root mount point found", "Failed to configure firewall.")

    # Check user selection or default to paranoid
    firewall_mode = libcalamares.globalstorage.value("ars_firewall_mode") or "paranoid"
    if firewall_mode not in ("paranoid", "standard", "airplane"):
        libcalamares.utils.warning(f"[Ars Arcanum] Unknown firewall mode '{firewall_mode}'; falling back to paranoid.")
        firewall_mode = "paranoid"
    libcalamares.utils.debug(f"[Ars Arcanum] Setting up firewall mode: {firewall_mode}")

    target_ruleset = os.path.join(root_mount_point, "etc", "nftables", f"{firewall_mode}.nft")
    target_conf = os.path.join(root_mount_point, "etc", "nftables.conf")

    if os.path.exists(target_ruleset):
        # Back up distro default before overwriting, preserving rollback path.
        if os.path.exists(target_conf):
            try:
                shutil.copy2(target_conf, target_conf + ".dist")
            except OSError as e:
                libcalamares.utils.warning(f"[Ars Arcanum] Could not back up {target_conf}: {e}")
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
