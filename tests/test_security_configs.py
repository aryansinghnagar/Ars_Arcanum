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
    ]
    for p in profiles:
        p_file = aa_dir / p
        assert p_file.exists(), f"Missing profile: {p}"
        content = p_file.read_text(encoding="utf-8")
        assert "deny network inet" in content
        assert "owner @{HOME}/Worlds/**" in content


def test_apt_exclusions_pinning():
    pref = BUILD_DIR / "config" / "apt" / "preferences.d" / "00-ars-exclusions.pref"
    assert pref.exists()
    content = pref.read_text(encoding="utf-8")
    assert "Package: chromium* firefox* epiphany-browser*" in content
    assert "Package: vlc* mpv*" in content
    assert "Package: discord* telegram-desktop*" in content
    assert "Pin-Priority: -1" in content
