#!/usr/bin/env python3
"""
/usr/local/bin/ars-welcome — Ars Arcanum Welcome Hub ("The Forge")
The primary daily desktop application for speculative fiction authors:
Manages active world projects, one-click quick actions, tutorials, shortcuts, and system controls.
"""

import sys
import shutil
import subprocess
import tkinter as tk
from tkinter import ttk
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from common.config import (
    DEFAULT_WORLDS_DIR,
    list_worlds,
    get_active_world_name,
    set_active_world_name,
    get_active_theme,
    set_active_theme,
    AVAILABLE_THEMES,
)
from common.git_ops import get_commit_history
from common.logger import calculate_world_word_count
from common.ui_helpers import show_notification, show_info_dialog


class ArsWelcomeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("The Forge — Ars Arcanum Creative Workstation")
        self.geometry("920x660")
        self.minsize(860, 580)
        self.configure(bg="#1a1a2e")

        self.theme_name = get_active_theme()
        self.active_world = get_active_world_name()

        self.setup_ui()

    def setup_ui(self):
        # Master Header
        header = tk.Frame(self, bg="#111122", height=75)
        header.pack(fill="x", side="top")

        title_lbl = tk.Label(
            header,
            text="THE FORGE — ARS ARCANUM WORKSTATION",
            font=("Cinzel", 15, "bold"),
            fg="#c9a96e",
            bg="#111122",
        )
        title_lbl.pack(pady=(12, 2))

        world_text = f"Active World: {self.active_world}" if self.active_world else "No World Selected"
        self.subtitle_lbl = tk.Label(
            header,
            text=f"{world_text}  |  Theme: {self.theme_name.capitalize()}  |  Network: Paranoid Encrypted",
            font=("Helvetica", 10),
            fg="#f5e6c8",
            bg="#111122",
        )
        self.subtitle_lbl.pack(pady=(0, 10))

        # Modern Custom Styled Notebook for Tabs
        style = ttk.Style()
        style.theme_use("default")
        style.configure("TNotebook", background="#1a1a2e", borderwidth=0)
        style.configure(
            "TNotebook.Tab",
            background="#2a2a3e",
            foreground="#f5e6c8",
            padding=[15, 8],
            font=("Helvetica", 10, "bold"),
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", "#c9a96e")],
            foreground=[("selected", "#1a1a2e")],
        )

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=15)

        # Build Tabs
        self.tab_worlds = tk.Frame(self.notebook, bg="#1a1a2e")
        self.tab_actions = tk.Frame(self.notebook, bg="#1a1a2e")
        self.tab_learn = tk.Frame(self.notebook, bg="#1a1a2e")
        self.tab_shortcuts = tk.Frame(self.notebook, bg="#1a1a2e")
        self.tab_system = tk.Frame(self.notebook, bg="#1a1a2e")

        self.notebook.add(self.tab_worlds, text="  Your Worlds  ")
        self.notebook.add(self.tab_actions, text="  Quick Actions  ")
        self.notebook.add(self.tab_learn, text="  Learn Workflow  ")
        self.notebook.add(self.tab_shortcuts, text="  Shortcuts  ")
        self.notebook.add(self.tab_system, text="  System & Security  ")

        self.render_tab_worlds()
        self.render_tab_actions()
        self.render_tab_learn()
        self.render_tab_shortcuts()
        self.render_tab_system()

    def render_tab_worlds(self):
        # Clear previous cards (wizard return path calls this repeatedly)
        for child in self.tab_worlds.winfo_children():
            child.destroy()
        # Header & Create Button
        top_bar = tk.Frame(self.tab_worlds, bg="#1a1a2e")
        top_bar.pack(fill="x", pady=10)

        tk.Label(
            top_bar,
            text="World Repositories in ~/Worlds:",
            font=("Helvetica", 12, "bold"),
            fg="#c9a96e",
            bg="#1a1a2e",
        ).pack(side="left")

        btn_new_world = tk.Button(
            top_bar,
            text="+ Create New World",
            command=self.open_world_wizard,
            bg="#c9a96e",
            fg="#1a1a2e",
            font=("Helvetica", 10, "bold"),
            padx=12,
            pady=4,
            relief="flat",
        )
        btn_new_world.pack(side="right")

        # Worlds List Frame
        list_frame = tk.Frame(self.tab_worlds, bg="#1a1a2e")
        list_frame.pack(fill="both", expand=True, pady=5)

        worlds = list_worlds()
        if not worlds:
            tk.Label(
                list_frame,
                text="No world projects found. Click '+ Create New World' to begin your first setting!",
                font=("Helvetica", 11, "italic"),
                fg="#f5e6c8",
                bg="#1a1a2e",
            ).pack(pady=40)
            return

        for w_name in worlds:
            w_path = DEFAULT_WORLDS_DIR / w_name
            word_count = calculate_world_word_count(w_path)
            commits = get_commit_history(w_path, max_count=1)
            last_commit = commits[0]["subject"] if commits else "Initial scaffold"

            card = tk.Frame(list_frame, bg="#22223a", padx=15, pady=12, highlightbackground="#3d2b1f", highlightthickness=1)
            card.pack(fill="x", pady=6)

            info_sub = tk.Frame(card, bg="#22223a")
            info_sub.pack(side="left", fill="both", expand=True)

            w_title = tk.Label(info_sub, text=f"⚔ {w_name}", font=("Cinzel", 12, "bold"), fg="#c9a96e", bg="#22223a")
            w_title.pack(anchor="w")

            meta_lbl = tk.Label(
                info_sub,
                text=f"Total Words: {word_count:,} words  |  Latest Snapshot: {last_commit}",
                font=("Helvetica", 9),
                fg="#d0c5b0",
                bg="#22223a",
            )
            meta_lbl.pack(anchor="w", pady=(2, 0))

            btn_group = tk.Frame(card, bg="#22223a")
            btn_group.pack(side="right")

            btn_select = tk.Button(
                btn_group,
                text="Set Active",
                command=lambda w=w_name: self.select_world(w),
                bg="#3a3a4e",
                fg="#f5e6c8",
                font=("Helvetica", 9),
                padx=8,
                pady=4,
                relief="flat",
            )
            btn_select.pack(side="left", padx=4)

            btn_obsidian = tk.Button(
                btn_group,
                text="World Bible 📖",
                command=lambda w=w_name: self.launch_obsidian(w),
                bg="#4a1942",
                fg="#f5e6c8",
                font=("Helvetica", 9, "bold"),
                padx=8,
                pady=4,
                relief="flat",
            )
            btn_obsidian.pack(side="left", padx=4)

            btn_draft = tk.Button(
                btn_group,
                text="Write Draft ✍",
                command=lambda w=w_name: self.launch_drafting(w),
                bg="#c9a96e",
                fg="#1a1a2e",
                font=("Helvetica", 9, "bold"),
                padx=8,
                pady=4,
                relief="flat",
            )
            btn_draft.pack(side="left", padx=4)

    def select_world(self, w_name: str):
        set_active_world_name(w_name)
        self.active_world = w_name
        self.subtitle_lbl.config(text=f"Active World: {self.active_world}  |  Theme: {self.theme_name.capitalize()}  |  Network: Paranoid Encrypted")
        show_notification("Active World Changed", f"Current world is now '{w_name}'.", urgency="low")

    def open_world_wizard(self):
        try:
            from gui.ars_wizard.main import ArsWizardApp
        except ImportError as e:
            show_info_dialog("Wizard Unavailable", f"Could not load world wizard:\n{e}")
            return
        try:
            wizard = ArsWizardApp()
            wizard.mainloop()
        except Exception as e:
            show_info_dialog("Wizard Error", f"World wizard failed:\n{e}")
        self.active_world = get_active_world_name()
        self.render_tab_worlds()

    def _launch(self, argv: list) -> None:
        try:
            subprocess.Popen(argv, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except (OSError, ValueError) as e:
            show_info_dialog("Launch Failed", f"Could not start {' '.join(argv)}:\n{e}")

    def launch_obsidian(self, world_name: str):
        vault_path = str(DEFAULT_WORLDS_DIR / world_name / "00-World-Bible")
        print(f"[*] Launching Obsidian World Bible: {vault_path}")
        if shutil.which("obsidian"):
            self._launch(["obsidian", vault_path])
        elif shutil.which("flatpak"):
            self._launch(["flatpak", "run", "md.obsidian.Obsidian", vault_path])
        else:
            show_info_dialog("Open World Bible", f"World Bible located at:\n{vault_path}")

    def launch_drafting(self, world_name: str):
        manuscript_path = str(DEFAULT_WORLDS_DIR / world_name / "01-Manuscripts")
        print(f"[*] Launching Drafting Suite: {manuscript_path}")
        if shutil.which("novelwriter"):
            self._launch(["novelwriter", manuscript_path])
        elif shutil.which("focuswriter"):
            self._launch(["focuswriter"])
        else:
            show_info_dialog("Manuscript Drafting", f"Manuscripts located at:\n{manuscript_path}")

    def render_tab_actions(self):
        lbl = tk.Label(
            self.tab_actions,
            text="One-Click Actions for the Active World:",
            font=("Helvetica", 12, "bold"),
            fg="#c9a96e",
            bg="#1a1a2e",
        )
        lbl.pack(anchor="w", pady=(10, 15))

        grid_frame = tk.Frame(self.tab_actions, bg="#1a1a2e")
        grid_frame.pack(fill="both", expand=True)

        actions = [
            ("⚡ Start Extreme Focus Session", "Enter fullscreen kiosk, start Timewarrior, hide panel (Super+F)", self.action_focus, "#c9a96e", "#1a1a2e"),
            ("📚 Compile Manuscript to PDF/EPUB", "Compile chapters via Typst & Pandoc into print-ready proofs", self.action_compile, "#4a1942", "#f5e6c8"),
            ("🔍 Audit Lore & Consistency", "Scan for character eye/hair mismatches and broken wiki-links", self.action_audit, "#2a3a4e", "#f5e6c8"),
            ("💾 Snapshot Git Repository", "Create timestamped offline Git commit across world files (Super+S)", self.action_snapshot, "#2d4a2d", "#f0ead6"),
            ("🗺 Open Map & Concept Canvas", "Launch Krita or Azgaar with world map assets pre-linked", self.action_maps, "#3e2723", "#f5e6c8"),
            ("🔒 3-2-1 BorgBackup Vault", "Create deduplicated encrypted archive or run restore drill", self.action_backup, "#111122", "#c9a96e"),
        ]

        for i, (title, desc, cmd, bg_col, fg_col) in enumerate(actions):
            r, c = divmod(i, 2)
            btn_card = tk.Button(
                grid_frame,
                text=f"{title}\n\n{desc}",
                command=cmd,
                bg=bg_col,
                fg=fg_col,
                font=("Helvetica", 10, "bold"),
                wraplength=340,
                padx=15,
                pady=15,
                relief="groove",
                cursor="hand2",
            )
            btn_card.grid(row=r, column=c, padx=12, pady=10, sticky="nsew")
            grid_frame.grid_columnconfigure(c, weight=1)
            grid_frame.grid_rowconfigure(r, weight=1)

    def action_focus(self):
        try:
            from cli.ars_focus import enter_extreme_mode
            enter_extreme_mode()
        except Exception as e:
            show_info_dialog("Focus Failed", f"Could not enter focus mode:\n{e}")

    def action_compile(self):
        try:
            from cli.ars_compile import compile_project
        except ImportError as e:
            show_info_dialog("Compile Unavailable", f"{e}")
            return
        if self.active_world:
            try:
                ok = compile_project(DEFAULT_WORLDS_DIR / self.active_world, output_format="pdf")
                show_info_dialog("Compilation Complete" if ok else "Compilation Failed",
                                 f"{'Compiled Typst proof for' if ok else 'Failed to compile'} '{self.active_world}'.")
            except Exception as e:
                show_info_dialog("Compilation Failed", f"{e}")
        else:
            show_info_dialog("No World", "Please select an active world first.")

    def action_audit(self):
        try:
            from cli.ars_audit import run_audit
        except ImportError as e:
            show_info_dialog("Audit Unavailable", f"{e}")
            return
        if self.active_world:
            try:
                count = run_audit(DEFAULT_WORLDS_DIR / self.active_world)
            except Exception as e:
                show_info_dialog("Lore Audit Failed", f"{e}")
                return
            if count == 0:
                show_info_dialog("Lore Audit", "Clean! Zero lore contradictions found.")
            else:
                show_info_dialog("Lore Audit", f"Found {count} continuity issues. Check terminal output for details.")

    def action_snapshot(self):
        try:
            from cli.ars_snapshot import run_snapshots
            run_snapshots(target_world=self.active_world)
        except Exception as e:
            show_info_dialog("Snapshot Failed", f"{e}")

    def action_maps(self):
        if shutil.which("krita"):
            self._launch(["krita"])
        elif shutil.which("inkscape"):
            self._launch(["inkscape"])
        else:
            show_info_dialog("Map Editor", "Opening 02-Maps directory...")

    def action_backup(self):
        try:
            from cli.ars_backup import run_backup
            run_backup()
        except Exception as e:
            show_info_dialog("Backup Failed", f"{e}")

    def render_tab_learn(self):
        scroll_canvas = tk.Canvas(self.tab_learn, bg="#1a1a2e", highlightthickness=0)
        scroll_frame = tk.Frame(scroll_canvas, bg="#1a1a2e")
        scroll_canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        scroll_canvas.pack(fill="both", expand=True, padx=10, pady=10)

        phases = [
            ("Phase 1: Brainstorm, Research & Lore", "Obsidian & Fantasia Archive manage your connected World Bible. Store characters, locations, factions, and investiture magic rules with YAML frontmatter."),
            ("Phase 2: Outline & Structural Logic", "Use novelWriter and Manuskript for Snowflake plotting and scene cards. Track multi-character chronological timelines in Timeline Project and bloodlines in Gramps."),
            ("Phase 3: Distraction-Free Drafting", "FocusWriter provides full-screen distraction-free vellum parchment. Blanket supplies ambient soundscapes (rain, tavern, stormy keep) with zero network exposure."),
            ("Phase 4: Cartography & Visual Arts", "Krita paints high-res continent maps with hardware OpenGL acceleration. Inkscape crafts vector heraldry and royal sigils for chapter headers."),
            ("Phase 5: Linguistic Construction & Reference", "PolyGlot constructs phonetic dictionaries and grammar engines. FontForge maps runes and scripts into installable TTF fonts. GoldenDict & Artha provide instant offline lookup."),
            ("Phase 6: Typesetting & Publishing Press", "Typst compiles 150,000 words into 300 DPI print-ready PDFs in sub-250ms with drop caps and running headers. Pandoc and Sigil produce validated EPUB 3 manuscripts."),
        ]

        for p_title, p_desc in phases:
            card = tk.Frame(scroll_frame, bg="#22223a", padx=12, pady=10, highlightbackground="#3d2b1f", highlightthickness=1)
            card.pack(fill="x", pady=6)
            tk.Label(card, text=p_title, font=("Cinzel", 11, "bold"), fg="#c9a96e", bg="#22223a").pack(anchor="w")
            tk.Label(card, text=p_desc, font=("Helvetica", 9), fg="#e0d5c0", bg="#22223a", wraplength=760, justify="left").pack(anchor="w", pady=(3, 0))

    def render_tab_shortcuts(self):
        shortcuts = [
            ("Super + Space", "Open Rofi Workflow Application Launcher"),
            ("Super + W", "Open / Raise Obsidian World Bible"),
            ("Super + D", "Open / Raise FocusWriter (Drafting)"),
            ("Super + N", "Open / Raise novelWriter (Structured Novel)"),
            ("Super + M", "Open / Raise Manuskript (Snowflake Outliner)"),
            ("Super + K", "Open Krita (Concept Painting & Cartography)"),
            ("Super + I", "Open Inkscape (Vector Heraldry & Sigils)"),
            ("Super + T", "Open Timeline Project (Chronological Tracker)"),
            ("Super + G", "Instant GoldenDict-ng Dictionary Popup"),
            ("Ctrl + Alt + W", "Instant Artha Thesaurus Lookup on Highlighted Word"),
            ("Super + F", "Engage Extreme Focus Mode (Kiosk + Timewarrior Timer)"),
            ("Super + Shift + F", "Toggle Do Not Disturb (DND) Mode"),
            ("Super + Escape", "Exit Focus Mode Ceremony (Log Words & Git Commit)"),
            ("Super + S", "Trigger Manual Git Auto-Snapshot"),
            ("Super + B", "Trigger Encrypted BorgBackup Vault"),
            ("F1", "Open Ars Arcanum Help Manual"),
        ]

        tk.Label(self.tab_shortcuts, text="Universal Keyboard Shortcut Matrix:", font=("Helvetica", 12, "bold"), fg="#c9a96e", bg="#1a1a2e").pack(anchor="w", pady=(10, 10))

        tree_frame = tk.Frame(self.tab_shortcuts, bg="#1a1a2e")
        tree_frame.pack(fill="both", expand=True)

        for key, desc in shortcuts:
            row = tk.Frame(tree_frame, bg="#22223a", padx=10, pady=4)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=key.ljust(18), font=("Consolas", 10, "bold"), fg="#c9a96e", bg="#22223a").pack(side="left")
            tk.Label(row, text=desc, font=("Helvetica", 9), fg="#f5e6c8", bg="#22223a").pack(side="left", padx=15)

    def render_tab_system(self):
        tk.Label(self.tab_system, text="System Maintenance & Configuration:", font=("Helvetica", 12, "bold"), fg="#c9a96e", bg="#1a1a2e").pack(anchor="w", pady=(10, 15))

        ctrl_frame = tk.Frame(self.tab_system, bg="#22223a", padx=15, pady=15, highlightbackground="#3d2b1f", highlightthickness=1)
        ctrl_frame.pack(fill="x", pady=6)

        tk.Label(ctrl_frame, text="Active Visual Theme:", font=("Helvetica", 10, "bold"), fg="#c9a96e", bg="#22223a").grid(row=0, column=0, sticky="w", pady=6)

        theme_var = tk.StringVar(value=self.theme_name)
        theme_combo = ttk.Combobox(ctrl_frame, textvariable=theme_var, values=AVAILABLE_THEMES, state="readonly", width=15)
        theme_combo.grid(row=0, column=1, sticky="w", padx=10, pady=6)

        def on_change_theme():
            set_active_theme(theme_var.get())
            from cli.ars_theme import apply_theme
            apply_theme(theme_var.get())
            show_info_dialog("Theme Applied", f"Switched to {theme_var.get().capitalize()}.")

        tk.Button(ctrl_frame, text="Apply Theme", command=on_change_theme, bg="#c9a96e", fg="#1a1a2e", font=("Helvetica", 9, "bold"), padx=10, pady=2, relief="flat").grid(row=0, column=2, padx=10)

        # OS Update Button
        tk.Label(ctrl_frame, text="Operating System Updates:", font=("Helvetica", 10, "bold"), fg="#c9a96e", bg="#22223a").grid(row=1, column=0, sticky="w", pady=10)
        tk.Button(ctrl_frame, text="Run Btrfs-Relayed OS Update", command=self.run_os_update, bg="#3a3a4e", fg="#f5e6c8", font=("Helvetica", 9), padx=10, pady=4, relief="flat").grid(row=1, column=1, columnspan=2, sticky="w", padx=10)

    def run_os_update(self):
        try:
            from cli.ars_update import run_system_update
            run_system_update()
        except Exception as e:
            show_info_dialog("Update Failed", f"{e}")


def main():
    app = ArsWelcomeApp()
    app.mainloop()


if __name__ == "__main__":
    main()
