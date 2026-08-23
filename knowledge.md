# Domain Knowledge & Architectural Insights

## 1. Debian 13 (Trixie) Live-Build System
- Debian `live-build` creates bootable ISO hybrid images via `lb config`, `lb build`, and `lb clean`.
- Package manifests in `config/package-lists/*.list.chroot` are installed during the debootstrap chroot phase.
- Files in `config/includes.chroot/` overlay directly onto the target root filesystem (`/`).
- Chroot hooks in `config/hooks/live/*.hook.chroot` execute inside the chroot environment to configure services, compile assets, and lockdown settings.

## 2. Hardened Security & Sandboxing
- **nftables**: Packet filtering replaces legacy iptables. Paranoid mode drops all inbound and outbound traffic except for package manager operations (`meta skuid _apt`, `meta skuid root` on ports 80/443), NTP (port 123), and loopback (`lo`).
- **AppArmor**: Mandatory Access Control confined per-binary. Restricts read/write access to `~/Worlds/**`, `/tmp`, and basic libraries while explicitly denying `network inet` and `network inet6`.
- **LUKS2 + Argon2id**: Uses memory-hard password hashing to prevent brute force attacks on manuscripts.

## 3. Cross-Tool Interoperability Data Contract
- Standardized YAML frontmatter header across all Markdown files:
  ```yaml
  ---
  title: "Scene Title"
  type: "scene" # scene | character | location | lore | timeline | magic
  world: "WorldName"
  project: "Book-01"
  chapter: 1
  scene: 1
  pov_character: "Character Name"
  location: "Setting Name"
  timeline_date: "Epoch Date"
  word_goal: 2500
  status: "draft"
  tags: [tag1, tag2]
  ---
  ```
- Parsed by `ars-audit`, `ars-compile`, Obsidian Dataview, and novelWriter.
