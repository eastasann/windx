#!/usr/bin/env python3
"""Sync .github/labels.yml to the repository's GitHub labels.

    python3 scripts/sync_labels.py --dry-run      # show what is defined, change nothing
    python3 scripts/sync_labels.py                # sync
    python3 scripts/sync_labels.py --prune        # also delete labels not in the file

Needs the gh CLI and GH_TOKEN (or a completed `gh auth login`).
No third-party dependencies: labels.yml is read by the minimal parser below.

The safe default is to leave labels that are not defined here alone, so that labels
already attached to Issues are never removed by accident. --prune only runs when asked.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LABELS_FILE = ROOT / ".github" / "labels.yml"
NAME_RE = re.compile(r"^[a-z0-9][a-z0-9/_.-]*$")
COLOR_RE = re.compile(r"^[0-9A-Fa-f]{6}$")


def unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def parse_labels(text: str) -> tuple[list[dict], list[str]]:
    """Read only the "- key: value" subset of labels.yml."""
    labels: list[dict] = []
    errors: list[str] = []
    current: dict | None = None
    for lineno, raw in enumerate(text.splitlines(), start=1):
        line = raw.split("#")[0].rstrip() if raw.lstrip().startswith("#") else raw.rstrip()
        if not line.strip():
            continue
        stripped = line.strip()
        if stripped.startswith("- "):
            current = {}
            labels.append(current)
            stripped = stripped[2:].strip()
        elif current is None:
            errors.append(f"line {lineno}: content outside a list item: {raw!r}")
            continue
        if ":" not in stripped:
            errors.append(f"line {lineno}: no ':' present: {raw!r}")
            continue
        key, _, value = stripped.partition(":")
        current[key.strip()] = unquote(value)
    return labels, errors


def validate(labels: list[dict]) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    for i, label in enumerate(labels, start=1):
        name = label.get("name", "")
        if not name:
            errors.append(f"label #{i} has no name")
            continue
        if not NAME_RE.match(name):
            errors.append(f"{name!r}: names may use lowercase letters, digits and '/._-' only (prefix convention)")
        if name in seen:
            errors.append(f"{name!r}: duplicate name")
        seen.add(name)
        color = label.get("color", "")
        if not COLOR_RE.match(color):
            errors.append(f"{name!r}: color must be 6 hex digits without '#'; got {color!r}")
        if not label.get("description"):
            errors.append(f"{name!r}: description is empty (always say what the label means)")
    return errors


def gh(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["gh", *args], capture_output=True, text=True)


def existing_labels() -> dict[str, dict]:
    result = gh("label", "list", "--limit", "200", "--json", "name,color,description")
    if result.returncode != 0:
        print(f"gh label list failed: {result.stderr.strip()}", file=sys.stderr)
        sys.exit(1)
    return {label["name"]: label for label in json.loads(result.stdout or "[]")}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dry-run", action="store_true", help="print the definitions only; never calls gh")
    parser.add_argument("--prune", action="store_true", help="delete labels that are not in labels.yml")
    args = parser.parse_args()

    labels, parse_errors = parse_labels(LABELS_FILE.read_text(encoding="utf-8"))
    errors = parse_errors + validate(labels)
    if errors:
        for error in errors:
            print(f"ERROR .github/labels.yml: {error}")
        return 1
    print(f".github/labels.yml: loaded {len(labels)} label definition(s)")

    if args.dry_run:
        for label in labels:
            print(f"  {label['name']:<24} #{label['color']}  {label['description']}")
        print("\n--dry-run: nothing was synced to GitHub.")
        return 0

    current = existing_labels()
    created = updated = unchanged = deleted = 0
    for label in labels:
        name, color, description = label["name"], label["color"].upper(), label["description"]
        found = current.get(name)
        if found is None:
            result = gh("label", "create", name, "--color", color, "--description", description)
            action = "create"
            created += 1
        elif found["color"].upper() != color or (found.get("description") or "") != description:
            result = gh("label", "edit", name, "--color", color, "--description", description)
            action = "update"
            updated += 1
        else:
            unchanged += 1
            continue
        if result.returncode != 0:
            print(f"ERROR failed to {action} {name}: {result.stderr.strip()}", file=sys.stderr)
            return 1
        print(f"  {action}: {name}")

    if args.prune:
        defined = {label["name"] for label in labels}
        for name in sorted(set(current) - defined):
            result = gh("label", "delete", name, "--yes")
            if result.returncode != 0:
                print(f"ERROR failed to delete {name}: {result.stderr.strip()}", file=sys.stderr)
                return 1
            print(f"  delete: {name}")
            deleted += 1

    print(f"\ncreated {created} / updated {updated} / unchanged {unchanged} / deleted {deleted}")
    if not args.prune:
        print("Labels not in the file were left alone (use --prune to delete them).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
