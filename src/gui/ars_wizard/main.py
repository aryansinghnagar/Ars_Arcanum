#!/usr/bin/env python3
"""
/usr/local/bin/ars-wizard — Ars Arcanum World Creation & First-Boot Wizard
A visual multi-step setup wizard for theme selection, tool manifest, template packs, and world scaffolding.
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from common.config import AVAILABLE_THEMES, set_active_theme, get_active_theme
from common.ui_helpers import show_notification
from gui.ars_wizard.scaffold import scaffold_world_project

THEME_DATA = {
    "grimoire": ("Grimoire", "#1a1a2e", "#f5e6c8", "#c9a96e", "Dark Parchment / High Fantasy"),
    "astral": ("Astral", "#0d1b2a", "#e0e0e0", "#7ec8e3", "Deep Space / Hard Sci-Fi"),
    "sylvan": ("Sylvan", "#1b2d1b", "#f0ead6", "#d4a017", "Forest / Elvish Mythos"),
    "obsidian": ("Obsidian", "#111111", "#ffffff", "#777777", "Monastic / Pure Focus Pitch Black"),
    "ivory": ("Ivory", "#faf3e0", "#2c1810", "#8b7355", "Daylight / Classical Manuscript"),
}

TOOL_MANIFEST = [
    ("Brainstorm & Lore", ["Obsidian (World Bible Vault)", "Fantasia Archive (Structured DB)", "Kiwix (Offline Encyclopedia)", "Xournal++ (Lore Sketches)"]),
    ("Outline & Structure", ["novelWriter (Structured Novel Organizer)", "Manuskript (Snowflake Outliner)", "The Timeline Project (Chronology)", "draw.io (Flowcharts & Magic Trees)"]),
    ("Draft & Composition", ["FocusWriter (Distraction-Free Kiosk)", "LibreOffice Writer (Manuscript Revision)", "ghostwriter (Markdown Short Stories)", "Blanket (Soundscapes)"]),
    ("Visuals & Maps", ["Krita (Concept Painting & Maps)", "Inkscape (Heraldry & Vector Sigils)", "Azgaar Fantasy Map Generator", "FontForge (Custom Conlang Fonts)"]),
    ("Linguistics & Press", ["PolyGlot (Conlang Studio)", "GoldenDict-ng (Offline Dictionary)", "Artha (Thesaurus)", "Typst (Ultra-Fast Typesetting Engine)"]),
]

TEMPLATE_PACKS = [
    ("sandersonian_magic", "Hard Magic System Builder (Sandersonian)", "Three Laws of Magic matrices, cosmic chronology sync, terminology linter."),
    ("martinian_realism", "Dynastic Realism Pack (Martinian)", "Medieval travel tables, Inkscape heraldry crests, multi-generational family trees, POV matrix."),
    ("jordanian_epic", "Epic Scale Lore Manager (Jordanian)", "Faction & power tier matrices, lunar/solar calendar cycles, living glossary compiler."),
    ("nagatsukian_loop", "Non-Linear Narrative Engine (Nagatsukian)", "Time-loop checkpoint state tracking, character knowledge matrices, draw.io branching graphs."),
    ("falcom_ecology", "Living World Ecology (Falcom-Grade)", "NPC schedules across story beats, geopolitical treaties, technological & cultural era trackers."),
]


class ArsWizardApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ars Arcanum — World Setup Wizard")
        self.geometry("820x620")
        self.minsize(760, 560)
        self.configure(bg="#1a1a2e")

        self.current_step = 0
        self.selected_theme = tk.StringVar(value="grimoire")
        self.world_name_var = tk.StringVar(value="Aethermoor")
        self.genre_var = tk.StringVar(value="Epic Fantasy")
        self.tool_vars = {}
        self.pack_vars = {}

        self.setup_ui()
        self.show_step(0)

    def setup_ui(self):
        # Header banner
        self.header_frame = tk.Frame(self, bg="#111122", height=70)
        self.header_frame.pack(fill="x", side="top")
        self.header_title = tk.Label(
            self.header_frame,
            text="ARS ARCANUM: THE WRITER'S FORGE",
            font=("Cinzel", 14, "bold"),
            fg="#c9a96e",
            bg="#111122",
        )
        self.header_title.pack(pady=(12, 2))
        self.header_subtitle = tk.Label(
            self.header_frame,
            text="Step 1 of 4: Select Your Visual Aesthetic",
            font=("Helvetica", 10),
            fg="#f5e6c8",
            bg="#111122",
        )
        self.header_subtitle.pack(pady=(0, 8))

        # Content container
        self.container = tk.Frame(self, bg="#1a1a2e")
        self.container.pack(fill="both", expand=True, padx=25, pady=15)

        # Navigation Footer
        self.footer_frame = tk.Frame(self, bg="#111122", height=60)
        self.footer_frame.pack(fill="x", side="bottom")

        self.btn_back = tk.Button(
            self.footer_frame,
            text="← Back",
            command=self.prev_step,
            bg="#2a2a3e",
            fg="#f5e6c8",
            font=("Helvetica", 10),
            padx=15,
            pady=6,
            relief="flat",
        )
        self.btn_back.pack(side="left", padx=20, pady=12)

        self.btn_next = tk.Button(
            self.footer_frame,
            text="Next Step →",
            command=self.next_step,
            bg="#c9a96e",
            fg="#1a1a2e",
            font=("Helvetica", 10, "bold"),
            padx=20,
            pady=6,
            relief="flat",
        )
        self.btn_next.pack(side="right", padx=20, pady=12)

    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def show_step(self, step_idx):
        self.clear_container()
        self.current_step = step_idx
        self.btn_back.config(state="normal" if step_idx > 0 else "disabled")

        if step_idx == 0:
            self.header_subtitle.config(text="Step 1 of 4: Select Your Visual Aesthetic & Color Theme")
            self.btn_next.config(text="Next: Choose Tools →")
            self.render_theme_page()
        elif step_idx == 1:
            self.header_subtitle.config(text="Step 2 of 4: Select Creative Tools & Workflow Modules")
            self.btn_next.config(text="Next: World & Templates →")
            self.render_tools_page()
        elif step_idx == 2:
            self.header_subtitle.config(text="Step 3 of 4: Create Your World & Select Methodology Packs")
            self.btn_next.config(text="Create World & Forge →")
            self.render_world_page()
        elif step_idx == 3:
            self.header_subtitle.config(text="Step 4 of 4: Setup Complete! Ready for the Forge")
            self.btn_next.config(text="Launch The Forge (Welcome App) 🚀")
            self.render_completion_page()

    def render_theme_page(self):
        lbl = tk.Label(
            self.container,
            text="Choose an eye-strain optimized color theme for your creative workstation:",
            font=("Helvetica", 11),
            fg="#f5e6c8",
            bg="#1a1a2e",
        )
        lbl.pack(anchor="w", pady=(0, 15))

        for tid, (tname, bg, fg, accent, desc) in THEME_DATA.items():
            card = tk.Frame(self.container, bg=bg, highlightbackground=accent, highlightthickness=2 if self.selected_theme.get() == tid else 1, padx=12, pady=10)
            card.pack(fill="x", pady=5)

            rb = tk.Radiobutton(
                card,
                text=f"{tname} — {desc}",
                variable=self.selected_theme,
                value=tid,
                command=self.on_theme_selected,
                bg=bg,
                fg=fg,
                selectcolor=bg,
                activebackground=bg,
                activeforeground=accent,
                font=("Helvetica", 11, "bold"),
            )
            rb.pack(side="left")

            preview = tk.Label(card, text="Aa Vellum Preview", bg=accent, fg=bg, font=("Cinzel", 10, "bold"), padx=10, pady=3)
            preview.pack(side="right")

    def on_theme_selected(self):
        set_active_theme(self.selected_theme.get())
        self.show_step(0)

    def render_tools_page(self):
        lbl = tk.Label(
            self.container,
            text="Pre-configured tools grouped by creative workflow phase (all 100% offline):",
            font=("Helvetica", 11),
            fg="#f5e6c8",
            bg="#1a1a2e",
        )
        lbl.pack(anchor="w", pady=(0, 10))

        scroll_canvas = tk.Canvas(self.container, bg="#1a1a2e", highlightthickness=0)
        scroll_frame = tk.Frame(scroll_canvas, bg="#1a1a2e")
        scroll_canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        scroll_canvas.pack(fill="both", expand=True)

        for phase, tools in TOOL_MANIFEST:
            p_lbl = tk.Label(scroll_frame, text=f"◆ {phase}", font=("Helvetica", 11, "bold"), fg="#c9a96e", bg="#1a1a2e")
            p_lbl.pack(anchor="w", pady=(8, 2))

            for tool in tools:
                if tool not in self.tool_vars:
                    self.tool_vars[tool] = tk.BooleanVar(value=True)
                cb = tk.Checkbutton(
                    scroll_frame,
                    text=tool,
                    variable=self.tool_vars[tool],
                    bg="#1a1a2e",
                    fg="#f5e6c8",
                    selectcolor="#111122",
                    activebackground="#1a1a2e",
                    activeforeground="#c9a96e",
                    font=("Helvetica", 10),
                )
                cb.pack(anchor="w", padx=20, pady=1)

    def render_world_page(self):
        form_frame = tk.Frame(self.container, bg="#1a1a2e")
        form_frame.pack(fill="x", pady=(0, 15))

        tk.Label(form_frame, text="World Name:", font=("Helvetica", 10, "bold"), fg="#c9a96e", bg="#1a1a2e").grid(row=0, column=0, sticky="w", pady=4)
        tk.Entry(form_frame, textvariable=self.world_name_var, font=("Helvetica", 11), width=30, bg="#2a2a3e", fg="#f5e6c8", insertbackground="#c9a96e").grid(row=0, column=1, sticky="w", padx=10, pady=4)

        tk.Label(form_frame, text="Primary Genre:", font=("Helvetica", 10, "bold"), fg="#c9a96e", bg="#1a1a2e").grid(row=1, column=0, sticky="w", pady=4)
        tk.Entry(form_frame, textvariable=self.genre_var, font=("Helvetica", 11), width=30, bg="#2a2a3e", fg="#f5e6c8", insertbackground="#c9a96e").grid(row=1, column=1, sticky="w", padx=10, pady=4)

        tk.Label(self.container, text="Select Author Methodology Template Packs:", font=("Helvetica", 11, "bold"), fg="#c9a96e", bg="#1a1a2e").pack(anchor="w", pady=(10, 5))

        for pid, pname, pdesc in TEMPLATE_PACKS:
            if pid not in self.pack_vars:
                self.pack_vars[pid] = tk.BooleanVar(value=True)

            pack_card = tk.Frame(self.container, bg="#22223a", padx=10, pady=6, highlightbackground="#3d2b1f", highlightthickness=1)
            pack_card.pack(fill="x", pady=4)

            cb = tk.Checkbutton(
                pack_card,
                text=pname,
                variable=self.pack_vars[pid],
                bg="#22223a",
                fg="#f5e6c8",
                selectcolor="#111122",
                activebackground="#22223a",
                activeforeground="#c9a96e",
                font=("Helvetica", 10, "bold"),
            )
            cb.pack(anchor="w")

            tk.Label(pack_card, text=pdesc, font=("Helvetica", 9, "italic"), fg="#b0a590", bg="#22223a").pack(anchor="w", padx=25)

    def render_completion_page(self):
        w_name = self.world_name_var.get().strip() or "Aethermoor"
        tk.Label(
            self.container,
            text=f"✨ World '{w_name}' Successfully Initialized! ✨",
            font=("Cinzel", 14, "bold"),
            fg="#c9a96e",
            bg="#1a1a2e",
        ).pack(pady=(20, 10))

        summary = f"""Your workspace has been structured under ~/Worlds/{w_name}/
