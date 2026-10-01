---
id: DD-0001
title: "Standardise the AI-driven development process"
type: design-doc
status: approved
owner: "@eastasann"
reviewers: ["@eastasann"]
created: 2026-09-22
updated: 2026-10-01
tracking_issue: null
related_adrs: ["ADR-0001", "ADR-0002", "ADR-0003", "ADR-0004"]
supersedes: []
superseded_by: null
---

<!--
This doc defines the development process of this repository, and is simultaneously an
example of a design doc written under that process (dogfooding).
-->

## Summary

Adapt Google's design docs culture to AI-driven development, and keep the whole process —
issue tracking, roadmap, and decision records included — inside GitHub. Human involvement is
confined to deciding at gates; research, writing, implementation, and verification are
executed by AI agents.

## Context

Google's design doc culture worked for two reasons. **Thinking by writing** — vague designs
cannot survive prose — and **agreement through review**, where objections arrive while they
are still cheap. Both rested on the same premise: writing a design took real time, and
implementing it cost more still.

When AI agents become the primary implementers, that premise breaks. Writing drops from days
to minutes, and implementation cost falls sharply too. The bottleneck therefore moves away
from *writing* and *building* and towards **deciding** and **verifying**.

Carrying the old process over while ignoring that move produces one of two failures. Either
humans try to read everything the AI produces and review becomes the bottleneck, or they
approve without reading and approval becomes hollow. Both are easy to observe, and the second
is more dangerous because it surfaces later, as a drop in quality.

At the same time, agents read the doc as their largest context at implementation time. So a
doc is **both the artifact humans agree on and a context input for AI**. That dual role is the
main reason to change anything about Google's version.

This project currently has no code, so the process can be defined first. That order is
cheaper than retrofitting a process later.

## Goals

- Define the flow from idea to shipped around **the points where a human decides** (gates)
- Redesign the design doc to serve both human agreement and agent-facing constraint
- Make human review load proportional to **the number of decisions**, not the length of the doc
- Make issue tracking, roadmap, and decision records operable entirely within GitHub
- Detect process violations **mechanically in CI**, not through human attention
- Let a newcomer, human or AI, start working from the documents in the repository alone

## Non-Goals

**Not this time**

- Product-specific technology choices (language, framework, infrastructure) — separate DDs
- CI for product code (lint / typecheck / test) — added once code lands
- Creating the Project and its fields by hand — this doc defines the design; a human performs
  the one-time creation
- Cross-repository roadmap management

**Not ever**

- Refining effort estimates, measuring velocity, burndown tracking
- A path for non-engineers to participate without Markdown or PRs
- Persisting decisions outside GitHub, in chat or an external document tool
  ([ADR-0001](../adr/ADR-0001-github-as-single-source-of-truth.md))

## Decision Points

### DP-1: Language of the documents

- **Option A**: Japanese body with English IDs and filename slugs
- **Option B**: English throughout, anticipating a multilingual team or an open-source release
- **AI recommendation**: A. The readers are Japanese speakers today, and a design doc's value
  lies in writing prose precisely; a second language costs precision and weakens the
  thinking-by-writing function that is the whole point. IDs and slugs are already restricted
  to ASCII, so translating only the bodies later remains possible
- **Cost of reversal**: Medium. Existing docs must be translated, which is cheap while there
  are few of them. **The earlier this is settled, the cheaper it is**
- **Decision**: **B (English throughout)** — Owner, 2026-10-01. The AI recommendation was not
  taken; the possibility of an open-source release and a multilingual team takes precedence.
  **The scope is the whole repository** (DDs, ADRs, process docs, templates, `CLAUDE.md`,
  `README.md`, Issue and PR templates, skills, and the output messages of the scripts), so
  that no Japanese/English mixture remains. Carried out as Implementation Plan #9

### DP-2: Threshold at which a design doc is mandatory

- **Option A**: Over 3 person-days / 3 sessions, **or** an API or schema change, **or** two or
  more alternatives
- **Option B**: Looser — mandatory only over a week, reducing the friction of writing docs
- **Option C**: Stricter — a one-pager or more for nearly every change
- **AI recommendation**: A to begin with, revisited after three months against reality. Writing
  is cheap for an AI, so a C-leaning practice is technically possible, but **the humans doing
  the reviewing are the rate limiter**. A is pitched at "a human reads a few a week"
