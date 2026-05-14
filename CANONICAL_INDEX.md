# DETERMA Canonical Repository Index

## Purpose

This document defines the canonical knowledge hierarchy for the DETERMA internal repository.

Its purpose is to:

- establish authoritative document locations
- separate public, diligence, and internal materials
- reduce architectural drift
- preserve continuity
- define the source of truth for each knowledge domain

---

# Canonical Repository Layers

| Layer | Purpose | Exposure Level |
|---|---|---|
| Public Showcase | Public positioning, onboarding, demos | Public |
| Curated Diligence | Guided investor and partner review | Restricted |
| Strategic Technical Review | Controlled deep review | Highly Restricted |
| Internal Authority Core | Canonical implementation and governance memory | Internal Only |

---

# Canonical Directories

## Public-Safe Material

```text
/diligence/public_safe/
```

Purpose:
- sanitized architecture
- onboarding
- public-safe runtime explanations
- partner-ready documentation

---

## Curated Diligence Material

```text
/diligence/curated/
```

Purpose:
- investor review
- design partner onboarding
- selected runtime evidence
- selected threat scenarios

---

## Internal Governance

```text
/docs/governance/
```

Purpose:
- disclosure doctrine
- governance doctrine
- operational governance policies
- repository governance

---

## Internal Runtime Doctrine

```text
/docs/core/
```

Purpose:
- runtime legitimacy
- execution semantics
- convergence rules
- authority doctrine
- threat modeling

---

## Internal Archive

```text
/internal_archive/
```

Purpose:
- sensitive invention materials
- deep technical materials
- long-term architecture materials
- sequencing strategy
- restricted internal knowledge

---

# Migration Rules

## Rule 1

Do not delete historical documents during migration.

Move deprecated or superseded material into archival locations.

---

## Rule 2

Restricted internal material must not be placed in:

- public repositories
- public NotebookLM corpora
- unrestricted diligence repositories

---

## Rule 3

Public material should explain:

- problem
- architecture direction
- operational outcome

without exposing internal mechanism details.

---

## Rule 4

All future repository restructuring should follow:

```text
internal → sanitized → external
```

---

# Canonical Operational Principle

```text
Public = proof.
Private = mechanism.
```