• 00-World-Bible (Obsidian Vault & Templates)
• 01-Manuscripts (novelWriter & Chapter Outlines)
• 02-Maps, 03-Art-Heraldry, 04-Languages, 05-Timelines
• Local Git Repository Initialized with Auto-Snapshot Protection

Essential Global Shortcuts:
  [Super+Space] Open Workflow Launcher
  [Super+W]     Open Obsidian World Bible
  [Super+D]     Open FocusWriter (Drafting)
  [Super+F]     Engage Extreme Focus Mode (Kiosk)
  [Super+Escape] Exit Focus Ceremony & Log Word Count
  [F1]          Ars Arcanum Help Manual
"""
        lbl = tk.Label(
            self.container,
            text=summary,
            font=("Consolas", 10),
            fg="#f5e6c8",
            bg="#111122",
            justify="left",
            padx=18,
            pady=15,
            relief="groove",
        )
        lbl.pack(fill="both", expand=True, pady=10)

    def next_step(self):
        if self.current_step == 2:
            # Execute scaffolding
            w_name = self.world_name_var.get().strip() or "Aethermoor"
            genre = self.genre_var.get().strip() or "Speculative Fiction"
            selected_packs = [pid for pid, var in self.pack_vars.items() if var.get()]

            try:
                scaffold_world_project(w_name, genre, selected_packs)
                show_notification("World Created", f"Successfully forged '{w_name}'.", urgency="normal")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to scaffold world: {e}")
                return
            self.show_step(3)
        elif self.current_step == 3:
            # Finish wizard and launch welcome app
            self.destroy()
            from gui.ars_welcome.main import ArsWelcomeApp
            app = ArsWelcomeApp()
            app.mainloop()
        else:
            self.show_step(self.current_step + 1)

    def prev_step(self):
        if self.current_step > 0:
            self.show_step(self.current_step - 1)


def main():
    app = ArsWizardApp()
    app.mainloop()


if __name__ == "__main__":
    main()
