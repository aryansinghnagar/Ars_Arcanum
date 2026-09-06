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

# Adjust module path for standalone CLI execution
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common.config import DEFAULT_CONFIG_DIR, get_active_world_path, ensure_base_directories
from common.git_ops import create_snapshot
from common.logger import log_writing_session, calculate_world_word_count
from common.ui_helpers import show_notification, ask_text_input

FOCUS_STATE_FILE = DEFAULT_CONFIG_DIR / "focus_state.txt"
FOCUS_START_TIME_FILE = DEFAULT_CONFIG_DIR / "focus_start_time.txt"
FOCUS_START_WORDS_FILE = DEFAULT_CONFIG_DIR / "focus_start_words.txt"
FOCUS_LOCK_FILE = DEFAULT_CONFIG_DIR / "focus.lock"
# Portable fallback when PID liveness cannot be determined (e.g. Windows sig 0)
_LOCK_STALE_AFTER_S = 24 * 3600


def _atomic_write(path: Path, text: str) -> None:
    """Atomic state-file write (tmp + rename) to avoid torn focus state."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)


def _pid_alive(pid: int) -> bool | None:
    """True if pid exists, False if definitely dead, None if the platform can't say.

    os.kill(pid, 0) is POSIX-only semantics: on Windows os.kill can terminate
    the target (including ourselves), so it must never be used there — callers
    fall back to age-based staleness instead.
    """
    if os.name != "posix":
        return None
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True  # a live process we may not signal
    except OSError:
        return None
    else:
        return True


def acquire_focus_lock(lock_path: Path = FOCUS_LOCK_FILE) -> bool:
    """Atomically claim the extreme-focus lock (O_EXCL create).

    Reclaims the lock only when the owner is provably dead, or — when PID
    liveness is indeterminable — when the lock is older than _LOCK_STALE_AFTER_S.
    At most two attempts; returns False when a live session owns the lock.
    """
    ensure_base_directories()
    for _ in range(2):
        try:
            fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            pass
        except OSError as e:
            print(f"[!] Cannot create focus lock: {e}")
            return False
        else:
            try:
                os.write(fd, f"{os.getpid()}:{time.time():.0f}".encode("utf-8"))
            finally:
                os.close(fd)
            return True
        try:
            pid_s, _, ts_s = lock_path.read_text(encoding="utf-8").strip().partition(":")
            owner_pid, owner_ts = int(pid_s), float(ts_s)
        except (OSError, ValueError):
            owner_pid, owner_ts = -1, 0.0
        alive = _pid_alive(owner_pid) if owner_pid > 0 else False
        stale = alive is False or (alive is None and time.time() - owner_ts > _LOCK_STALE_AFTER_S)
        if not stale:
            print(f"[*] Focus session already owned by live process {owner_pid}; refusing concurrent session.")
            return False
        try:
            lock_path.unlink()
        except OSError:
            return False
    return False


def release_focus_lock(lock_path: Path = FOCUS_LOCK_FILE) -> None:
    try:
        lock_path.unlink(missing_ok=True)
    except OSError:
        pass


def get_current_focus_mode() -> str:
    """Return 'off', 'dnd', or 'extreme'."""
    try:
        if FOCUS_STATE_FILE.exists():
            mode = FOCUS_STATE_FILE.read_text(encoding="utf-8").strip().lower()
            if mode in ("dnd", "extreme"):
                return mode
    except OSError:
        pass
    return "off"


def set_focus_mode_record(mode: str) -> None:
    ensure_base_directories()
    _atomic_write(FOCUS_STATE_FILE, mode.lower())


def pause_notifications(pause: bool = True) -> None:
    """Toggle Dunst notification daemon state."""
    if shutil.which("dunstctl"):
        try:
            cmd = ["dunstctl", "set-paused", "true" if pause else "false"]
            subprocess.run(cmd, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except OSError:
            pass


def start_timewarrior(tag: str = "Drafting") -> None:
    """Start Timewarrior tracking."""
    if shutil.which("timew"):
        try:
            subprocess.run(["timew", "start", tag], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except OSError:
            pass


def stop_timewarrior() -> None:
    """Stop Timewarrior tracking."""
    if shutil.which("timew"):
        try:
            subprocess.run(["timew", "stop"], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except OSError:
            pass


def enter_dnd_mode() -> None:
    """Engage Do Not Disturb (DND) Mode."""
    set_focus_mode_record("dnd")
    pause_notifications(True)
    show_notification("Focus Mode: DND", "Notifications paused. Multi-window workspace active.", urgency="normal", icon="weather-clouds")
    print("[*] Focus Mode engaged: Do Not Disturb (DND).")


def enter_extreme_mode() -> None:
    """Engage Extreme Focus Mode (kiosk, fullscreen drafting, panel hide, timer start)."""
    if get_current_focus_mode() == "extreme":
        print("[*] Extreme Focus already active — not overwriting session start.")
        return
    if not acquire_focus_lock():
        return
    world_path = get_active_world_path()
    start_words = calculate_world_word_count(world_path) if world_path else 0

    ensure_base_directories()
    _atomic_write(FOCUS_START_TIME_FILE, str(time.time()))
    _atomic_write(FOCUS_START_WORDS_FILE, str(start_words))
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
        except OSError:
            pass

    # Fullscreen active window via wmctrl or xdotool
    if shutil.which("wmctrl"):
        try:
            subprocess.run(["wmctrl", "-r", ":ACTIVE:", "-b", "add,fullscreen"], check=False)
        except OSError:
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
        except (ValueError, OSError):
            pass

    duration_min = max(0.1, (time.time() - start_time) / 60.0)

    # Calculate word delta
    world_path = get_active_world_path()
    start_words = 0
    if FOCUS_START_WORDS_FILE.exists():
        try:
            start_words = int(FOCUS_START_WORDS_FILE.read_text(encoding="utf-8").strip())
        except (ValueError, OSError):
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
        except OSError:
            pass

    # Remove fullscreen kiosk
    if shutil.which("wmctrl"):
        try:
            subprocess.run(["wmctrl", "-r", ":ACTIVE:", "-b", "remove,fullscreen"], check=False)
        except OSError:
            pass

    set_focus_mode_record("off")
    release_focus_lock()

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
