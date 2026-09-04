"""
Ars Arcanum — Writing Session Logger & Metrics Tracker
Logs drafting duration, words added, focus mode duration into ~/Worlds/<World>/09-Backups/session_logs.md
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Optional
from .lore_parser import parse_frontmatter


def log_writing_session(
    world_dir: Path,
    duration_minutes: float,
    words_written: int,
    session_type: str = "Drafting",
    notes: Optional[str] = None,
) -> None:
    """Append structured session record to 09-Backups/session_logs.md."""
    backups_dir = world_dir / "09-Backups"
    backups_dir.mkdir(parents=True, exist_ok=True)
    log_file = backups_dir / "session_logs.md"

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    header_needed = not log_file.exists() or log_file.stat().st_size == 0

    entry = []
    if header_needed:
        entry.append("# Ars Arcanum — Writing Session & Word Count Logs\n")
        entry.append("| Timestamp | Session Type | Duration (min) | Words Logged | Notes |")
        entry.append("|---|---|---|---|---|")

    safe_notes = (notes or "Normal deep work session").replace("|", "-").replace("\n", " ").replace("\r", " ")[:500]
    try:
        duration_val = float(duration_minutes)
    except (TypeError, ValueError):
        duration_val = 0.0
    try:
        words_val = int(words_written)
    except (TypeError, ValueError):
        words_val = 0
    safe_type = str(session_type).replace("|", "-").replace("\n", " ")[:80]
    entry.append(
        f"| {now_str} | {safe_type} | {duration_val:.1f} | {words_val:+d} | {safe_notes} |"
    )

    with open(log_file, "a", encoding="utf-8") as f:
        f.write("\n".join(entry) + "\n")


def calculate_world_word_count(world_dir: Path) -> int:
    """Calculate total words across all markdown files in 01-Manuscripts."""
    manuscripts_dir = world_dir / "01-Manuscripts"
    if not manuscripts_dir.exists():
        return 0

    total_words = 0
    for md_file in manuscripts_dir.rglob("*.md"):
        try:
            text = md_file.read_text(encoding="utf-8", errors="ignore")
            _, body = parse_frontmatter(text)
            words = body.split()
            total_words += len(words)
        except OSError:
            continue
    return total_words
