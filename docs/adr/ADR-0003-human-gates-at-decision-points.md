---
id: ADR-0003
title: "Human review is limited to Decision Points, not whole docs"
status: accepted
date: 2026-09-22
deciders: ["@eastasann"]
related_docs: ["DD-0001"]
supersedes: []
superseded_by: null
---

## Context

The volume of code and documents an AI produces easily exceeds what humans can review. The
traditional arrangement — a human reads everything and approves — always lands in one of two
places.

1. **Review becomes the bottleneck**, the AI's speed is wasted, and the queue grows
2. **Approval decays into a formality**, LGTM without reading, and approval loses its meaning

Both are worth avoiding, and the second is more dangerous because quality degradation surfaces
late. So "what should a human read" has to be redefined.

Observation: in a design document, **very little of the text is expensive to reverse**. Most of
it either follows mechanically once a fork is settled, or can be corrected cheaply during
implementation. What is expensive is **the choice at a fork**, and those are scattered
throughout the doc.

## Decision

Human review is scoped to the **Decision Points**, not the whole document.

- A `## Decision Points` section is mandatory in a design doc and collects every fork that
  needs judgment
- Each one carries **two or more options**, **the AI's recommendation with reasoning**, and
  **the cost of reversal**
- The Owner approves the doc by answering the Decision Points. Reading it end to end is not an
  obligation
- **A Decision Point that is cheap to reverse is marked `[proceed on the recommendation, revisable]`
  and skips human judgment**
- CI verifies that no unresolved Decision Point remains in a doc at `status: approved` or
  `implemented`

In short, the principle is to make **the cost of deciding proportional to the cost of reversing**.

## Consequences

### Good outcomes

- Human review time scales with **the number of forks**, not the length of the doc
- The AI can write a long doc without increasing the human cost, so cheaper writing is usable
- "What was approved" is explicitly recorded as the answers to the Decision Points
- Proceeding to implementation with an open decision is mechanically prevented in CI

### Bad outcomes / costs accepted

- **A missed Decision Point becomes critical.** If the AI does not surface a fork, the human
  never gets the chance to decide it — and in a practice where the whole doc is not read, nobody
  notices
- **Humans get anchored by the AI's recommendation.** Presenting a recommendation with reasoning
  speeds the decision and simultaneously makes dissent harder
- **If the AI misjudges the cost of reversal, a heavy decision gets skipped**
- Because the doc is not read end to end, factual errors outside the Decision Points survive
  until implementation

### Signals that this should be revisited

- Rework of the form "I did not think that was the design" happens twice or more in a quarter
  (missed Decision Points have become routine)
- The Owner's answers agree with the AI's recommendation 95% of the time or more
  (judgment may have decayed into anchoring)
- A decision marked "cost of reversal: low" turns out to have been expensive to withdraw

## Alternatives Considered

- **Humans read and approve the whole doc**: the strongest form of approval, but review becomes
  the bottleneck and in practice decays into formal LGTM. It does not survive the volume AI
  produces.
- **An AI reviewer does the first pass, humans only final approval**: handles the volume, but it
  delegates the expensive-to-reverse judgments to an AI and blurs accountability. AI review is
  used alongside, as part of CI, never as the human gate.
- **Sampling review (read a random portion in depth)**: useful for a statistical read on
  quality, but it cannot substitute for the judgment of which way to settle a fork.
