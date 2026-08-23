#!/usr/bin/env python3
"""
/usr/local/bin/ars-theme — Ars Arcanum Cross-Desktop Theme Applicator
Applies handcrafted color palettes across XFCE, GTK, Obsidian CSS, FocusWriter, Rofi, and Terminal.
"""

import sys
import shutil
import argparse
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common.config import AVAILABLE_THEMES, get_active_theme, set_active_theme, DEFAULT_WORLDS_DIR, list_worlds
from common.ui_helpers import show_notification

THEME_PALETTES = {
    "grimoire": {
        "name": "Grimoire (Dark Parchment / Fantasy)",
        "bg": "#1a1a2e",
        "fg": "#f5e6c8",
        "accent": "#c9a96e",
        "secondary": "#4a1942",
        "border": "#3d2b1f",
    },
    "astral": {
        "name": "Astral (Deep Space / Sci-Fi)",
        "bg": "#0d1b2a",
        "fg": "#e0e0e0",
        "accent": "#7ec8e3",
        "secondary": "#1b0033",
        "border": "#1b263b",
    },
    "sylvan": {
        "name": "Sylvan (Forest / Mythos)",
        "bg": "#1b2d1b",
        "fg": "#f0ead6",
        "accent": "#d4a017",
        "secondary": "#3e2723",
        "border": "#2d4a2d",
    },
    "obsidian": {
        "name": "Obsidian (Monastic Pitch Black)",
        "bg": "#111111",
        "fg": "#ffffff",
        "accent": "#777777",
        "secondary": "#222222",
        "border": "#333333",
    },
    "ivory": {
        "name": "Ivory (Daylight / Classical Vellum)",
        "bg": "#faf3e0",
        "fg": "#2c1810",
        "accent": "#8b7355",
        "secondary": "#e8dcc8",
        "border": "#d2b48c",
    },
}


def generate_gtk_css(palette: dict) -> str:
    return f"""/* Ars Arcanum Dynamic GTK 3/4 Theme CSS */
@define-color theme_bg_color {palette['bg']};
@define-color theme_fg_color {palette['fg']};
@define-color theme_base_color {palette['bg']};
@define-color theme_text_color {palette['fg']};
@define-color theme_selected_bg_color {palette['accent']};
@define-color theme_selected_fg_color {palette['bg']};
@define-color borders {palette['border']};

window, dialog {{
    background-color: @theme_bg_color;
    color: @theme_fg_color;
}}

textview, entry, list, treeview {{
    background-color: @theme_bg_color;
    color: @theme_fg_color;
    border-color: @borders;
}}

button {{
    background-color: {palette['secondary']};
    color: @theme_fg_color;
    border: 1px solid {palette['accent']};
    border-radius: 4px;
    padding: 6px 12px;
}}

button:hover {{
    background-color: {palette['accent']};
    color: {palette['bg']};
}}

headerbar {{
    background-color: @theme_bg_color;
    border-bottom: 1px solid {palette['accent']};
}}
"""


def generate_obsidian_css(palette: dict) -> str:
    return f"""/* Ars Arcanum Obsidian Theme Snippet */
.theme-dark, .theme-light {{
  --background-primary: {palette['bg']} !important;
  --background-secondary: {palette['secondary']} !important;
  --text-normal: {palette['fg']} !important;
  --text-accent: {palette['accent']} !important;
  --interactive-accent: {palette['accent']} !important;
  --text-muted: {palette['border']} !important;
  --font-family-editor: "EB Garamond", "Libertinus Serif", serif;
}}
"""


def apply_theme(theme_name: str) -> None:
    theme = theme_name.lower()
    if theme not in THEME_PALETTES:
        print(f"[!] Invalid theme '{theme_name}'. Available: {', '.join(AVAILABLE_THEMES)}")
        return

    palette = THEME_PALETTES[theme]
    set_active_theme(theme)

    # 1. Update GTK CSS
    gtk_config_dir = Path.home() / ".config" / "gtk-3.0"
    gtk_config_dir.mkdir(parents=True, exist_ok=True)
    (gtk_config_dir / "gtk.css").write_text(generate_gtk_css(palette), encoding="utf-8")

    # 2. Update Obsidian Vaults snippets
    obsidian_css = generate_obsidian_css(palette)
    for world in list_worlds():
        vault_snippets = DEFAULT_WORLDS_DIR / world / "00-World-Bible" / ".obsidian" / "snippets"
        vault_snippets.mkdir(parents=True, exist_ok=True)
        (vault_snippets / "ars-theme.css").write_text(obsidian_css, encoding="utf-8")

    # 3. Update XFCE theme settings if xfconf is present
    if shutil.which("xfconf-query"):
        try:
            subprocess.run(["xfconf-query", "-c", "xsettings", "-p", "/Net/ThemeName", "-s", f"ars-{theme}"], check=False)
            subprocess.run(["xfconf-query", "-c", "xfwm4", "-p", "/general/theme", "-s", f"ars-{theme}"], check=False)
        except Exception:
            pass

    print(f"[+] Applied Theme: {palette['name']}")
    show_notification("Theme Updated", f"Applied {palette['name']}", urgency="low", icon="preferences-desktop-theme")


def main():
    parser = argparse.ArgumentParser(description="Ars Arcanum Cross-Desktop Theme Applicator")
    parser.add_argument("theme", choices=AVAILABLE_THEMES, nargs="?", help="Theme name to apply")
    parser.add_argument("-l", "--list", action="store_true", help="List all available themes")
    args = parser.parse_args()

    if args.list:
        print("\nAvailable Ars Arcanum Themes:")
        curr = get_active_theme()
        for k, v in THEME_PALETTES.items():
            mark = " (Active)" if k == curr else ""
            print(f"  • {k.ljust(10)} : {v['name']}{mark}")
        print()
        return

    if args.theme:
        apply_theme(args.theme)
    else:
        print(f"Active Theme: {get_active_theme().upper()}")


if __name__ == "__main__":
    main()
