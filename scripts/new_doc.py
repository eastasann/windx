#!/usr/bin/env python3
"""Create a numbered design doc, one-pager, or ADR.

    python3 scripts/new_doc.py design   "Change the session store" --slug session-store
    python3 scripts/new_doc.py onepager "Switch logs to JSON"      --slug json-logging
    python3 scripts/new_doc.py adr      "Adopt Redis for sessions" --slug session-store-redis

Options:
    --owner @handle   the front matter owner (default: derived from git config)
    --slug foo-bar    the filename slug (default: derived from the title)

After creating the file it appends a row to the index README and prints what to do next.
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
    """Build an ASCII slug. Returns empty when the title has no ASCII to work with."""
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
    """Append a row to the last table in the index README. False if no table was found."""
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
    parser.add_argument("--slug", default=None, help="slug used in the filename")
    args = parser.parse_args()

    prefix, directory, template_path = KINDS[args.kind]
    if not template_path.exists():
        print(f"template not found: {template_path}", file=sys.stderr)
        return 1

    slug = args.slug or slugify(args.title)
    if not slug:
        print(
            "could not derive a slug from the title (non-ASCII titles need one).\n"
            f'  e.g. python3 scripts/new_doc.py {args.kind} "{args.title}" --slug session-store',
            file=sys.stderr,
        )
        return 1

    doc_id = next_id(directory, prefix)
    path = directory / f"{doc_id}-{slug}.md"
    if path.exists():
        print(f"already exists: {path}", file=sys.stderr)
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

    print(f"created: {path.relative_to(ROOT)}")
    if indexed:
        print("index:   updated")
    else:
        print(f"index:   add the row by hand -> {(directory / 'README.md').relative_to(ROOT)}")
    print("\nNext:")
    print(f"  1. Read {guide} and fill in each section")
    if prefix == "DD":
        print("  2. Give every Decision Point its options, your recommendation, and the cost of reversal")
        print("  3. Write two or three workable alternatives, including 'do nothing'")
    else:
        print("  2. Name two or more bad outcomes in Consequences")
    print("  4. Validate with: python3 scripts/validate_docs.py")
    kind_label = "design" if prefix == "DD" else "adr"
    print(f"  5. Submit as its own PR, titled: docs({kind_label}): {doc_id} {args.title}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
