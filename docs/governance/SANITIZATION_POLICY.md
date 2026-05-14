# DETERMA Sanitization Policy

## Purpose

This document defines how internal DETERMA materials should be sanitized before appearing in:

- public repositories
- diligence repositories
- presentations
- NotebookLM corpora
- onboarding systems
- partner-facing materials

---

# Canonical Principle

```text
Sanitization should preserve understanding while removing moat-critical mechanics.
```

---

# Sanitization Objectives

Sanitized materials should:

- preserve conceptual clarity
- explain operational outcomes
- communicate runtime philosophy
- support technical legitimacy
- avoid exposing restricted implementation semantics

---

# Remove or Abstract

## Remove

- cryptographic enforcement mechanics
- replay invalidation internals
- authority issuance semantics
- capability lifecycle mechanics
- hidden runtime invariants
- orchestration internals
- moat-critical sequencing
- invention-sensitive details

---

## Abstract

Instead of:

```text
exact implementation semantics
```

prefer:

```text
runtime philosophy and operational outcome
```

---

# Approved Public Concepts

Public-safe materials may explain:

- fail-open vs fail-closed
- governed execution
- constrained mutation
- replay-aware governance
- execution legitimacy
- runtime lineage concepts
- stale execution state risks

without exposing exact enforcement mechanics.

---

# Canonical Workflow

All external material should follow:

```text
internal → sanitized → external
```

---

# Review Requirement

Sanitized materials should be reviewed before external exposure.

Especially when discussing:

- replay semantics
- runtime legitimacy
- authority models
- governance architecture

---

# NotebookLM Rule

NotebookLM corpora should ingest sanitized derivatives rather than unrestricted internal archives.

---

# Canonical Principle

```text
The public layer should explain why the system matters.
The private layer should preserve how the system works.
```
