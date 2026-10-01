# 05. Issues and the roadmap

Everything lives in GitHub. **No decision or state is kept** in an external tracker,
spreadsheet, or document tool. A broken link means lost knowledge.

| Purpose | What it is on GitHub |
| --- | --- |
| Unit of work | **Issues** |
| Design documents | `docs/design/DD-xxxx-*.md` + a tracking Issue |
| Decision records | `docs/adr/ADR-xxxx-*.md` |
| Kanban / state | **Projects (v2)** board view |
| Roadmap | **Projects (v2)** roadmap view + **Milestones** |
| Unit of release | **Milestones** → **Releases** |
| Open-ended discussion | **Discussions** (once settled, becomes an Issue or an ADR) |

---

## Issue granularity

**1 Issue = 1 verifiable outcome.** Aim for **half a day to two days** (1–3 AI sessions).

| Signs it is too big | Signs it is too small |
| --- | --- |
| More than five acceptance criteria | You cannot write an acceptance criterion |
| A vague title like "improve X" or "handle Y" | One line of change |
| The PR would exceed 500 lines | It delivers no value on its own |
| It spans several DDs | It must always merge together with another Issue |

Too big: split it. Too small: fold it in.
**Split along value, not along phase** — not "design / build / test" Issues, but
"endpoint A / endpoint B".

---

## Issue templates

In `.github/ISSUE_TEMPLATE/`.

