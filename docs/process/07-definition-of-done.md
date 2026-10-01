# 07. Definition of done (DoR / DoD)

## The principle

> **A done you cannot verify is not done.**

An AI can quickly build something that *looks* like it works. So quality no longer rests on
"being careful". It rests on **making it produce verifiable output, and verifying it**.

---

## Definition of Ready — may we start?

Apply `agent/ready` to an Issue only when **all** of these hold.

- [ ] **The problem fits in one sentence** (not "improve X" but "when X, Y should not happen")
- [ ] **Acceptance criteria are verifiable** (Given / When / Then + the command)
- [ ] **The affected surface is identified** (files, modules)
- [ ] If a design doc is needed, it is **`status: approved`** and referenced from the Issue
- [ ] **No unresolved Decision Point**
- [ ] It is not `size/xl` (split it first)
- [ ] Any dependency Issue is closed or ready to start

**`agent/ready` is the single switch controlling AI autonomy, and a human throws it.**
Applied carelessly, the AI interprets a vague instruction on its own and builds that.
**Kill the ambiguity before work starts.**

---

## Definition of Done — may we merge?

### Every PR

- [ ] `Closes #<issue>` is present (1 PR = 1 Issue)
- [ ] **Every acceptance criterion met, with the verification output in the PR body**
- [ ] New behaviour has tests / a bug fix **started from a failing test**
- [ ] CI is green (**not by skipping, disabling, or deleting a test**)
- [ ] No changes outside the doc's or Issue's scope
- [ ] Review approved (two reviewers for `risk/high`)
- [ ] No secrets (tokens, keys, internal hostnames)

### Additionally, for a design-doc change

- [ ] `Design doc: DD-xxxx` in the PR body
- [ ] The implementation matches the doc (or the doc was updated in this same PR)
- [ ] The doc's `status` moved to `implemented` (on the last Issue)
- [ ] Any durable decision was recorded as an ADR

### Additionally, when behaviour changes

- [ ] A rollback path exists (especially where reverting the code is not enough)
- [ ] Observability exists — you will notice when it fails
- [ ] If a migration is needed, the steps exist and **both states can coexist during it**

### Additionally, for `risk/high`

- [ ] Two reviewer approvals
- [ ] The blast radius of failure stated in the PR body
- [ ] Staged rollout (flag / canary) considered

---

## Writing acceptance criteria

### Good

```markdown
- **AC-1**: Given an expired session, When `/api/me` is called,
  Then it returns 401 and writes one `session_expired` audit line
  - Verify: `pytest tests/auth/test_session_expiry.py -q`

- **AC-2**: Given 500 concurrent connections, When sessions are validated,
  Then p99 latency stays under 50ms
  - Verify: `make bench-auth` (paste the p99 line into the PR)
```

### Bad, and how to fix it

| Bad | What's wrong | Fix |
| --- | --- | --- |
| "It works correctly" | "Correct" is undefined | State the input and the expected output |
| "Performance improves" | Not measurable | State the metric, the threshold, the method |
| "Nothing existing breaks" | Scope is everything | Name the fragile spots individually |
| "Review finds no problems" | Depends on the person | Restate it so a machine can judge |
| "Handle errors" | Which errors | Enumerate the specific failure cases |

**A criterion with no way to verify it is not a criterion.** Rewrite it, or move it to
`Open Questions` and resolve it first.

---

## Quality gates (CI)

Running today:

| Workflow | Checks |
| --- | --- |
| [`docs-lint.yml`](../../.github/workflows/docs-lint.yml) | DD/ADR front matter, required headings, ID–filename agreement, index agreement, relative links, label definitions |
| [`pr-checks.yml`](../../.github/workflows/pr-checks.yml) | PR traceability (`Closes #n`, `Design doc:`) |
| [`labels.yml`](../../.github/workflows/labels.yml) | Syncs `labels.yml` to GitHub labels |
| [`project-sync.yml`](../../.github/workflows/project-sync.yml) | Syncs labels and state to Projects fields |

Add these once product code lands:

| To add | Why |
| --- | --- |
| lint / format | So humans never raise it in review |
| typecheck | Catches an AI calling an API that does not exist |
| unit tests | Regression detection on behaviour |
| dependency vulnerability scan | Supply-chain risk |
| secret scanning | Keeps secrets out of docs and code |

> If a human keeps raising the same point in review, that point belongs in CI.
> **Human review is for what cannot be written as a check.**

---

## The other side of done: deciding not to

There are only two reasons to close an Issue.

1. **Done** — it met the DoD
2. **Dropped** — we decided not to. **Write the reason in a comment before closing**

Silent closes and death by neglect are banned.
**"What we decided not to do" is worth keeping as a decision.**
When the same proposal returns in six months, that record makes the call fast.
