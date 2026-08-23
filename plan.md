# Ars Arcanum — Execution Plan & Roadmap

## 1. Linked Workstreams & Milestones

- **Workstream 1: Repository & Substrate Initialization**
  - [x] Milestone 1.1: Canonical operating file pack (`project.md`, `plan.md`, `tasks.md`, `knowledge.md`, `decisions.md`, `status.md`, `handoff.md`, `FAILURE.md`)
  - [ ] Milestone 1.2: Complete directory skeleton scaffold

- **Workstream 2: Security & Confinement Layer**
  - [ ] Milestone 2.1: `sysctl` kernel hardening profile (`99-ars-security.conf`)
  - [ ] Milestone 2.2: `nftables` rulesets (`paranoid.nft` & `standard.nft`)
  - [ ] Milestone 2.3: AppArmor profile suite for creative applications
  - [ ] Milestone 2.4: USBGuard policy and `udev` no-automount rules
  - [ ] Milestone 2.5: APT package exclusion pinning (`00-ars-exclusions.pref`)

- **Workstream 3: The `ars-*` Core Engine & CLI Tool Suite**
  - [ ] Milestone 3.1: Foundational common library (`src/common/`)
  - [ ] Milestone 3.2: Focus Controller (`ars-focus` with DND & Extreme Kiosk modes)
  - [ ] Milestone 3.3: Git Auto-Snapshotter (`ars-snapshot`)
  - [ ] Milestone 3.4: Universal Book Compiler (`ars-compile` with Typst & Pandoc)
  - [ ] Milestone 3.5: Manuscript Consistency & Lore Auditor (`ars-audit`)
  - [ ] Milestone 3.6: Worldbuilder Travel Calculator (`ars-travel`)
  - [ ] Milestone 3.7: Non-Linear Loop & Knowledge Tracker (`ars-loop`)
  - [ ] Milestone 3.8: Theme Applicator (`ars-theme`)
  - [ ] Milestone 3.9: 3-2-1 Encrypted Backup Engine (`ars-backup`)
  - [ ] Milestone 3.10: System Updater, USB Mounter, Extension Manager, and Help Launcher (`ars-update`, `ars-mount`, `ars-extensions`, `ars-help`)

- **Workstream 4: Graphical User Interfaces (PyQt6 / GTK)**
  - [ ] Milestone 4.1: First-Boot World Creation Wizard (`ars-wizard`)
  - [ ] Milestone 4.2: "The Forge" Desktop Control Hub (`ars-welcome`)

- **Workstream 5: Aesthetic Design & Visual Themes**
  - [ ] Milestone 5.1: Grimoire (Default Dark Parchment / Fantasy)
  - [ ] Milestone 5.2: Astral (Deep Space / Sci-Fi)
  - [ ] Milestone 5.3: Sylvan (Forest / Mythos)
  - [ ] Milestone 5.4: Obsidian (Monastic Pitch Black)
  - [ ] Milestone 5.5: Ivory (Daylight / Classical Manuscript)

- **Workstream 6: Author Methodology Template Packs & Sample World**
  - [ ] Milestone 6.1: Sandersonian Hard Magic Builder
  - [ ] Milestone 6.2: Martinian Dynastic Realism Pack
  - [ ] Milestone 6.3: Jordanian Epic Scale Lore Manager
  - [ ] Milestone 6.4: Nagatsukian Non-Linear Narrative Engine
  - [ ] Milestone 6.5: Falcom Living World Ecology
  - [ ] Milestone 6.6: Pre-installed "World of Elaris" Reference Project

- **Workstream 7: Built-in Help System & Typst Book Manual**
  - [ ] Milestone 7.1: Offline HTML/CSS Help Browser (`docs/help_html/`)
  - [ ] Milestone 7.2: Complete Typst Source Book Manual (`docs/typst_manual/Ars-Arcanum-Manual.typ`)

- **Workstream 8: Debian Live-Build Configuration & Calamares Installer**
  - [ ] Milestone 8.1: Package lists (`config/package-lists/*.list.chroot`)
  - [ ] Milestone 8.2: Live-build chroot hooks and includes overlays
  - [ ] Milestone 8.3: Calamares installer configuration & custom branding/modules

- **Workstream 9: Automated Verification & Evaluation Suite**
  - [ ] Milestone 9.1: Unit tests for all `ars-*` CLI tools
  - [ ] Milestone 9.2: GUI component tests
  - [ ] Milestone 9.3: Template pack schema validation
  - [ ] Milestone 9.4: Typst compilation speed benchmarks
  - [ ] Milestone 9.5: Security syntax and policy linting
