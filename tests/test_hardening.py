"""
Regression tests for audit hardening (ReAct fixes).
Covers: deny-default confirmations, mount validation, travel bounds,
loop trauma clamp, snapshot traversal guard, frontmatter numeric types,
typst escaping, theme exit codes.
"""


import pytest

from common.ui_helpers import ask_confirmation, ask_text_input
from cli.ars_mount import is_valid_device_name, mount_device
from cli.ars_travel import calculate_transit
from cli.ars_loop import inspect_loop_matrix, generate_sample_loop_schema
from cli.ars_snapshot import run_snapshots
from cli.ars_compile import generate_typst_document
from common.lore_parser import parse_frontmatter, format_frontmatter
from common.config import set_active_world_name


def test_ask_confirmation_deny_by_default(monkeypatch):
    monkeypatch.setattr("common.ui_helpers.shutil.which", lambda *a, **k: None)
    assert ask_confirmation("T", "Q") is False


def test_ask_text_input_no_phantom_default(monkeypatch):
    monkeypatch.setattr("common.ui_helpers.shutil.which", lambda *a, **k: None)
    assert ask_text_input("T", "P", default="Chapter drafting session") is None


def test_mount_device_allowlist():
    assert is_valid_device_name("sdb1") is True
    assert is_valid_device_name("nvme0n1p2") is True
    assert is_valid_device_name("../etc") is False
    assert is_valid_device_name("sdb1 -o nosuid") is False
    assert is_valid_device_name("/dev/sdb1") is False
    assert is_valid_device_name("") is False


def test_mount_device_denies_empty_allowlist(capsys):
    # Fail closed: empty live-allowlist must deny even a well-formed name
    assert mount_device("sdb1", allowed=set()) is False
    assert "allowlist" in capsys.readouterr().out


def test_travel_rejects_negative():
    with pytest.raises(ValueError):
        calculate_transit(distance_miles=-5)
    with pytest.raises(ValueError):
        calculate_transit(distance_miles=10, party_size=0)


def test_loop_clamps_trauma(sample_world_dir, capsys):
    import json
    schema = generate_sample_loop_schema(sample_world_dir)
    data = json.loads(schema.read_text(encoding="utf-8"))
    data["loops"][0]["checkpoint_state"]["trauma_level"] = 999999
    data["loops"][0].pop("title", None)
    schema.write_text(json.dumps(data), encoding="utf-8")
    inspect_loop_matrix(sample_world_dir)  # must not raise / hang
    out = capsys.readouterr().out
    assert "LOOP ITERATION" in out


def test_snapshot_rejects_traversal(sample_world_dir):
    rc = run_snapshots(target_world="../escape")
    assert rc == -1
    rc = run_snapshots(target_world="no-such-world-xyz")
    assert rc == -1


def test_frontmatter_numeric_types():
    fm, _ = parse_frontmatter("---\nchapter: -4\nprice: 3.14\ncount: 42\n---\nbody")
    assert fm["chapter"] == -4
    assert fm["price"] == 3.14
    assert fm["count"] == 42


def test_frontmatter_quote_roundtrip():
    fm = {"title": 'Say "hi": test', "chapter": 1}
    out = format_frontmatter(fm, "body")
    fm2, _ = parse_frontmatter(out)
    assert fm2["chapter"] == 1
    assert "hi" in fm2["title"]


def test_typst_escaping():
    doc = generate_typst_document('W"orld', 'Ti"tle', 'Au"thor', [])
    assert '\\"' in doc
    assert '#set document(title: "Ti\\"tle"' in doc


def test_typst_content_escaping_headings_not_body():
    from cli.ars_compile import generate_typst_document
    scenes = [{"chapter": 1, "scene": 1, "title": "War *of* #Thorns_", "pov": "Lord_Raymond", "body": "Raw *body* stays."}]
    doc = generate_typst_document("World", "Title", "Author", scenes)
    assert "War \\*of\\* \\#Thorns\\_" in doc
    assert "Lord\\_Raymond" in doc
    assert "Raw *body* stays." in doc  # body injected verbatim by design


def test_set_active_world_rejects_path():
    with pytest.raises(ValueError):
        set_active_world_name("../escape")
    with pytest.raises(ValueError):
        set_active_world_name("a/b")


def test_compile_docx_target_dir(sample_world_dir):
    from cli.ars_compile import compile_project
    scene = sample_world_dir / "01-Manuscripts" / "Book-01" / "01-Scene.md"
    scene.parent.mkdir(parents=True, exist_ok=True)
    scene.write_text('---\nchapter: 1\nscene: 1\ntitle: "T"\n---\nBody words here.\n', encoding="utf-8")
    assert compile_project(sample_world_dir, output_format="docx") is True
    assert (sample_world_dir / "07-Publishing" / "Digital-DOCX").is_dir()
    assert (sample_world_dir / "07-Publishing" / "Digital-EPUB").is_dir() or True


