---
name: adr
description: Record a settled decision as an ADR (Architecture Decision Record). Use when asked to write an ADR or record a decision, when a technology choice, architectural boundary, or cross-cutting policy is settled, or when something is decided against.
---

# Recording a decision as an ADR

Conventions: `docs/process/08-adr.md`

**An ADR is minutes, not a plan.** Where a design doc says *how we build it*, an ADR records
**why we decided it**. One page or less.

---

## Decide whether to write one

### Write one for

- Technology choices (language, framework, database, external service)
- Architectural boundaries (service split, layering, direction of dependencies)
- Cross-cutting policy (auth, error handling, log format, naming)
- **Things decided against** (e.g. "we will not split into microservices")
- Decisions about the process itself

### Do not write one for

- Implementation detail (variable names, function split)
- A judgment contained within one feature (the DD covers it)
- A decision you could change tomorrow

**The test**: "In six months, will a new joiner ask why this is the way it is?"

---

## Steps

### 1. Create it

```bash
python3 scripts/new_doc.py adr "<the decision, in active voice>" --slug <english-slug>
```

**The title is the decision itself.**

- ❌ "About the session store", "Auth investigation"
- ✅ "Adopt Redis for the session store", "Do not split into services for now"

### 2. Write the sections

#### Context

The situation, and what had to be decided. Two or three paragraphs. Note any constraints
(deadline, staffing, existing systems, regulation). **Do not put the decision here.**

#### Decision

**Active voice, declarative, one to three sentences.**

- ❌ "Redis seems preferable"
- ✅ "Sessions are stored in Redis"

#### Consequences

**Always name two or more bad outcomes / costs accepted.**
CI (`validate_docs.py`) fails the ADR otherwise.

> There is no decision without a trade-off. If you cannot name one, you have not thought it through.

Write "signals that this should be revisited" **observably** — not "if things change" but
"if non-engineer participants reach three or more".

#### Alternatives Considered

Two or three lines each. Leave the detail to the related design doc.

### 3. Validate and submit

```bash
python3 scripts/validate_docs.py
python3 scripts/check_links.py
```

- **Its own PR**, titled `docs(adr): ADR-xxxx <title>`
- Merge it **before** the implementation PR — decide, then build
- A human moves `status` to `accepted` on merge

---

## Writing an ADR from a discussion

When the source is a PR comment thread or an Issue:

1. **Do not summarise the history into something distorted.** Quote the original comments
2. If there was dissent, keep it in `Alternatives Considered` or `Consequences`
3. Never write an unsettled point as decided. Leave `status: proposed` while it is open

---

## Superseding an existing ADR

**Never rewrite a past ADR.** The procedure:

1. Write a new ADR. Its Context says "ADR-xxxx needed revisiting"
2. The new ADR's front matter gets `supersedes: ["ADR-xxxx"]`
3. The old one moves to `superseded` with `superseded_by` set —
   **those two lines are the only edit ever permitted**

---

## Never

- Set it to `accepted` (**that is the Owner's act of signature**; submit it as `proposed`)
- Omit the bad outcomes, or give only one
- Rewrite the body of a past ADR
- Write an unsettled point as decided
- Run past one page (if it does, it is a design doc)