- **Cost of reversal**: **Low**. Rewriting one line of the test, with no effect on existing docs
  `[proceed on the recommendation, revisable]`
- **Decision**: **A (keep the current threshold)** — Owner, 2026-10-01, as recommended. The
  rate limiter is the reviewing human, so "a few a week" is the intended ceiling.
  **Re-evaluate after three months (around 2027-01)**: shift towards B if docs exceed five a
  week and review stalls, towards C if design rework starts appearing

### DP-3: Who applies the `agent/ready` label

- **Option A**: **Humans only.** A human explicitly opens the AI's scope of autonomy
- **Option B**: The AI judges the Definition of Ready itself and applies the label; humans
  revoke it afterwards
- **AI recommendation**: A. This label is the single switch that opens AI autonomous execution
  (see [07-definition-of-done.md](../process/07-definition-of-done.md)), and self-judgment
  closes a loop in which the AI marks a vague Issue ready and then implements its own
  interpretation of it. **Separating judgment from execution** is the core of this process, so
  it is worth protecting here. Drafting the acceptance criteria needed to satisfy the DoR can
  still be the AI's work
- **Cost of reversal**: Low in form — only a practice change. But going from B back to A means
  tightening a practice that has already been loosened, which is hard in reality
- **Decision**: **A (humans only)** — Owner, 2026-10-01, as recommended. The middle option
  (letting AI self-assess for `risk/low` and `size/xs|s` only) was also declined; the
  separation of judgment from execution holds for every Issue without exception.
  **The agent's responsibility ends at preparing the Issue to meet the DoR and asking.**
  Signal to revisit: if the Owner's labelling falls behind to the point where the AI waits on
  an empty `Agent Queue` for more than a day a week, reconsider the middle option

### DP-4: How strict "1 PR = 1 Issue" is

- **Option A**: Strictly 1:1. Dependent work is serialised
- **Option B**: Allow stacked PRs to raise parallelism
- **AI recommendation**: A to begin with. B suits AI parallel execution and is tempting, but
  review load rises sharply and conflict resolution tangles across agents. It is cheaper to
  reach for B once A has demonstrably failed
- **Cost of reversal**: **Low**. Loosening a practice later affects nothing already produced
  `[proceed on the recommendation, revisable]`
- **Decision**: **A (strictly 1:1)** — Owner, 2026-10-01, as recommended. The current
  implementation, where `scripts/check_pr.py` rejects multiple `Closes`, stands unchanged.
  Signal to revisit: when measured waiting caused by serialisation exceeds 30% of lead time.
  Even then, revisit Issue decomposition granularity before moving to B

### DP-5: How Projects (v2) automation is built

- **Option A**: GitHub's built-in Project workflows only, configured through the GUI
- **Option B**: Code the automation with GitHub Actions and the GraphQL API, managed in the
  repository
- **AI recommendation**: A to begin with. B has the advantage of version-controlled
  configuration, but the Projects GraphQL API changes often and the maintenance cost is
  ongoing. Move to B once a requirement appears that built-in workflows cannot express
- **Cost of reversal**: Medium. Migrating from A to B means swapping the automation while
  preserving the state of existing items
- **Decision**: **B (code it with Actions and GraphQL)** — Owner, 2026-10-01. The AI
  recommendation was not taken; consistency with
  [ADR-0001](../adr/ADR-0001-github-as-single-source-of-truth.md) — keep every decision in the
  repository — takes precedence, making the Projects configuration reviewable and
  reproducible. **Established precondition**: `GITHUB_TOKEN` cannot operate on Projects v2
  regardless of owner type (the `permissions:` entry `repository-projects` applies to classic
  projects), so another token is required; which one depends on ownership, settled in DP-6.
  Built as Implementation Plan #10

### DP-6: Project ownership type and the authentication method

Raised by DP-5=B. Since `GITHUB_TOKEN` cannot operate on Projects v2, the token has to be
chosen — and **the usable tokens differ by who owns the project** (the research is in
Appendix A-3).

