---
name: decompose
description: Break an approved design doc into implementation Issues and file them. Use when asked to decompose a DD, cut implementation tasks, or create Issues, or once a design doc reaches approved and implementation begins.
---

# Decomposing a design doc into Issues

Conventions: `docs/process/05-issues-roadmap.md`, `docs/process/07-definition-of-done.md`

---

## Preconditions — **do not decompose unless these hold**

```bash
grep -E '^(id|status|owner|tracking_issue):' docs/design/DD-xxxx-*.md
python3 scripts/validate_docs.py
```

- `status: approved`. Never decompose a doc at `draft` or `in-review`
- **No unresolved Decision Point** (`validate_docs.py` enforces this)

If they do not hold, do not decompose — report that the doc has not cleared G1.

---

## Principles

### Granularity

**1 Issue = 1 verifiable outcome.** Aim for half a day to two days (1–3 AI sessions).

| Too big | Too small |
| --- | --- |
| More than five acceptance criteria | You cannot write an acceptance criterion |
| A title like "improve X" or "handle Y" | One line of change |
| The PR would exceed 500 lines | It delivers no value on its own |

### Split along value, not phase

- ❌ design Issue → build Issue → test Issue
- ✅ endpoint A → endpoint B → migration script

**Never split tests into their own Issue.** Tests are part of each Issue's completion.

### Dependencies

Write `Depends on #n` in the body and **run dependent Issues serially**. More parallel units
make the whole thing faster, but ignoring dependencies creates rework.

---

## What every Issue must contain

```markdown
Design doc: DD-xxxx

## What to do
<one to three sentences, at a granularity where you can say "implement X">

## Acceptance criteria
- **AC-1**: Given <precondition>, When <action>, Then <expected result>
  - Verify: `<command>`

## Affected surface
- May touch: <copied from the doc's Context for Agents>
- Must not touch:
- Follow this pattern:

Depends on #<n>   <!-- if any -->
```

**Copy the acceptance criteria from the doc.** Do not invent new ones. If a needed AC is
missing from the doc, that is a gap in the doc — add it there, or raise it as a Decision Point.

---

## Labels

| Label | How to apply |
| --- | --- |
| `type/task` | Required |
| `priority/*` | Inherit from the doc; `priority/p2` if unclear |
| `stage/g2-build` | The implementation stage |
| `size/*` | The estimate. **Split anything that comes out `size/xl`** |
| `risk/high` | When it involves security, billing, data migration, or irreversible operations |
| **`agent/ready`** | **Do not apply it. A human does** |

### Why you never apply `agent/ready`

It is the single switch that opens AI autonomous execution, and **a human throws it**.
Applying it yourself closes a loop where you mark a vague Issue ready and then implement your
own interpretation of it.

Instead, **prepare the Issue until it satisfies the Definition of Ready**, then ask a human
whether the label may be applied.

---

## Filing

1. Start from the doc's `Implementation Plan` (it will not always be usable as is)
2. Expand each row into an Issue body in the shape above
3. File them (`mcp__github__issue_write`, or `gh issue create`)
4. Set the doc's front matter **`tracking_issue`** to the parent Issue number
5. Add the filed Issue numbers to the doc's `Implementation Plan` table
6. Re-check the dependencies once the numbers are assigned

---

## Always include in your final report

1. The Issues you filed — number, title, size, dependencies
2. The execution order, naming anything that must be serial
3. **That you are asking whether `agent/ready` may be applied**
4. Anything you had to fill in because the doc did not say (report it as a gap in the doc)

---

## Never

- Decompose a doc that is not `approved`
- Apply `agent/ready` yourself
- Create an Issue with no acceptance criteria
- Turn work the doc does not describe into an Issue (scope expansion)
- Split tests into a standalone Issue
- Start implementing while decomposing
