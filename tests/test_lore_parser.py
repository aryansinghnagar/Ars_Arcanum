"""
Unit tests for lore_parser.py and continuity auditing.
"""

from common.lore_parser import (
    parse_frontmatter,
    format_frontmatter,
    audit_manuscript_consistency,
)


def test_parse_and_format_frontmatter():
    sample_text = """---
title: "The Fall of Valdane"
type: "scene"
chapter: 4
scene: 2
pov_character: "Lord Raymond"
tags: ["battle", "magic"]
---

The siege had begun at dusk."""

    fm, body = parse_frontmatter(sample_text)
    assert fm["title"] == "The Fall of Valdane"
    assert fm["chapter"] == 4
    assert fm["scene"] == 2
    assert fm["pov_character"] == "Lord Raymond"
    assert "battle" in fm["tags"]
    assert "The siege had begun at dusk." in body

    # Test roundtrip formatting
    reformatted = format_frontmatter(fm, body)
    fm2, body2 = parse_frontmatter(reformatted)
    assert fm2["title"] == fm["title"]
    assert fm2["chapter"] == fm["chapter"]
    assert body2.strip() == body.strip()


def test_audit_manuscript_contradictions(sample_world_dir):
    # 1. Create character lore file with violet eyes
    char_file = sample_world_dir / "00-World-Bible" / "Characters" / "Lord_Raymond.md"
    char_file.parent.mkdir(parents=True, exist_ok=True)
    char_file.write_text("""---
title: "Lord Raymond"
type: "character"
eyes: "violet"
hair: "silver"
---
Lord Raymond is the High Warden.
""", encoding="utf-8")

    # 2. Create clean scene
    scene1 = sample_world_dir / "01-Manuscripts" / "Book-01" / "01-Scene.md"
    scene1.parent.mkdir(parents=True, exist_ok=True)
    scene1.write_text("""---
title: "Clean Scene"
---
Lord Raymond surveyed the field with his violet eyes.
""", encoding="utf-8")

    findings_clean = audit_manuscript_consistency(sample_world_dir)
    assert len(findings_clean) == 0

    # 3. Create contradicting scene (blue eyes instead of violet)
    scene2 = sample_world_dir / "01-Manuscripts" / "Book-01" / "02-Scene.md"
    scene2.write_text("""---
title: "Contradicting Scene"
---
Lord Raymond stared with bright blue eyes at the messenger.
""", encoding="utf-8")

    findings_mismatch = audit_manuscript_consistency(sample_world_dir)
    assert len(findings_mismatch) >= 1
    assert any("Eye color mismatch" in f["message"] for f in findings_mismatch)
