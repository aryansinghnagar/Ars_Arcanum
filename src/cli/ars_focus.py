#!/usr/bin/env python3
"""
/usr/local/bin/ars-focus — Ars Arcanum Focus Controller & Session Kiosk
Coordinates Dunst notification suppression, XFCE panel state, Timewarrior tracking, and exit ceremonies.
"""

import os
import sys
import time
import shutil
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

# Adjust module path for standalone CLI execution
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common.config import DEFAULT_CONFIG_DIR, get_active_world_path, ensure_base_directories
from common.git_ops import create_snapshot
from common.logger import log_writing_session, calculate_world_word_count
from common.ui_helpers import show_notification, ask_text_input, show_info_dialog

FOCUS_STATE_FILE = DEFAULT_CONFIG_DIR / "focus_state.txt"
FOCUS_START_TIME_FILE = DEFAULT_CONFIG_DIR / "focus_start_time.txt"
FOCUS_START_WORDS_FILE = DEFAULT_CONFIG_DIR / "focus_start_words.txt"


def get_current_focus_mode() -> str:
    """Return 'off', 'dnd', or 'extreme'."""
    if FOCUS_STATE_FILE.exists():
        mode = FOCUS_STATE_FILE.read_text(encoding="utf-8").strip().lower()
        if mode in ("dnd", "extreme"):
            return mode
    return "off"


def set_focus_mode_record(mode: str) -> None:
    ensure_base_directories()
    FOCUS_STATE_FILE.write_text(mode.lower(), encoding="utf-8")


def pause_notifications(pause: bool = True) -> None:
    """Toggle Dunst notification daemon state."""
    if shutil.which("dunstctl"):
        try:
            cmd = ["dunstctl", "set-paused", "true" if pause else "false"]
            subprocess.run(cmd, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass


def start_timewarrior(tag: str = "Drafting") -> None:
    """Start Timewarrior tracking."""
    if shutil.which("timew"):
        try:
            subprocess.run(["timew", "start", tag], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass


def stop_timewarrior() -> None:
    """Stop Timewarrior tracking."""
    if shutil.which("timew"):
        try:
            subprocess.run(["timew", "stop"], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass


def enter_dnd_mode() -> None:
    """Engage Do Not Disturb (DND) Mode."""
    set_focus_mode_record("dnd")
    pause_notifications(True)
    show_notification("Focus Mode: DND", "Notifications paused. Multi-window workspace active.", urgency="normal", icon="weather-clouds")
    print("[*] Focus Mode engaged: Do Not Disturb (DND).")


def enter_extreme_mode() -> None:
    """Engage Extreme Focus Mode (kiosk, fullscreen drafting, panel hide, timer start)."""
    world_path = get_active_world_path()
    start_words = calculate_world_word_count(world_path) if world_path else 0

    ensure_base_directories()
    FOCUS_START_TIME_FILE.write_text(str(time.time()), encoding="utf-8")
    FOCUS_START_WORDS_FILE.write_text(str(start_words), encoding="utf-8")
    set_focus_mode_record("extreme")

    # Mute notifications
    pause_notifications(True)

    # Start Timewarrior
    start_timewarrior("Deep Writing")

    # Hide XFCE Panel if running in X11
    if shutil.which("xfconf-query"):
        try:
            # Set panel autohide or minimize
            subprocess.run(["xfconf-query", "-c", "xfce4-panel", "-p", "/panels/panel-1/autohide-behavior", "-s", "2"], check=False)
        except Exception:
            pass

    # Fullscreen active window via wmctrl or xdotool
    if shutil.which("wmctrl"):
        try:
            subprocess.run(["wmctrl", "-r", ":ACTIVE:", "-b", "add,fullscreen"], check=False)
        except Exception:
            pass

    show_notification("Extreme Focus Activated", "Kiosk engaged. Press Super+Escape when finished.", urgency="critical", icon="dialog-password")
    print("[*] Extreme Focus Mode engaged. Kiosk locked.")


def exit_focus_mode() -> None:
    """Exit Focus Mode with ceremony (word count logging, git snapshot, UI restore)."""
    current_mode = get_current_focus_mode()
    if current_mode == "off":
        print("[*] Focus Mode is already OFF.")
        return

    # Calculate session duration
    start_time = time.time()
    if FOCUS_START_TIME_FILE.exists():
        try:
            start_time = float(FOCUS_START_TIME_FILE.read_text(encoding="utf-8").strip())
        except ValueError:
            pass

    duration_min = max(0.1, (time.time() - start_time) / 60.0)

    # Calculate word delta
    world_path = get_active_world_path()
    start_words = 0
    if FOCUS_START_WORDS_FILE.exists():
        try:
            start_words = int(FOCUS_START_WORDS_FILE.read_text(encoding="utf-8").strip())
        except ValueError:
            pass

    current_words = calculate_world_word_count(world_path) if world_path else 0
    words_written = max(0, current_words - start_words)

    # Un-pause notifications
    pause_notifications(False)

    # Stop Timewarrior
    stop_timewarrior()

    # Restore XFCE Panel
    if shutil.which("xfconf-query"):
        try:
            subprocess.run(["xfconf-query", "-c", "xfce4-panel", "-p", "/panels/panel-1/autohide-behavior", "-s", "0"], check=False)
        except Exception:
            pass

    # Remove fullscreen kiosk
    if shutil.which("wmctrl"):
        try:
            subprocess.run(["wmctrl", "-r", ":ACTIVE:", "-b", "remove,fullscreen"], check=False)
        except Exception:
            pass

    set_focus_mode_record("off")

    # Clean temporary timestamp files
    if FOCUS_START_TIME_FILE.exists():
        FOCUS_START_TIME_FILE.unlink(missing_ok=True)
    if FOCUS_START_WORDS_FILE.exists():
        FOCUS_START_WORDS_FILE.unlink(missing_ok=True)

    # Ceremony: prompt user for session notes
    note = ask_text_input(
        title="Session Completed",
        prompt=f"Great work! Duration: {duration_min:.1f} min | Words Added: +{words_written}\nAdd optional session notes for your journal:",
        default="Chapter drafting session",
    )

    # Log to World Bible
    if world_path:
        log_writing_session(
            world_dir=world_path,
            duration_minutes=duration_min,
            words_written=words_written,
            session_type=f"Focus ({current_mode.upper()})",
            notes=note or "Session concluded",
        )
        # Auto-snapshot world repository
        snap_res = create_snapshot(world_path, message_prefix="Post-Focus Auto-Snapshot")
        if snap_res["committed"]:
            print(f"[*] Snapshot committed: {snap_res['hash']} ({snap_res['files_changed']} files)")

    show_notification("Focus Session Finished", f"Logged {duration_min:.1f} mins and +{words_written} words.", urgency="normal", icon="document-save")
    print(f"[*] Focus Mode deactivated. Duration: {duration_min:.1f} min, Words added: {words_written}.")


def main():
    parser = argparse.ArgumentParser(description="Ars Arcanum Focus Mode Controller")
    parser.add_argument("mode", choices=["dnd", "extreme", "off", "status", "toggle"], nargs="?", default="status")
    args = parser.parse_args()

    if args.mode == "dnd":
        enter_dnd_mode()
    elif args.mode == "extreme":
        enter_extreme_mode()
    elif args.mode == "off":
        exit_focus_mode()
    elif args.mode == "toggle":
        current = get_current_focus_mode()
        if current == "off":
            enter_dnd_mode()
        else:
            exit_focus_mode()
    elif args.mode == "status":
        print(f"Focus Mode: {get_current_focus_mode().upper()}")


if __name__ == "__main__":
    main()
