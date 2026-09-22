#!/usr/bin/env python3
""".github/labels.yml の内容を GitHub のラベルに同期する。

    python3 scripts/sync_labels.py --dry-run      # 差分の確認のみ
    python3 scripts/sync_labels.py                # 実際に同期
    python3 scripts/sync_labels.py --prune        # 定義にないラベルも削除する

gh CLI と GH_TOKEN（または gh auth login 済み）が必要。
依存ライブラリなし（labels.yml は本スクリプト内の最小パーサで読む）。

安全側の既定として、定義にないラベルは削除しない。既存 Issue に付いた
ラベルを不用意に消さないため、--prune は明示的に指定したときだけ動く。
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
    """labels.yml のうち「- key: value」形式の部分集合だけを読む。"""
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
            errors.append(f"{lineno} 行目: リスト項目の外に内容がある: {raw!r}")
            continue
        if ":" not in stripped:
            errors.append(f"{lineno} 行目: ':' がない: {raw!r}")
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
            errors.append(f"{i} 番目のラベルに name がない")
            continue
        if not NAME_RE.match(name):
            errors.append(f"{name!r}: 名前は英小文字・数字・'/._-' のみ（プレフィックス規約のため）")
        if name in seen:
            errors.append(f"{name!r}: 名前が重複している")
        seen.add(name)
        color = label.get("color", "")
        if not COLOR_RE.match(color):
            errors.append(f"{name!r}: color は 6 桁の 16 進数（'#' なし）。実際: {color!r}")
        if not label.get("description"):
            errors.append(f"{name!r}: description が空（ラベルの意味は必ず書く）")
    return errors


def gh(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["gh", *args], capture_output=True, text=True)


def existing_labels() -> dict[str, dict]:
    result = gh("label", "list", "--limit", "200", "--json", "name,color,description")
    if result.returncode != 0:
        print(f"gh label list に失敗: {result.stderr.strip()}", file=sys.stderr)
        sys.exit(1)
    return {label["name"]: label for label in json.loads(result.stdout or "[]")}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dry-run", action="store_true", help="差分を表示するだけ（gh を呼ばない）")
    parser.add_argument("--prune", action="store_true", help="labels.yml にないラベルを削除する")
    args = parser.parse_args()

    labels, parse_errors = parse_labels(LABELS_FILE.read_text(encoding="utf-8"))
    errors = parse_errors + validate(labels)
    if errors:
        for error in errors:
            print(f"ERROR .github/labels.yml: {error}")
        return 1
    print(f".github/labels.yml: {len(labels)} 件のラベル定義を読み込んだ")

    if args.dry_run:
        for label in labels:
            print(f"  {label['name']:<24} #{label['color']}  {label['description']}")
        print("\n--dry-run のため GitHub への同期は行わない。")
        return 0

    current = existing_labels()
    created = updated = unchanged = deleted = 0
    for label in labels:
        name, color, description = label["name"], label["color"].upper(), label["description"]
        found = current.get(name)
        if found is None:
            result = gh("label", "create", name, "--color", color, "--description", description)
            action = "作成"
            created += 1
        elif found["color"].upper() != color or (found.get("description") or "") != description:
            result = gh("label", "edit", name, "--color", color, "--description", description)
            action = "更新"
            updated += 1
        else:
            unchanged += 1
            continue
        if result.returncode != 0:
            print(f"ERROR {name} の{action}に失敗: {result.stderr.strip()}", file=sys.stderr)
            return 1
        print(f"  {action}: {name}")

    if args.prune:
        defined = {label["name"] for label in labels}
        for name in sorted(set(current) - defined):
            result = gh("label", "delete", name, "--yes")
            if result.returncode != 0:
                print(f"ERROR {name} の削除に失敗: {result.stderr.strip()}", file=sys.stderr)
                return 1
            print(f"  削除: {name}")
            deleted += 1

    print(f"\n作成 {created} / 更新 {updated} / 変更なし {unchanged} / 削除 {deleted}")
    if not args.prune:
        print("定義にないラベルは残してある（消すなら --prune）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
