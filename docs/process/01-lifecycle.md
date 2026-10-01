# 01. Lifecycle and the four gates

## The idea

Traditional processes are divided by **phase** — requirements, design, build, test.
Under AI-driven development the duration of each phase shifts so much that dividing by
phase stops meaning anything.

This process divides by **the points where a human has to decide** instead.
We call those **gates**. Between gates, AI runs continuously. At a gate, it always stops.

> A gate is not a place to report progress. It is a place to **make a decision that is
> expensive to reverse**. If no decision is needed, there should be no gate.

---

## The flow

```
        ┌──────────────────────────────────────────────────────────────────┐
        │                                                                  │
 idea ──┴→ [G0] frame ──→ [G1] design ──→ [G2] build ──→ [G3] ship ──→ operate
             │               │               │              │
          open an Issue   Design Doc     Pull Request     Release
          type/*          DD-xxxx        Closes #n        Milestone
          priority/*      status:        CI green         ADRs updated
                          approved
             │               │               │              │
          [HUMAN]        [HUMAN]         [HUMAN]        [HUMAN]
          worth solving? this design?    this code?     ship it?
             │               │               │              │
          [AI]           [AI]            [AI]           [AI]
          research,      draft the doc,  decompose,     release notes
          shape it       alternatives    build, verify
```

---

## G0 — Framing gate

**The decision**: is this worth solving at all, and now?

| | |
| --- | --- |
| Input | A fragment — a request, a bug report, an idea, a measurement |
| AI does | Reproduce, scope the impact, check for duplicate Issues, shape the Issue body |
| Output | An Issue, labelled `type/*` and `priority/*` |
| Human decides | Priority; whether to reject or defer |
| Passes when | The Issue says who is hurting and what changes if it's solved |

**Why stopping here pays**: the cheapest rejection is the one before any work starts.

---

## G1 — Design agreement gate

**The decision**: is this the right approach, and how do the Decision Points resolve?

| | |
| --- | --- |
| Input | An Issue that cleared G0 |
| AI does | Study the existing code, draft the design doc, present **two or three alternatives**, extract the Decision Points |
| Output | `docs/design/DD-xxxx-*.md`, reviewed as a PR |
| Human decides | **Answers the Decision Points**; approves or sends it back |
| Passes when | The doc is `status: approved` and every Decision Point is settled |

**Why stopping here pays**: overturning a design after it is built costs ten times more
than before. Making AI build faster only means **building the wrong design faster**.

Changes that do not need a design doc (see the test in `CLAUDE.md`) skip G1 and go to G2.

---

## G2 — Implementation gate

**The decision**: should this land on the main branch?

| | |
| --- | --- |
| Input | An approved design doc, or an Issue judged not to need one |
| AI does | Decompose into Issues, implement, write tests, get CI green, respond to review |
| Output | A pull request (1 PR = 1 Issue) |
| Human decides | Is this the intent; does it stay inside the doc; does it meet the acceptance criteria |
| Passes when | CI is green, the evidence shows the acceptance criteria met, review approves |

**How to read the code**: when reviewing AI-written code, look at **intent and structure**
rather than line-level correctness. Leave syntax and convention to CI and linters. Humans
ask "is this abstraction right" and "does it follow the doc". See [04-review.md](04-review.md).

---

## G3 — Ship gate

**The decision**: should this go out into the world now?

| | |
| --- | --- |
| Input | Merged changes, grouped by Milestone |
| AI does | Generate release notes, collect the changes, confirm migration steps, write the rollback |
| Output | A GitHub Release and tag; the Milestone closed |
| Human decides | Whether and when to ship |
| Passes when | Every Issue in the Milestone is closed and a rollback path exists |

---

## How much AI may run unattended between gates

| Stretch | Autonomous | Condition |
| --- | --- | --- |
| idea → G0 | Yes | Research and opening the Issue. A human sets the priority |
| G0 → G1 | Yes | Drafting and presenting alternatives. **Never settle the Decision Points** |
| G1 → G2 | Yes | Strictly inside the approved doc. If the work wants to leave it, stop and ask |
| G2 → G3 | Conditional | Merging is a human act. Fixing CI and answering review is autonomous |

---

## When the implementation disagrees with the doc

Mid-build you sometimes learn the doc's design will not work. **That is not a failure —
it is a normal discovery.** Pick one of the two below. **Silently changing the
implementation is the only forbidden option.**

| Size of the drift | What to do |
| --- | --- |
| Small (the doc is imprecise at the implementation-detail level) | Fix the doc in the same implementation PR and say so in the PR body |
| Large (the approach, an interface, or the data model changes) | Stop building. **Update the doc and send it back to G1** as a new Decision Point |

If you cannot tell which it is, treat it as large.
