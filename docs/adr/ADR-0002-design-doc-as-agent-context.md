---
id: ADR-0002
title: "Design docs are structured as context input for AI agents"
status: accepted
date: 2026-09-22
deciders: ["@eastasann"]
related_docs: ["DD-0001"]
supersedes: []
superseded_by: null
---

## Context

Google's design docs are written as prose for human readers. The property that vague designs
cannot survive prose was itself the quality mechanism.

In this project the implementer is an AI agent, which changes who reads the doc. The agent
reads it on every implementation and assembles the work from it as its largest context. Two
degradations are observable in practice, both caused by what the doc leaves out.

1. **Scope creep** — with no statement of what is out of scope, surrounding code gets modified
2. **Ignored patterns** — with no reference implementation named, the agent invents its own structure

Separately, we want the doc's state — who it waits on, which Issue it corresponds to — to be
handled mechanically. Prose alone cannot do that.

## Decision

A design doc has two layers: a prose body and a machine-readable structure.

- **Front matter is mandatory**, carrying `id` / `status` / `owner` / `tracking_issue` and
  similar fixed keys. CI (`scripts/validate_docs.py`) validates the structure
- The sections inherited from Google — Context, Goals, Non-Goals, Design, Alternatives,
  Cross-cutting Concerns — stay as prose
- Two sections are added for agents
  - **`Context for Agents`**: where it may and may not touch, patterns to follow, permitted
    dependencies, known traps
  - **`Acceptance Criteria`**: Given/When/Then plus **the verifying command**

Non-Goals and Context for Agents are positioned not as courtesy to a human reader but as
**runtime constraints on the agent's search space**.

## Consequences

### Good outcomes

- Handing work to an agent needs one link, with no context pasted into the prompt
- Scope deviation and ignored patterns are suppressed through doc quality rather than prompting
- Doc state can be aggregated mechanically and violations caught in CI
- Because the verifying command lives in the doc, "is it done" is decoupled from human opinion

### Bad outcomes / costs accepted

- **Writing a doc costs more.** There are more mandatory sections than in Google's version, and
  formal constraints on top (though with an AI writing, the added human cost is limited)
- **The structural validation risks becoming theatre.** Filling in sections can become the goal
  and leave them hollow. Only structure is checkable; the soundness of the content still
  depends on human review
- **A front matter schema change forces a bulk edit of every doc**
- **Every change to the implementation creates an obligation to update the doc.** Neglect it and
  the agent reads a falsehood as a premise, which does more damage than when only humans read it

### Signals that this should be revisited

- Agents repeatedly produce implementations that ignore `Context for Agents`
  (the conclusion would be to constrain through tooling rather than the doc)
- Hollow docs that merely fill sections become the majority
- Model context capability improves enough to infer the constraints from the repository itself

## Alternatives Considered

- **Use Google's design doc as is**: sufficient for human agreement, but it cannot satisfy
  mechanical state tracking or agent constraint.
- **Keep docs as prose and put agent constraints in `CLAUDE.md`**: fine for constraints shared
  across the whole repository, but it cannot express per-change constraints such as "do not
  touch `src/billing/**` in this one" — which is exactly what is needed.
- **Write docs as structured data (YAML/JSON)**: maximises machine readability but loses the
  core of the design doc culture, the vagueness only prose can detect.
