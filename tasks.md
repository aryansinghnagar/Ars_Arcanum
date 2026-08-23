# Master Task Graph & Definition of Done (DoD)

## Active Momentum Queues

### `now` (Completed Phase)
- [x] Task 1.1: Initialize canonical operating file pack (`project.md`, `plan.md`, `tasks.md`, `knowledge.md`, `decisions.md`, `status.md`, `handoff.md`, `FAILURE.md`)
- [x] Task 1.2: Scaffold directory tree (`build/`, `calamares/`, `src/`, `themes/`, `templates/`, `sample_world/`, `security/`, `docs/`, `tests/`)
- [x] Task 2.1: Write `security/sysctl/99-ars-security.conf`
- [x] Task 2.2: Write `security/nftables/paranoid.nft`, `standard.nft`, `airplane.nft`
- [x] Task 2.3: Write `security/apparmor/` profiles for all creative applications
- [x] Task 2.4: Write `security/udev/99-no-automount.rules` & `security/usbguard/rules.conf`
- [x] Task 2.5: Write APT package exclusion preference `build/config/apt/preferences.d/00-ars-exclusions.pref`
- [x] Task 3.1: Implement `src/common/` (`config.py`, `lore_parser.py`, `git_ops.py`, `logger.py`, `ui_helpers.py`, `__init__.py`)
- [x] Task 3.2: Implement `src/cli/ars_focus.py` (DND, Extreme Focus kiosk, Timewarrior, Dunst pause, Exit Ceremony)
- [x] Task 3.3: Implement `src/cli/ars_snapshot.py` (Local Git auto-snapshotting)
- [x] Task 3.4: Implement `src/cli/ars_compile.py` (Typst 300 DPI PDF & Pandoc EPUB 3 compiler)
- [x] Task 3.5: Implement `src/cli/ars_audit.py` (Continuity & attribute mismatch linter)
- [x] Task 3.6: Implement `src/cli/ars_travel.py` (Realistic medieval/sci-fi transit calculator)
- [x] Task 3.7: Implement `src/cli/ars_loop.py` (Non-linear timeline & loop state tracker + draw.io XML)
- [x] Task 3.8: Implement `src/cli/ars_theme.py` (Cross-desktop theme switcher)
- [x] Task 3.9: Implement `src/cli/ars_backup.py` (3-2-1 encrypted BorgBackup engine & drill tests)
- [x] Task 3.10: Implement `src/cli/ars_mount.py`, `ars_update.py`, `ars_extensions.py`, `ars_help.py`
- [x] Task 4.1: Implement `src/gui/ars_wizard/` (Theme preview, tool manifest, template picker, world scaffolding)
- [x] Task 4.2: Implement `src/gui/ars_welcome/` ("The Forge" daily hub: worlds, quick actions, learn, shortcuts, system)
- [x] Task 5.1: Package 5 complete visual themes with 1080p SVG wallpapers & custom desktop icons
- [x] Task 6.1: Author 5 methodology template packs (`sandersonian_magic`, `martinian_realism`, `jordanian_epic`, `nagatsukian_loop`, `falcom_ecology`)
- [x] Task 6.2: Build complete "World of Elaris" reference project with vector cartography (`sample_world/`)
- [x] Task 7.1: Build offline HTML/CSS help system (`docs/help_html/`) & Typst book manual (`docs/typst_manual/`)
- [x] Task 7.2: Bundle Lightweight Reference Pack (Kiwix ZIM 937MB + 5 Worldbuilder Classics)
- [x] Task 8.1: Configure Debian `live-build` manifests, chroot hooks, and container runner (`build/`)
- [x] Task 8.2: Configure Calamares installer settings, branding, and custom Python firewall/security modules (`calamares/`)
- [x] Task 9.1: Implement and verify automated pytest test suite (`tests/` — 20/20 passing)
- [x] Task 10.1: Execute containerized ISO live-build and generate hybrid bootable ISO image (`build/output/live-image-amd64.hybrid.iso`)

### `next`
- [ ] Flash bootable USB media using Rufus (DD mode) or Ventoy
- [ ] Boot and execute dual-boot installation on target hardware (**The-Garden-Of-Words**: Intel i5-1335U, Iris Xe)

### `blocked`
*(None)*

### `recurring`
- [x] Pre-commit pytest verification
- [x] Lore continuity audits on world projects
