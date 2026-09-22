#!/usr/bin/env python3
"""design doc / ADR の構造を検証する。

プロセス標準（docs/process/03-design-doc.md, 08-adr.md）が守られているかを
機械的にチェックする。CI (.github/workflows/docs-lint.yml) から実行される。

    python3 scripts/validate_docs.py            # 全件検証
    python3 scripts/validate_docs.py docs/design/DD-0001-foo.md   # 個別検証

依存ライブラリなし（front matter は本スクリプト内の最小パーサで読む）。
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DESIGN_DIR = ROOT / "docs" / "design"
ADR_DIR = ROOT / "docs" / "adr"

# --- スキーマ定義 -----------------------------------------------------------

DESIGN_STATUSES = {"draft", "in-review", "approved", "implemented", "rejected", "superseded"}
ADR_STATUSES = {"proposed", "accepted", "rejected", "superseded", "deprecated"}

DESIGN_KEYS = [
    "id", "title", "type", "status", "owner", "reviewers",
    "created", "updated", "tracking_issue", "related_adrs",
    "supersedes", "superseded_by",
]
ADR_KEYS = ["id", "title", "status", "date", "deciders", "related_docs", "supersedes", "superseded_by"]

HEADINGS = {
    "design-doc": [
        "Summary", "Context", "Goals", "Non-Goals", "Decision Points", "Design",
        "Alternatives Considered", "Cross-cutting Concerns", "Acceptance Criteria",
        "Implementation Plan", "Context for Agents", "Open Questions",
    ],
    "one-pager": [
        "Summary", "Context", "Non-Goals", "Decision Points", "Design",
        "Alternatives Considered", "Acceptance Criteria", "Context for Agents",
    ],
    "adr": ["Context", "Decision", "Consequences", "Alternatives Considered"],
}

# 承認済み扱いの状態では、未解決の Decision Point が残っていてはならない
SETTLED_DESIGN = {"approved", "implemented"}

PLACEHOLDERS = ["DD-0000", "ADR-0000", "0000-00-00", "<github-handle>"]

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ISSUE_RE = re.compile(r"^#\d+$")


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def error(self, path: Path, msg: str) -> None:
        self.errors.append(f"{rel(path)}: {msg}")

    def warn(self, path: Path, msg: str) -> None:
        self.warnings.append(f"{rel(path)}: {msg}")


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


# --- front matter パーサ（YAML のうち本スキーマが使う部分集合だけ） ---------

def parse_front_matter(text: str) -> tuple[dict | None, str, str | None]:
    """(data, body, error) を返す。"""
    if not text.startswith("---\n"):
        return None, text, "front matter がない（1 行目が '---' で始まること）"
    end = text.find("\n---\n", 3)
    if end == -1:
        return None, text, "front matter が閉じていない（'---' の終端がない）"
    raw, body = text[4:end], text[end + 5:]

    data: dict = {}
    pending_key: str | None = None
    for lineno, line in enumerate(raw.split("\n"), start=2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith((" ", "\t")):  # ブロックリストの要素
            item = line.strip()
            if item.startswith("- ") and pending_key:
                data.setdefault(pending_key, [])
                if isinstance(data[pending_key], list):
                    data[pending_key].append(scalar(item[2:].strip()))
                continue
            return None, body, f"front matter {lineno} 行目を解釈できない: {line!r}"
        if ":" not in line:
            return None, body, f"front matter {lineno} 行目に ':' がない: {line!r}"
        key, _, value = line.partition(":")
        key, value = key.strip(), value.strip()
        if value == "":
            data[key] = []          # 次行以降のブロックリスト、または空
            pending_key = key
        else:
            data[key] = scalar(value)
            pending_key = None
    return data, body, None


def scalar(value: str):
    value = value.strip()
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        return [scalar(v) for v in inner.split(",")] if inner else []
    if value in ("null", "~", ""):
        return None
    if value in ("true", "false"):
        return value == "true"
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


# --- 個別チェック -----------------------------------------------------------

def headings_of(body: str) -> list[str]:
    return [m.group(1).strip() for m in re.finditer(r"^##\s+(.+?)\s*$", body, re.M)]


def check_headings(path: Path, body: str, kind: str, rep: Report) -> None:
    required = HEADINGS[kind]
    found = headings_of(body)
    missing = [h for h in required if h not in found]
    if missing:
        rep.error(path, f"必須の見出しがない: {', '.join('## ' + m for m in missing)}")
    present = [h for h in found if h in required]
    canonical = [h for h in required if h in found]
    if present != canonical:
        rep.error(path, f"見出しの順序が規約と違う。期待: {' → '.join(canonical)}")


def check_common(path: Path, data: dict, keys: list[str], rep: Report) -> None:
    for key in keys:
        if key not in data:
            rep.error(path, f"front matter に '{key}' がない")
    if data.get("title") in (None, "", []):
        rep.error(path, "front matter の title が空")


def check_placeholders(path: Path, text: str, rep: Report) -> None:
    for ph in PLACEHOLDERS:
        if ph in text:
            rep.error(path, f"テンプレートのプレースホルダ '{ph}' が残っている")


# 決定行。[ \t]* を使う（\s* は改行を跨ぎ、空の決定が次行を拾ってしまう）
DECISION_RE = re.compile(r"^[ \t]*-?[ \t]*\*\*決定\*\*[ \t]*[:：][ \t]*(.*)$", re.M)


def check_decision_points(path: Path, body: str, status: str, rep: Report) -> None:
    """approved / implemented の doc に未決の Decision Point を残さない。"""
    section = body_section(body, "Decision Points")
    blocks = re.split(r"^###\s+(DP-\d+[^\n]*)$", section, flags=re.M)
    if len(blocks) < 3:
        if status in SETTLED_DESIGN and "なし" not in section:
            rep.warn(path, "Decision Points に DP-n 見出しがない（判断不要なら『なし』と明記する）")
        return
    for title, block in zip(blocks[1::2], blocks[2::2]):
        decided = DECISION_RE.search(block)
        value = (decided.group(1).strip() if decided else "")
        value = re.sub(r"<!--.*?-->", "", value, flags=re.S).strip()
        if not decided:
            rep.error(path, f"'{title}' に '- **決定**:' の行がない")
        elif status in SETTLED_DESIGN and not value:
            rep.error(path, f"status={status} だが '{title}' の **決定** が空（G1 未通過）")
        if "**AI の推奨**" not in block:
            rep.warn(path, f"'{title}' に **AI の推奨** がない")


def body_section(body: str, heading: str) -> str:
    m = re.search(rf"^##\s+{re.escape(heading)}\s*$(.*?)(?=^##\s|\Z)", body, re.M | re.S)
    return m.group(1) if m else ""


def check_acceptance(path: Path, body: str, rep: Report) -> None:
    section = body_section(body, "Acceptance Criteria")
    acs = re.findall(r"\*\*AC-\d+\*\*", section)
    if not acs:
        rep.error(path, "Acceptance Criteria に '**AC-n**' 形式の項目がない")
        return
    if "検証:" not in section and "検証：" not in section:
        rep.error(path, "Acceptance Criteria に検証手段（'検証: <コマンド>'）がない")


def check_supersede(path: Path, data: dict, terminal: str, rep: Report) -> None:
    if data.get("status") == terminal and not data.get("superseded_by"):
        rep.error(path, f"status={terminal} だが superseded_by が空")


# --- ファイル種別ごとの検証 -------------------------------------------------

def validate_design(path: Path, rep: Report) -> str | None:
    text = path.read_text(encoding="utf-8")
    data, body, err = parse_front_matter(text)
    if err:
        rep.error(path, err)
        return None
    assert data is not None

    check_common(path, data, DESIGN_KEYS, rep)
    check_placeholders(path, text, rep)

    doc_id = str(data.get("id", ""))
    if not re.fullmatch(r"DD-\d{4}", doc_id):
        rep.error(path, f"id が 'DD-nnnn' 形式でない: {doc_id!r}")
    elif not path.name.startswith(doc_id + "-"):
        rep.error(path, f"ファイル名が id と一致しない（{doc_id}-... であること）")

    kind = data.get("type")
    if kind not in HEADINGS or kind == "adr":
        rep.error(path, f"type は 'design-doc' か 'one-pager'。実際: {kind!r}")
        kind = "design-doc"

    status = data.get("status")
    if status not in DESIGN_STATUSES:
        rep.error(path, f"status が不正: {status!r}（{sorted(DESIGN_STATUSES)}）")

    for key in ("created", "updated"):
        value = data.get(key)
        if not (isinstance(value, str) and DATE_RE.fullmatch(value)):
            rep.error(path, f"{key} は YYYY-MM-DD 形式であること。実際: {value!r}")

    owner = data.get("owner")
    if not (isinstance(owner, str) and owner.startswith("@")):
        rep.error(path, f"owner は '@handle' 形式であること。実際: {owner!r}")

    issue = data.get("tracking_issue")
    if issue is not None and not (isinstance(issue, str) and ISSUE_RE.fullmatch(issue)):
        rep.error(path, f"tracking_issue は '#123' か null。実際: {issue!r}")

    check_headings(path, body, kind, rep)
    check_decision_points(path, body, str(status), rep)
    check_acceptance(path, body, rep)
    check_supersede(path, data, "superseded", rep)

    if status in SETTLED_DESIGN and not data.get("reviewers"):
        rep.error(path, f"status={status} だが reviewers が空（誰も承認していない）")
    if status == "implemented" and data.get("tracking_issue") is None:
        rep.warn(path, "status=implemented だが tracking_issue が未設定")

    return doc_id


def validate_adr(path: Path, rep: Report) -> str | None:
    text = path.read_text(encoding="utf-8")
    data, body, err = parse_front_matter(text)
    if err:
        rep.error(path, err)
        return None
    assert data is not None

    check_common(path, data, ADR_KEYS, rep)
    check_placeholders(path, text, rep)

    doc_id = str(data.get("id", ""))
    if not re.fullmatch(r"ADR-\d{4}", doc_id):
        rep.error(path, f"id が 'ADR-nnnn' 形式でない: {doc_id!r}")
    elif not path.name.startswith(doc_id + "-"):
        rep.error(path, f"ファイル名が id と一致しない（{doc_id}-... であること）")

    status = data.get("status")
    if status not in ADR_STATUSES:
        rep.error(path, f"status が不正: {status!r}（{sorted(ADR_STATUSES)}）")

    date = data.get("date")
    if not (isinstance(date, str) and DATE_RE.fullmatch(date)):
        rep.error(path, f"date は YYYY-MM-DD 形式であること。実際: {date!r}")

    if not data.get("deciders"):
        rep.error(path, "deciders が空（決定の責任者が不明）")

    check_headings(path, body, "adr", rep)
    check_supersede(path, data, "superseded", rep)

    # Consequences に「悪い結果」を必ず書かせる（docs/process/08-adr.md）
    consequences = body_section(body, "Consequences")
    if "悪い結果" not in consequences:
        rep.error(path, "Consequences に『悪い結果 / 引き受けたコスト』の節がない")
    else:
        bad = consequences.split("悪い結果", 1)[1]
        bad = bad.split("### ", 1)[0]
        items = [ln for ln in bad.splitlines() if ln.strip().startswith("- ") and len(ln.strip()) > 3]
        if len(items) < 2:
            rep.error(path, "『悪い結果』は 2 項目以上書くこと（トレードオフのない決定は存在しない）")

    return doc_id


def validate_index(index: Path, docs: dict[str, Path], pattern: str, rep: Report) -> None:
    """索引 README と実ファイルの整合を検証する。"""
    if not index.exists():
        rep.error(index, "索引ファイルがない")
        return
    text = index.read_text(encoding="utf-8")
    linked = set(re.findall(pattern, text))
    actual = {p.name for p in docs.values()}
    for missing in sorted(actual - linked):
        rep.error(index, f"索引に載っていない doc がある: {missing}")
    for dangling in sorted(linked - actual):
        rep.error(index, f"索引のリンク先が存在しない: {dangling}")


def check_unique(ids: list[tuple[str, Path]], rep: Report) -> None:
    seen: dict[str, Path] = {}
    for doc_id, path in ids:
        if doc_id in seen:
            rep.error(path, f"id が重複している: {doc_id}（{rel(seen[doc_id])} と同じ）")
        else:
            seen[doc_id] = path


def main(argv: list[str]) -> int:
    rep = Report()
    targets = [Path(a).resolve() for a in argv[1:]]

    design_files = sorted(DESIGN_DIR.glob("DD-*.md")) if DESIGN_DIR.exists() else []
    adr_files = sorted(ADR_DIR.glob("ADR-*.md")) if ADR_DIR.exists() else []
    if targets:
        design_files = [p for p in design_files if p in targets]
        adr_files = [p for p in adr_files if p in targets]

    design_ids, adr_ids = [], []
    design_docs: dict[str, Path] = {}
    adr_docs: dict[str, Path] = {}

    for path in design_files:
        doc_id = validate_design(path, rep)
        if doc_id:
            design_ids.append((doc_id, path))
            design_docs[doc_id] = path
    for path in adr_files:
        doc_id = validate_adr(path, rep)
        if doc_id:
            adr_ids.append((doc_id, path))
            adr_docs[doc_id] = path

    check_unique(design_ids, rep)
    check_unique(adr_ids, rep)

    if not targets:
        validate_index(DESIGN_DIR / "README.md", design_docs, r"\((DD-\d{4}-[^)]+\.md)\)", rep)
        validate_index(ADR_DIR / "README.md", adr_docs, r"\((ADR-\d{4}-[^)]+\.md)\)", rep)

    total = len(design_files) + len(adr_files)
    for warning in rep.warnings:
        print(f"WARN  {warning}")
    for error in rep.errors:
        print(f"ERROR {error}")

    print(f"\n{total} 件を検証: エラー {len(rep.errors)} 件 / 警告 {len(rep.warnings)} 件")
    if rep.errors:
        print("規約は docs/process/03-design-doc.md と docs/process/08-adr.md を参照。")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
