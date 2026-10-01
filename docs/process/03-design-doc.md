# 03. Design doc standard

## What we keep from Google's design docs, and what we change

| | Google's design doc | Here | Why |
| --- | --- | --- | --- |
| Form | Prose (avoiding bullet dumps) | **Kept** | Prose is what detects vagueness |
| Goals / Non-goals | Required | **Kept, strengthened** | Non-Goals directly suppress AI scope creep |
| Alternatives Considered | Required (often lip service) | **Strengthened** | An AI can actually write three. Drop the pretence |
| Cross-cutting concerns | Required | **Kept** | Security / privacy / observability / cost |
| Length | 3–10 pages | **1–5 pages + appendix** | Keep the part humans read short; push detail to the appendix |
| Audience | Humans only | **Humans + AI** | ← the biggest difference |
| Approval | The whole doc | **The Decision Points** | Concentrate human judgment at the forks |
| Machine-readable | No | **Front matter required** | For tracking, validation, automation |
| Stored in | An internal doc tool | **Markdown in the repository** | Reviewed in the same PR, kept in the same history |

---

## When to write one

Write a **design doc (DD)** if any of these hold.

- It spans more than one component or service
- It changes a public API, a schema, or the shape of persisted data
- It is expensive to change later (a migration would be needed)
- Two or more reasonable alternatives exist and picking one takes judgment
- It touches security, privacy, billing, or availability
- The estimate exceeds roughly 3 person-days / 3 sessions

If none hold:

| Size | Use |
| --- | --- |
| Medium (1–3 days, options exist but are light) | A [one-pager](../templates/one-pager.md) — lives in `docs/design/` with reduced front matter |
| Small (under half a day, no design judgment) | The Issue body alone |

**When in doubt, write it.** Writing is cheap for an AI; the rework from not writing is not.

---

## Structure

Template: [`docs/templates/design-doc.md`](../templates/design-doc.md)

```
front matter        ← machine-readable metadata (validated by CI)
## Summary          ← three sentences or fewer; read this and you know what happens
## Context          ← how things are now, and what's wrong (prose)
## Goals            ← what gets achieved, stated verifiably
## Non-Goals        ← what does not  ★ acts as the agent's scope boundary
## Decision Points  ← ★ what a human decides. This is the body of the review
## Design           ← the design itself (prose + diagrams + interfaces)
## Alternatives Considered  ← two or three workable options and why they lost
## Cross-cutting Concerns   ← security / privacy / observability / cost / operations
## Acceptance Criteria      ← ★ verifiable criteria (Given/When/Then + the command)
## Implementation Plan      ← the proposed decomposition into Issues
## Context for Agents       ← ★ constraints for AI (where to touch, patterns, prohibitions)
## Open Questions           ← what is still unresolved
## Appendix                 ← detailed data, measurements, long research logs
```

★ marks the additions specific to this process.

---

## What the three additions are for

### ★ Decision Points — concentrate human judgment at the forks

Approving a whole doc means a human reads a whole doc. That does not scale.
Instead, lift out **only the points that need judgment** and put them near the top.

Every Decision Point carries:

- **Two or more options** ("do it / don't" is a legitimate pair)
- **The AI's recommendation and its reasoning** — never hand the question over bare
- **The cost of reversal** — how expensive it is to change later

A decision that is cheap to reverse can be marked `[proceed on the recommendation, revisable]`
and skip human judgment entirely. **Match the cost of deciding to the cost of reversing.**

```markdown
### DP-1: Where sessions are stored

- **Option A**: Redis (recommended) — reuses the existing cluster, no new operational cost
- **Option B**: a table in the RDB — nothing new to operate, but write throughput becomes the bottleneck
- **AI recommendation**: A. Peak writes today are 1,200 req/s, which exceeds the headroom B would need (see Appendix A-2)
- **Cost of reversal**: Medium. A storage abstraction makes swapping possible, but migrating needs downtime
```

### ★ Acceptance Criteria — make verifiability part of the design

An AI can quickly build something that *looks* like it works. So quality rests on
**verifiability**. Write every criterion as **Given / When / Then** plus **the command**.

```markdown
- **AC-1**: Given an expired session, When the API is called, Then it returns 401 and writes one audit log line
  - Verify: `pytest tests/auth/test_session_expiry.py`
```

A criterion with no way to verify it is not a criterion. **Rewrite it, or move it to Open Questions.**

### ★ Context for Agents — constrain the search space in the design

Given too much room to explore, an AI will implement something that ignores existing
patterns. Fence it in up front.

```markdown
## Context for Agents
- May touch: `src/auth/**`, `tests/auth/**`
- Must not touch: `src/billing/**` (being reworked under DD-0007)
- Follow this pattern: the repository pattern in `src/auth/token.py`
- Dependencies: existing ones only. Adding one is a Decision Point
- Known trap: `SessionStore.get()` reads a cache, so tests need `flush()`
```

---

## State transitions

The front matter `status` is one of:

```
draft ──→ in-review ──→ approved ──→ implemented
  │           │                          │
  │           └──→ rejected               └──→ superseded (replaced by another DD)
  └──────────────→ rejected
```

| status | Meaning | Who moves it |
| --- | --- | --- |
| `draft` | Being written, not yet up for review | Agent |
| `in-review` | Under review (a PR is open) | Agent, when the PR goes up |
| `approved` | Cleared G1; implementation may begin | **Owner only** |
| `implemented` | Built and merged; updated to as-built | Agent, in the implementation PR |
| `rejected` | Rejected. **Keep the doc** — it prevents re-litigating the same argument | Owner |
| `superseded` | Replaced by a newer DD; `superseded_by` names it | Owner |

**Never delete a rejected doc.** "Why we didn't" is worth as much as "why we did".

---

## Numbering and location

```bash
python3 scripts/new_doc.py design "Change the session store" --slug session-store
```

- ID: `DD-0001` form (four digits, zero-padded, never reused)
- Filename: `DD-<number>-<short-lowercase-kebab-summary>.md`
- Index: [`docs/design/README.md`](../design/README.md) — consistency is checked by `scripts/validate_docs.py`

Note that `new_doc.py` cannot derive a slug from a non-ASCII title; pass `--slug` explicitly.

---

## How review runs

1. Put the design doc up as **its own PR** (no implementation)
2. PR title: `docs(design): DD-xxxx <title>`
3. **Copy the Decision Points into the top of the PR body** so reviewers can discuss them on GitHub
4. Discuss each Decision Point in its own comment thread
5. When all are settled, the Owner sets `status: approved` and merges

See [04-review.md](04-review.md) for details.

---

## Updating to as-built after implementation

**A doc is not a spec you write once. It is an asset you maintain.**

When the implementation PR merges, update the doc in that same PR.

- Move `status` to `implemented`
- Fix anything in `Design` that no longer matches the code
- Add constraints discovered during the build to `Cross-cutting Concerns` or the `Appendix`
- If the *approach itself* changed, do not patch the doc — **write a new DD and mark this one `superseded`**

A doc that stops being updated becomes **a document that lies** six months later.
An AI will read it as true, so the damage is larger than when only humans read it.
