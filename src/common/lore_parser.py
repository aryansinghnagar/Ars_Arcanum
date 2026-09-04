"""
Ars Arcanum — Markdown YAML Frontmatter & Lore Consistency Parser
Parses world bible sheets and manuscripts for entity models, continuity checking, and compilation.
"""

import os
import re
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional


def parse_frontmatter(content: str) -> Tuple[Dict[str, Any], str]:
    """
    Extract YAML frontmatter and body from Markdown text.
    Handles standard --- delimited YAML frontmatter blocks.
    """
    frontmatter: Dict[str, Any] = {}
    body = content

    pattern = r"^---\s*\r?\n(.*?)\r?\n---\s*\r?\n?(.*)$"
    match = re.match(pattern, content, re.DOTALL)
    if match:
        raw_yaml, body = match.groups()
        for line in raw_yaml.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if ":" in line:
                key, val = line.split(":", 1)
                key = key.strip()
                val = val.strip()
                if val.startswith("[") and val.endswith("]"):
                    items = [x.strip().strip("'\"") for x in val[1:-1].split(",") if x.strip()]
                    frontmatter[key] = items
                elif val.lower() in ("true", "yes"):
                    frontmatter[key] = True
                elif val.lower() in ("false", "no"):
                    frontmatter[key] = False
                else:
                    try:
                        frontmatter[key] = int(val)
                    except ValueError:
                        try:
                            frontmatter[key] = float(val)
                        except ValueError:
                            frontmatter[key] = val.strip("'\"")

    return frontmatter, body.strip()


def format_frontmatter(metadata: Dict[str, Any], body: str) -> str:
    """Format dictionary metadata into standard YAML frontmatter block preceding body."""
    lines = ["---"]
    for k, v in metadata.items():
        if isinstance(v, list):
            items = [str(x).replace('"', '\\"') for x in v]
            items_str = ", ".join([f'"{x}"' if (" " in x or ":" in x or '"' in x) else x for x in items])
            lines.append(f"{k}: [{items_str}]")
        elif isinstance(v, bool):
            lines.append(f"{k}: {'true' if v else 'false'}")
        elif isinstance(v, (int, float)):
            lines.append(f"{k}: {v}")
        else:
            s = str(v).replace('"', '\\"')
            if "\n" in s or ":" in s or '"' in str(v) or s != str(v).strip():
                lines.append(f'{k}: "{s}"')
            else:
                lines.append(f"{k}: {s}")
    lines.append("---")
    lines.append("")
    lines.append(body.lstrip("\r\n"))
    return "\n".join(lines)


class EntityRecord:
    """Represents a tracked lore entity (character, faction, location, magic item)."""

    def __init__(self, name: str, filepath: Path, entity_type: str = "general"):
        self.name = name
        self.filepath = filepath
        self.entity_type = entity_type
        self.attributes: Dict[str, str] = {}
        self.aliases: List[str] = [name, name.replace("_", " ")]
        self.tags: List[str] = []

    def __repr__(self) -> str:
        return f"<EntityRecord {self.name} ({self.entity_type}): {self.attributes}>"


def _norm_name(s: str) -> str:
    """Canonical form for name matching: underscores/spaces unified, case-insensitive."""
    return str(s).replace("_", " ").casefold().strip()


def _name_variants(name: str) -> List[str]:
    """All spelling variants of an entity name (space/underscore, original case kept)."""
    variants = {name, name.replace("_", " "), name.replace(" ", "_")}
    return [v for v in variants if v]


