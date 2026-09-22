#!/usr/bin/env python3
"""design doc / one-pager / ADR を採番して作成する。

    python3 scripts/new_doc.py design   "セッション保存先の変更"
    python3 scripts/new_doc.py onepager "ログ形式を JSON に揃える"
    python3 scripts/new_doc.py adr      "セッション保存先に Redis を採用する"

オプション:
    --owner @handle   front matter の owner（既定: git config user.name）
    --slug foo-bar    ファイル名の slug（既定: タイトルから自動生成）

作成後、索引 README に行を追加し、次にやることを表示する。
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KINDS = {
    "design":   ("DD",  ROOT / "docs" / "design", ROOT / "docs" / "templates" / "design-doc.md"),
    "onepager": ("DD",  ROOT / "docs" / "design", ROOT / "docs" / "templates" / "one-pager.md"),
    "adr":      ("ADR", ROOT / "docs" / "adr",    ROOT / "docs" / "templates" / "adr.md"),
}


def slugify(title: str) -> str:
    """ASCII の slug を作る。日本語タイトルなど ASCII 化できない場合は空を返す。"""
    normalized = unicodedata.normalize("NFKD", title)
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii").lower()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_only).strip("-")
    return "-".join(slug.split("-")[:6])


def next_id(directory: Path, prefix: str) -> str:
    directory.mkdir(parents=True, exist_ok=True)
    used = [
        int(m.group(1))
        for p in directory.glob(f"{prefix}-*.md")
        if (m := re.match(rf"{prefix}-(\d{{4}})-", p.name))
    ]
    return f"{prefix}-{max(used, default=0) + 1:04d}"


def git_handle() -> str:
    for key in ("user.username", "user.name"):
        try:
            value = subprocess.run(
                ["git", "config", "--get", key], capture_output=True, text=True, check=False
            ).stdout.strip()
        except OSError:
            value = ""
        if value:
            return "@" + re.sub(r"\s+", "-", value)
    return "@TODO-set-owner"


def fill(template: str, *, doc_id: str, title: str, owner: str, today: str) -> str:
    placeholder = "DD-0000" if doc_id.startswith("DD-") else "ADR-0000"
    text = template.replace(placeholder, doc_id)
    text = re.sub(r'^title:.*$', f'title: "{title}"', text, count=1, flags=re.M)
    text = text.replace("0000-00-00", today)
    return text.replace('"@<github-handle>"', f'"{owner}"')


def append_to_index(index: Path, row: str) -> bool:
    """索引 README の表の末尾に行を追加する。表が見つからなければ False。"""
    if not index.exists():
        return False
    lines = index.read_text(encoding="utf-8").splitlines()
    last_row = None
    for i, line in enumerate(lines):
        if line.strip().startswith("|") and line.strip().endswith("|"):
            last_row = i
    if last_row is None:
        return False
    lines.insert(last_row + 1, row)
    index.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("kind", choices=sorted(KINDS))
    parser.add_argument("title")
    parser.add_argument("--owner", default=None, help="@github-handle")
    parser.add_argument("--slug", default=None, help="ファイル名に使う slug")
    args = parser.parse_args()

    prefix, directory, template_path = KINDS[args.kind]
    if not template_path.exists():
        print(f"テンプレートがない: {template_path}", file=sys.stderr)
        return 1

    slug = args.slug or slugify(args.title)
    if not slug:
        print(
            "タイトルから slug を作れなかった（日本語タイトルなど）。\n"
            f'  例: python3 scripts/new_doc.py {args.kind} "{args.title}" --slug session-store',
            file=sys.stderr,
        )
        return 1

    doc_id = next_id(directory, prefix)
    path = directory / f"{doc_id}-{slug}.md"
    if path.exists():
        print(f"すでに存在する: {path}", file=sys.stderr)
        return 1

    today = dt.date.today().isoformat()
    owner = args.owner or git_handle()
    path.write_text(
        fill(template_path.read_text(encoding="utf-8"),
             doc_id=doc_id, title=args.title, owner=owner, today=today),
        encoding="utf-8",
    )

    if prefix == "DD":
        row = f"| [{doc_id}]({path.name}) | {args.title} | `draft` | {owner} | {today} |"
        guide = "docs/process/03-design-doc.md"
    else:
        row = f"| [{doc_id}]({path.name}) | {args.title} | `proposed` | {today} |"
        guide = "docs/process/08-adr.md"
    indexed = append_to_index(directory / "README.md", row)

    print(f"作成: {path.relative_to(ROOT)}")
    print(f"索引: {'更新した' if indexed else '手動で追記すること → ' + str((directory / 'README.md').relative_to(ROOT))}")
    print("\n次にやること:")
    print(f"  1. {guide} を読んで各節を埋める")
    if prefix == "DD":
        print("  2. Decision Points に『選択肢 / AI の推奨 / 覆すコスト』を必ず書く")
        print("  3. Alternatives Considered に実行可能な案を 2〜3 案書く（『何もしない』を含める）")
    print("  4. python3 scripts/validate_docs.py で検証")
    print(f"  5. 単独 PR で提出（タイトル: docs({'design' if prefix == 'DD' else 'adr'}): {doc_id} {args.title}）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
