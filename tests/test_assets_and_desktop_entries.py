"""
Automated validation of SVG assets, wallpapers, desktop entries, and Calamares modules.
"""

import xml.etree.ElementTree as ET
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
THEMES_DIR = REPO_ROOT / "themes"
CALAMARES_DIR = REPO_ROOT / "calamares"
ICONS_DIR = REPO_ROOT / "build" / "config" / "includes.chroot" / "usr" / "share" / "icons" / "hicolor" / "scalable" / "apps"
APPLICATIONS_DIR = REPO_ROOT / "build" / "config" / "includes.chroot" / "usr" / "share" / "applications"
SAMPLE_WORLD_MAPS = REPO_ROOT / "sample_world" / "02-Maps" / "Regional-Maps"


def test_svg_wallpapers_valid_xml():
    wallpapers = [
        THEMES_DIR / "grimoire" / "background.svg",
        THEMES_DIR / "astral" / "background.svg",
        THEMES_DIR / "sylvan" / "background.svg",
        THEMES_DIR / "obsidian" / "background.svg",
        THEMES_DIR / "ivory" / "background.svg",
    ]
    for w in wallpapers:
        assert w.exists(), f"Missing wallpaper: {w}"
        tree = ET.parse(w)
        root = tree.getroot()
        assert root.tag.endswith("svg")
        assert "viewBox" in root.attrib or ("width" in root.attrib and "height" in root.attrib)


def test_calamares_branding_and_icons():
    assets = [
        CALAMARES_DIR / "branding" / "arsarcanum" / "logo.svg",
        CALAMARES_DIR / "branding" / "arsarcanum" / "icon.svg",
        CALAMARES_DIR / "branding" / "arsarcanum" / "welcome.svg",
    ]
    for a in assets:
        assert a.exists(), f"Missing Calamares asset: {a}"
        tree = ET.parse(a)
        assert tree.getroot().tag.endswith("svg")


def test_custom_app_icons_exist_and_valid():
    icons = [
        ICONS_DIR / "ars-forge.svg",
        ICONS_DIR / "ars-wizard.svg",
        ICONS_DIR / "ars-compile.svg",
        ICONS_DIR / "ars-audit.svg",
        ICONS_DIR / "ars-focus.svg",
        ICONS_DIR / "ars-travel.svg",
    ]
    for ic in icons:
        assert ic.exists(), f"Missing application icon: {ic}"
        tree = ET.parse(ic)
        assert tree.getroot().tag.endswith("svg")


def test_sample_world_regional_map():
    map_svg = SAMPLE_WORLD_MAPS / "Ashmarch_Regional_Map.svg"
    assert map_svg.exists()
    tree = ET.parse(map_svg)
    assert tree.getroot().tag.endswith("svg")


def test_freedesktop_entries():
    desktop_files = [
        APPLICATIONS_DIR / "ars-welcome.desktop",
        APPLICATIONS_DIR / "ars-wizard.desktop",
        APPLICATIONS_DIR / "ars-focus.desktop",
        APPLICATIONS_DIR / "ars-compile.desktop",
        APPLICATIONS_DIR / "ars-audit.desktop",
        APPLICATIONS_DIR / "ars-travel.desktop",
        APPLICATIONS_DIR / "ars-loop.desktop",
        APPLICATIONS_DIR / "ars-help.desktop",
    ]
    for df in desktop_files:
        assert df.exists(), f"Missing desktop file: {df}"
        content = df.read_text(encoding="utf-8")
        assert "[Desktop Entry]" in content
        assert "Name=" in content
        assert "Exec=" in content
        assert "Icon=" in content
        assert "Type=Application" in content
