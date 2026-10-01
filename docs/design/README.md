# Design Docs Index

The design documents (DDs). Conventions are in
[`docs/process/03-design-doc.md`](../process/03-design-doc.md).

```bash
python3 scripts/new_doc.py design   "<title>" --slug <english-slug>   # a normal DD
python3 scripts/new_doc.py onepager "<title>" --slug <english-slug>   # the light form
python3 scripts/validate_docs.py                                     # before submitting
```

## States

| status | Meaning |
| --- | --- |
| `draft` | Being written, not yet up for review |
| `in-review` | Under review (a PR is open) |
| `approved` | Cleared G1; implementation may begin |
| `implemented` | Built and updated to as-built |
| `rejected` | Rejected (kept as a record, never deleted) |
| `superseded` | Replaced by a newer DD |

## The documents

| ID | Title | status | Owner | Updated |
| --- | --- | --- | --- | --- |
| [DD-0001](DD-0001-development-process.md) | Standardise the AI-driven development process | `approved` | @eastasann | 2026-10-01 |
