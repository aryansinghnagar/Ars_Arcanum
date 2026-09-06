# Ars Arcanum — The Writer's Forge & Worldbuilder's OS

> *"The Art of Secrets"* — A purpose-built, distraction-free, beginner-accessible Linux workstation for the complete lifecycle of fantasy and science fiction worldbuilding and long-form prose composition.

[![Status: Work in Progress](https://img.shields.io/badge/Status-Work--In--Progress-orange.svg)](#)
[![Testing: Untested](https://img.shields.io/badge/Testing-Untested-red.svg)](#)
[![Stability: Experimental](https://img.shields.io/badge/Stability-Experimental-red.svg)](#)
[![License: GPL v3](https://img.shields.io/badge/License-GPL_v3-blue.svg)](LICENSE)

> [!CAUTION]
> ### ⚠️ EXPERIMENTAL & UNTESTED — WORK IN PROGRESS
> This repository is an active **Work-In-Progress (WIP)** and is currently **untested on live bare-metal hardware**.
>
> - **Experimental Operating System Appliance**: Build recipes, live-build chroot hooks, ISO packaging configurations, and security scripts are actively experimental and undergoing iteration.
> - **Not Intended for General End Users or Production Machines**: Do not attempt to install or flash this system image to primary hardware, unpartitioned production drives, or machines without independent verified backups.
> - **Use at Your Own Risk**: Low-level disk partitioning, LUKS2 encryption hooks, and firewall/sysctl rules carry inherent system risks if executed outside strictly isolated virtualized environments (e.g., test VMs).

---

## 🧭 System Identity & Overview

Ars Arcanum transforms a Debian 13 (Trixie) base into a hardened, distraction-free creative appliance:
- **Distraction Elimination by Construction**: Non-authoring daemons, browsers, video decoders, streaming services, and social apps are eliminated at the package level.
- **Vault-Grade Security**: LUKS2 full-disk encryption with `argon2id` KDF, sysctl kernel hardening, AppArmor mandatory access control profiles sandboxed to `~/Worlds/**`, and strict `nftables` packet filtering.
- **Open Formats & Zero Vendor Lock-In**: Human-readable formats (Markdown with YAML frontmatter, Typst markup, SVG, PNG, OpenDocument) versioned with local Git.
- **Dual-Session Desktop**: XFCE 4.18 (primary desktop) with alternative `labwc` (Wayland session).

---

## 📂 Monorepo Architecture

```text
Ars Arcanum/
├── build/         # Debian live-build package manifests, chroot hooks, overlays
├── calamares/     # Calamares installer configuration, branding, custom modules
├── src/           # Python & POSIX source code for ars-* tool suite & GUI apps
│   ├── common/    # Shared libraries (git_ops, lore_parser, config, logger)
│   ├── cli/       # CLI commands (ars-wizard, ars-compile, ars-audit, etc.)
│   └── gui/       # Desktop applications (ars-welcome, etc.)
├── themes/        # Core theme packages (Grimoire, Astral, Sylvan, Obsidian, Ivory)
├── templates/     # Author methodology template packs
├── sample_world/  # "World of Elaris" reference project
├── security/      # AppArmor profiles, nftables rules, sysctl hardening, udev rules
├── docs/          # Offline HTML help browser and Typst manual
└── tests/         # Automated pytest test suite
```

---

## 📖 Further Documentation

- **[Project Charter](project.md)**: Foundational directives, desktop specifications, and monorepo structure.
- **[Status Report](status.md)**: Current build and testing status.
- **[Plan & Roadmap](plan.md)**: Implementation stages, milestones, and architectural decisions.
- **[Task List](tasks.md)**: Current development tracking and outstanding items.
