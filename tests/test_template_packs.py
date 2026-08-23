"""
Unit tests for template packs and sample world validation.
"""

from pathlib import Path
from common.lore_parser import parse_frontmatter, extract_world_entities

TEMPLATES_ROOT = Path(__file__).resolve().parent.parent / "templates"
SAMPLE_WORLD_ROOT = Path(__file__).resolve().parent.parent / "sample_world"


def test_template_packs_exist_and_valid():
    packs = [
        "sandersonian_magic",
        "martinian_realism",
        "jordanian_epic",
        "nagatsukian_loop",
        "falcom_ecology",
    ]
    for p in packs:
        p_dir = TEMPLATES_ROOT / p
        assert p_dir.exists(), f"Pack directory missing: {p}"
        vault_dir = p_dir / "obsidian_vault"
        assert vault_dir.exists(), f"Obsidian vault templates missing in {p}"
        for md_file in vault_dir.glob("*.md"):
            content = md_file.read_text(encoding="utf-8")
            fm, body = parse_frontmatter(content)
            assert "title" in fm, f"Missing title frontmatter in {md_file}"
            assert "type" in fm, f"Missing type frontmatter in {md_file}"


def test_sample_world_structure():
    assert SAMPLE_WORLD_ROOT.exists()
    assert (SAMPLE_WORLD_ROOT / "00-World-Bible").exists()
    assert (SAMPLE_WORLD_ROOT / "01-Manuscripts").exists()
    assert (SAMPLE_WORLD_ROOT / "03-Art-Heraldry" / "Heraldry-Sigils" / "House_Vael_Crest.svg").exists()
    assert (SAMPLE_WORLD_ROOT / "04-Languages" / "Elaris_Conlang_Lexicon.md").exists()
    assert (SAMPLE_WORLD_ROOT / "05-Timelines" / "Elaris_Chronology.timeline").exists()

    entities = extract_world_entities(SAMPLE_WORLD_ROOT)
    assert "Lord_Raymond_Vael" in entities
    assert "Lady_Aurelia_Sol" in entities
    assert entities["Lord_Raymond_Vael"].attributes.get("eyes") == "violet"
    assert entities["Lord_Raymond_Vael"].attributes.get("hair") == "silver"
    assert entities["Lady_Aurelia_Sol"].attributes.get("eyes") == "golden"
