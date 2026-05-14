# Diligence NotebookLM Manifest

STATUS: CANONICAL
EXPOSURE: DILIGENCE

## Purpose

This manifest defines the approved diligence NotebookLM ingestion set for DETERMA.

The objective is to:

- support guided investor understanding
- preserve disclosure boundaries
- standardize diligence corpora
- reduce retrieval leakage

---

# Approved Diligence Sources

## Public-Safe Layer

- `/diligence/public_safe/PUBLIC_POSITIONING_CANON.md`
- `/diligence/public_safe/SANITIZED_GOVERNED_EXECUTION_OVERVIEW.md`
- `/diligence/public_safe/SANITIZED_RUNTIME_SUCCESS_CRITERIA.md`
- `/diligence/public_safe/SANITIZED_THREAT_SCENARIOS.md`

---

## Curated Diligence Layer

- `/diligence/curated/SANITIZED_MVP_ARCHITECTURE_OVERVIEW.md`
- `/diligence/curated/CURATED_DILIGENCE_INDEX.md`
- `/diligence/curated/DESIGN_PARTNER_OVERVIEW.md`
- `/diligence/curated/INVESTOR_ONBOARDING_FLOW.md`

---

## Governance Orientation

- `/docs/governance/NOTEBOOKLM_DISCLOSURE_POLICY.md`
- `/docs/governance/SANITIZATION_POLICY.md`
- `/docs/governance/REPOSITORY_SEGMENTATION_MODEL.md`

---

# Explicitly Forbidden Sources

Do not ingest:

- unrestricted `/internal_archive/`
- patent-sensitive material
- replay invalidation internals
- authority issuance semantics
- governance mutation semantics
- cryptographic enforcement details

---

# Refresh Rules

## Rule 1

Deprecated or superseded documents should be removed from diligence corpora.

---

## Rule 2

Curated diligence corpora should prioritize conceptual understanding over implementation depth.

---

# Canonical Principle

```text
Diligence corpora should maximize strategic understanding while minimizing moat exposure.
```
