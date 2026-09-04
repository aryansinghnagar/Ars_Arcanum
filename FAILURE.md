# Postmortem & Failure Log

## [2026-09-04] Audit: 5 High + 12 Medium findings → fixed via ReAct loop
- **Context**: Independent audit flagged hardcoded Borg passphrase, unsafe USB mount + auto-yes, dead Calamares modules, tracked .pyc, security self-conflicts, unpinned builds, CLI/GUI robustness gaps.
- **Root Cause**: Hardcoded secrets for dev convenience; default-allow headless fallbacks; generated overlay mixed with hand-authored files; Flatpak vs. hardening policies designed in isolation.
- **Disproven Hypothesis**: "20/20 tests passing means secure/reproducible" — tests were substring-only, missed calamares/hooks/negative paths.
- **Guardrail / Fix Implemented**: BORG_PASSPHRASE env/prompt + env preservation; device allowlist + default-deny confirmations; Calamares exec wiring + module.desc + SVG branding; `git rm --cached` pycache + overlay .gitignore; sysctl/udev/usbguard/nftables/AppArmor reconciliation; pinned typst/novelwriter + sbctl/kiwix-tools/python3-tk/fonts-cinzel; CLI exit codes + input validation; `tests/test_hardening.py` + extended `test_security_configs.py` (18 regression tests total).

## [2026-09-04] Re-audit residuals → fixed via ReAct loop
- **Context**: Re-audit verified all prior fixes and found 4 medium residuals (mount fail-open on empty allowlist, docx/all target bug, firewall generic-conf fallback, unpinned supply chain) plus doc drift and dead code.
- **Root Cause**: Fail-open defaults in edge paths; pandoc multi-target not modeled; distro-generic fallback trusted; version pins without checksums.
- **Disproven Hypothesis**: "Deny-by-default in the common path is sufficient" — edge paths (empty allowlist, missing ruleset) need their own fail-closed handling.
- **Guardrail / Fix Implemented**: Mount denies on empty allowlist (+noexec); per-format pandoc targets + Digital-DOCX dir; mode-specific firewall files only with honest relock reporting; TYPST_SHA256 opt-in verification + flatpak commit recording; python3-tk/pyqt6 manifest cleanup; plan.md tkinter correction. Suite: 38/38 passing.

## [2026-09-04] Design limitations → fixed via ReAct loop (user-directed scope)
- **Context**: Typst body escaping, lore case/alias/line semantics, focus-file race left as documented limitations; user chose scope for each.
- **Root Cause**: Markup-context escaping conflated with string escaping; attributes lowercased at extraction; check-then-write without mutual exclusion.
- **Disproven Hypothesis**: "os.kill(pid, 0) is a portable liveness check" — on Windows it can terminate the target (killed the test runner with zero output); POSIX-gated now.
- **Guardrail / Fix Implemented**: Dual-context Typst escaping (string vs content) + verbatim-body contract; case-preserving attributes with casefold compare, bidirectional normalized aliases, DOTALL multiline scan with offset-derived line numbers; O_EXCL lockfile with dead-PID/age-based reclaim, POSIX-gated liveness. Suite: 44/44 passing.

### Entry Format Reference
```markdown
## [YYYY-MM-DD] Incident: <Title>
- **Context**: Description of the attempted operation.
- **Root Cause**: Underlying factor causing failure or error.
- **Disproven Hypothesis**: What assumption was invalidated.
- **Guardrail / Fix Implemented**: Preventative regression test, config rule, or code guardrail.
```