| Template | `type/*` | For |
| --- | --- | --- |
| Design Doc | `type/design-doc` | Proposing and tracking a DD (links the doc's PR) |
| Feature | `type/feature` | New functionality or improvement |
| Bug | `type/bug` | A defect. Reproduction steps are mandatory |
| Task | `type/task` | A unit decomposed from a DD, or chores |
| Spike | `type/spike` | Time-boxed research. **The output is always a document** |

---

## Label taxonomy

Defined in [`.github/labels.yml`](../../.github/labels.yml) and synced to GitHub by the
[`labels` workflow](../../.github/workflows/labels.yml) on push to `main`.

### `type/*` — what it is (required, exactly one)

`design-doc` / `feature` / `bug` / `task` / `spike` / `chore` / `process`

### `priority/*` — when (required, exactly one)

| Label | Meaning | Expected response |
| --- | --- | --- |
| `priority/p0` | Production outage, data loss, security | Now. Stop other work |
| `priority/p1` | Must land in the current milestone | This sprint |
| `priority/p2` | Will happen. Timing undecided | Top of the backlog |
| `priority/p3` | Nice to have | Someday |

### `stage/*` — which gate it is at (one)

`g0-problem` / `g1-design` / `g2-build` / `g3-release`

Mirrored by the Projects Status field (below).

### `agent/*` — AI autonomy (the important one)

| Label | Meaning |
| --- | --- |
| `agent/ready` | **AI may start autonomously.** Applied only when the DoR below is met |
| `agent/wip` | AI is working on it. Prevents double-starting |
| `agent/needs-human` | A human decision or action is required. AI does not start |
| `agent/blocked` | Stopped by something external. Say why in a comment |

**Conditions for `agent/ready` (Definition of Ready)**

1. Acceptance criteria are written verifiably
2. The affected surface (files, modules) is identified
3. If a design doc is needed, it is `approved` and referenced from the Issue
4. No unresolved Decision Point remains

This label is **the single switch that controls AI autonomy**. Do not apply it casually,
and **a human always applies it** — never the agent itself.

### `risk/*` — how careful to be

`risk/high` (security, billing, data migration, irreversible operations) / `risk/medium` / `risk/low`

`risk/high` requires **two reviewers**; AI may not merge it alone.

### `size/*` — estimate (optional)

`xs` (<2h) / `s` (<0.5d) / `m` (<2d) / `l` (<1w) / `xl` (must be split)

**`size/xl` must never carry `agent/ready`** until it is split.

### `area/*` — which part of the product

Only `area/docs` and `area/ci` exist as placeholders. Add more to
`.github/labels.yml` once the product's structure is settled.

---

## Projects (v2) design

**Project name**: `windx Roadmap` (one across the repository)

### Custom fields

| Field | Type | Values | Purpose |
| --- | --- | --- | --- |
| **Status** | Single select | `Inbox` / `Triaged` / `Designing` / `Ready` / `In Progress` / `In Review` / `Done` / `Dropped` | Day-to-day kanban |
| **Stage** | Single select | `G0` / `G1` / `G2` / `G3` | Gate position (mirrors `stage/*`) |
| **Target** | Iteration | 2 weeks | When work starts |
| **Milestone** | (built in) | — | When it ships |
| **Design Doc** | Text | `DD-0004` | The originating doc |
| **Confidence** | Single select | `High` / `Medium` / `Low` | Roadmap certainty. **Lower the further out** |
| **Size** | Single select | `XS`–`XL` | Estimate |

### Views

| View | Type | Purpose |
| --- | --- | --- |
| **Board** | Board (by Status) | Daily work; shows `agent/wip` |
| **Roadmap** | Roadmap (by Milestone) | The roadmap, internal and external |
| **Triage** | Table (`Status = Inbox`) | Waiting on G0 |
| **Needs Decision** | Table (`agent/needs-human`) | **Everything waiting on a human. This is the human's task list** |
| **Agent Queue** | Table (`agent/ready`, by priority) | **The Issues AI picks up next** |

The last two are the heart of this process.
**Humans watch Needs Decision; AI watches Agent Queue.** Keeping the two queues separate
is what makes the division of labour real.

### Automation

Field and status synchronisation is **implemented as code**
(see `DD-0001` DP-5 and DP-6): [`project-sync.yml`](../../.github/workflows/project-sync.yml)
driving [`scripts/project_sync.py`](../../scripts/project_sync.py).

| Trigger | Effect |
| --- | --- |
| Issue opened | Added to the Project, `Status = Inbox` |
| `agent/ready` applied | `Status = Ready` |
| `agent/wip` applied | `Status = In Progress` |
| A PR referencing the Issue opens | `Status = In Review` |
| Issue closed | `Status = Done` (or `Dropped` if closed as not planned) |
| `stage/*` applied | `Stage` field set to the matching gate |

`GITHUB_TOKEN` cannot write to Projects v2, so the workflow needs a `PROJECTS_TOKEN`
secret. Setup is in [09-setup-checklist.md](09-setup-checklist.md); the reasoning and the
token matrix are in `DD-0001` Appendix A-3.

---

## Milestones are the roadmap's time axis

| Grain | Naming | Meaning |
| --- | --- | --- |
| Release | `v0.3.0` | Unit of shipping, 1:1 with a Release |
| Period | `2026-Q4` | What the quarter achieves |
| Special | `hardening-2026-10` | A cross-cutting effort |

- **Put three sentences in the Milestone description saying what it achieves.** A Milestone that is only a date means nothing
- Work that will not fit does not move the date — **it leaves the Milestone** (cut scope)
- Closing a Milestone is G3: cut a Release, and have AI generate the notes

### The external roadmap

Publish the Projects roadmap view. **Always show Confidence.**

> Showing a distant future as `High` is the same as lying.
> Default: the next Milestone is `High`, the one after `Medium`, everything beyond `Low`.

---

## Traceability

Every piece of work hangs off this chain.

```
ADR-xxxx  ←─ why we decided it
   ↑
DD-xxxx   ←─ how we build it
   ↑
Issue #n  ←─ what we do
   ↑
PR #m     ←─ what we actually did (Closes #n)
```

The link rules:

- **Issue → DD**: an Issue from a DD carries `Design doc: DD-xxxx` in its body
- **PR → Issue**: `Closes #n` in the PR body (1 PR = 1 Issue)
- **PR → DD**: `Design doc: DD-xxxx` if it came from one
- **DD → Issue**: the doc's front matter `tracking_issue`
- **DD → ADR**: significant decisions listed in `related_adrs`

CI enforces the doc side ([`docs-lint.yml`](../../.github/workflows/docs-lint.yml)) and the
PR side ([`pr-checks.yml`](../../.github/workflows/pr-checks.yml)).

---

## Triage (30 minutes, once a week)

Work the `Triage` view (`Status = Inbox`) from the top. Two minutes per item, maximum.

1. **Duplicate?** Close it and link
2. **Doing it?** If not, mark `Dropped` and **say why in a comment** (silent closes are banned)
3. **Apply `priority/*`**
4. **Needs a DD?** If so, open a `type/design-doc` Issue and set `Stage = G1`
5. **If not**, write the acceptance criteria (AI may draft them) and apply `agent/ready`

If an item takes longer than two minutes, drop it to `priority/p3` and move on.
**Do not start designing during triage.**