def extract_world_entities(world_dir: Path) -> Dict[str, EntityRecord]:
    """
    Extract all defined entities and attributes from 00-World-Bible.
    Scans YAML frontmatter and body text for attributes (eyes, hair, title, faction, etc.).
    """
    entities: Dict[str, EntityRecord] = {}
    bible_dir = world_dir / "00-World-Bible"
    if not bible_dir.exists():
        return entities

    for md_file in bible_dir.rglob("*.md"):
        try:
            content = md_file.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue

        name = md_file.stem
        frontmatter, body = parse_frontmatter(content)
        entity_type = frontmatter.get("type", md_file.parent.name.lower())

        record = EntityRecord(name=name, filepath=md_file, entity_type=str(entity_type))
        record.tags = frontmatter.get("tags", []) if isinstance(frontmatter.get("tags"), list) else []
        # Bidirectional aliases: filename with spaces AND underscores, plus title variants
        for variant in _name_variants(name):
            if variant not in record.aliases:
                record.aliases.append(variant)

        if "title" in frontmatter and frontmatter["title"]:
            t_title = str(frontmatter["title"]).strip()
            for variant in _name_variants(t_title):
                if variant not in record.aliases:
                    record.aliases.append(variant)

        # Populate attributes from frontmatter, preserving original case.
        # Comparisons elsewhere use .casefold() so "Violet" matches "violet".
        for k, v in frontmatter.items():
            if k not in ("title", "type", "tags", "world", "project"):
                record.attributes[k.lower()] = str(v)

        # Regex scan body for physical & lore attributes if not in frontmatter
        # (original case preserved; matching is case-insensitive downstream)
        if "eyes" not in record.attributes:
            eye_match = re.search(r"\beyes?:\s*([a-zA-Z][a-zA-Z\-]*)", content, re.IGNORECASE)
            if eye_match:
                record.attributes["eyes"] = eye_match.group(1)

        if "hair" not in record.attributes:
            hair_match = re.search(r"\bhair:\s*([a-zA-Z][a-zA-Z\-]*)", content, re.IGNORECASE)
            if hair_match:
                record.attributes["hair"] = hair_match.group(1)

        if "title" not in record.attributes:
            title_match = re.search(r"\btitle:\s*([a-zA-Z][a-zA-Z\s\-']{1,80})", content, re.IGNORECASE)
            if title_match:
                record.attributes["title"] = title_match.group(1).strip()

        if "faction" not in record.attributes:
            faction_match = re.search(r"\bfaction:\s*([a-zA-Z][a-zA-Z\s\-']{1,80})", content, re.IGNORECASE)
            if faction_match:
                record.attributes["faction"] = faction_match.group(1).strip()

        entities[name] = record
        for alias in record.aliases:
            entities[alias] = record

        # Register custom aliases list if present in frontmatter
        if "aliases" in frontmatter and isinstance(frontmatter["aliases"], list):
            for alias in frontmatter["aliases"]:
                if alias not in record.aliases:
                    record.aliases.append(alias)
                entities[alias] = record

    return entities


def audit_manuscript_consistency(world_dir: Path) -> List[Dict[str, Any]]:
    """
    Cross-checks all manuscript chapters against defined World Bible entities.
    """
    findings: List[Dict[str, Any]] = []
    entities = extract_world_entities(world_dir)
    manuscripts_dir = world_dir / "01-Manuscripts"

    if not manuscripts_dir.exists():
        return findings

    # Dedupe aliased records once (aliases map to the same EntityRecord)
    unique_records: List[EntityRecord] = list({id(r): r for r in entities.values()}.values())
    norm_names = {_norm_name(n) for n in entities}

    for md_file in sorted(manuscripts_dir.rglob("*.md")):
        try:
            content = md_file.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        rel = str(md_file.relative_to(world_dir))

        # Check 1 (per line): broken wiki-links, matched bidirectionally + case-insensitively
        for idx, line in enumerate(content.splitlines(), 1):
            for link in re.findall(r"\[\[(.*?)\]\]", line):
                target = link.split("|")[0].strip()
                if _norm_name(target) not in norm_names:
                    findings.append({
                        "file": rel,
                        "line": idx,
                        "severity": "WARNING",
                        "category": "Broken Lore Link",
                        "message": f"Wiki-link [[{target}]] has no corresponding entry in World Bible.",
                    })

        # Check 2 (whole file, DOTALL): attribute contradictions may span line breaks,
        # e.g. "Lord Raymond stared\nwith bright blue eyes". Line numbers derived
        # from the match offset. Gated on name presence per record for performance.
        for record in unique_records:
            present = any(
                cand and re.search(rf"\b{re.escape(cand)}\b", content, re.IGNORECASE)
                for cand in [record.name] + record.aliases
            )
            if not present:
                continue
            for attr, lore_value, words, label in (
                ("eyes", record.attributes.get("eyes"), ("his", "her", "their", "the", "with", "both"), "Eye color"),
                ("hair", record.attributes.get("hair"), ("his", "her", "their", "the", "with", "long", "short"), "Hair color"),
            ):
                if not lore_value:
                    continue
                for cand in [record.name] + record.aliases:
                    if not cand:
                        continue
                    m = re.search(
                        rf"\b{re.escape(cand)}\b.*?([a-zA-Z][a-zA-Z\-]*)\s+{attr}\b",
                        content, re.IGNORECASE | re.DOTALL,
                    )
                    if m:
                        found = m.group(1)
                        if found.casefold() != lore_value.casefold() and found.casefold() not in words:
                            line_no = content.count("\n", 0, m.start()) + 1
                            findings.append({
                                "file": rel,
                                "line": line_no,
                                "severity": "ERROR",
                                "category": "Attribute Contradiction",
                                "message": f"{label} mismatch for '{cand}': '{found}' vs Lore '{lore_value}' in {record.filepath.name}",
                            })
                        break

    return findings