- **Option A**: **Support both.** Hold the owner type (`user` / `organization`) as
  configuration and abstract the credential behind a single secret name, `PROJECTS_TOKEN`, so
  the same code runs whether that holds a classic PAT or a GitHub App installation token
- **Option B**: **Assume organisation ownership** and standardise on a GitHub App (GitHub's
  recommended setup). Does not work for a personal account
- **Option C**: **Assume user ownership** (classic PAT) and rebuild when moving to an organisation
- **AI recommendation**: **A**. The Projects v2 GraphQL mutations themselves do not depend on
  owner type; the only differences are (1) whether the project is looked up through
  `user(login:)` or `organization(login:)`, and (2) where the token comes from. Switching those
  two on configuration is cheap, whereas C means rebuilding the automation on a move to an
  organisation and B does not work on the current personal account. **Supporting both is the
  cheapest.** It also means a later move to an organisation only requires swapping the
  contents of `PROJECTS_TOKEN` for an App installation token, which is the narrower permission
- **Cost of reversal**: **Low**. Two configuration values and one query branch, so dropping
  either side later is easy `[proceed on the recommendation, revisable]`
- **Decision**: **A (support both)** — proceeded on the recommendation, 2026-10-01, under the
  Owner's explicit instruction to carry the work to completion. Permitted because the cost of
  reversal is low and the DP is marked `[proceed on the recommendation, revisable]`. Recorded
  as [ADR-0004](../adr/ADR-0004-projects-automation-owner-agnostic.md). If the Owner wants B
  or C instead, the change is a configuration edit plus deleting one branch

## Design

### Structure

The process is divided by **the points where a human decides**, not by phase. We call these
gates. Dividing by phase loses meaning under AI-driven work: the duration of each phase shifts
sharply, and the boundary that actually matters is where responsibility changes hands.

```
G0 frame the problem ──→ G1 agree on design ──→ G2 approve the build ──→ G3 decide to ship
   Issue                   Design Doc              Pull Request             Release
   "worth solving?"        "this design?"          "this code?"             "ship it?"
```

Between gates AI runs continuously. At a gate it always stops.
**No gate is placed where no decision is needed** — we do not invent meetings for progress
reports. Details in [`docs/process/01-lifecycle.md`](../process/01-lifecycle.md).

### A design doc in two layers

Google's prose structure is kept, with a machine-readable layer laid over it
([ADR-0002](../adr/ADR-0002-design-doc-as-agent-context.md)).

| Layer | Contents | Reader |
| --- | --- | --- |
| front matter | `id` / `status` / `owner` / `tracking_issue` and so on | CI, automation |
| prose body | Context / Goals / Design / Alternatives / Cross-cutting | Humans |
| **Decision Points** | The forks needing judgment, the AI's recommendation, cost of reversal | **Humans (the body of the review)** |
| **Acceptance Criteria** | Given/When/Then plus the verifying command | Humans, AI, CI |
| **Context for Agents** | Where to touch, patterns to follow, prohibitions | **AI (execution constraint)** |

### Concentrating human judgment in Decision Points

Having humans approve a whole doc collapses under the volume AI produces
([ADR-0003](../adr/ADR-0003-human-gates-at-decision-points.md)). Instead, only the forks that
are expensive to reverse are lifted out as Decision Points, and humans answer those.
**The cost of deciding is matched to the cost of reversing.**

A Decision Point that is cheap to reverse is marked `[proceed on the recommendation, revisable]`
and skips human judgment. DP-2, DP-4, and DP-6 in this doc are the worked examples.

### Two separate queues

GitHub Projects carries one work queue for humans and one for AI.

| View | Filter | Who watches it |
| --- | --- | --- |
| **Needs Decision** | `agent/needs-human` | **Humans.** What is waiting on a decision |
| **Agent Queue** | `agent/ready`, by priority | **AI.** What it may start autonomously |

`agent/ready` is applied only when the Definition of Ready is met, and only by a human (DP-3).
It is the single switch controlling AI autonomy.

### Projects automation, independent of ownership

Per DP-5 and DP-6, field and status synchronisation lives in
[`scripts/project_sync.py`](../../scripts/project_sync.py), driven by
[`project-sync.yml`](../../.github/workflows/project-sync.yml). The script takes
`PROJECT_OWNER`, `PROJECT_OWNER_TYPE`, and `PROJECT_NUMBER` as configuration and a credential
from `PROJECTS_TOKEN`, so the same code serves a user-owned and an organisation-owned project.

