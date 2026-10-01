---
id: ADR-0004
title: "Projects automation is implemented independently of project ownership type"
status: accepted
date: 2026-10-01
deciders: ["@eastasann"]
related_docs: ["DD-0001"]
supersedes: []
superseded_by: null
---

## Context

DD-0001 DP-5 settled that the Projects (v2) automation would be code in the repository rather
than GUI configuration, for consistency with ADR-0001. That raised the question of which
credential the automation uses, because **`GITHUB_TOKEN` cannot operate on Projects v2 at all**.
The `repository-projects` entry under a workflow's `permissions:` key applies to classic
projects (v1) and has no effect here.

The usable credential then depends on who owns the project, and the two cases do not overlap
(the full matrix is in DD-0001 Appendix A-3):

- **user-owned**: only a classic PAT with the `project` scope works. A GitHub App cannot reach
  user-level Projects, and a fine-grained PAT cannot obtain Projects permission for a personal
  account
- **org-owned**: a GitHub App with organisation `Projects: read and write` is GitHub's
  recommended setup and the narrowest permission; a classic PAT also works

The repository currently sits under a personal account, so the obvious move would be to write
for the user-owned case. But the Owner asked that organisation ownership be accommodated too,
and an organisation is the better destination: the App path keeps the credential far narrower
than a classic PAT, whose `project` scope cannot be restricted to a single repository.

## Decision

The automation is written to be independent of ownership type. Concretely:

- The owner type is configuration — `PROJECT_OWNER_TYPE` is `user` or `organization` — alongside
  `PROJECT_OWNER` and `PROJECT_NUMBER`
- The credential is abstracted behind a single secret name, **`PROJECTS_TOKEN`**. The same code
  runs whether it holds a classic PAT or a GitHub App installation token
- The only ownership-dependent logic is the GraphQL lookup, which selects between
  `user(login:)` and `organization(login:)`

## Consequences

### Good outcomes

- The same automation serves the current personal account and a future organisation
- Moving to an organisation requires swapping the contents of `PROJECTS_TOKEN` for an App
  installation token — no code change — which migrates towards the narrower permission
- The ownership-dependent surface is confined to one query branch, so it is easy to read and to
  delete if one side is ever dropped
- The sync can be exercised without a credential (`--self-test`, `--dry-run`), so CI validates
  the mapping logic without secrets

### Bad outcomes / costs accepted

- **Two authentication paths must be documented and kept working.** The setup checklist carries
  both, and only one of them is ever exercised by this repository, so the other can rot unnoticed
- **While the project stays user-owned, the broad classic PAT remains in use.** Its `project`
  scope cannot be narrowed, and with `repo` it reaches every repository the Owner can see; the
  mitigation is only operational (token exclusive to Projects, expiry within 90 days)
- **The ownership branch is a small amount of permanently dead code** — one of the two paths is
  always unused at runtime
- **Carrying both delays the move to an organisation**, because the personal-account path keeps
  working and removes the pressure to migrate

### Signals that this should be revisited

- The project moves to an organisation and the user-owned path goes unexercised for a quarter
  (delete it and standardise on the App)
- GitHub grants `GITHUB_TOKEN` access to Projects v2 (the whole token question disappears)
- Fine-grained PATs gain Projects permission for personal accounts (the classic PAT path can go)

## Alternatives Considered

- **Assume organisation ownership and standardise on a GitHub App**: GitHub's recommended setup
  and the narrowest permission, but it does not work on the current personal account, so the
  automation could not be exercised at all today.
- **Assume user ownership with a classic PAT**: the smallest code, but it locks the automation to
  a broad credential and means rebuilding on a move to an organisation.
- **Keep the built-in Project workflows (no code)**: zero maintenance, but it contradicts
  DP-5 and ADR-0001 by leaving the configuration unreviewable and unreproducible.
