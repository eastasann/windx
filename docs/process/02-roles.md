# 02. Roles

## What is actually scarce

In AI-driven development, the ability to write code is not the scarce resource.

| Resource | Scarcity | Who holds it |
| --- | --- | --- |
| Writing code | Abundant | AI |
| Writing documents | Abundant | AI |
| Researching | Abundant | AI |
| **Judgment with context** | **Scarce** | **Humans** |
| **Taking responsibility** | **Scarce** | **Humans** |
| **Deciding not to do something** | **Scarce** | **Humans** |

So there is one principle for dividing the work.

> **Spend human time on judgment only.**
> If a human is writing prose, or reading an AI's output end to end, the design is wrong.

---

## The roles

| Role | Who | Owns |
| --- | --- | --- |
| **Owner** | One human | Final responsibility for that Issue or doc. Answers the Decision Points. Approves |
| **Reviewer** | One or more humans | Raises objections to design and code. Objections go on the record |
| **Agent** | AI | Executes research, drafting, decomposition, implementation, verification, recording |
| **Approver** | Human | Decides G3 (ship). On a small team, the same person as the Owner |

A doc or Issue with no Owner does not move. **Pick the Owner when you open it.**

---

## RACI

R = responsible, A = accountable, C = consulted, I = informed

| Activity | Agent | Owner | Reviewer |
| --- | --- | --- | --- |
| Research and reproduction | **R** | A | I |
| Opening and shaping Issues | **R** | A | I |
| Setting priority | C | **R/A** | C |
| Writing the design doc | **R** | A | I |
| Enumerating alternatives | **R** | A | C |
| **Answering the Decision Points** | C | **R/A** | **C** |
| Approving the doc (G1) | I | **R/A** | **C** |
| Decomposing into Issues | **R** | A | I |
| Implementation | **R** | A | I |
| Writing tests | **R** | A | I |
| Code review | C | A | **R** |
| Merging (G2) | I | **R/A** | C |
| Ship decision (G3) | I | C | I |
| Writing ADRs | **R** | **A** | C |

How to read it: **AI holds R widely but never holds A.**
Accountability always sits with a human. That is not a statement about AI's capability —
it is a statement about where responsibility lives.

---

## The four things humans never hand over

1. **Answering the Decision Points** — choosing at a design fork
2. **Rejecting scope** — deciding "we will not do this"
3. **Accepting the work** — agreeing that it solves the problem
4. **The ship decision** — the responsibility of releasing

Everything else can be delegated to AI. If you choose not to delegate something,
write down why, so you can tell an outdated process from insufficient AI output quality.

---

## Choosing reviewers

| Nature of the change | Reviewers required |
| --- | --- |
| Ordinary change | 1 reviewer |
| Public API or schema change | 2 reviewers, one familiar with the area |
| Security, auth, permissions, billing | 2 reviewers plus the `risk/high` label. **AI approval alone is not valid** |
| A change to the process itself | Owner plus 1 reviewer; an ADR is mandatory |
| Typos, wording, formatting | No review needed if CI passes |

---

## "An AI wrote it" is not a reason

- ❌ "An AI wrote this code, so I'll read every line to be safe" → review becomes the bottleneck
- ❌ "An AI wrote it, so it's fine" → abdicating accountability
- ✅ **"Make it produce verifiable output, then judge from the verification."**

If review is exhausting you, the thing to fix is not your diligence. It is the
**granularity of the acceptance criteria** and the **coverage of CI**
(see [07-definition-of-done.md](07-definition-of-done.md)).
