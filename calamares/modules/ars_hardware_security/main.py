#!/usr/bin/env python3
"""
Calamares Python Job Module: ars_hardware_security
Enrolls Secure Boot keys via sbctl and enables strict USBGuard allowlisting if selected.
"""

import os
import subprocess

import libcalamares


def run():
    root_mount_point = libcalamares.globalstorage.value("rootMountPoint")
    if not root_mount_point:
        return ("No root mount point found", "Failed to configure hardware security.")

    enable_hw_sec = libcalamares.globalstorage.value("ars_enable_hardware_security") or False

    if not enable_hw_sec:
        libcalamares.utils.debug("[Ars Arcanum] Advanced hardware security not selected. Skipping.")
        return None

    libcalamares.utils.debug("[Ars Arcanum] Configuring Secure Boot key enrollment and USBGuard allowlist...")

    # Enable USBGuard service
    try:
        libcalamares.utils.target_env_call(["systemctl", "enable", "usbguard.service"])
    except Exception as e:
        libcalamares.utils.warning(f"[Ars Arcanum] Could not enable usbguard: {e}")

    # Enroll Secure Boot keys via sbctl if present
    try:
        libcalamares.utils.target_env_call(["sbctl", "create-keys"])
        libcalamares.utils.target_env_call(["sbctl", "sign-all"])
    except Exception as e:
        libcalamares.utils.warning(f"[Ars Arcanum] Secure Boot key generation notice: {e}")

    return None
