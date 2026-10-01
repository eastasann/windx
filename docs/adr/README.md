# ADR Index

The decision records. Conventions are in [`docs/process/08-adr.md`](../process/08-adr.md).

```bash
python3 scripts/new_doc.py adr "<the decision, in active voice>" --slug <english-slug>
python3 scripts/validate_docs.py
```

**An ADR is never rewritten once accepted.** When a decision changes, write a new ADR and
mark the old one `superseded` (the `status` and `superseded_by` lines are the only edit
ever permitted).

## States

| status | Meaning |
| --- | --- |
| `proposed` | Proposed (PR under review) |
| `accepted` | Adopted. Current policy |
| `rejected` | Rejected (kept as a record) |
| `superseded` | Replaced by a new ADR (see `superseded_by`) |
| `deprecated` | Its premise disappeared |

## The records

| ID | Title | status | Date |
| --- | --- | --- | --- |
| [ADR-0001](ADR-0001-github-as-single-source-of-truth.md) | GitHub is the single source of truth; no decisions live in external tools | `accepted` | 2026-09-22 |
| [ADR-0002](ADR-0002-design-doc-as-agent-context.md) | Design docs are structured as context input for AI agents | `accepted` | 2026-09-22 |
| [ADR-0003](ADR-0003-human-gates-at-decision-points.md) | Human review is limited to Decision Points, not whole docs | `accepted` | 2026-09-22 |
| [ADR-0004](ADR-0004-projects-automation-owner-agnostic.md) | Projects automation is implemented independently of project ownership type | `accepted` | 2026-10-01 |
