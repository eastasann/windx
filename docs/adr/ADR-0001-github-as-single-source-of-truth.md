---
id: ADR-0001
title: "GitHub is the single source of truth; no decisions live in external tools"
status: accepted
date: 2026-09-22
deciders: ["@eastasann"]
related_docs: ["DD-0001"]
supersedes: []
superseded_by: null
---

## Context

We have to decide where the pieces of the development process live: issue tracking, the
roadmap, design documents, decision records, and review. The common arrangement is
distributed — Jira or Linear for issues, Notion or Confluence for documents, GitHub for code.

This project, however, treats AI agents as the primary executors. For them, a distributed
arrangement carries costs that it does not carry for humans.

- An agent must cross several tools, APIs, and authentication systems to assemble context
- Each tool's state updates independently, and nothing can decide mechanically which is current
- There is no way to detect drift between code and design documents, because they live in
  different repositories and different systems
- Links between tools break easily, and a broken link is equivalent to lost knowledge

Code will live in GitHub; that is settled. So the question is really
**whether everything else moves there too, or stays distributed.**

## Decision

Issue tracking, the roadmap, design documents, decision records, and review all live in
GitHub. Design documents and ADRs are **Markdown files in the same repository as the code**,
reviewed through the same pull request process. Issues handle tracking; Projects (v2) and
Milestones handle the roadmap.

No decision, state, or rationale is persisted outside GitHub — not in chat, a spreadsheet, or
an external document tool. Anything settled in a synchronous conversation is not treated as
settled until it is written back into GitHub.

## Consequences

### Good outcomes

- An agent reaches the whole context through one authentication and one API
- Design documents and code ride the same PR and the same history, so drift is detectable in CI
- The rationale for a decision persists in `git log` and in PRs, traceable six months later
- Cross-tool synchronisation, and the inconsistencies from failing to synchronise, cannot occur

### Bad outcomes / costs accepted

- **Issues and Projects are less expressive than dedicated tools.** Effort rollups,
  dependency graphs, and sprint burndowns must be built by hand or given up
- **The barrier for non-engineers rises.** Markdown and PRs carry a learning cost for
  product, sales, and others who would otherwise contribute directly
- **A single point of dependency on GitHub.** During an outage, neither issue tracking nor
  the documents are reachable
- **Projects (v2) automation must track GitHub's own API changes**

### Signals that this should be revisited

- Non-engineer participants reach three or more on an ongoing basis and Issue filing stalls
- Roadmap requirements that Projects (v2) cannot express (cross-repository dependency
  management, say) become routine
- GitHub outages start stopping work on a monthly basis

## Alternatives Considered

- **Jira/Linear + Notion + GitHub, distributed**: each tool is more expressive, but an agent
  needs three authentication systems and three APIs to assemble context, and no tool can
  guarantee consistency across them. Being unable to decide currency mechanically is fatal
  under AI-driven work.
- **Design documents in a separate repository**: this separates permissions cleanly, but it
  makes "update the doc to as-built in the same PR as the implementation" impossible, which
  loses drift detection.
- **Design documents in the GitHub Wiki**: review does not ride a PR, history is harder to
  follow, and structural validation cannot run in CI.
