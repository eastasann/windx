# Process Standard

| # | Document | What's in it |
| --- | --- | --- |
| 01 | [Lifecycle and the four gates](01-lifecycle.md) | The flow from idea to shipped, and the four points where a human decides |
| 02 | [Roles](02-roles.md) | What humans own versus what AI owns (RACI), and how reviewers are chosen |
| 03 | [Design doc standard](03-design-doc.md) | When to write one, what goes in it, state transitions, the AI-specific additions |
| 04 | [Review standard](04-review.md) | Doc review and code review, SLAs, how to handle disagreement |
| 05 | [Issues and the roadmap](05-issues-roadmap.md) | Label taxonomy, Projects design, Milestone practice |
| 06 | [Agent execution protocol](06-agent-protocol.md) | The AI execution loop, session design, limits of autonomy |
| 07 | [Definition of done](07-definition-of-done.md) | DoR / DoD and the quality gates |
| 08 | [ADR standard](08-adr.md) | How to record decisions, and how to reject or supersede them |
| 09 | [Setup checklist](09-setup-checklist.md) | What a human configures on GitHub (Projects, branch protection, and the rest) |

## One-page summary

```
G0 frame the problem ──→ G1 agree on design ──→ G2 approve the build ──→ G3 decide to ship
   Issue                   Design Doc              Pull Request             Release
```

- **AI does**: research, writing, decomposition, implementation, verification, recording
- **Humans do**: decide at the gates — Decision Points, acceptance, ship-or-not
- **Where records live**: all of it in GitHub (Issues / PRs / `docs/` / Projects / Milestones)

## Changing this process

The process follows its own process. To change it:

1. Open an Issue with the `type/process` label
2. If the impact is large, write a design doc (this process's own is `DD-0001`)
3. Review it as a PR, and record anything settled as an ADR
