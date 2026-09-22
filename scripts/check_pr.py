#!/usr/bin/env python3
"""PR 本文のトレーサビリティを検証する。

CI (.github/workflows/pr-checks.yml) から実行される。ローカルでも試せる:

    PR_BODY="$(cat /tmp/body.md)" PR_LABELS="type/task" python3 scripts/check_pr.py

検証する規約（docs/process/05-issues-roadmap.md）:
  - PR は 1 つの Issue を閉じる（`Closes #n`）
  - design doc 由来なら `Design doc: DD-xxxx`、不要なら「不要（理由）」と明記する

逃げ道: `skip-traceability` ラベルを付けた PR は検証をスキップする
（リリース用 PR など、Issue に紐づかない例外のため）。
"""
from __future__ import annotations

import os
import re
import sys

CLOSES_RE = re.compile(r"\b(?:closes|fixes|resolves)\s+#(\d+)\b", re.I)
DESIGN_RE = re.compile(r"^\s*[-*]?\s*Design doc\s*[:：]\s*(.*)$", re.M | re.I)
DD_RE = re.compile(r"\bDD-\d{4}\b")
SKIP_LABEL = "skip-traceability"


def strip_comments(text: str) -> str:
    """埋められなかった HTML コメントを空扱いにする。"""
    return re.sub(r"<!--.*?-->", "", text, flags=re.S)


def check(body: str, labels: set[str], is_draft: bool) -> list[str]:
    errors: list[str] = []
    if SKIP_LABEL in labels:
        return errors
    body = strip_comments(body)

    closes = CLOSES_RE.findall(body)
    if not closes:
        errors.append(
            "PR 本文に `Closes #<issue>` がない。1 PR = 1 Issue が原則です。"
            f"\n        例外扱いにするなら `{SKIP_LABEL}` ラベルを付けてください。"
        )
    elif len(set(closes)) > 1 and not is_draft:
        errors.append(
            f"`Closes` が複数ある（#{', #'.join(sorted(set(closes)))}）。"
            "1 PR = 1 Issue に分割してください（docs/process/05-issues-roadmap.md）。"
        )

    design = DESIGN_RE.search(body)
    value = design.group(1).strip() if design else ""
    if not value:
        errors.append(
            "PR 本文に `Design doc:` の行がないか、空欄です。"
            "\n        DD 由来なら `Design doc: DD-xxxx`、不要なら `Design doc: 不要（<理由>）` と書いてください。"
        )
    elif not DD_RE.search(value) and "不要" not in value and "なし" not in value:
        errors.append(
            f"`Design doc:` の値を解釈できません: {value!r}"
            "\n        `DD-xxxx` か `不要（<理由>）` の形式で書いてください。"
        )
    return errors


def main() -> int:
    body = os.environ.get("PR_BODY", "")
    labels = {label.strip() for label in os.environ.get("PR_LABELS", "").split(",") if label.strip()}
    is_draft = os.environ.get("PR_DRAFT", "false").lower() == "true"

    if not body.strip():
        print("ERROR PR 本文が空です。テンプレートを埋めてください。")
        return 1

    errors = check(body, labels, is_draft)
    for error in errors:
        print(f"ERROR {error}")
    if errors:
        print("\nPR テンプレート: .github/pull_request_template.md")
        return 1
    print("OK トレーサビリティの検証を通過しました。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