### Traceability

```
ADR-xxxx ←── DD-xxxx ←── Issue #n ←── PR #m
why decided  how built   what to do   what was done
```

Link conventions (Issue→DD, PR→Issue, DD→ADR) are fixed, and the doc side is validated in CI.

### Enforcement

Conventions are not kept by people being careful. Anything checkable goes into CI.

| Check | Mechanism |
| --- | --- |
| Front matter keys and state values | `scripts/validate_docs.py` |
| Required headings, present and in order | same |
| **No unresolved Decision Point in an approved doc** | same |
| **Two or more bad outcomes in an ADR's Consequences** | same |
| ID–filename agreement, index agreement | same |
| Relative links resolve | `scripts/check_links.py` |
| PR traceability (`Closes #n`, `Design doc:`) | `scripts/check_pr.py` |
| Label definitions match reality | `scripts/sync_labels.py` |
| Projects fields match labels and state | `scripts/project_sync.py` |

## Alternatives Considered

### Alternative 1: Carry Google's design doc practice over unchanged

- **How it works**: Write three to ten pages of prose; a reviewer reads all of it and approves.
  Issues live in an existing tracker, docs in a document tool
- **What you give up**: The benefit of cheap writing. Drift detection between doc and code
- **Why rejected**: The premise that a human reads the whole thing does not scale to the volume
  AI produces, leaving a choice between review as the bottleneck and hollow approval. It also
  cannot serve the doc's new role as AI input, so scope creep and ignored patterns cannot be
  suppressed through the doc

### Alternative 2: A light process (Issues and PRs only, no design docs)

- **How it works**: Requirements go in the Issue, AI implements, review happens on the PR. No
  design documents; everything is decided in the PR
- **What you give up**: Agreement before building. Consideration of alternatives. The recorded
  rationale
- **Why rejected**: Cheap implementation **does not make it acceptable to build the wrong
  design quickly**. The structure in which design rework is most expensive after
  implementation has not changed. And "why we did this" gets buried in a diff, untraceable six
  months later. With AI having lowered the cost of writing, the case for not writing is at its
  weakest

### Alternative 3: Let an AI reviewer do the first pass, humans only final approval

- **How it works**: AI reviews docs and code and raises findings; humans approve based on the
  AI's review
- **What you give up**: Clarity about who is accountable for a judgment
- **Why rejected**: It delegates decisions that are expensive to reverse to an AI, which blurs
  accountability. This is a question of responsibility structure, not of AI capability.
  **Running AI review as part of CI is adopted** — it simply is not a substitute for the human gate

### Alternative 4: Do nothing (no defined process, decide case by case)

- **How it works**: No written process; judgment in the moment
- **Why rejected**: AI agents cannot infer unwritten conventions. Tribal knowledge works for
  human teams but stops working once AI is a primary executor. The result is repeating the same
  correction forever, whose total cost exceeds the cost of writing things down

## Cross-cutting Concerns

| Concern | Impact and response |
| --- | --- |
| Security | Secrets are banned from docs, Issues, and PRs (a hard rule in `CLAUDE.md`); secret scanning joins CI when product code lands. **The cost of DP-5=B**: operating Projects v2 needs a token other than `GITHUB_TOKEN`. For organisation-owned projects a GitHub App with organisation `Projects: write` keeps the permission narrow and is preferred. For user-owned projects only a classic PAT works, and its `project` scope cannot be narrowed — combined with `repo` it reaches every repository the user can see. Limit the blast radius by (a) keeping the token exclusive to Projects, (b) expiring it within 90 days with renewal in the routine, (c) moving to organisation ownership with an App as soon as possible |
| Privacy / personal data | This process handles none. Designs touching customer data address it in their own Cross-cutting section |
| Observability (will you notice failure) | Process violations surface as a `docs-lint` or `pr-checks` failure. Practice decay — missed Decision Points, hollow docs — is not CI-detectable and relies on humans working the failure-pattern table in [06-agent-protocol.md](../process/06-agent-protocol.md) |
| Performance | `validate_docs.py` is linear in doc count; expected to stay under a second into the hundreds |
| Cost | No new billing. Within the standard GitHub Actions allowance |
| Operations, migration, rollback | No prior process to migrate from. Rollback is reverting this PR |
| Backwards compatibility | N/A (new repository) |

