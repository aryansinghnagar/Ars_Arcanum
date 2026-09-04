"""
Ars Arcanum — Local Git Operations & Snapshot Engine
Manages automatic, timestamped version control across user world projects (100% offline).
"""

import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional


def init_world_git(world_dir: Path) -> bool:
    """Initialize a local git repository in the world project if not already present."""
    if not (world_dir / ".git").exists():
        try:
            subprocess.run(
                ["git", "init"],
                cwd=str(world_dir),
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            # Configure local identity
            subprocess.run(
                ["git", "config", "user.name", "Ars Arcanum Author"],
                cwd=str(world_dir),
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            subprocess.run(
                ["git", "config", "user.email", "author@ars-arcanum.local"],
                cwd=str(world_dir),
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            # Create standard .gitignore
            gitignore_content = """# Ars Arcanum Git Ignore
09-Backups/
*.tmp
*.bak
*.swp
.DS_Store
Thumbs.db
"""
            (world_dir / ".gitignore").write_text(gitignore_content, encoding="utf-8")
            return True
        except (subprocess.CalledProcessError, OSError) as e:
            print(f"[!] git init failed for {world_dir}: {e}")
            return False
    return True


def create_snapshot(world_dir: Path, message_prefix: str = "Session Snapshot") -> Dict[str, Any]:
    """
    Stage all modified/new files and commit with a timestamped message.
    Returns status dictionary with commit hash, changed file count, and message.
    """
    if not (world_dir / ".git").exists():
        init_world_git(world_dir)

    result = {
        "world": world_dir.name,
        "success": False,
        "committed": False,
        "hash": "",
        "message": "",
        "files_changed": 0,
    }

    try:
        # Check status
        status_proc = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=str(world_dir),
            capture_output=True,
            text=True,
            check=True,
        )
        changes = status_proc.stdout.strip().splitlines()
        if not changes:
            result["success"] = True
            result["message"] = "No changes to commit."
            return result

        # Stage all files
        subprocess.run(["git", "add", "-A"], cwd=str(world_dir), check=True, capture_output=True)

        # Build commit message
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        commit_msg = f"{message_prefix} — {timestamp} [{len(changes)} files modified]"

        subprocess.run(
            ["git", "commit", "-m", commit_msg],
            cwd=str(world_dir),
            capture_output=True,
            text=True,
            check=True,
        )

        # Get latest commit hash
        hash_proc = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(world_dir),
            capture_output=True,
            text=True,
            check=True,
        )

        result["success"] = True
        result["committed"] = True
        result["hash"] = hash_proc.stdout.strip()
        result["message"] = commit_msg
        result["files_changed"] = len(changes)

    except subprocess.CalledProcessError as e:
        result["message"] = f"Git error: {e.stderr if e.stderr else str(e)}"
    except OSError as e:
        result["message"] = f"Execution error: {str(e)}"

    return result


def get_commit_history(world_dir: Path, max_count: int = 10) -> List[Dict[str, str]]:
    """Retrieve recent commit log for the world project."""
    history = []
    if not (world_dir / ".git").exists():
        return history

    try:
        count = int(max_count)
    except (TypeError, ValueError):
        count = 10
    count = max(1, min(100, count))

    try:
        proc = subprocess.run(
            ["git", "log", f"-n{count}", "--pretty=format:%h|%ad|%s", "--date=short"],
            cwd=str(world_dir),
            capture_output=True,
            text=True,
            check=True,
        )
        for line in proc.stdout.strip().splitlines():
            if "|" in line:
                h, d, s = line.split("|", 2)
                history.append({"hash": h, "date": d, "subject": s})
    except (subprocess.CalledProcessError, OSError):
        pass
    return history
