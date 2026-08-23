# Ars Arcanum — Project Charter

> *"The Art of Secrets"* — A purpose-built, distraction-free, beginner-accessible Linux workstation for the complete lifecycle of fantasy and science fiction worldbuilding and long-form prose composition.

---

## 1. System Identity
- **Name**: Ars Arcanum
- **Tagline**: The Writer's Forge. The Worldbuilder's OS.
- **Classification**: Dedicated Creative Workstation & Hardened Appliance
- **Upstream Base**: Debian GNU/Linux 13 (Trixie) Minimal
- **Primary Desktop**: XFCE 4.18+ (X11) / Alternative: `labwc` (Wayland)
- **Primary Workstation Target**: 13th Gen Intel Core i5-1335U, 16GB RAM, Intel Iris Xe Graphics, NVMe SSD (Dual-boot alongside Windows)

---

## 2. Foundational Directives
1. **The Machine Is an Instrument, Not an Environment**: Every daemon, config, and utility strictly serves speculative fiction authoring.
2. **Distraction Elimination by Construction**: Web browsers, video decoders, social/messaging apps, streaming audio, and AI/LLM components are structurally eliminated at the package level.
3. **Vault-Grade Data Security**: LUKS2 full-disk encryption with `argon2id` KDF, sysctl kernel hardening, AppArmor MAC profiles (`deny network`, sandboxed to `~/Worlds/**`), and `nftables` Paranoid/Standard firewall.
4. **Open Formats & Zero Vendor Lock-In**: Human-readable formats (Markdown with YAML frontmatter, Typst markup, SVG, PNG, OpenDocument, XML/JSON) versioned with local Git.
5. **Unified Toolchain Cohesion**: Standardized schema integration, cross-tool hotkeys, automated compilation pipelines, and continuity linting utilities.
6. **Beginner Accessibility**: Graphical interface as the primary interaction path for every function (`ars-wizard`, `ars-welcome`, `ars-compile`, etc.), with full CLI power-user parity.

---

## 3. Monorepo Directory Architecture
```text
6-Ars Arcanum/
├── build/                 # Debian live-build package manifests, chroot hooks, overlays
├── calamares/             # Calamares installer configuration, branding, custom modules
├── src/                   # Python & POSIX source code for the ars-* tool suite & GUI apps
│   ├── common/            # Shared libraries (git_ops, lore_parser, config, logger)
│   ├── cli/               # CLI commands installed to /usr/local/bin/
│   └── gui/               # PyQt6 desktop applications (ars-wizard, ars-welcome)
├── themes/                # 5 core theme packages (Grimoire, Astral, Sylvan, Obsidian, Ivory)
├── templates/             # 5 author methodology template packs
├── sample_world/          # "World of Elaris" reference project
├── security/              # AppArmor profiles, nftables rules, sysctl hardening, udev rules
├── docs/                  # Offline HTML help browser and Typst book manual
└── tests/                 # Automated pytest verification test suite
```
