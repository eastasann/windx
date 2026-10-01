# CLAUDE.md — Standing rules for AI agents

Every AI agent working in this repository follows this file, every session.
The full process lives in `docs/process/`. This file is its **runtime summary**.

---

## 0. The three rules that outrank everything

1. **Do not decide on your own.** Never settle a design fork yourself — **surface it as a Decision Point** and let a human decide.
2. **Do not assert without evidence.** "This should work" is banned. Speak in **commands run and output observed**.
3. **Every decision gets written down.** Anything settled only in conversation **does not exist** until it is in a doc or an ADR.

---

## 1. Before you start

Check these, in this order.

1. **Is there an Issue?** If not, open one first (`.github/ISSUE_TEMPLATE/`).
2. **Which gate are you at?** G0–G3 in `docs/process/01-lifecycle.md`.
3. **Does this need a design doc?** Use the test below.
4. **Does the Issue carry `agent/ready`?** Never start autonomous implementation without it.

### Does this need a design doc?

A **design doc (DD) is required** if any of these hold.

- It spans more than one component or service
- It changes a public API, a schema, or the shape of persisted data
- It is expensive to change later (a migration would be needed)
- Two or more reasonable alternatives exist and picking one takes judgment
- It touches security, privacy, billing, or availability
- The estimate exceeds roughly 3 person-days / 3 sessions

If none hold, a **one-pager** (`docs/templates/one-pager.md`) or just the Issue body is enough.
**When in doubt, write the doc** — writing is cheap for an AI.

---

## 2. The execution loop

```
Explore → Design → Decide → Decompose → Implement → Verify → Record
research   draft     human     into        build     prove    update
           the doc   decides   Issues                         doc/ADR
```

What not to do in each phase:

| Phase | Do not |
| --- | --- |
| Explore | Write a design without reading the existing code |
| Design | Offer only one alternative / leave Decision Points empty |
| Decide | Start building before a human approves |
| Decompose | Create an Issue with no acceptance criteria |
| Implement | Pack several Issues into one PR / reach outside the doc's scope |
| Verify | Skip, disable, or delete a test to go green |
| Record | Leave the doc stale while the implementation has moved on |

---

## 3. Writing documents

- **design doc**: copy `docs/templates/design-doc.md`, or let `scripts/new_doc.py design "<title>" --slug <slug>` number it for you.
- **ADR**: `docs/templates/adr.md`, or `scripts/new_doc.py adr "<title>" --slug <slug>`.
- Required front matter keys and headings are enforced by `scripts/validate_docs.py`. **Run it locally before you submit.**

```bash
python3 scripts/validate_docs.py
python3 scripts/check_links.py
```

### How to write Alternatives Considered

Writing is cheap for an AI, so **always produce two or three genuinely workable alternatives**,
and for each one write:

- How it works (one paragraph)
- What you give up by choosing it (the trade-off)
- **Why it was rejected.** "Too complex" is not a reason — say what is complex about it and who pays that cost

### How to write Decision Points

List only what you want a human to decide. Every entry carries:

- Two or more options ("do it / don't do it" is a legitimate pair)
- **Your recommendation and the reasoning behind it**
- **The cost of reversing this decision later.** If reversing is cheap, say so and mark it `[proceed on the recommendation, revisable]`

**A doc with empty Decision Points must never be sent for review.**

---

## 4. Issues and the roadmap

- 1 Issue = 1 verifiable outcome. Break work down to half a day to two days.
- Required labels: `type/*`, `priority/*`. Add `agent/ready` only when it is genuinely ready.
- An Issue decomposed from a design doc **must** carry `Design doc: DD-xxxx` in its body.
- The roadmap is Milestones (time) plus the Projects Status/Stage fields.
  See `docs/process/05-issues-roadmap.md`.

**You never apply `agent/ready` yourself — a human does.** See `docs/process/07-definition-of-done.md`.

---

## 5. Pull requests

- **1 PR = 1 Issue.** Put `Closes #<issue>` in the body.
- If it came from a design doc, add `Design doc: DD-xxxx`.
- Fill in the checklist in `.github/pull_request_template.md` — do not delete items.
- **Before pushing**, run the repository's lint / typecheck / tests locally and **paste the results into the PR body**.
- Never leave a PR red and call it "waiting on review". Red CI is your job.

---

## 6. How to verify

- Write acceptance criteria as **Given / When / Then**, each with **the command that proves it**.
- For a bug fix, **write a failing test that reproduces it first**, then fix it.
- "It's flaky" is not a root cause. Re-run at most once.
- Skipping, disabling, or deleting a test to go green is forbidden, for any reason.

---

## 7. Hard rules (never do these)

- Start implementing a change that needs a design doc before a human approves it (G1)
- Decide a Decision Point yourself and write it into the doc as settled
- Extend the implementation beyond what the doc describes (scope creep)
- Put secrets (tokens, keys, internal hostnames) in a doc, Issue, or PR
- Leave the reasoning behind a decision only outside GitHub (chat and the like)
