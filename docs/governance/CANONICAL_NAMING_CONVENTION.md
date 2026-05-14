# DETERMA Canonical Naming Convention

## Purpose

This document defines the canonical naming conventions used across DETERMA repositories.

The objective is to:

- reduce ambiguity
- improve discoverability
- preserve semantic clarity
- support long-term maintainability
- simplify governance workflows

---

# Canonical Principle

```text
Names should communicate governance meaning, not just file identity.
```

---

# Naming Categories

## Canonical Documents

Pattern:

```text
<CANONICAL_CONCEPT>.md
```

Examples:

- `RUNTIME_SUCCESS_CRITERIA.md`
- `THREAT_SCENARIOS.md`
- `PUBLIC_PRIVATE_DISCLOSURE_DOCTRINE.md`

---

## Sanitized Derivatives

Pattern:

```text
SANITIZED_<CONCEPT>.md
```

Examples:

- `SANITIZED_RUNTIME_SUCCESS_CRITERIA.md`
- `SANITIZED_THREAT_SCENARIOS.md`
- `SANITIZED_GOVERNED_EXECUTION_OVERVIEW.md`

---

## Governance Policies

Pattern:

```text
<POLICY_NAME>_POLICY.md
```

Examples:

- `SOURCE_OF_TRUTH_POLICY.md`
- `SANITIZATION_POLICY.md`
- `REPOSITORY_ACCESS_POLICY.md`

---

## Governance Models

Pattern:

```text
<MODEL_NAME>_MODEL.md
```

Examples:

- `REPOSITORY_SEGMENTATION_MODEL.md`
- `CANONICAL_REFERENCE_MODEL.md`

---

## Governance Workflows

Pattern:

```text
<WORKFLOW_NAME>_WORKFLOW.md
```

Examples:

- `NOTEBOOKLM_CURATION_WORKFLOW.md`

---

## Governance Checklists

Pattern:

```text
<CHECKLIST_NAME>_CHECKLIST.md
```

Examples:

- `DISCLOSURE_REVIEW_CHECKLIST.md`

---

# Archive Naming

Restricted archival directories should reflect:

- semantic category
- governance boundary
- disclosure meaning

Examples:

```text
/internal_archive/patents/
/internal_archive/cryptography/
/internal_archive/governance/
```

---

# Canonical Principle

```text
Consistent naming reduces semantic drift.
```