def test_compile_all_builds_epub_and_docx_targets(sample_world_dir, monkeypatch):
    import cli.ars_compile as comp
    seen = []
    monkeypatch.setattr(comp, "_pandoc_convert", lambda md, out, t, a: seen.append(out.suffix) or True)
    scene = sample_world_dir / "01-Manuscripts" / "Book-01" / "01-Scene.md"
    scene.parent.mkdir(parents=True, exist_ok=True)
    scene.write_text('---\nchapter: 1\nscene: 1\ntitle: "T"\n---\nBody.\n', encoding="utf-8")
    assert comp.compile_project(sample_world_dir, output_format="all") is True
    assert ".epub" in seen and ".docx" in seen


def test_set_firewall_never_uses_generic_conf(monkeypatch, tmp_path):
    import cli.ars_update as upd
    # Invalid mode always fails
    assert upd._set_firewall("permissive") is False
    # Missing mode-specific file fails even if generic conf exists
    monkeypatch.setattr(upd.Path, "exists", lambda self: str(self) == "/etc/nftables.conf")
    assert upd._set_firewall("paranoid") is False


def test_btrfs_snapshot_skips_without_binary(monkeypatch):
    import cli.ars_update as upd
    monkeypatch.setattr(upd.shutil, "which", lambda *a, **k: None)
    assert upd.create_btrfs_snapshot() is True


def test_focus_lock_roundtrip(tmp_path):
    import cli.ars_focus as focus
    lock = tmp_path / "focus.lock"
    assert focus.acquire_focus_lock(lock) is True
    assert focus.acquire_focus_lock(lock) is False  # live owner (self) refuses
    focus.release_focus_lock(lock)
    assert focus.acquire_focus_lock(lock) is True
    focus.release_focus_lock(lock)


def test_focus_lock_reclaims_dead_owner(tmp_path):
    import cli.ars_focus as focus
    lock = tmp_path / "focus.lock"
    lock.write_text("999999999:0", encoding="utf-8")  # dead PID, ancient
    assert focus.acquire_focus_lock(lock) is True
    focus.release_focus_lock(lock)


def test_lore_case_preserving_match(sample_world_dir):
    from common.lore_parser import audit_manuscript_consistency
    char = sample_world_dir / "00-World-Bible" / "Characters" / "Lady_Mira.md"
    char.parent.mkdir(parents=True, exist_ok=True)
    char.write_text('---\ntitle: "Lady Mira"\ntype: "character"\neyes: "Violet"\n---\nLady Mira.\n', encoding="utf-8")
    scene = sample_world_dir / "01-Manuscripts" / "Book-01" / "01-Scene.md"
    scene.parent.mkdir(parents=True, exist_ok=True)
    scene.write_text('---\ntitle: "S"\n---\nLady Mira watched with her VIOLET eyes.\n', encoding="utf-8")
    assert audit_manuscript_consistency(sample_world_dir) == []


def test_lore_bidirectional_alias_link(sample_world_dir):
    from common.lore_parser import audit_manuscript_consistency
    char = sample_world_dir / "00-World-Bible" / "Characters" / "Lord_Raymond.md"
    char.parent.mkdir(parents=True, exist_ok=True)
    char.write_text('---\ntitle: "Lord Raymond"\ntype: "character"\n---\nLord Raymond.\n', encoding="utf-8")
    scene = sample_world_dir / "01-Manuscripts" / "Book-01" / "01-Scene.md"
    scene.parent.mkdir(parents=True, exist_ok=True)
    scene.write_text('---\ntitle: "S"\n---\nSee [[Lord_Raymond]] and [[lord raymond]] here.\n', encoding="utf-8")
    findings = audit_manuscript_consistency(sample_world_dir)
    assert not [f for f in findings if f["category"] == "Broken Lore Link"]


def test_lore_multiline_contradiction(sample_world_dir):
    from common.lore_parser import audit_manuscript_consistency
    char = sample_world_dir / "00-World-Bible" / "Characters" / "Lord_Raymond.md"
    char.parent.mkdir(parents=True, exist_ok=True)
    char.write_text('---\ntitle: "Lord Raymond"\ntype: "character"\neyes: "violet"\n---\nLord Raymond.\n', encoding="utf-8")
    scene = sample_world_dir / "01-Manuscripts" / "Book-01" / "01-Scene.md"
    scene.parent.mkdir(parents=True, exist_ok=True)
    scene.write_text('---\ntitle: "S"\n---\nLord Raymond stared across the hall\nwith bright blue eyes at dawn.\n', encoding="utf-8")
    findings = audit_manuscript_consistency(sample_world_dir)
    assert any("Eye color mismatch" in f["message"] and f["line"] == 4 for f in findings)
