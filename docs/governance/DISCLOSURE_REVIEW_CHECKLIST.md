# DETERMA Disclosure Review Checklist

## Purpose

This checklist defines the canonical review process before exposing DETERMA material externally.

The objective is to:

- reduce accidental exposure
- preserve moat boundaries
- standardize disclosure decisions
- support disclosure-aware governance

---

# Canonical Principle

```text
External exposure should be intentional, not incidental.
```

---

# Review Categories

## Category 1 — Exposure Level

Determine intended exposure:

| Level | Meaning |
|---|---|
| Public | Public-safe showcase material |
| Diligence | Curated investor or partner material |
| Strategic Review | Controlled deep technical review |
| Internal | Internal-only knowledge |
| Restricted | Highly sensitive invention or moat material |

---

## Category 2 — Mechanism Leakage

Review whether the material exposes:

- replay invalidation internals
- authority issuance semantics
- capability lifecycle mechanics
- orchestration internals
- cryptographic enforcement details
- moat-critical sequencing

If yes, restrict exposure.

---

## Category 3 — Strategic Compression Risk

Ask:

```text
Could a sophisticated competitor accelerate replication using this material?
```

If yes, reduce disclosure depth.

---

## Category 4 — Narrative Value

Ask:

```text
Does this materially improve:
- understanding
- credibility
- positioning
- trust
- category framing
```

without exposing moat mechanics?

---

## Category 5 — Sanitization Verification

Confirm that:

- sensitive semantics were abstracted
- restricted internals were removed
- runtime philosophy remains accurate
- conceptual meaning remains intact

---

# NotebookLM Review Rule

Before adding material to NotebookLM corpora:

- classify exposure level
- verify sanitization status
- confirm corpus scope
- review retrieval leakage risk

---

# Canonical Principle

```text
Strong positioning should not require unrestricted disclosure.
```