## Acceptance Criteria

- **AC-1**: Given a design doc missing a required heading, When `validate_docs.py` runs, Then it exits non-zero and lists the missing headings
  - Verify: `python3 scripts/validate_docs.py`
- **AC-2**: Given a doc at `status: approved` with an unresolved Decision Point, When validation runs, Then it fails as "G1 not cleared"
  - Verify: `python3 scripts/validate_docs.py` (temporarily blank a `**Decision**` value to confirm)
- **AC-3**: Given an ADR with one or fewer bad outcomes, When validation runs, Then it fails
  - Verify: `python3 scripts/validate_docs.py`
- **AC-4**: Given a doc absent from the index README, When validation runs, Then it fails on index disagreement
  - Verify: `python3 scripts/validate_docs.py`
- **AC-5**: Given a new doc created with an English slug, When `new_doc.py` runs, Then the numbered file exists, a row is appended to the index, and validation passes
  - Verify: `python3 scripts/new_doc.py design "Scratch" --slug scratch-test && python3 scripts/validate_docs.py`
- **AC-6**: Given a push to `main`, When CI runs, Then `docs-lint` and `labels` both succeed
  - Verify: the GitHub Actions run
- **AC-7**: Given the repository after translation, When tracked files are searched for Japanese (hiragana, katakana, kanji), Then nothing is found
  - Verify: `! git grep -qlP '(*UTF)[\x{3041}-\x{309F}\x{30A0}-\x{30FF}\x{4E00}-\x{9FFF}]' -- .`
    (omitting `(*UTF)` makes PCRE reject the ranges with a fatal error)
- **AC-8**: Given `PROJECT_OWNER_TYPE` set to either `user` or `organization`, When `project_sync.py` builds its lookup, Then it emits the matching GraphQL query and the label-to-field mapping without contacting the network
  - Verify: `python3 scripts/project_sync.py --self-test`

## Implementation Plan

| # | Work | Acceptance | Depends on | Size |
| --- | --- | --- | --- | --- |
| 1 | Process documents (`docs/process/`) | Nine documents exist with no broken cross-links | — | M |
| 2 | Templates (design doc / one-pager / ADR) | Generated by `new_doc.py` and pass validation | — | S |
| 3 | Validation and scaffolding scripts | AC-1 to AC-5 | 2 | M |
| 4 | Issue templates, PR template, label definitions | Templates selectable on GitHub; labels sync | — | S |
| 5 | CI workflows (`docs-lint` / `pr-checks` / `labels`) | AC-6 | 3, 4 | S |
| 6 | Claude Code skills (design-doc / decompose / adr) | Each follows this process | 1, 2 | S |
| 7 | **Create the Project and its fields** (manual) | Five views exist; Agent Queue and Needs Decision work | 4 | S |
| 8 | **First Milestone and start of operation** | Its description states the goal in three sentences | 7 | XS |
| 9 | **Translate the repository to English** (from DP-1) | AC-7 | DP-1 | L |
| 10 | **Code the Projects automation** (from DP-5, DP-6) | AC-8 | DP-5, DP-6 | L |

Items 1–6, 9, and 10 are in this PR.
**Items 7 and 8 require the GitHub GUI and a credential, so the Owner performs them**
(the steps are in [09-setup-checklist.md](../process/09-setup-checklist.md)).

## Context for Agents

- **May touch**: `docs/**`, `.github/**`, `scripts/**`, `.claude/**`, `README.md`, `CLAUDE.md`
- **Must not touch**: product code (none exists yet)
- **Follow these patterns**:
  - A new process document is named `docs/process/NN-<topic>.md` and added to the table in `docs/process/README.md`
  - A new validation rule is one more check function in `scripts/validate_docs.py`
  - When adding a convention, **always add the matching check to CI or write it into `CLAUDE.md`**. A convention that lives only in prose is not followed
  - All prose, comments, and script output are in English (DP-1)
