# 08. ADR standard

An ADR (Architecture Decision Record) is the durable record of **why we decided this**.

## How it differs from a design doc

| | design doc (DD) | ADR |
| --- | --- | --- |
| The question | **How we build it** | **Why we decided it** |
| Tense | A plan, before the build | **A record of the moment of decision** |
| Lifetime | Rarely read once built | **Read for years** |
| Length | 1–5 pages | **One page or less** |
| Updates | Updated to as-built | **Never updated** — supersede it with a new ADR |
| Count | One per feature | One per decision (0–3 come out of one DD) |

> A DD is a plan; an ADR is **the minutes**. Rewriting an ADR afterwards is falsifying history.

---

## When to write one

Write down decisions that **someone will later ask "why?" about**.

- Technology choices (language, framework, database, external service)
- Architectural boundaries (service split, layering, direction of dependencies)
- Cross-cutting policy (auth, error handling, log format, naming)
- **Things we decided not to do** (e.g. "we will not split into microservices")
- Decisions about the process itself (such as `ADR-0001` here)

Do not write one for:

- Implementation detail (variable names, function split)
- A judgment contained within one feature (the DD covers it)
- A decision you could change tomorrow

**The test**: "In six months, will a new joiner ask why this is the way it is?"
If yes, write the ADR.

---

## How to write it

```bash
python3 scripts/new_doc.py adr "Adopt Redis for the session store" --slug session-store-redis
```

Template: [`docs/templates/adr.md`](../templates/adr.md)

```
front matter    ← id / status / date / deciders / related
## Context      ← the situation, and what had to be decided
## Decision     ← what was decided (active voice, declarative, 1–3 sentences)
## Consequences ← good outcomes / bad outcomes / risk accepted
## Alternatives Considered ← the other options and why they lost (2–3 lines each)
```

### Craft notes

- **The title is the decision itself**
  - ❌ "About the session store" ❌ "Auth investigation"
  - ✅ "Adopt Redis for the session store" ✅ "Do not split into services for now"
- **Write the Decision in active, declarative voice**
  - ❌ "Redis seems preferable" → ✅ "Sessions are stored in Redis"
- **Consequences must include the bad outcomes**
  - There is no decision without a trade-off. If you cannot name one, you have not thought it through
- **If it runs past one page, it is a design doc**

---

## States

```
proposed ──→ accepted ──→ superseded (replaced by a new ADR)
    │            │
    └──→ rejected└──→ deprecated (no longer applies, with no replacement)
```

| status | Meaning |
| --- | --- |
| `proposed` | Proposed (PR under review) |
| `accepted` | Adopted. Current policy |
| `rejected` | Rejected. **Kept**, to prevent re-litigating it |
| `superseded` | Replaced; `superseded_by: ADR-xxxx` names the successor |
| `deprecated` | Its premise disappeared (the feature was removed, etc.) |

**Never rewrite a past ADR.** When a decision changes:

1. Write a new ADR (its Context says "ADR-xxxx needed revisiting")
2. The new ADR gets `supersedes: [ADR-xxxx]`
3. The old one moves to `superseded` with `superseded_by` set — **those two lines are the
   only edit ever permitted to an old ADR**

---

## Review and merge

- An ADR goes up as **its own PR**, titled `docs(adr): ADR-xxxx <title>`
- The reviewer's question is "**can I genuinely live with these Consequences?**"
- Merging makes it `accepted`
- Merge it **before** the implementation PR — decide, then build

---

## When AI writes the ADR

Watch for these degradations in particular.

| Likely degradation | Countermeasure |
| --- | --- |
| The "bad outcomes" are thin | **Require two or more.** If you cannot, the thinking is incomplete |
| Alternatives rejected as "too complex" | Make it say who pays what cost |
| The history gets summarised into something distorted | Quote the PR comment threads |
| Undecided things written as decided | Keep `proposed` until the Owner makes it `accepted` |

The A (accountability) for an ADR **always sits with the human Owner**.
AI writes the draft; moving it to `accepted` is the Owner's act of signature.

---

## Index

[`docs/adr/README.md`](../adr/README.md) holds the list of all ADRs.
`scripts/validate_docs.py` checks the index against the files.
