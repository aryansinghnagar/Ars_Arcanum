// Ars Arcanum Operating System Complete Manual & Reference Guide
// Compiled via Typst

#set document(
  title: "Ars Arcanum: Complete System & Operating Manual",
  author: "The Ars Arcanum Project",
)

#set page(
  paper: "a4",
  margin: (top: 2.5cm, bottom: 2.5cm, inside: 3cm, outside: 2.5cm),
  header: align(center)[
    #text(8pt, font: "Cinzel", tracking: 0.15em)[
      #smallcaps("Ars Arcanum — The Writer's Forge Manual")
    ]
  ],
  footer: [
    #align(center)[#counter(page).display()]
  ]
)

#set text(font: "EB Garamond", size: 11pt, lang: "en")
#set par(justify: true, leading: 0.75em, first-line-indent: 1.5em)

// Cover Page
#align(center + horizon)[
  #text(32pt, font: "Cinzel", weight: "bold", fill: rgb("#c9a96e"))[ARS ARCANUM] \
  #v(0.8em)
  #text(16pt, font: "Cinzel", fill: rgb("#1a1a2e"))[THE WRITER'S FORGE. THE WORLDBUILDER'S OS.] \
  #v(2.5em)
  #text(12pt, style: "italic")[A Complete Architectural & Operational Manual for Speculative Fiction Authors] \
  #v(4em)
  #text(10pt)[Debian 13 (Trixie) Appliance • Vault-Grade Security • Distraction-Eliminated]
]
#pagebreak()

// Table of Contents
#outline(title: [Table of Contents], depth: 2, indent: 1.5em)
#pagebreak()

= Part I: Philosophy & System Identity

== 1.1 The Five Foundational Directives
Ars Arcanum is engineered as an immutable creative instrument rather than a general-purpose desktop operating system.

1. *The Machine is an Instrument, Not an Environment*: Every daemon, script, and UI element exists solely to serve narrative worldbuilding and long-form prose composition.
2. *Distraction Elimination by Construction*: Web browsers, video decoders, streaming media, and social chat clients are permanently omitted at the package manifest level.
3. *Vault-Grade Security*: Full-disk LUKS2 encryption with memory-hard Argon2id KDF, AppArmor mandatory access control, and default-drop `nftables` packet filtering guarantee manuscript integrity.
4. *Open Formats & Zero Lock-In*: Narrative assets are stored strictly in plain text Markdown with YAML frontmatter, Typst markup, SVG, PNG, and XML/JSON versioned by local Git.
5. *Unified Toolchain Cohesion*: Cross-application schemas, shared project directories, and automated compiler pipelines bind isolated creative tools into a single forge.

= Part II: Security & Confinement Control Plane

== 2.1 LUKS2 Argon2id Encryption & zram Swap
All user world repositories in `~/Worlds` reside within an encrypted container. Swap space is maintained entirely in compressed RAM via `zram` to prevent plaintext pages from leaking to NVMe storage.

== 2.2 AppArmor Sandboxing & Network Containment
Every creative binary runs under an enforced AppArmor profile restricting read/write access exclusively to `~/Worlds/**` while denying network socket creation (`deny network inet, deny network inet6`).

= Part III: The 6 Creative Workflow Arcs

== 3.1 Phase 1: Brainstorming & World Bible
- *Obsidian Vault*: Connected-notes knowledge base, graph visualization, and Dataview query tables.
- *Fantasia Archive*: Offline structured database for character dossiers, artifacts, and settlement sheets.

== 3.2 Phase 2: Outlining & Narrative Logic
- *novelWriter & Manuskript*: Snowflake plotting, scene synopses, and viewpoint balance matrices.
- *The Timeline Project*: Interactive multi-arc chronological tracking with custom lunar/solar calendars.

== 3.3 Phase 3: Drafting & Composition
- *FocusWriter*: Fullscreen distraction-free vellum kiosk with customizable word count targets.
- *Blanket*: Offline ambient soundscape player (Medieval study, starship bridge, rainstorm).

== 3.4 Phase 4: Visuals & Cartography
- *Krita*: Hardware-accelerated OpenGL digital painting for regional and planetary maps.
- *Inkscape*: Vector heraldic sigils, banners, and chapter headpiece illustrations.

== 3.5 Phase 5: Linguistics & Reference
- *PolyGlot*: Complete conlang construction with IPA phonology and declension generators.
- *FontForge*: Custom runic and alien script font creation, auto-installed to `~/.local/share/fonts/`.

== 3.6 Phase 6: Typesetting & Publishing Press
- *Typst*: High-speed native Rust typesetting engine producing 300 DPI print-ready proofs in milliseconds.
- *Pandoc & Sigil*: Clean document conversion into validated EPUB 3 and DOCX formats.

= Part IV: The ars-\* Tool Suite Reference

#table(
  columns: (1.5fr, 1.2fr, 2.5fr),
  align: (left, left, left),
  table.header([*Command*], [*Access*], [*Function*]),
  [`ars-focus [dnd|extreme|off]`], [`Super+F`], [Coordinates Dunst notifications, panel autohide, Timewarrior.],
  [`ars-snapshot [world]`], [`Super+S`], [Automated local Git snapshot across active world projects.],
  [`ars-compile [world]`], [Desktop Icon], [Compiles Markdown drafts to Typst print PDFs or EPUBs.],
  [`ars-audit [world]`], [Welcome App], [Continuity linter checking character eyes, hair, and lore links.],
  [`ars-travel <miles>`], [Welcome App], [Realistic medieval & sci-fi transit time and supply calculator.],
  [`ars-loop [world]`], [Welcome App], [Non-linear time loop and character knowledge graph tracker.],
  [`ars-theme [name]`], [Welcome App], [Applies unified color palettes across XFCE, GTK, and Obsidian.],
  [`ars-backup [-d]`], [`Super+B`], [3-2-1 BorgBackup encrypted vault creation & restore drills.],
  [`ars-update`], [Welcome App], [Pre-update Btrfs snapshotting and firewall-relayed package update.],
  [`ars-wizard`], [First Boot], [Multi-step world creation and template pack scaffolding.]
)

= Part V: Universal Keyboard Shortcut Matrix

#table(
  columns: (1fr, 2fr),
  align: (left, left),
  table.header([*Shortcut*], [*Action*]),
  [`Super + Space`], [Open Rofi Workflow Application Launcher],
  [`Super + W`], [Open / Focus Obsidian World Bible],
  [`Super + D`], [Open / Focus FocusWriter Drafting Kiosk],
  [`Super + N`], [Open / Focus novelWriter Structured Project],
  [`Super + M`], [Open / Focus Manuskript Snowflake Planner],
  [`Super + K`], [Open Krita Concept Painting & Cartography],
  [`Super + I`], [Open Inkscape Vector Heraldry & Sigils],
  [`Super + T`], [Open Timeline Project Chronological Tracker],
  [`Super + G`], [Instant GoldenDict-ng Offline Dictionary Popup],
  [`Ctrl + Alt + W`], [Instant Artha Thesaurus Lookup on Selected Word],
  [`Super + F`], [Engage Extreme Focus Mode (Kiosk + Timewarrior)],
  [`Super + Shift + F`], [Toggle Do Not Disturb (DND) Mode],
  [`Super + Escape`], [Exit Focus Mode (Ceremony, Word Count Log, Git Snapshot)],
  [`Super + S`], [Trigger Manual Git Auto-Snapshot],
  [`Super + B`], [Trigger Encrypted BorgBackup Vault Snapshot],
  [`F1`], [Open Ars Arcanum Offline Help System]
)
