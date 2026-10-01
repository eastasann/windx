<!--
1 PR = 1 Issue. Do not delete the checklist items — fill them in, or write "N/A: <reason>".
Definition of done: docs/process/07-definition-of-done.md
-->

## What this PR does

<!-- Two or three sentences. The intent should be clear without reading the diff. -->

## Traceability

- Closes #
- Design doc: <!-- DD-xxxx, or "not needed (<reason>)" -->
- Related ADR: <!-- ADR-xxxx, or none -->

## Verification of the acceptance criteria

<!--
For each AC in the Issue or doc, give the command and **its actual output**.
"It should pass" is not acceptable. Paste what you ran.
-->

| AC | Command | Result |
| --- | --- | --- |
| AC-1 | `` | pass / fail |

<details>
<summary>Run log</summary>

```text

```

</details>

## Agreement with the design

- [ ] Implemented as the design doc describes
- [ ] Where it drifted, **the doc was updated in this same PR** (what changed: )
- [ ] There was **no drift in the approach itself** (if there was, it goes back to G1)
- [ ] No changes outside the scope of the doc or Issue

## Checklist

- [ ] `Closes #<issue>` is present (1 PR = 1 Issue)
- [ ] Every acceptance criterion is met, with the verification above
- [ ] New behaviour has tests / a bug fix **started from a failing test**
- [ ] CI is green (**not by skipping, disabling, or deleting a test**)
- [ ] No secrets (tokens, keys, internal hostnames)

## Only when behaviour changes

- [ ] A rollback path exists: <!-- revert is enough / these steps are needed: -->
- [ ] Failure is observable (logs, metrics, alerts)
- [ ] If a migration is needed, the old and new states can coexist during it

## Only for risk/high

- [ ] Two reviewer approvals
- [ ] Blast radius of failure: <!-- who is affected, and how -->
- [ ] Staged rollout (flag / canary) considered: <!-- adopted / declined (reason) -->

## For the reviewer

<!--
What you especially want looked at, and anything you want a decision on.
Prefix comments with [blocker] / [question] / [suggestion] / [nit] (docs/process/04-review.md).
-->
