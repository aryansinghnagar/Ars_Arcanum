"""
Ars Arcanum — World Scaffolding Engine for ars-wizard
Creates complete ~/Worlds/<WorldName> directory tree and installs selected template packs.
"""

import os
import shutil
import textwrap
from pathlib import Path
from typing import List

from common.config import DEFAULT_WORLDS_DIR, WORLD_SUBDIRS, set_active_world_name
from common.git_ops import init_world_git, create_snapshot


def _resolve_templates_dir() -> Path:
    """Resolve template packs dir across dev checkout and installed layouts."""
    candidates = []
    env = os.environ.get("ARS_TEMPLATES_DIR")
    if env:
        candidates.append(Path(env))
    candidates.append(Path(__file__).resolve().parent.parent.parent.parent / "templates")
    candidates.append(Path("/usr/share/ars-arcanum/templates"))
    candidates.append(Path.home() / ".local" / "share" / "ars-arcanum" / "templates")
    for c in candidates:
        if c.is_dir():
            return c
    return candidates[1]


TEMPLATES_SRC_DIR = _resolve_templates_dir()


def scaffold_world_project(world_name: str, genre: str, selected_packs: List[str]) -> Path:
    """
    Generate the complete directory structure for a new world and populate templates.
    Raises OSError on filesystem failures; missing pack IDs are skipped with warning.
    """
    clean_name = "".join(c for c in world_name if c.isalnum() or c in ("-", "_", " ")).strip()
    if not clean_name:
        clean_name = "Aethermoor"

    world_dir = DEFAULT_WORLDS_DIR / clean_name
    try:
        world_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        raise OSError(f"Cannot create world directory {world_dir}: {e}") from e

    # 1. Create all standard subdirectories
    for subdir in WORLD_SUBDIRS:
        try:
            (world_dir / subdir).mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise OSError(f"Cannot create subdirectory {subdir}: {e}") from e

    safe_genre = str(genre).replace('"', "'")[:80]
    # 2. Write master World Bible root README / Index (never overwrite existing)
    index_path = world_dir / "00-World-Bible" / "Index.md"
    if not index_path.exists():
        index_md = f"""---
        title: "World Bible — {clean_name}"
        type: "lore"
        world: "{clean_name}"
        genre: "{safe_genre}"
        status: "active"
        tags: [world-bible, core-index]
        ---

        # The World of {clean_name}

        Welcome to the **{clean_name}** World Bible. This directory serves as your master knowledge repository, structured lore vault, and Obsidian root.

        ## Creative Organization
        - **00-World-Bible**: Character sheets, locations, factions, magic/technology, religions, and session notes.
        - **01-Manuscripts**: Active novels, short fiction, and scene outlines.
        - **02-Maps**: World maps, regional cartography, city battle maps, and custom brushes.
        - **03-Art-Heraldry**: Character concept portraits, vector coats of arms, and custom fonts.
        - **04-Languages**: Conlang lexicons, phonology, and grammar sheets.
        - **05-Timelines**: Chronological timelines and non-linear loop schemas.
        - **06-Genealogy**: Dynastic bloodline trees and noble house records.
        - **07-Publishing**: Typst book typesetting templates, 300 DPI print proofs, and EPUB files.
        - **08-Research**: Clippings, historical references, and scientific notes.
        - **09-Backups**: Encrypted vault archives and automated session logs.
        """
        index_path.write_text(textwrap.dedent(index_md), encoding="utf-8")

    # 3. Copy selected Author Methodology Template Packs
    templates_dest = world_dir / "00-World-Bible" / "Templates"
    try:
        templates_dest.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        raise OSError(f"Cannot create templates dir: {e}") from e

    templates_src = _resolve_templates_dir()
    for pack_id in selected_packs:
        pack_dir = templates_src / pack_id
        if not pack_dir.is_dir():
            print(f"[!] Template pack '{pack_id}' not found in {templates_src}; skipping.")
            continue
        vault_src = pack_dir / "obsidian_vault"
        if not vault_src.is_dir():
            vault_src = pack_dir
        try:
            for item in vault_src.glob("*.md"):
                dest_file = templates_dest / f"[{pack_id}] {item.name}"
                shutil.copy2(item, dest_file)
        except OSError as e:
            print(f"[!] Could not install pack '{pack_id}': {e}")

    # 4. Initialize Git repository
    init_world_git(world_dir)
    create_snapshot(world_dir, message_prefix=f"Initial World Scaffolding ({clean_name})")

    # 5. Set as active world
    set_active_world_name(clean_name)
    return world_dir
