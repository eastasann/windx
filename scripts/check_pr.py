#!/usr/bin/env python3
"""Validate the traceability of a pull request body.

Run from CI (.github/workflows/pr-checks.yml). Also usable locally:

    PR_BODY="$(cat /tmp/body.md)" PR_LABELS="type/task" python3 scripts/check_pr.py

The conventions enforced (docs/process/05-issues-roadmap.md):
  - A PR closes exactly one Issue (`Closes #n`)
  - If it came from a design doc, `Design doc: DD-xxxx`; otherwise say so explicitly

Escape hatch: a PR labelled `skip-traceability` is not checked, for the occasional
release PR that is not tied to an Issue.
"""
from __future__ import annotations

import os
import re
import sys

CLOSES_RE = re.compile(r"\b(?:closes|fixes|resolves)\s+#(\d+)\b", re.I)
DESIGN_RE = re.compile(r"^\s*[-*]?\s*Design doc\s*:\s*(.*)$", re.M | re.I)
DD_RE = re.compile(r"\bDD-\d{4}\b")
NOT_NEEDED_RE = re.compile(r"\b(?:not needed|not required|none|n/?a)\b", re.I)
SKIP_LABEL = "skip-traceability"


def strip_comments(text: str) -> str:
    """Treat an HTML comment that was never filled in as empty."""
    return re.sub(r"<!--.*?-->", "", text, flags=re.S)


def check(body: str, labels: set[str], is_draft: bool) -> list[str]:
    errors: list[str] = []
    if SKIP_LABEL in labels:
        return errors
    body = strip_comments(body)

    closes = CLOSES_RE.findall(body)
    if not closes:
        errors.append(
            "the PR body has no `Closes #<issue>`. The rule is 1 PR = 1 Issue."
            f"\n        To make an exception, apply the `{SKIP_LABEL}` label."
        )
    elif len(set(closes)) > 1 and not is_draft:
        errors.append(
            f"several `Closes` entries (#{', #'.join(sorted(set(closes)))})."
            " Split it so that 1 PR = 1 Issue (docs/process/05-issues-roadmap.md)."
        )

    design = DESIGN_RE.search(body)
    value = design.group(1).strip() if design else ""
    if not value:
        errors.append(
            "the PR body has no `Design doc:` line, or it is empty."
            "\n        Write `Design doc: DD-xxxx`, or `Design doc: not needed (<reason>)`."
        )
    elif not DD_RE.search(value) and not NOT_NEEDED_RE.search(value):
        errors.append(
            f"cannot interpret the `Design doc:` value: {value!r}"
            "\n        Use either `DD-xxxx` or `not needed (<reason>)`."
        )
    return errors


def main() -> int:
    body = os.environ.get("PR_BODY", "")
    labels = {label.strip() for label in os.environ.get("PR_LABELS", "").split(",") if label.strip()}
    is_draft = os.environ.get("PR_DRAFT", "false").lower() == "true"

    if not body.strip():
        print("ERROR the PR body is empty. Fill in the template.")
        return 1

    errors = check(body, labels, is_draft)
    for error in errors:
        print(f"ERROR {error}")
    if errors:
        print("\nPR template: .github/pull_request_template.md")
        return 1
    print("OK traceability checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
