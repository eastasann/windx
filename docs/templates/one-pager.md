---
id: DD-0000
title: "<short title>"
type: one-pager
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
A one-pager is the light form for changes that carry design judgment but little of it
(roughly 1–3 days).
Usage:        python3 scripts/new_doc.py onepager "<title>" --slug <english-slug>
Conventions:  docs/process/03-design-doc.md

If the change is larger, spans several components, or is expensive to reverse, use the
design-doc template instead. If it stops fitting while you write, promote it without
hesitation (change `type` to design-doc and add the missing sections).
-->

## Summary

<!-- Three sentences or fewer. What happens. -->

## Context

<!-- How things are now and what is wrong. One or two paragraphs. -->

## Non-Goals

<!-- ★ Do not skip this even in a short doc. It is the agent's scope boundary. -->

-

## Decision Points

<!--
★ What needs deciding. If there is genuinely nothing, write "none (the change is obvious)".
-->

### DP-1: <what has to be decided>

- **Option A / B**:
- **AI recommendation**: <which> — <reasoning>
- **Cost of reversal**: <low / medium / high>
- **Decision**:

## Design

<!-- How it is built. One to three paragraphs, plus a diagram or interface if useful. -->

## Alternatives Considered

- **<Option A>**: <why rejected>
- **Do nothing**: <why rejected>

## Acceptance Criteria

- **AC-1**: Given <precondition>, When <action>, Then <expected result>
  - Verify: `<command>`

## Context for Agents

- **May touch**:
- **Follow this pattern**:
- **Known traps**:
