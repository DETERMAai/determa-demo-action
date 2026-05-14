# DETERMA Canonical Reference Model

## Purpose

This document defines how canonical references should work across DETERMA repositories and governance layers.

The objective is to:

- reduce ambiguity
- prevent duplicate truths
- preserve architectural consistency
- support long-term maintainability

---

# Canonical Principle

```text
One concept should map to one authoritative source.
```

---

# Canonical Reference Structure

Each major concept should define:

| Field | Meaning |
|---|---|
| Canonical Source | The authoritative document |
| Derivative Sources | Sanitized or simplified explanations |
| Exposure Level | Public, Diligence, Internal, Restricted |
| Status | Canonical, Superseded, Deprecated, Archived |

---

# Example Model

## Runtime Legitimacy

| Field | Value |
|---|---|
| Canonical Source | `/docs/core/RUNTIME_SUCCESS_CRITERIA.md` |
| Derivative Sources | `SANITIZED_RUNTIME_SUCCESS_CRITERIA.md` |
| Exposure Level | Diligence |
| Status | Canonical |

---

## Threat Scenarios

| Field | Value |
|---|---|
| Canonical Source | `/docs/core/THREAT_SCENARIOS.md` |
| Derivative Sources | `SANITIZED_THREAT_SCENARIOS.md` |
| Exposure Level | Diligence |
| Status | Canonical |

---

## Public Positioning

| Field | Value |
|---|---|
| Canonical Source | `PUBLIC_POSITIONING_CANON.md` |
| Derivative Sources | public presentations and onboarding |
| Exposure Level | Public |
| Status | Canonical |

---

# Derivative Material Rules

Derivative materials:

- simplify
- sanitize
- contextualize

but should not redefine canonical semantics.

---

# Governance Rule

When canonical semantics change:

- derivative layers must be reviewed
- outdated public explanations should be updated
- contradictory narratives should be removed

---

# NotebookLM Rule

NotebookLM systems should prioritize:

- canonical materials
- approved sanitized derivatives

and avoid:

- conflicting superseded sources
- deprecated semantics
- unrestricted archives

---

# Canonical Principle

```text
Narratives may vary.
Canonical meaning should not.
```
