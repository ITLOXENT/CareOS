#!/usr/bin/env python3
from __future__ import annotations

import os
import re
import sys
from pathlib import Path


PLACEHOLDER_PATTERN = re.compile(r"\b(TODO|FIXME|PLACEHOLDER|STUB)\b", re.IGNORECASE)
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


def scan_files(paths: list[Path]) -> list[tuple[Path, int, str]]:
    hits: list[tuple[Path, int, str]] = []
    for path in paths:
        if is_binary(path):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for index, line in enumerate(text.splitlines(), start=1):
            if PLACEHOLDER_PATTERN.search(line):
                hits.append((path, index, line.strip()))
    return hits


def main() -> int:
    repo_root = find_repo_root(Path(__file__).parent)
    target_dirs = [
        repo_root / "apps",
        repo_root / "packages",
        repo_root / "infra",
    ]
    existing = [path for path in target_dirs if path.exists()]
    if not existing:
        print("No apps/packages/infra directories found; skipping placeholder scan.")
        return 0

    files: list[Path] = []
    for target in existing:
        files.extend(iter_files(target))

    hits = scan_files(files)
    if not hits:
        print("No placeholder markers found.")
        return 0

    print("Placeholder markers detected:")
    for path, line_no, line in hits:
        rel_path = path.relative_to(repo_root)
        print(f"- {rel_path}:{line_no}: {line}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
