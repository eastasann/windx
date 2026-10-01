---
id: ADR-0000
title: "<the decision itself, in active voice>"
status: proposed
date: 0000-00-00
deciders: ["@<github-handle>"]
related_docs: []
supersedes: []
superseded_by: null
---

<!--
Usage:        python3 scripts/new_doc.py adr "<title>" --slug <english-slug>
Conventions:  docs/process/08-adr.md

Rules:
- The title is the decision ("Adopt X", not "About X")
- If it runs past one page, it is a design doc
- Never rewrite it after accepted. To reverse it, write a new ADR and mark this superseded
-->

## Context

<!--
The situation, and what had to be decided. Two or three paragraphs.
Note any constraints (deadline, staffing, existing systems, regulation).
Do not put the decision itself here.
-->

## Decision

<!--
What was decided. Active voice, declarative, one to three sentences.
❌ "Redis seems preferable" → ✅ "Sessions are stored in Redis"
-->

## Consequences

### Good outcomes

-

### Bad outcomes / costs accepted

<!-- ★ Two or more, always. There is no decision without a trade-off. -->

-
-

### Signals that this should be revisited

<!-- What would make you supersede this ADR. State it observably. -->

-

## Alternatives Considered

<!-- Two or three lines each. Leave the detail to the related design doc. -->

- **<Option A>**: <why rejected>
- **<Option B>**: <why rejected>
