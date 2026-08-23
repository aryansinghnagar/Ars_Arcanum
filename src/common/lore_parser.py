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
                elif val.isdigit():
                    frontmatter[key] = int(val)
                else:
                    frontmatter[key] = val.strip("'\"")

    return frontmatter, body.strip()


def format_frontmatter(metadata: Dict[str, Any], body: str) -> str:
    """Format dictionary metadata into standard YAML frontmatter block preceding body."""
    lines = ["---"]
    for k, v in metadata.items():
        if isinstance(v, list):
            items_str = ", ".join([f'"{x}"' if " " in str(x) else str(x) for x in v])
            lines.append(f"{k}: [{items_str}]")
        elif isinstance(v, bool):
            lines.append(f"{k}: {'true' if v else 'false'}")
        elif isinstance(v, (int, float)):
            lines.append(f"{k}: {v}")
        else:
            if "\n" in str(v) or ":" in str(v):
                lines.append(f'{k}: "{v}"')
            else:
                lines.append(f"{k}: {v}")
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
        except Exception:
            continue

        name = md_file.stem
        frontmatter, body = parse_frontmatter(content)
        entity_type = frontmatter.get("type", md_file.parent.name.lower())

        record = EntityRecord(name=name, filepath=md_file, entity_type=str(entity_type))
        record.tags = frontmatter.get("tags", []) if isinstance(frontmatter.get("tags"), list) else []

        if "title" in frontmatter and frontmatter["title"]:
            t_title = str(frontmatter["title"]).strip()
            if t_title not in record.aliases:
                record.aliases.append(t_title)

        # Populate attributes from frontmatter
        for k, v in frontmatter.items():
            if k not in ("title", "type", "tags", "world", "project"):
                record.attributes[k.lower()] = str(v).lower()

        # Regex scan body for physical & lore attributes if not in frontmatter
        if "eyes" not in record.attributes:
            eye_match = re.search(r"\beyes?:\s*([a-zA-Z]+)", content, re.IGNORECASE)
            if eye_match:
                record.attributes["eyes"] = eye_match.group(1).lower()

        if "hair" not in record.attributes:
            hair_match = re.search(r"\bhair:\s*([a-zA-Z]+)", content, re.IGNORECASE)
            if hair_match:
                record.attributes["hair"] = hair_match.group(1).lower()

        if "title" not in record.attributes:
            title_match = re.search(r"\btitle:\s*([a-zA-Z\s]+)", content, re.IGNORECASE)
            if title_match:
                record.attributes["title"] = title_match.group(1).strip().lower()

        if "faction" not in record.attributes:
            faction_match = re.search(r"\bfaction:\s*([a-zA-Z\s]+)", content, re.IGNORECASE)
            if faction_match:
                record.attributes["faction"] = faction_match.group(1).strip().lower()

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

    all_entity_names = set(entities.keys())

    for md_file in sorted(manuscripts_dir.rglob("*.md")):
        try:
            content = md_file.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        lines = content.splitlines()
        for idx, line in enumerate(lines, 1):
            # Check 1: Broken wiki-links [[Entity Name]]
            wiki_links = re.findall(r"\[\[(.*?)\]\]", line)
            for link in wiki_links:
                target = link.split("|")[0].strip()
                if target not in all_entity_names and target.replace(" ", "_") not in all_entity_names:
                    findings.append({
                        "file": str(md_file.relative_to(world_dir)),
                        "line": idx,
                        "severity": "WARNING",
                        "category": "Broken Lore Link",
                        "message": f"Wiki-link [[{target}]] has no corresponding entry in World Bible.",
                    })

            # Check 2: Attribute contradictions across known entities
            for name, record in entities.items():
                if name in line:
                    expected_eyes = record.attributes.get("eyes")
                    if expected_eyes:
                        eye_regex = rf"\b{re.escape(name)}.*?([a-zA-Z]+)\s+eyes\b"
                        m = re.search(eye_regex, line, re.IGNORECASE)
                        if m:
                            found_color = m.group(1).lower()
                            if found_color != expected_eyes and found_color not in ("his", "her", "their", "the", "with", "both"):
                                findings.append({
                                    "file": str(md_file.relative_to(world_dir)),
                                    "line": idx,
                                    "severity": "ERROR",
                                    "category": "Attribute Contradiction",
                                    "message": f"Eye color mismatch for '{name}': '{found_color}' vs Lore '{expected_eyes}' in {record.filepath.name}",
                                })

                    expected_hair = record.attributes.get("hair")
                    if expected_hair:
                        hair_regex = rf"\b{re.escape(name)}.*?([a-zA-Z]+)\s+hair\b"
                        m = re.search(hair_regex, line, re.IGNORECASE)
                        if m:
                            found_hair = m.group(1).lower()
                            if found_hair != expected_hair and found_hair not in ("his", "her", "their", "the", "with", "long", "short"):
                                findings.append({
                                    "file": str(md_file.relative_to(world_dir)),
                                    "line": idx,
                                    "severity": "ERROR",
                                    "category": "Attribute Contradiction",
                                    "message": f"Hair color mismatch for '{name}': '{found_hair}' vs Lore '{expected_hair}' in {record.filepath.name}",
                                })

    return findings
