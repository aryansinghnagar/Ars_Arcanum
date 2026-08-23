# Bare-Metal Hardware Deployment & Verification Runbook

## Target System: `The-Garden-Of-Words`
- **Processor**: 13th Gen Intel® Core™ i5-1335U (2P+8E cores, 12 threads, up to 4.60 GHz)
- **Memory**: 16.0 GB DDR4/DDR5 RAM
- **Graphics**: Intel® Iris® Xe Graphics (Mesa OpenGL/Vulkan)
- **Storage**: 477 GB NVMe SSD (Dual-Booting with Windows 11; ~100 GB allocated for Ars Arcanum)
- **Display**: 1920×1080 Full HD (100% integer scaling, subpixel font rendering)

---

## 1. Pre-Installation BIOS / UEFI Configuration
1. **Enter UEFI Settings**: Press `F2` or `Delete` during cold power-on.
2. **Disable Windows Fast Startup** (in Windows Control Panel → Power Options) to prevent NTFS filesystem locking.
3. **Storage Controller**: Ensure SATA/NVMe mode is set to **AHCI / NVMe** (not Intel RST RAID).
4. **Secure Boot**:
   - If deploying with Standard Security: Secure Boot can remain enabled (using standard Debian signed shim).
   - If opting into `sbctl` Advanced Hardware Security: Clear platform keys to enter *Setup Mode*.

---

## 2. Flashing the Bootable USB Media
### Option A: Using Rufus (Windows)
1. Insert a USB 3.0 flash drive (≥ 8 GB).
2. Open Rufus → Select `live-image-amd64.hybrid.iso`.
3. Partition Scheme: **GPT** | Target System: **UEFI (non CSM)**.
4. Write mode: Select **Write in DD Image mode** when prompted.

### Option B: Using Ventoy
1. Install Ventoy to the USB drive.
2. Copy `live-image-amd64.hybrid.iso` directly into the Ventoy partition.

---

## 3. Live Boot & Calamares Installation
1. Boot into the live session via `F12` / boot menu.
2. Verify live desktop loads within target budget (**≤ 10 seconds**).
3. Click desktop icon **"Install Ars Arcanum"** to launch Calamares:
   - **Partitioning**: Select **"Install alongside existing OS"** (Calamares auto-shrinks Windows partition to allocate 80–100 GB for Ars Arcanum).
   - **Encryption**: Check **"Encrypt disk with LUKS2"** (Enter memorable master passphrase; Argon2id memory-hard hashing is active).
   - **Firewall Selection**: Select **Paranoid Mode** (recommended for sensitive manuscripts).
   - **Hardware Security**: Check **"Enable Secure Boot key enrollment + USBGuard"** if desired.
4. Complete installation and reboot. Remove USB installation media.

---

## 4. Post-Install Empirical Verification Checklist

### Check 1: Hardware Acceleration (Intel Iris Xe)
Open terminal (`Super+Enter`) and verify OpenGL driver:
```bash
glxinfo -B | grep -E "OpenGL vendor|OpenGL renderer|OpenGL version"
```
*Expected output: Intel Iris Xe Graphics with Mesa 24+.*

### Check 2: Krita Canvas 60 FPS Responsiveness
1. Press `Super+K` to launch Krita.
2. Open `~/Worlds/Elaris/02-Maps/Regional-Maps/Ashmarch_Regional_Map.svg` or create a new 4K canvas.
3. Pan and zoom across canvas; verify smooth 60 FPS hardware rendering.

### Check 3: Typst Compilation Benchmark
Execute book compilation test:
```bash
ars-compile Elaris -f pdf
```
*Verify rendering completes in under 250 milliseconds.*

### Check 4: Network Isolation & AppArmor Lockdown Audit
Verify that Obsidian and drafting tools are strictly denied network sockets:
```bash
sudo apparmor_status
# Confirm obsidian, novelwriter, focuswriter, krita, inkscape are in 'enforce' mode.
```
Test firewall containment:
```bash
# In Paranoid mode, ping and curl must fail:
curl -I https://google.com
# Expected: Connection refused or admin-prohibited.
```

### Check 5: Focus Mode & Session Ceremony
1. Press `Super+F` to engage Extreme Focus kiosk.
2. Verify XFCE panel hides completely, notification daemon pauses, and Timewarrior starts tracking.
3. Press `Super+Escape` to trigger exit ceremony, enter word count notes, and verify automatic Git commit in `~/Worlds/Elaris/`.
4. Run `ars-backup --drill` to confirm 3-2-1 BorgBackup archive integrity.
