---
name: design-doc
description: Draft a design doc from a problem. Presents several alternatives and extracts the points a human must decide as Decision Points. Use when asked to write a design doc, draft a DD, or think through the design of a change, or whenever a change needs design agreement before implementation.
---

# Drafting a design doc

**The goal is not to reach the conclusion. It is to assemble what a human needs to decide.**

Conventions: `docs/process/03-design-doc.md`

---

## Steps

### 1. Decide whether one is needed

Write a DD if any of these hold.

- It spans more than one component or service
- It changes a public API, a schema, or the shape of persisted data
- It is expensive to change later (a migration would be needed)
- Two or more reasonable alternatives exist and picking one takes judgment
- It touches security, privacy, billing, or availability
- The estimate exceeds roughly 3 person-days / 3 sessions

For 1–3 days with light judgment, use `onepager`. Under half a day with no design
judgment, the Issue body is enough. **When in doubt, write it.**

### 2. Research first — always

Gather facts before writing any design.

- The relevant existing code and the patterns in use there
- Past DDs and ADRs (`docs/design/README.md`, `docs/adr/README.md`)
- Related Issues and past PRs — has this argument already happened?
- Measure whatever can be stated in numbers; never present a guess as evidence

A doc written without research is plausible and useless for deciding.

### 3. Create it

```bash
python3 scripts/new_doc.py design "<title>" --slug <english-slug>
```

`--slug` is required for any title that is not plain ASCII.

### 4. Fill in the sections

Do not cut corners on these.

#### Non-Goals

**Never leave it empty.** This is not courtesy — it becomes the scope boundary for your own
implementation later. Separate "not this time" from "not ever".

#### Decision Points — the body of the doc

List **only** the forks that need judgment. Each one carries:

- **Two or more options** ("do it / don't" is a legitimate pair)
- **Your recommendation and its reasoning** — cite numbers or facts about the existing code. Never hand the question over bare
- **The cost of reversal** (low / medium / high) and why you can say that
- **Decision**: left **empty** — that field is the human's. Never fill it in yourself

If reversal is cheap, you may mark it `[proceed on the recommendation, revisable]`.
**Match the cost of deciding to the cost of reversing.**

#### Alternatives Considered

**Two or three workable alternatives.** Writing is cheap, so drop the pretence.

- **Always include "do nothing"** — it is the cheapest option
- Never let a rejection stop at "too complex". Say **what is complex and who pays that cost**
- Overlapping with a Decision Point is fine; the reader's path through them differs

#### Acceptance Criteria

Given / When / Then plus **the verifying command**.

```markdown
- **AC-1**: Given an expired session, When `/api/me` is called, Then it returns 401
  - Verify: `pytest tests/auth/test_session_expiry.py -q`
```

A criterion you cannot verify is not a criterion. Rewrite it or move it to `Open Questions`.

#### Context for Agents

Constraints for whoever implements this — including a future you in another session. If this
is thin, the implementation will drift from the design.

- Where it may and may not touch (concrete paths)
- Patterns to follow (**name the existing file**)
- Permitted dependencies (adding one is a Decision Point)
- Known traps

### 5. Validate

```bash
python3 scripts/validate_docs.py
python3 scripts/check_links.py
```

### 6. Submit as its own PR

- **No implementation.** The PR contains the doc only
- PR title: `docs(design): DD-xxxx <title>`
- **Copy the Decision Points into the top of the PR body** so they can be discussed on GitHub
- Add `Design doc: DD-xxxx`, and `Closes #n` if there is a tracking Issue

---

## Always include in your final report

1. The doc's path and ID
2. **The list of Decision Points** — what you want a human to decide
3. Your recommendation for each, with the reasoning in brief
4. Any unresolved Open Questions

---

## Never

- **Fill in a Decision Point's `Decision` field yourself** — approval is a human act of signature
- Request review with the Decision Points empty
- Write only one alternative
- Write a design without researching (presenting a guess as evidence)
- Mix implementation into a doc PR
- Start implementing before approval
