"""
Ars Arcanum — Common Foundation Library
Core configuration, filesystem resolution, and environment discovery.
"""

import os
from pathlib import Path
from typing import Optional, List, Dict, Any

# Root filesystem constants
DEFAULT_WORLDS_DIR = Path.home() / "Worlds"
DEFAULT_CONFIG_DIR = Path.home() / ".config" / "ars-arcanum"
DEFAULT_CACHE_DIR = Path.home() / ".cache" / "ars-arcanum"
SYSTEM_THEMES_DIR = Path("/usr/share/themes/ars-arcanum")
LOCAL_THEMES_DIR = DEFAULT_CONFIG_DIR / "themes"
DOCS_DIR = Path("/usr/share/doc/ars-arcanum")

# Standard World Subdirectories
WORLD_SUBDIRS = [
    "00-World-Bible",
    "00-World-Bible/Characters",
    "00-World-Bible/Locations",
    "00-World-Bible/Factions-Dynasties",
    "00-World-Bible/Magic-Technology",
    "00-World-Bible/Species-Cultures",
    "00-World-Bible/History-Eras",
    "00-World-Bible/Languages-Dialects",
    "00-World-Bible/Religion-Mythology",
    "00-World-Bible/Bestiary-Flora",
    "00-World-Bible/Items-Artifacts",
    "00-World-Bible/Templates",
    "00-World-Bible/Session-Notes",
    "01-Manuscripts",
    "01-Manuscripts/Book-01",
    "01-Manuscripts/Short-Fiction",
    "01-Manuscripts/Outlines",
    "02-Maps",
    "02-Maps/World-Maps",
    "02-Maps/Regional-Maps",
    "02-Maps/City-Battle-Maps",
    "02-Maps/Brushes-Tilesets",
    "03-Art-Heraldry",
    "03-Art-Heraldry/Character-Portraits",
    "03-Art-Heraldry/Heraldry-Sigils",
    "03-Art-Heraldry/Custom-Fonts",
    "03-Art-Heraldry/Cover-Designs",
    "04-Languages",
    "05-Timelines",
    "06-Genealogy",
    "07-Publishing",
    "07-Publishing/Typst-Templates",
    "07-Publishing/Print-PDF",
    "07-Publishing/Digital-EPUB",
    "08-Research",
    "09-Backups",
]

AVAILABLE_THEMES = ["grimoire", "astral", "sylvan", "obsidian", "ivory"]


def ensure_base_directories() -> None:
    """Ensure user workspace and config folders exist."""
    DEFAULT_WORLDS_DIR.mkdir(parents=True, exist_ok=True)
    DEFAULT_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    DEFAULT_CACHE_DIR.mkdir(parents=True, exist_ok=True)


def get_active_world_name() -> Optional[str]:
    """Retrieve the currently active world name from config."""
    state_file = DEFAULT_CONFIG_DIR / "active_world.txt"
    if state_file.exists():
        world = state_file.read_text(encoding="utf-8").strip()
        if world and (DEFAULT_WORLDS_DIR / world).is_dir():
            return world
    worlds = list_worlds()
    return worlds[0] if worlds else None


def set_active_world_name(world_name: str) -> None:
    """Persist the currently active world name."""
    ensure_base_directories()
    state_file = DEFAULT_CONFIG_DIR / "active_world.txt"
    state_file.write_text(world_name.strip(), encoding="utf-8")


def get_active_world_path() -> Optional[Path]:
    """Get Path to active world."""
    world = get_active_world_name()
    if world:
        path = DEFAULT_WORLDS_DIR / world
        if path.is_dir():
            return path
    return None


def resolve_world_path(target: Optional[str] = None) -> Optional[Path]:
    """
    Universally resolve a world path:
    1. If target is a valid directory path (relative or absolute), return Path(target).
    2. If target is a world name in ~/Worlds, return DEFAULT_WORLDS_DIR / target.
    3. If target is None, return get_active_world_path().
    """
    if target:
        p = Path(target)
        if p.is_dir():
            return p.resolve()
        w_p = DEFAULT_WORLDS_DIR / target
        if w_p.is_dir():
            return w_p.resolve()
    return get_active_world_path()


def list_worlds() -> List[str]:
    """List all initialized world project directories in ~/Worlds."""
    if not DEFAULT_WORLDS_DIR.exists():
        return []
    return sorted(
        [
            d.name
            for d in DEFAULT_WORLDS_DIR.iterdir()
            if d.is_dir() and (d / "00-World-Bible").exists()
        ]
    )


def get_active_theme() -> str:
    """Retrieve current theme name (defaults to 'grimoire')."""
    theme_file = DEFAULT_CONFIG_DIR / "active_theme.txt"
    if theme_file.exists():
        theme = theme_file.read_text(encoding="utf-8").strip().lower()
        if theme in AVAILABLE_THEMES:
            return theme
    return "grimoire"


def set_active_theme(theme_name: str) -> None:
    """Persist active theme name."""
    if theme_name.lower() in AVAILABLE_THEMES:
        ensure_base_directories()
        theme_file = DEFAULT_CONFIG_DIR / "active_theme.txt"
        theme_file.write_text(theme_name.lower(), encoding="utf-8")
