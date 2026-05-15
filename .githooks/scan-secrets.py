"""
Pre-commit secret + sensitive-file scanner.

Runs against staged changes. Exits non-zero if any check fails.
Bypass with `git commit --no-verify`.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

RED = "\033[31m"
YELLOW = "\033[33m"
GREEN = "\033[32m"
RESET = "\033[0m"


def red(s: str) -> str:
    return f"{RED}{s}{RESET}"


def yellow(s: str) -> str:
    return f"{YELLOW}{s}{RESET}"


def green(s: str) -> str:
    return f"{GREEN}{s}{RESET}"


# Paths that should never be committed.
BLOCKED_PATH_PATTERNS = [
    (r"^\.env$", ".env file"),
    (r"^\.env\.local$", ".env.local file"),
    (r"^\.env\.(?!example$|sample$|template$)[^/]+$", "environment file"),
    (r"\.pem$", "private key (.pem)"),
    (r"\.key$", "private key (.key)"),
    (r"\.p12$", "PKCS#12 archive"),
    (r"\.pfx$", "PKCS#12 archive"),
    (r"\.pdf$", "PDF artifact (gitignored)"),
    (r"^data/.+\.md$", "personal data (real resume content)"),
    (r"^output/", "generated application output"),
    (r"^analysis/", "gap analysis output"),
    (r"^projects/", "project schematics"),
    (r"^scans/[^/]+/", "scan output"),
    (r"^_tmp/", "scratch / temp output"),
    (r"^config/google-form\.md$", "Google Form config (real form IDs)"),
    (r"^config/target-companies\.yml$", "target companies watchlist"),
    (r"^id_rsa$|^id_ed25519$|^id_ecdsa$|^id_dsa$", "SSH private key"),
    (r"credentials.*\.json$", "credentials JSON"),
    (r"^\.aws/credentials$", "AWS credentials"),
    (r"\.kubeconfig$|^kubeconfig$", "kubeconfig"),
]

# Allowlist — names that look sensitive but are templates/examples.
ALLOWED_PATH_PATTERNS = [
    r"\.example\.",
    r"\.sample\.",
    r"\.template\.",
    r"^data/.+\.example\.md$",
    r"^config/.+\.example\.",
]

# Secret content patterns. Each entry: (regex, human-readable name).
SECRET_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b"), "AWS access key"),
    (re.compile(r"\bghp_[A-Za-z0-9]{36}\b"), "GitHub personal access token"),
    (re.compile(r"\bgho_[A-Za-z0-9]{36}\b"), "GitHub OAuth token"),
    (re.compile(r"\bghu_[A-Za-z0-9]{36}\b"), "GitHub user-to-server token"),
    (re.compile(r"\bghs_[A-Za-z0-9]{36}\b"), "GitHub server-to-server token"),
    (re.compile(r"\bghr_[A-Za-z0-9]{36}\b"), "GitHub refresh token"),
    (re.compile(r"\bgithub_pat_[A-Za-z0-9_]{82}\b"), "GitHub fine-grained PAT"),
    (re.compile(r"\bsk-ant-[A-Za-z0-9_-]{50,}\b"), "Anthropic API key"),
    (re.compile(r"\bsk-proj-[A-Za-z0-9_-]{40,}\b"), "OpenAI project key"),
    (re.compile(r"\bsk-[A-Za-z0-9]{48}\b"), "OpenAI API key (legacy)"),
    (re.compile(r"\bxox[abprs]-[0-9]{10,}-[0-9]{10,}-[A-Za-z0-9-]{20,}\b"), "Slack token"),
    (re.compile(r"\bsk_live_[A-Za-z0-9]{24,}\b"), "Stripe live secret key"),
    (re.compile(r"\brk_live_[A-Za-z0-9]{24,}\b"), "Stripe live restricted key"),
    (re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b"), "Google API key"),
    (re.compile(r"\bnpm_[A-Za-z0-9]{36}\b"), "npm token"),
    (re.compile(r"\bglpat-[A-Za-z0-9_-]{20,}\b"), "GitLab personal access token"),
    (re.compile(r"-----BEGIN (?:RSA|DSA|EC|OPENSSH|PGP|ENCRYPTED)? ?PRIVATE KEY-----"), "private key block"),
    (re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\b"), "JWT token"),
    (re.compile(r"\b(?:postgres|postgresql|mysql|mongodb(?:\+srv)?|redis|amqp)://[^\s:@/]+:[^\s:@/]{4,}@[^\s/]+"), "URL with embedded credentials"),
]

# Soft-warn patterns: high entropy strings that often signal a hardcoded secret
# but produce false positives. Just warn, don't block.
WARN_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r'(?i)\b(?:api[_-]?key|secret|password|token|passwd)["\']?\s*[:=]\s*["\'][A-Za-z0-9+/=_-]{20,}["\']'), "assignment that looks like a secret"),
]

# File size threshold: warn if a single staged file exceeds this.
LARGE_FILE_BYTES = 5 * 1024 * 1024  # 5 MB

# Skip scanning files larger than this (perf cap).
SCAN_SIZE_CAP_BYTES = 1 * 1024 * 1024  # 1 MB


def git_staged_files() -> list[str]:
    out = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
        capture_output=True, text=True, check=True,
    ).stdout
    return [line for line in out.splitlines() if line.strip()]


def git_staged_diff(path: str) -> str:
    """Return only the added lines for a given staged file."""
    out = subprocess.run(
        ["git", "diff", "--cached", "-U0", "--", path],
        capture_output=True, text=True, check=False,
    ).stdout
    added = []
    for line in out.splitlines():
        if line.startswith("+++"):
            continue
        if line.startswith("+"):
            added.append(line[1:])
    return "\n".join(added)


def path_is_allowed(path: str) -> bool:
    return any(re.search(p, path) for p in ALLOWED_PATH_PATTERNS)


def check_blocked_paths(files: list[str]) -> list[str]:
    errors = []
    for f in files:
        if path_is_allowed(f):
            continue
        for pat, name in BLOCKED_PATH_PATTERNS:
            if re.search(pat, f):
                errors.append(f"{red('BLOCKED FILE')}: {f}  ({name})")
                break
    return errors


def check_secrets(files: list[str]) -> list[str]:
    errors = []
    for f in files:
        p = Path(f)
        if not p.exists() or not p.is_file():
            continue
        try:
            if p.stat().st_size > SCAN_SIZE_CAP_BYTES:
                continue
        except OSError:
            continue

        added = git_staged_diff(f)
        if not added:
            continue

        for pat, name in SECRET_PATTERNS:
            for m in pat.finditer(added):
                snippet = m.group(0)
                # Redact middle of long matches for safer display.
                if len(snippet) > 24:
                    snippet = snippet[:10] + "…" + snippet[-6:]
                errors.append(f"{red('SECRET')}: {f} | {name} ({snippet})")

        for pat, name in WARN_PATTERNS:
            for m in pat.finditer(added):
                snippet = m.group(0)
                if len(snippet) > 60:
                    snippet = snippet[:50] + "…"
                errors.append(f"{yellow('WARN')}: {f} | {name}: {snippet}")

    return errors


def check_large_files(files: list[str]) -> list[str]:
    warnings = []
    for f in files:
        p = Path(f)
        if not p.exists() or not p.is_file():
            continue
        try:
            size = p.stat().st_size
        except OSError:
            continue
        if size > LARGE_FILE_BYTES:
            mb = size / 1024 / 1024
            warnings.append(f"{yellow('LARGE FILE')}: {f} ({mb:.1f} MB), consider Git LFS or .gitignore")
    return warnings


def main() -> int:
    files = git_staged_files()
    if not files:
        return 0

    blocked = check_blocked_paths(files)
    secrets = check_secrets(files)
    large = check_large_files(files)

    issues = blocked + secrets + large
    blocking = [m for m in issues if "WARN" not in m and "LARGE FILE" not in m]

    for msg in issues:
        print(msg)

    if blocking:
        print()
        print(red(f"Pre-commit blocked {len(blocking)} issue(s)."))
        print(yellow("Fix the issues above, or bypass with: git commit --no-verify"))
        return 1

    if issues:
        # Warnings only — let the commit through but make them visible.
        print()
        print(yellow(f"Pre-commit passed with {len(issues)} warning(s)."))
        return 0

    print(green("pre-commit: no secrets, sensitive paths, or oversized files"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
