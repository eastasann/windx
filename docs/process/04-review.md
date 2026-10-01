# 04. Review standard

## Review is not a hunt for mistakes

Under AI-driven development, syntax errors, type errors, and convention drift are caught
by CI and linters. Human review has exactly three jobs.

1. **Confirm the intent** — is this the right problem to solve
2. **Confirm the structure** — will this abstraction, boundary, or interface survive six months
3. **Catch the omission** — a missing assumption that appears in neither the doc nor CI

> If a human is saying "the indentation here is off", that is a linter misconfiguration,
> not a review.

---

## Design doc review (G1)

### How it runs

| Step | Who | What |
| --- | --- | --- |
| 1 | Agent | Opens a doc-only PR. `status: in-review` |
| 2 | Agent | **Copies the Decision Points into the top of the PR body** |
| 3 | Reviewer | Comments on the Decision Points. **No obligation to read the whole doc** |
| 4 | Owner | Settles each Decision Point, with the chosen option and the reasoning |
| 5 | Agent | Reflects the outcome in the doc as `**Decision**: A (<reason>)` |
| 6 | Owner | Sets `status: approved` and merges |

### The seven questions a reviewer asks

1. **Are the Non-Goals sufficient?** Is there an unstated "we will not do this"?
2. **Are the alternatives real?** Does any rejection stop at "too complex"?
3. **Was the cheapest option considered?** Are "do nothing" and "use what exists" on the list?
4. **Can the acceptance criteria be verified?** Is there a command for each?
5. **What happens if it fails?** Is there a rollback or a staged rollout?
6. **Who operates it?** Has someone accepted the operational cost?
7. **Could you build it from this doc alone?** Any assumption left implicit — an AI cannot fill it in.

### SLA

| Doc size | First review due |
| --- | --- |
| one-pager | 1 business day |
| Normal DD | 2 business days |
| Tagged `risk/high` | 3 business days, 2 reviewers |

Past the deadline the Owner either chases it or **settles the Decision Points provisionally
and moves on** — noting in the doc that it is provisional so it can be revisited.
**Stalling is the worst outcome.**

---

## Code review (G2)

### What to look at, and what to leave alone

| Look at | Leave to CI |
| --- | --- |
| Does it match the doc's design | Formatting and indentation |
| Does it stay inside the doc's scope | Type consistency |
| Placement of abstractions, split of responsibility | Lint rules |
| Do the tests verify *behaviour* | Whether tests pass |
| Error handling and boundary conditions | Import ordering |
| Naming consistent with existing code | Line length |

If a human is flagging something CI could flag, **fixing CI is the correct response**.

### Things specific to AI-written code

- **Plausible lies**: calls to APIs that do not exist (typecheck and run it)
- **Over-abstraction**: an interface with exactly one caller
- **Reinvention**: reimplementing a utility that already exists
- **Hollow tests**: assertions that only confirm a mock's return value
- **Out-of-scope changes**: "fixed this while I was here" — send it back if the doc or Issue did not ask

That last one matters most. **Scope creep is the most likely degradation under AI-driven work.**

### Weighting comments

Prefix each comment so the obligation is explicit.

| Prefix | Meaning | Obligation |
| --- | --- | --- |
| `[blocker]` | Cannot merge with this present | Required |
| `[question]` | I don't understand the intent | An answer is required; a code change may not be |
| `[suggestion]` | I think this would be better | Optional. If declining, give a one-line reason |
| `[nit]` | Taste | Optional. No reply needed |

An unprefixed comment is treated as `[suggestion]`.

### Handling disagreement

- If two rounds do not settle it, **move to a synchronous conversation** — but **write the conclusion back into the PR**
- If the objection is about the approach, do not push through at G2. **Send it back to G1** (update the doc, review again)
- If the outcome will matter in the future, **promote it to an ADR** ([08-adr.md](08-adr.md))

> A discussion that was never written back into GitHub did not happen.

---

## Letting AI review

AI review in CI is fine, as long as **its position is fixed**.

- AI review is **part of CI**, not a substitute for human review
- Treat its findings as **bug reports**: verify, then fix, or give a one-line reason not to
- A finding the AI marks `nit` or `optional` **does not by itself justify a push** — pick it up with the next code change
- An AI approval does not satisfy the G2 approval requirement. **Approval is always human.**

---

## Diagnosing a stuck review

| Symptom | Real cause | Fix |
| --- | --- | --- |
| The PR is too big to read | Issues are decomposed too coarsely | Return to the granularity rules in [05](05-issues-roadmap.md) |
| The same comment keeps recurring | The convention is undocumented | Move it into CLAUDE.md or a linter |
| Review is always slow | One person carries all of it | Spread reviewers by area |
| Design arguments erupt after the build | G1 is being skipped | Revisit the design-doc test |
| "Sure, LGTM" is spreading | The acceptance criteria are too vague to judge against | Rewrite them to be verifiable |
