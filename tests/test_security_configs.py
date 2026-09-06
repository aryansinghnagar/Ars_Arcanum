"""
Validation tests for security configurations, sysctl, nftables, AppArmor, and APT exclusions.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SECURITY_DIR = REPO_ROOT / "security"
BUILD_DIR = REPO_ROOT / "build"


def test_sysctl_hardening_rules():
    conf = SECURITY_DIR / "sysctl" / "99-ars-security.conf"
    assert conf.exists()
    content = conf.read_text(encoding="utf-8")
    assert "kernel.kptr_restrict = 2" in content
    assert "kernel.dmesg_restrict = 1" in content
    assert "kernel.unprivileged_bpf_disabled = 1" in content
    assert "kernel.yama.ptrace_scope = 2" in content
    assert "net.ipv4.conf.all.send_redirects = 0" in content
    # Regression: unprivileged_userns_clone=0 breaks Flatpak; must stay disabled/commented
    active = [line for line in content.splitlines() if line.strip() and not line.strip().startswith("#")]
    assert not any("unprivileged_userns_clone" in line for line in active)


def test_nftables_paranoid_ruleset():
    nft = SECURITY_DIR / "nftables" / "paranoid.nft"
    assert nft.exists()
    content = nft.read_text(encoding="utf-8")
    assert "chain input {" in content
    assert "policy drop" in content
    assert "meta skuid _apt tcp dport { 80, 443 } accept" in content
    assert "udp dport 123 accept" in content


def test_apparmor_profiles_exist():
    aa_dir = SECURITY_DIR / "apparmor"
    assert aa_dir.exists()
    profiles = [
        "md.obsidian.Obsidian",
        "usr.bin.novelwriter",
        "usr.bin.focuswriter",
        "usr.bin.manuskript",
        "usr.bin.krita",
        "usr.bin.inkscape",
        "usr.bin.blanket",
        "usr.bin.drawio",
        "usr.bin.fontforge",
        "usr.bin.polyglot",
    ]
    for p in profiles:
        p_file = aa_dir / p
        assert p_file.exists(), f"Missing profile: {p}"
        content = p_file.read_text(encoding="utf-8")
        assert "deny network inet" in content
    # Worlds confinement applies to file-managing apps (blanket is audio-only)
    for p in ["md.obsidian.Obsidian", "usr.bin.novelwriter", "usr.bin.focuswriter"]:
        assert "owner @{HOME}/Worlds/**" in (aa_dir / p).read_text(encoding="utf-8")


def test_apt_exclusions_pinning():
    pref = BUILD_DIR / "config" / "apt" / "preferences.d" / "00-ars-exclusions.pref"
    assert pref.exists()
    content = pref.read_text(encoding="utf-8")
    assert "Package: chromium* firefox* epiphany-browser*" in content
    assert "Package: vlc* mpv*" in content
    assert "Package: discord* telegram-desktop*" in content
    assert "Pin-Priority: -1" in content


def test_udev_scoped_to_usb():
    rules = (SECURITY_DIR / "udev" / "99-no-automount.rules").read_text(encoding="utf-8")
    assert 'SUBSYSTEM=="block"' in rules
    assert 'ENV{ID_BUS}=="usb"' in rules
    # No bare global ENV that would hide internal disks
    for line in rules.splitlines():
        s = line.strip()
        if s.startswith("ENV{UDISKS_") and not s.startswith("#"):
            assert "SUBSYSTEM" in line, f"Unscoped udev rule: {line}"


def test_usbguard_documents_mount_workflow():
    content = (SECURITY_DIR / "usbguard" / "rules.conf").read_text(encoding="utf-8")
    assert content.strip().splitlines()[-1].strip() == "block"
    assert "allow-device" in content or "ars-mount" in content


def test_calamares_modules_wired():
    repo = REPO_ROOT / "calamares"
    settings = (repo / "settings.conf").read_text(encoding="utf-8")
    assert "ars_firewall" in settings
    assert "ars_hardware_security" in settings
    for mod in ("ars_firewall", "ars_hardware_security"):
        assert (repo / "modules" / mod / "module.desc").exists()
        assert (repo / "modules" / mod / "main.py").exists()
    branding = (repo / "branding" / "arsarcanum" / "branding.desc").read_text(encoding="utf-8")
    assert ".png" not in branding or ".svg" in branding
    for img in ("logo.svg", "icon.svg", "welcome.svg"):
        assert (repo / "branding" / "arsarcanum" / img).exists()
