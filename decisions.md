# Architecture Decision Records (ADRs)

## ADR-001: Debian 13 (Trixie) as Upstream Base
- **Context**: Need a rock-solid, ultra-stable Linux foundation with broad package availability, modern hardware enablement (13th Gen Intel Iris Xe), and zero corporate telemetry.
- **Decision**: Adopt Debian 13 (Trixie) Stable as the base distribution.
- **Alternatives Considered**: Arch Linux (rolling release risk for non-technical writers), Ubuntu (snapd overhead and corporate tracking), Fedora (rapid release cycle requiring frequent disruptive upgrades).
- **Consequences**: Uncompromised stability, native `live-build` toolchain, vast package repositories.

## ADR-002: Dual Display Server Strategy (X11 Primary + labwc Alternative)
- **Context**: Graphics tablet pressure sensitivity, Krita hardware-accelerated OpenGL canvas, and global system hotkeys (`Super+F`, `Super+G`, `Ctrl+Alt+W`) require flawless reliability.
- **Decision**: X11 (Xorg) with XFCE 4.18 as default desktop; lightweight `labwc` (Wayland) as an optional sub-150MB session selectable at LightDM login.
- **Alternatives Considered**: Wayland-only (risk of tablet input driver inconsistencies in legacy creative tools).
- **Consequences**: Guaranteed out-of-the-box hardware tablet compatibility and global shortcut capture.

## ADR-003: Typst as Primary Typesetting Engine
- **Context**: Authors require instant, publication-grade print PDFs without the multi-gigabyte bloat and sluggish compile times of LaTeX.
- **Decision**: Adopt Typst (Rust native binary) as the primary PDF compilation engine alongside Pandoc for EPUB 3 and DOCX conversion.
- **Alternatives Considered**: LaTeX / XeTeX (slow compilation, complex error messages), LibreOffice headless CLI (inconsistent microtypography).
- **Consequences**: Sub-250ms compilation for full-length 150k-word manuscripts with drop caps and professional typography.

## ADR-004: Anti-Distraction Enforcement at Package & Firewall Layer
- **Context**: Psychological self-control fails; writers require structural elimination of distractions.
- **Decision**: Permanently omit browsers, video players, social media clients, and streaming audio at the APT package preference and manifest layer, backed by default-drop `nftables` network isolation.
- **Alternatives Considered**: Time-limiters or browser extensions (easily bypassed).
- **Consequences**: 100% distraction-free environment by construction.
