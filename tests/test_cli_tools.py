"""
Unit tests for Ars Arcanum CLI tool suite.
"""

from pathlib import Path
from common.config import list_worlds, get_active_theme, set_active_theme
from common.git_ops import create_snapshot, get_commit_history
from common.logger import calculate_world_word_count, log_writing_session
from cli.ars_travel import calculate_transit
from cli.ars_loop import generate_sample_loop_schema, export_drawio_timeline
from cli.ars_compile import collect_manuscript_chapters, generate_typst_document


def test_git_snapshot_and_history(sample_world_dir):
    test_note = sample_world_dir / "00-World-Bible" / "Note1.md"
    test_note.write_text("Some lore thoughts", encoding="utf-8")

    res = create_snapshot(sample_world_dir, message_prefix="Test Commit")
    assert res["success"] is True
    assert res["committed"] is True
    assert res["hash"] != ""

    history = get_commit_history(sample_world_dir, max_count=5)
    assert len(history) >= 1
    assert "Test Commit" in history[0]["subject"]


def test_logger_and_word_count(sample_world_dir):
    scene_file = sample_world_dir / "01-Manuscripts" / "Book-01" / "Scene1.md"
    scene_file.parent.mkdir(parents=True, exist_ok=True)
    scene_file.write_text("""---
title: "Test Scene"
---
One two three four five six seven eight nine ten words.
""", encoding="utf-8")

    count = calculate_world_word_count(sample_world_dir)
    assert count == 11

    log_writing_session(sample_world_dir, duration_minutes=25.0, words_written=500, notes="Unit test run")
    log_path = sample_world_dir / "09-Backups" / "session_logs.md"
    assert log_path.exists()
    content = log_path.read_text(encoding="utf-8")
    assert "500" in content
    assert "Unit test run" in content


def test_travel_calculator():
    res = calculate_transit(distance_miles=100.0, mode="infantry", terrain="plains", weather="clear", party_size=4)
    assert res["distance"] == 100.0
    assert res["effective_speed_mpd"] == 20.0
    assert res["days"] == 5.0
    assert res["camp_stops"] == 5

    res_mountains = calculate_transit(distance_miles=100.0, mode="infantry", terrain="mountains", weather="clear", party_size=4)
    assert res_mountains["days"] > res["days"]


def test_loop_matrix_and_drawio(sample_world_dir):
    schema_path = generate_sample_loop_schema(sample_world_dir)
    assert schema_path.exists()

    xml_path = export_drawio_timeline(sample_world_dir)
    assert xml_path.exists()
    assert "<mxfile" in xml_path.read_text(encoding="utf-8")


def test_compile_typst_document(sample_world_dir):
    scene = sample_world_dir / "01-Manuscripts" / "Book-01" / "01-Scene.md"
    scene.parent.mkdir(parents=True, exist_ok=True)
    scene.write_text("""---
chapter: 1
scene: 1
title: "The Battle of Valdane"
pov_character: "Lord Raymond"
---
The armies collided in thunder.
""", encoding="utf-8")

    scenes = collect_manuscript_chapters(sample_world_dir / "01-Manuscripts")
    assert len(scenes) == 1
    assert scenes[0]["title"] == "The Battle of Valdane"

    typst_doc = generate_typst_document("TestAethermoor", "Book-01", "Author", scenes)
    assert "The Battle of Valdane" in typst_doc
    assert "The armies collided in thunder." in typst_doc
    assert 'font: "Cinzel"' in typst_doc


def test_theme_settings(temp_world_env):
    import common.config as cfg
    # Isolated: temp_world_env monkeypatches DEFAULT_CONFIG_DIR
    set_active_theme("sylvan")
    assert get_active_theme() == "sylvan"
    assert (cfg.DEFAULT_CONFIG_DIR / "active_theme.txt").exists()
    set_active_theme("grimoire")
    assert get_active_theme() == "grimoire"