- **Dependencies allowed**: **the Python standard library only**. Do not add third-party
  dependencies to `scripts/` (it keeps CI setup light). If one is needed, raise it as a
  Decision Point
- **Known traps**:
  - The front matter parser in `validate_docs.py` understands only a subset of YAML; nested
    mappings and block scalars (`|`, `>`) are not handled
  - Templates in `docs/templates/` are excluded from validation because they contain
    placeholders; never place them in `docs/design/` or `docs/adr/`
  - `new_doc.py` cannot derive a slug from a non-ASCII title; pass `--slug`
  - `git grep -P` needs the `(*UTF)` prefix before `\x{...}` ranges above U+00FF

## Open Questions

- [ ] Define the granularity of `area/*` labels once the product structure is settled — owner: @eastasann
- [ ] Choose the tool for AI review in CI — owner: @eastasann
- [ ] Can `risk/high` be assigned mechanically from the touched paths — owner: @eastasann
- [ ] How to measure whether this process works (rework rate, missed Decision Points) — owner: @eastasann

## Appendix

### A-1. Differences from Google's design doc

| Item | Google | Here | Basis |
| --- | --- | --- | --- |
| Form | Prose | Prose (kept) | Detects vagueness |
| Goals / Non-goals | Required | Required (strengthened) | Non-Goals bound the agent's scope |
| Alternatives | Required, often lip service | Required, two or three at a workable level | Cheap writing lets us drop the pretence |
| Length | 3–10 pages | 1–5 pages + appendix | Keep the human-read body short |
| Unit of approval | The whole doc | **Decision Points** | ADR-0003 |
| Machine-readable | None | **Front matter required** | ADR-0002 |
| Stored in | An internal doc tool | **Markdown in the repository** | ADR-0001 |
| Added sections | — | **Context for Agents / Acceptance Criteria** | ADR-0002 |

### A-2. What this doc is

This is the first design doc written under this process, and doubles as the worked example of
the template. Its Decision Points were genuinely open during review; the Owner's answers of
2026-10-01 moved it to `status: approved`.

### A-3. Authenticating to Projects v2 (research, 2026-10-01)

`GITHUB_TOKEN` cannot operate on Projects v2. The `repository-projects` entry available under
the `permissions:` key applies to **classic projects (v1)** and has no effect on Projects v2.
GitHub's own recommendation is **a GitHub App for organisation-owned projects and a personal
access token for user-owned projects**.

| Owner | `GITHUB_TOKEN` | GitHub App | classic PAT | fine-grained PAT |
| --- | --- | --- | --- | --- |
| user-owned | ✗ | ✗ cannot reach user-level Projects | ✓ `project` scope | ✗ cannot obtain Projects permission for a personal account |
| org-owned | ✗ | ✓ **recommended**, `organization_projects: write` | ✓ `project` scope | △ possible, with known GraphQL issues reported |

Notes:

- A GitHub App needs **organisation projects read/write**; repository Projects permission is
  not sufficient
- The installation token is minted in the workflow (for example with `actions/create-github-app-token`)
- With insufficient permission, mutations such as `addProjectV2ItemById` return
  `Resource not accessible by integration`
- A classic PAT's `project` scope **cannot be narrowed to one repository**; combined with
  `repo` it reaches every repository the user can see

Sources:

- [GITHUB_TOKEN - GitHub Docs](https://docs.github.com/en/actions/concepts/security/github_token)
- [Assigning permissions to jobs - GitHub Docs](https://docs.github.com/en/actions/using-jobs/assigning-permissions-to-jobs)
- [Automating Projects using Actions - GitHub Docs](https://docs.github.com/en/issues/planning-and-tracking-with-projects/automating-your-project/automating-projects-using-actions)
- [Permissions required for GitHub Apps - GitHub Docs](https://docs.github.com/en/rest/authentication/permissions-required-for-github-apps)
- [Permissions required for fine-grained personal access tokens - GitHub Docs](https://docs.github.com/en/rest/authentication/permissions-required-for-fine-grained-personal-access-tokens)
- [Authenticating with a GitHub App to create V2 projects (community discussion #46681)](https://github.com/orgs/community/discussions/46681)
- [actions/add-to-project issue #289: fine-grained tokens and the GraphQL API](https://github.com/actions/add-to-project/issues/289)
