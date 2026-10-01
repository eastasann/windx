# 09. Setup checklist

What **a human configures on GitHub** after taking this repository in.
It covers only the parts that cannot be expressed as code — creating the Project,
branch protection, and so on.

---

## 1. Sync the labels

Once this lands on `main`, the [`labels` workflow](../../.github/workflows/labels.yml) runs
and creates the 33 labels in [`.github/labels.yml`](../../.github/labels.yml).

To run it by hand:

```bash
gh workflow run labels.yml           # from Actions
GH_REPO=eastasann/windx python3 scripts/sync_labels.py   # or locally
```

- [ ] The labels exist on GitHub (`gh label list`)
- [ ] Delete the defaults you do not want (`bug`, `enhancement`, …)
      (`scripts/sync_labels.py --prune` removes everything not in `labels.yml`.
      **Do it right after onboarding**, since it detaches labels from existing Issues)

---

## 2. Set up Projects (v2)

The design is in [05-issues-roadmap.md](05-issues-roadmap.md).
Per DP-5 and DP-6 in [`DD-0001`](../design/DD-0001-development-process.md), field and status
synchronisation **is implemented as code**
([`project-sync.yml`](../../.github/workflows/project-sync.yml) +
[`scripts/project_sync.py`](../../scripts/project_sync.py)).
Two things stay manual.

### 2-1. Create the Project (first time only)

- [ ] Create a project named `windx Roadmap`
- [ ] Note its number (the `/projects/<number>` in the URL)
- [ ] Add the custom fields

| Field | Type | Values |
| --- | --- | --- |
| Status | Single select | `Inbox` / `Triaged` / `Designing` / `Ready` / `In Progress` / `In Review` / `Done` / `Dropped` |
| Stage | Single select | `G0` / `G1` / `G2` / `G3` |
| Target | Iteration | 2 weeks |
| Design Doc | Text | — |
| Confidence | Single select | `High` / `Medium` / `Low` |
| Size | Single select | `XS` / `S` / `M` / `L` / `XL` |

- [ ] Create the views

| View | Type | Filter |
| --- | --- | --- |
| Board | Board (by Status) | — |
| Roadmap | Roadmap (by Milestone) | — |
| Triage | Table | `Status = Inbox` |
| **Needs Decision** | Table | `label:agent/needs-human` |
| **Agent Queue** | Table | `label:agent/ready`, by priority |

> **Separating Needs Decision from Agent Queue is the heart of this process.**
> Humans watch the first; AI watches the second.

### 2-2. Provide a token for the sync (**required by the automation**)

**`GITHUB_TOKEN` cannot write to Projects v2** regardless of who owns the project
(the `repository-projects` permission is for classic projects). The token depends on the
owner type — see `DD-0001` Appendix A-3 for the full matrix.

**If the project is owned by an organisation** (GitHub's recommended setup):

- [ ] Create a GitHub App with **organisation `Projects: read and write`**
      (repository Projects permission is *not* sufficient)
- [ ] Install it on the organisation
- [ ] Store the App ID and private key as secrets, and mint an installation token in the
      workflow (e.g. `actions/create-github-app-token`)
- [ ] Expose that token to the workflow as **`PROJECTS_TOKEN`**

**If the project is owned by a personal account**:

- [ ] Create a **classic** PAT with the **`project`** scope
      (a fine-grained PAT cannot obtain Projects permission for a personal account)
- [ ] Set its expiry to **90 days or less** and put renewal into your routine
- [ ] Store it as the repository secret **`PROJECTS_TOKEN`**
- [ ] Do not reuse this token for anything else

> A classic PAT's `project` scope cannot be narrowed to one repository, and combined with
> `repo` it reaches every repository the user can see. Prefer organisation ownership with a
> GitHub App as soon as that is possible.

### 2-3. Configure the sync

- [ ] Set the repository variables (Settings → Variables):
      `PROJECT_OWNER` (the user or organisation login),
      `PROJECT_OWNER_TYPE` (`user` or `organization`),
      `PROJECT_NUMBER`
- [ ] Verify with `python3 scripts/project_sync.py --dry-run --issue <n>`
- [ ] Apply `agent/ready` to one Issue and confirm it appears in `Agent Queue`

---

## 3. Create the first Milestone

- [ ] Create one Milestone (e.g. `v0.1.0` or `2026-Q4`)
- [ ] **Write three sentences in the description saying what it achieves**
      (a Milestone that is only a date means nothing)

---

## 4. Configure branch protection

On `main`:

- [ ] Require pull requests to merge
- [ ] Require status checks: `docs-lint`, `pr-checks`
- [ ] Require at least one review approval
- [ ] Delete branches automatically after merge

> The "two reviewers for `risk/high`" rule cannot be fully expressed in GitHub settings;
> treat it as practice, per [04-review.md](04-review.md).

---

## 5. Enable Discussions

- [ ] Enable Discussions (the Issue template `config.yml` already links to it)

It is where "we have not decided whether to do this" lives. Once settled, it becomes an
Issue or an ADR.

---

## 6. Verify

```bash
python3 scripts/validate_docs.py
python3 scripts/check_links.py
python3 scripts/sync_labels.py --dry-run
python3 scripts/project_sync.py --dry-run
PR_BODY="Closes #1
Design doc: not needed (smoke test)" python3 scripts/check_pr.py
```

- [ ] All five succeed
- [ ] `docs-lint` and `pr-checks` are green on the first PR

---

## 7. Add these once product code lands

- [ ] lint / format / typecheck / unit tests in CI
- [ ] Secret scanning and dependency vulnerability scanning
- [ ] `area/*` labels matching the product's structure
- [ ] Build and test commands in `CLAUDE.md`
- [ ] AI review in CI (**never as a substitute for the human gate**)
