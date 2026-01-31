#!/usr/bin/env python3
from __future__ import annotations

import os
import re
import sys
from pathlib import Path


SECRET_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("aws_access_key_id", re.compile(r"\b(AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("github_token", re.compile(r"\bghp_[0-9A-Za-z]{36,}\b")),
    ("google_api_key", re.compile(r"\bAIza[0-9A-Za-z\-_]{35}\b")),
    ("slack_token", re.compile(r"\bxox[baprs]-[0-9A-Za-z-]{10,}\b")),
    ("stripe_live_key", re.compile(r"\bsk_live_[0-9a-zA-Z]{16,}\b")),
    (
        "private_key_block",
        re.compile(r"-----BEGIN (RSA|EC|OPENSSH|DSA|PRIVATE) KEY-----"),
    ),
    (
        "aws_secret_access_key",
        re.compile(
            r"\bAWS_SECRET_ACCESS_KEY\s*=\s*['\"][A-Za-z0-9/+=]{40}['\"]"
        ),
    ),
]

SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".idea",
    ".vscode",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "build",
    ".next",
    ".turbo",
    ".cache",
    "coverage",
    ".terraform",
}


def find_repo_root(start: Path) -> Path:
    current = start.resolve()
    for parent in [current] + list(current.parents):
        if (parent / ".git").exists():
            return parent
    return current


def is_binary(path: Path) -> bool:
    try:
        with path.open("rb") as handle:
            chunk = handle.read(2048)
            return b"\x00" in chunk
    except OSError:
        return True


def iter_files(root: Path) -> list[Path]:
    collected: list[Path] = []
    for base, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
        for name in files:
            if name.startswith("."):
                continue
            path = Path(base) / name
            if path.is_file():
                collected.append(path)
    return collected


def scan_files(paths: list[Path], repo_root: Path) -> list[tuple[Path, int, str]]:
    hits: list[tuple[Path, int, str]] = []
    for path in paths:
        if is_binary(path):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for index, line in enumerate(text.splitlines(), start=1):
            for label, pattern in SECRET_PATTERNS:
                if pattern.search(line):
                    hits.append((path, index, label))
    return hits


def main() -> int:
    repo_root = find_repo_root(Path(__file__).parent)
    files = iter_files(repo_root)
    hits = scan_files(files, repo_root)
    if not hits:
        print("No secret-like patterns detected.")
        return 0

    print("Secret-like patterns detected:")
    for path, line_no, label in hits:
        rel_path = path.relative_to(repo_root)
        print(f"- {rel_path}:{line_no} ({label})")
    return 1


if __name__ == "__main__":
    sys.exit(main())
