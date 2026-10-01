# 06. Agent execution protocol

How AI agents (Claude Code and similar) work in this repository.
The standing rules the agent itself reads are in [`CLAUDE.md`](../../CLAUDE.md).
This document explains the **reasoning behind them**.

---

## The execution loop

```
 ┌─────────┐   ┌────────┐   ┌────────┐   ┌───────────┐
 │ Explore │ → │ Design │ → │ Decide │ → │ Decompose │
 └─────────┘   └────────┘   └────────┘   └───────────┘
   research      draft        [HUMAN]       into Issues
                                 │
 ┌─────────┐   ┌────────┐   ┌────────┐      │
 │ Record  │ ← │ Verify │ ← │Implement│ ←────┘
 └─────────┘   └────────┘   └────────┘
  update        prove        build
  doc/ADR
```

### 1. Explore — research

**Goal**: gather the facts the design needs. **Do not start writing the design here.**

- Read the relevant existing code and the patterns in use there
- Read related past DDs and ADRs (`docs/design/README.md`, `docs/adr/README.md`)
- Search related Issues and past PRs — has this argument already happened?
- Reproduce if reproduction matters (**for a bug, do not start until it reproduces**)

**Output**: research notes (an Issue comment, or the doc's Context / Appendix)

### 2. Design — draft

**Goal**: assemble what a human needs to decide. **Not to reach the conclusion.**

- Draft the design doc (`docs/templates/design-doc.md`)
- Write **two or three alternatives** at a workable level of detail
- Extract the forks that need judgment as **Decision Points**
- Give each one **your recommendation with reasoning**, and **the cost of reversal**

**Output**: a PR containing the doc at `status: in-review`

### 3. Decide — the human decides (AI waits)

**Stop here.** Do not get ahead of it and start building.

- The Owner answers the Decision Points
- The Agent reflects each answer in the doc as `**Decision**: <option> (<reason>)`
- The Owner sets `status: approved` and merges — G1 cleared

### 4. Decompose — break it down

- Turn the doc's `Implementation Plan` into Issues
- Give each Issue **verifiable acceptance criteria**
- State dependencies in the body (`Depends on #n`)
- **Do not apply `agent/ready` yourself.** Prepare the Issue so it meets the DoR, then ask

### 5. Implement — build

- **1 PR = 1 Issue.** Branch name: `<type>/<issue-number>-<short-summary>`
- Obey the doc's `Context for Agents` (where to touch, which patterns to follow)
- **If the work wants to leave that scope, stop and ask.** "While I was here" is banned
- Apply `agent/wip` when you start; remove it when you finish

### 6. Verify — prove it

- For each acceptance criterion, paste **the command and its output** into the PR body
- Run lint / typecheck / tests locally before pushing
- If CI is red, **that is your job**. Fix it until it is green

### 7. Record — write it down

- Update the doc to as-built and set `status: implemented`
- Promote any durable decision discovered during the build to an **ADR**
- If you found more work, open an Issue — do not just implement it

---

## Session design

An AI's context window is finite, and accuracy drops as a session grows.
**Align session boundaries with gates.**

| Session | Input | Output | Budget |
| --- | --- | --- | --- |
| Research | An Issue | Research notes | 1 session |
| Design | Issue + notes | A doc PR | 1 session |
| Implementation | **An approved doc + one Issue** | One PR | 1–2 sessions |
| Fix-up | PR + CI logs / review comments | Extra commits | Short |

**An implementation session should need nothing beyond the doc and the Issue.**
If it needs more, that is a defect in the doc — thicken `Context for Agents`.

> If a session is dragging and going in circles, do not push through.
> **Throw it away, fix the doc, and start again.** That is cheaper than salvaging a
> session with polluted context.

---

## The boundary of autonomy

### Proceed without asking

- Research, reproduction, reading existing code
- Drafting and shaping docs, Issues, PRs
- Implementing an Issue that carries `agent/ready`
- Fixing red CI on your own PR
- Small, local review comments

### Always ask

- **Settling a Decision Point**
- Any change beyond the doc's or Issue's scope
- Adding or upgrading a dependency
- Changing a public API or schema
- Irreversible operations (deleting data, running a migration, releasing)
- Anything labelled `risk/high`
- "I think this Issue is unnecessary" — **rejection is a human power**

### The default when unsure

> **Ask.** But not "what should I do?" — ask **with options and a recommendation**.
> A bare question has not reduced the human's cost of deciding.

---

## Splitting work across agents

When running several AI sessions in parallel:

- **1 Issue = 1 session.** Two sessions never touch the same files
- Apply `agent/wip` on start, to prevent double-starting
- Run dependent Issues serially (honour `Depends on #n`)
- **Open a separate session for review.** You cannot review your own code —
  that is as true for an AI as for a human

---

## Prompt convention

Hand work to an agent in this shape.

```
Goal:        <link to the Issue>
Reference:   <link to the DD>, if any
Deliverable: <PR / doc / research notes>
Constraints: <where you may touch, which dependencies you may use>
Done when:   <acceptance criteria and the verifying commands>
```

**Pass links, not pasted content.** Pasted content drifts from the original and nobody can
tell which is authoritative. The copy in GitHub is always the single source of truth.

---

## Failure patterns and what to do

| Symptom | Real cause | Fix |
| --- | --- | --- |
| The build drifts from the design | `Context for Agents` is thin | Write the constraints concretely |
| Scope expands on its own | `Non-Goals` is empty | State what you are not doing |
| Plausible code that does not run | Verification is weak | Require a command on every AC |
| The same comment every time | The convention is tribal knowledge | Move it to `CLAUDE.md` or a linter |
| Sessions go in circles | The Issue is too big | Split to half a day–two days |
| Review exhausts the human | The ACs are too vague to judge | Rewrite them to be verifiable |
| AI decides things on its own | Decision Points were never extracted | Check for them during doc review |

**In every case, the thing to fix is a process artifact — the doc, the Issue, or CI —
not the prompt.**
