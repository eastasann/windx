---
id: DD-0000
title: "<short title containing a decisive verb>"
type: design-doc
status: draft
owner: "@<github-handle>"
reviewers: []
created: 0000-00-00
updated: 0000-00-00
tracking_issue: null
related_adrs: []
supersedes: []
superseded_by: null
---

<!--
Usage:
  python3 scripts/new_doc.py design "<title>" --slug <english-slug>   # numbers and copies this
  python3 scripts/validate_docs.py                                   # always run before submitting

Conventions: docs/process/03-design-doc.md
The sections marked ★ are specific to this process. They are the three that matter most
under AI-driven development — never leave them empty.
-->

## Summary

<!-- Three sentences or fewer. Reading only this should tell you what happens. -->

## Context

<!--
Write prose (avoid a pile of bullets). How things are now, and what is wrong.
Always include "why now". Assume a colleague who does not know this area.
-->

## Goals

<!-- What gets achieved, stated verifiably. Three to five items. -->

- <!-- e.g. Bring p99 session-validation latency under 50ms -->

## Non-Goals

<!--
★ What you are not doing. This acts directly as the agent's scope boundary, so fill it in.
Separate "not this time" from "not ever".
-->

- <!-- e.g. Changes to authorisation logic (covered by a separate doc) -->

## Decision Points

<!--
★ What a human decides. This is the body of the review. Never request review with it empty.
Every DP needs two or more options, the AI's recommendation, and the cost of reversal.
If reversal is cheap, you may mark it [proceed on the recommendation, revisable].
-->

### DP-1: <what has to be decided>

- **Option A**: <the option, and what follows from choosing it>
- **Option B**: <the option, and what follows from choosing it>
- **AI recommendation**: <which> — <reasoning; cite numbers or facts about the existing code>
- **Cost of reversal**: <low / medium / high> — <why you can say that>
- **Decision**: <!-- the Owner writes the chosen option and the reason here -->

## Design

<!--
The design itself. Prose + diagrams + interface definitions.
- System shape (a text diagram is fine)
- Key interfaces / APIs / schemas
- Data flow and state transitions
- Behaviour on failure
Push long detail (measurements, full API definitions) into the Appendix.
-->

## Alternatives Considered

<!--
★ Two or three workable alternatives. Writing is cheap for an AI, so drop the pretence.
Always include "do nothing" and "use what already exists" — they are the cheapest options.
Never let a rejection stop at "too complex": say what is complex and who pays for it.
-->

### Alternative 1: <name>

- **How it works**: <one paragraph>
- **What you give up**: <the trade-off>
- **Why rejected**: <concretely>

### Alternative 2: Do nothing

- **How it works**: <what happens if this is left alone>
- **Why rejected**: <why the cost of leaving it is unacceptable>

## Cross-cutting Concerns

<!-- For anything that does not apply, write "N/A" and why. Do not leave blanks. -->

| Concern | Impact and response |
| --- | --- |
| Security | |
| Privacy / personal data | |
| Observability (will you notice failure) | |
| Performance | |
| Cost | |
| Operations, migration, rollback | |
| Backwards compatibility | |

## Acceptance Criteria

<!--
★ Verifiable criteria. Given / When / Then plus the command that proves it.
A criterion you cannot verify is not a criterion — rewrite it or move it to Open Questions.
-->

- **AC-1**: Given <precondition>, When <action>, Then <expected result>
  - Verify: `<command>`

## Implementation Plan

<!-- The proposed Issue decomposition. One row = half a day to two days. State dependencies. -->

| # | Work | Acceptance | Depends on | Size |
| --- | --- | --- | --- | --- |
| 1 | | AC-1 | — | S |

## Context for Agents

<!--
★ Constraints for AI. Fence in the search space in the design.
If this is thin, the implementation will drift from the design.
-->

- **May touch**:
- **Must not touch**:
- **Follow this pattern**: <the existing file to imitate>
- **Dependencies allowed**: <existing only / if additions are allowed, which>
- **Known traps**:

## Open Questions

<!-- Still unresolved. Say who resolves it and by when. Write "none" if there are none. -->

- [ ] <question> — owner: @<handle>

## Appendix

<!-- Measurements, full API definitions, research logs. Where detail goes so the body stays short. -->
