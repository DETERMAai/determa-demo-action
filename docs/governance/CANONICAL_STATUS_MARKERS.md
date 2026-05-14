# DETERMA Canonical Status Marker Specification

## Purpose

This document defines the canonical metadata markers used across DETERMA repositories and knowledge layers.

The objective is to:

- reduce ambiguity
- identify canonical ownership
- support repository governance
- preserve continuity during migration
- distinguish originals from sanitized derivatives

---

# Canonical Principle

```text
Every important document should describe its governance state.
```

---

# Standard Markers

## Status Marker

Defines lifecycle state.

### Allowed Values

```text
STATUS: CANONICAL
STATUS: SANITIZED_DERIVATIVE
STATUS: SUPERSEDED
STATUS: DEPRECATED
STATUS: ARCHIVED
```

---

## Exposure Marker

Defines disclosure level.

### Allowed Values

```text
EXPOSURE: PUBLIC_SAFE
EXPOSURE: DILIGENCE
EXPOSURE: INTERNAL_CORE
EXPOSURE: RESTRICTED
```

---

## Canonical Source Marker

Used for derivative materials.

Example:

```text
CANONICAL_SOURCE: /docs/core/RUNTIME_SUCCESS_CRITERIA.md
```

---

## Supersession Marker

Example:

```text
SUPERSEDED_BY: /docs/core/NEW_RUNTIME_MODEL.md
```

---

# Example Header

```text
STATUS: SANITIZED_DERIVATIVE
EXPOSURE: DILIGENCE
CANONICAL_SOURCE: /docs/core/THREAT_SCENARIOS.md
```

---

# Governance Rules

## Rule 1

Derivative documents should reference their canonical source.

---

## Rule 2

Restricted documents should always contain explicit exposure markers.

---

## Rule 3

Superseded documents should remain archived for lineage preservation.

---

# NotebookLM Rule

NotebookLM corpora should prioritize:

- canonical sources
- approved sanitized derivatives

and avoid:

- deprecated semantics
- conflicting superseded documents

---

# Canonical Principle

```text
Governed systems require governed metadata.
```
