"""
Ars Arcanum — Unified Desktop UI Dialog & Notification Helpers
Provides seamless GUI dialogs with Zenity/Yad fallback if running in minimal headless or CLI environments.
"""

import os
import shutil
import subprocess
from typing import Optional, List


def show_notification(title: str, message: str, urgency: str = "normal", icon: str = "document-edit") -> None:
    """Send desktop notification via notify-send or dunst."""
    if shutil.which("notify-send"):
        try:
            subprocess.run(
                ["notify-send", "-u", urgency, "-i", icon, title, message],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return
        except Exception:
            pass
    print(f"[{urgency.upper()}] {title}: {message}")


def show_info_dialog(title: str, text: str) -> None:
    """Display information dialog via Zenity/Yad or stdout."""
    if shutil.which("zenity"):
        try:
            subprocess.run(["zenity", "--info", "--title", title, "--text", text, "--width=400"], check=False)
            return
        except Exception:
            pass
    elif shutil.which("yad"):
        try:
            subprocess.run(["yad", "--info", "--title", title, "--text", text, "--width=400"], check=False)
            return
        except Exception:
            pass
    print(f"=== {title} ===\n{text}\n")


def show_error_dialog(title: str, text: str) -> None:
    """Display error dialog via Zenity/Yad or stderr."""
    if shutil.which("zenity"):
        try:
            subprocess.run(["zenity", "--error", "--title", title, "--text", text, "--width=400"], check=False)
            return
        except Exception:
            pass
    elif shutil.which("yad"):
        try:
            subprocess.run(["yad", "--error", "--title", title, "--text", text, "--width=400"], check=False)
            return
        except Exception:
            pass
    print(f"[ERROR] {title}: {text}")


def ask_text_input(title: str, prompt: str, default: str = "") -> Optional[str]:
    """Prompt user for single-line text input."""
    if shutil.which("zenity"):
        try:
            proc = subprocess.run(
                ["zenity", "--entry", "--title", title, "--text", prompt, f"--entry-text={default}"],
                capture_output=True,
                text=True,
            )
            if proc.returncode == 0:
                return proc.stdout.strip()
            return None
        except Exception:
            pass
    elif shutil.which("yad"):
        try:
            proc = subprocess.run(
                ["yad", "--entry", "--title", title, "--text", prompt, f"--entry-text={default}"],
                capture_output=True,
                text=True,
            )
            if proc.returncode == 0:
                return proc.stdout.strip()
            return None
        except Exception:
            pass
    # Fallback to non-blocking or default
    return default


def ask_confirmation(title: str, question: str) -> bool:
    """Prompt user for confirmation (Yes/No)."""
    if shutil.which("zenity"):
        try:
            proc = subprocess.run(
                ["zenity", "--question", "--title", title, "--text", question],
                check=False,
            )
            return proc.returncode == 0
        except Exception:
            pass
    return True
