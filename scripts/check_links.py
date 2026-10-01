#!/usr/bin/env python3
"""Check that relative Markdown links resolve to real files.

    python3 scripts/check_links.py

The process documents are built from cross-references, and agents follow those links to
assemble context. A broken link is equivalent to lost knowledge, so CI fails on one
(docs/process/05-issues-roadmap.md).

External URLs (http/https) and bare anchors are not checked.
No third-party dependencies.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
TARGET_DIRS = ["docs", ".github", ".claude"]
ROOT_FILES = ["README.md", "CLAUDE.md"]

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
CODE_FENCE_RE = re.compile(r"^```")
SKIP_SCHEMES = ("http://", "https://", "mailto:", "#")


def markdown_files() -> list[Path]:
    files = [ROOT / name for name in ROOT_FILES if (ROOT / name).exists()]
    for directory in TARGET_DIRS:
        base = ROOT / directory
        if base.exists():
            files.extend(sorted(base.rglob("*.md")))
    return files


def strip_code_blocks(text: str) -> str:
    """Exclude fenced code blocks from link checking."""
    lines, inside, kept = text.splitlines(), False, []
    for line in lines:
        if CODE_FENCE_RE.match(line.strip()):
            inside = not inside
            kept.append("")
            continue
        kept.append("" if inside else line)
    return "\n".join(kept)


def main() -> int:
    errors: list[str] = []
    files = markdown_files()
    checked = 0

    for path in files:
        text = strip_code_blocks(path.read_text(encoding="utf-8"))
        # Links inside HTML comments (template examples) are out of scope
        text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
        for target in LINK_RE.findall(text):
            if target.startswith(SKIP_SCHEMES):
                continue
            checked += 1
            # Drop the anchor and query, leaving just the path
            bare = unquote(target.split("#", 1)[0].split("?", 1)[0])
            if not bare:
                continue
            resolved = (ROOT / bare.lstrip("/")) if bare.startswith("/") else (path.parent / bare)
            if not resolved.resolve().exists():
                errors.append(f"{path.relative_to(ROOT)}: broken link -> {target}")

    for error in errors:
        print(f"ERROR {error}")
    print(f"\nchecked {checked} relative link(s) across {len(files)} file(s): {len(errors)} error(s)")
    if errors:
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
