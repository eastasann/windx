#!/usr/bin/env python3
"""Markdown 内の相対リンクが実在するかを検証する。

    python3 scripts/check_links.py

プロセス文書は相互参照で成り立っており、AI はそのリンクを辿って文脈を集める。
リンク切れは「知識の消失」と同義なので CI で落とす（docs/process/05-issues-roadmap.md）。

外部 URL（http/https）とアンカーのみのリンクは検証対象外。
依存ライブラリなし。
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
    """フェンス内のコードはリンク検証の対象外にする。"""
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
        # HTML コメント内のリンク（テンプレートの記入例）は対象外
        text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
        for target in LINK_RE.findall(text):
            if target.startswith(SKIP_SCHEMES):
                continue
            checked += 1
            # アンカーとクエリを落として実体のパスだけを見る
            bare = unquote(target.split("#", 1)[0].split("?", 1)[0])
            if not bare:
                continue
            resolved = (ROOT / bare.lstrip("/")) if bare.startswith("/") else (path.parent / bare)
            if not resolved.resolve().exists():
                errors.append(f"{path.relative_to(ROOT)}: リンク切れ -> {target}")

    for error in errors:
        print(f"ERROR {error}")
    print(f"\n{len(files)} ファイル / 相対リンク {checked} 件を検証: エラー {len(errors)} 件")
    if errors:
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
