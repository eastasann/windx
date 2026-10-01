# windx — Development Process Standard

A process standard and toolchain that adapts Google's **design docs culture** to
AI-driven development, keeping **issue tracking, the roadmap, and decision records
entirely inside GitHub**.

---

## 1. Why design docs (redefined for AI-driven work)

Google's design docs worked for two reasons.

1. **Thinking by writing** — vague designs cannot survive prose
2. **Agreement through review** — objections arrive while they are still cheap

AI-driven development changes the structure underneath those two reasons.

| | Before | AI-driven |
| --- | --- | --- |
| Cost of writing a design | High (days) | **Near zero** (minutes) |
| Cost of implementation | High | Low |
| **Bottleneck** | Writing and building | **Deciding and verifying** |
| Alternatives considered | Tends to be lip service | **Three real options are affordable** |
| Audience of the doc | Humans only | **Humans + AI agents** |

Which leads to this.

> **A doc is both the artifact humans agree on and the largest context input an AI agent receives.**

So the design docs here keep Google's prose structure while adding machine-readable
front matter, verifiable acceptance criteria, and explicit constraints for agents.
And humans do not approve the whole doc — they **decide the Decision Points**.

The reasoning behind each choice lives in
[`docs/design/DD-0001-development-process.md`](docs/design/DD-0001-development-process.md),
this process's own design doc.

---

## 2. The shape of it

```
   ┌── G0 ──────────┐   ┌── G1 ────────┐   ┌── G2 ──────────┐   ┌── G3 ───────┐
   │ Frame the      │ → │ Agree on the │ → │ Approve the    │ → │ Decide to   │
   │ problem        │   │ design       │   │ implementation │   │ ship        │
   └────────────────┘   └──────────────┘   └────────────────┘   └─────────────┘
     Issue                Design Doc          Pull Request         Release
    (type/*)              (DD-xxxx)           (1 PR = 1 Issue)     (Milestone)
        │                     │                     │                   │
        └─────────────────────┴──────── ADR (ADR-xxxx) ─────────────────┘
                        the durable record of "why we chose this"

   AI:     runs the research, writing, decomposition, implementation, verification
   Human:  decides at the gates (Decision Points / acceptance / ship-or-not)
```

How that maps onto GitHub:

| Concept | What it is on GitHub |
| --- | --- |
| Problems and tasks | Issues (typed by `type/*` labels) |
| Design documents | `docs/design/DD-xxxx-*.md` + a tracking Issue |
| Decision records | `docs/adr/ADR-xxxx-*.md` |
| Roadmap | GitHub Projects (Roadmap view) + Milestones |
| Review and agreement | Pull Requests (docs are reviewed as PRs too) |
| Quality gates | GitHub Actions |

---

## 3. Where to start

| If you want to | Read |
| --- | --- |
| Understand the whole process | [`docs/process/01-lifecycle.md`](docs/process/01-lifecycle.md) |
| Know who decides what | [`docs/process/02-roles.md`](docs/process/02-roles.md) |
| Write a design doc | [`docs/process/03-design-doc.md`](docs/process/03-design-doc.md) / [template](docs/templates/design-doc.md) |
| Review something | [`docs/process/04-review.md`](docs/process/04-review.md) |
| Run issues and the roadmap | [`docs/process/05-issues-roadmap.md`](docs/process/05-issues-roadmap.md) |
| Put an AI agent to work | [`docs/process/06-agent-protocol.md`](docs/process/06-agent-protocol.md) |
| Check what "done" means | [`docs/process/07-definition-of-done.md`](docs/process/07-definition-of-done.md) |
| Record a decision | [`docs/process/08-adr.md`](docs/process/08-adr.md) |
| **Finish the GitHub-side setup** | [`docs/process/09-setup-checklist.md`](docs/process/09-setup-checklist.md) |

AI agents (Claude Code and friends) read [`CLAUDE.md`](CLAUDE.md) as their standing rules.

---

## 4. Tooling

```bash
# Create a numbered design doc or ADR
python3 scripts/new_doc.py design "Rework the upload pipeline" --slug upload-pipeline
python3 scripts/new_doc.py adr    "Adopt S3 for object storage"  --slug s3-object-storage

# Run the same checks CI runs
python3 scripts/validate_docs.py     # doc structure
python3 scripts/check_links.py       # relative links
python3 scripts/sync_labels.py --dry-run
python3 scripts/project_sync.py --dry-run   # Projects field sync
```

Claude Code skills (`.claude/skills/`):

| Skill | What it does |
| --- | --- |
| `design-doc` | Drafts a design doc from a problem, with alternatives and Decision Points |
| `decompose` | Breaks an approved design doc into implementation Issues |
| `adr` | Records a settled decision as an ADR |

---

## 5. Principles (come back here when in doubt)

1. **Humans decide, AI executes.** Spend human time only on judgment.
2. **Agree before building.** The most expensive rework is a design change after implementation.
3. **A decision that is not written down does not exist.** Move anything settled in conversation into a doc or an ADR.
4. **There is no done without verification.** Every acceptance criterion ships with the command that proves it.
5. **Docs are living assets.** When the implementation drifts from the doc, fix the doc.
6. **Everything in GitHub.** Never leave a decision in an external tool. A broken link is lost knowledge.
