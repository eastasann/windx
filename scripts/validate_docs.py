#!/usr/bin/env python3
"""Validate the structure of design docs and ADRs.

Checks mechanically that the process standard (docs/process/03-design-doc.md and
08-adr.md) is being followed. Run from CI (.github/workflows/docs-lint.yml).

    python3 scripts/validate_docs.py            # everything
    python3 scripts/validate_docs.py docs/design/DD-0001-foo.md   # one file

No third-party dependencies: front matter is read by the minimal parser below.
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DESIGN_DIR = ROOT / "docs" / "design"
ADR_DIR = ROOT / "docs" / "adr"

# --- Schema ----------------------------------------------------------------

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

# In these states no Decision Point may be left unresolved
SETTLED_DESIGN = {"approved", "implemented"}

PLACEHOLDERS = ["DD-0000", "ADR-0000", "0000-00-00", "<github-handle>"]

# The decision line. Use [ \t]* rather than \s*, which would cross a newline and let an
# empty decision match the next line of the document.
DECISION_RE = re.compile(r"^[ \t]*-?[ \t]*\*\*Decision\*\*[ \t]*:[ \t]*(.*)$", re.M)
BAD_OUTCOMES_HEADING = "Bad outcomes"
RECOMMENDATION_MARKER = "**AI recommendation**"

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


# --- Front matter parser (only the YAML subset this schema uses) ------------

def parse_front_matter(text: str) -> tuple[dict | None, str, str | None]:
    """Return (data, body, error)."""
    if not text.startswith("---\n"):
        return None, text, "no front matter (line 1 must be '---')"
    end = text.find("\n---\n", 3)
    if end == -1:
        return None, text, "front matter is not closed (no terminating '---')"
    raw, body = text[4:end], text[end + 5:]

    data: dict = {}
    pending_key: str | None = None
    for lineno, line in enumerate(raw.split("\n"), start=2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith((" ", "\t")):  # an item of a block list
            item = line.strip()
            if item.startswith("- ") and pending_key:
                data.setdefault(pending_key, [])
                if isinstance(data[pending_key], list):
                    data[pending_key].append(scalar(item[2:].strip()))
                continue
            return None, body, f"cannot parse front matter line {lineno}: {line!r}"
        if ":" not in line:
            return None, body, f"front matter line {lineno} has no ':': {line!r}"
        key, _, value = line.partition(":")
        key, value = key.strip(), value.strip()
        if value == "":
            data[key] = []          # a block list follows, or it is empty
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


# --- Individual checks -----------------------------------------------------

def headings_of(body: str) -> list[str]:
    return [m.group(1).strip() for m in re.finditer(r"^##\s+(.+?)\s*$", body, re.M)]


def check_headings(path: Path, body: str, kind: str, rep: Report) -> None:
    required = HEADINGS[kind]
    found = headings_of(body)
    missing = [h for h in required if h not in found]
    if missing:
        rep.error(path, f"missing required heading(s): {', '.join('## ' + m for m in missing)}")
    present = [h for h in found if h in required]
    canonical = [h for h in required if h in found]
    if present != canonical:
        rep.error(path, f"headings are out of order; expected: {' -> '.join(canonical)}")


def check_common(path: Path, data: dict, keys: list[str], rep: Report) -> None:
    for key in keys:
        if key not in data:
            rep.error(path, f"front matter is missing '{key}'")
    if data.get("title") in (None, "", []):
        rep.error(path, "front matter 'title' is empty")


def check_placeholders(path: Path, text: str, rep: Report) -> None:
    for ph in PLACEHOLDERS:
        if ph in text:
            rep.error(path, f"template placeholder '{ph}' is still present")


def body_section(body: str, heading: str) -> str:
    m = re.search(rf"^##\s+{re.escape(heading)}\s*$(.*?)(?=^##\s|\Z)", body, re.M | re.S)
    return m.group(1) if m else ""


def check_decision_points(path: Path, body: str, status: str, rep: Report) -> None:
    """No Decision Point may be unresolved in an approved or implemented doc."""
    section = body_section(body, "Decision Points")
    blocks = re.split(r"^###\s+(DP-\d+[^\n]*)$", section, flags=re.M)
    if len(blocks) < 3:
        if status in SETTLED_DESIGN and "none" not in section.lower():
            rep.warn(path, "Decision Points has no DP-n heading (say 'none' if nothing needs deciding)")
        return
    for title, block in zip(blocks[1::2], blocks[2::2]):
        decided = DECISION_RE.search(block)
        value = (decided.group(1).strip() if decided else "")
        value = re.sub(r"<!--.*?-->", "", value, flags=re.S).strip()
        if not decided:
            rep.error(path, f"'{title}' has no '- **Decision**:' line")
        elif status in SETTLED_DESIGN and not value:
            rep.error(path, f"status={status} but '{title}' has an empty **Decision** (G1 not cleared)")
        if RECOMMENDATION_MARKER not in block:
            rep.warn(path, f"'{title}' has no {RECOMMENDATION_MARKER}")


def check_acceptance(path: Path, body: str, rep: Report) -> None:
    section = body_section(body, "Acceptance Criteria")
    if not re.findall(r"\*\*AC-\d+\*\*", section):
        rep.error(path, "Acceptance Criteria has no '**AC-n**' entries")
        return
    if "Verify:" not in section:
        rep.error(path, "Acceptance Criteria has no means of verification ('Verify: <command>')")


def check_supersede(path: Path, data: dict, terminal: str, rep: Report) -> None:
    if data.get("status") == terminal and not data.get("superseded_by"):
        rep.error(path, f"status={terminal} but superseded_by is empty")


# --- Per-kind validation ---------------------------------------------------

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
        rep.error(path, f"id is not in 'DD-nnnn' form: {doc_id!r}")
    elif not path.name.startswith(doc_id + "-"):
        rep.error(path, f"filename does not match id (must start with {doc_id}-)")

    kind = data.get("type")
    if kind not in HEADINGS or kind == "adr":
        rep.error(path, f"type must be 'design-doc' or 'one-pager'; got {kind!r}")
        kind = "design-doc"

    status = data.get("status")
    if status not in DESIGN_STATUSES:
        rep.error(path, f"invalid status {status!r} (one of {sorted(DESIGN_STATUSES)})")

    for key in ("created", "updated"):
        value = data.get(key)
        if not (isinstance(value, str) and DATE_RE.fullmatch(value)):
            rep.error(path, f"{key} must be YYYY-MM-DD; got {value!r}")

    owner = data.get("owner")
    if not (isinstance(owner, str) and owner.startswith("@")):
        rep.error(path, f"owner must be '@handle'; got {owner!r}")

    issue = data.get("tracking_issue")
    if issue is not None and not (isinstance(issue, str) and ISSUE_RE.fullmatch(issue)):
        rep.error(path, f"tracking_issue must be '#123' or null; got {issue!r}")

    check_headings(path, body, kind, rep)
    check_decision_points(path, body, str(status), rep)
    check_acceptance(path, body, rep)
    check_supersede(path, data, "superseded", rep)

    if status in SETTLED_DESIGN and not data.get("reviewers"):
        rep.error(path, f"status={status} but reviewers is empty (nobody approved it)")
    if status == "implemented" and data.get("tracking_issue") is None:
        rep.warn(path, "status=implemented but tracking_issue is unset")

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
        rep.error(path, f"id is not in 'ADR-nnnn' form: {doc_id!r}")
    elif not path.name.startswith(doc_id + "-"):
        rep.error(path, f"filename does not match id (must start with {doc_id}-)")

    status = data.get("status")
    if status not in ADR_STATUSES:
        rep.error(path, f"invalid status {status!r} (one of {sorted(ADR_STATUSES)})")

    date = data.get("date")
    if not (isinstance(date, str) and DATE_RE.fullmatch(date)):
        rep.error(path, f"date must be YYYY-MM-DD; got {date!r}")

    if not data.get("deciders"):
        rep.error(path, "deciders is empty (nobody is accountable for the decision)")

    check_headings(path, body, "adr", rep)
    check_supersede(path, data, "superseded", rep)

    # Consequences must name the bad outcomes (docs/process/08-adr.md)
    consequences = body_section(body, "Consequences")
    if BAD_OUTCOMES_HEADING not in consequences:
        rep.error(path, f"Consequences has no '{BAD_OUTCOMES_HEADING} / costs accepted' section")
    else:
        bad = consequences.split(BAD_OUTCOMES_HEADING, 1)[1].split("### ", 1)[0]
        items = [ln for ln in bad.splitlines() if ln.strip().startswith("- ") and len(ln.strip()) > 3]
        if len(items) < 2:
            rep.error(path, "list two or more bad outcomes (there is no decision without a trade-off)")

    return doc_id


def validate_index(index: Path, docs: dict[str, Path], pattern: str, rep: Report) -> None:
    """Check the index README against the files on disk."""
    if not index.exists():
        rep.error(index, "index file is missing")
        return
    text = index.read_text(encoding="utf-8")
    linked = set(re.findall(pattern, text))
    actual = {p.name for p in docs.values()}
    for missing in sorted(actual - linked):
        rep.error(index, f"doc is not listed in the index: {missing}")
    for dangling in sorted(linked - actual):
        rep.error(index, f"index links to a file that does not exist: {dangling}")


def check_unique(ids: list[tuple[str, Path]], rep: Report) -> None:
    seen: dict[str, Path] = {}
    for doc_id, path in ids:
        if doc_id in seen:
            rep.error(path, f"duplicate id {doc_id} (same as {rel(seen[doc_id])})")
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

    print(f"\nvalidated {total} file(s): {len(rep.errors)} error(s), {len(rep.warnings)} warning(s)")
    if rep.errors:
        print("Conventions: docs/process/03-design-doc.md and docs/process/08-adr.md")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
