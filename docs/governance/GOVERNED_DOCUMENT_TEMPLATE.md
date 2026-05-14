# Governed Document Template

## Purpose

This template standardizes how governed documents should appear across the DETERMA repositories.

The objective is to:

- preserve metadata consistency
- support canonical governance
- reduce ambiguity
- maintain lineage visibility
- standardize exposure handling

---

# Canonical Header Template

```text
STATUS: <CANONICAL | SANITIZED_DERIVATIVE | SUPERSEDED | DEPRECATED | ARCHIVED>
EXPOSURE: <PUBLIC_SAFE | DILIGENCE | INTERNAL_CORE | RESTRICTED>
CANONICAL_SOURCE: <path if derivative>
SUPERSEDED_BY: <path if superseded>
```

---

# Recommended Structure

## 1. Purpose

Define:

- why the document exists
- intended audience
- governance scope

---

## 2. Canonical Principle

Provide the governing principle for the document.

---

## 3. Main Content

Explain:

- architecture
- doctrine
- runtime behavior
- onboarding
- governance semantics

according to the disclosure level.

---

## 4. Restricted Areas

If applicable, explicitly define:

- omitted mechanics
- abstracted semantics
- protected implementation areas

---

## 5. Governance Notes

Reference:

- canonical sources
- lineage relationships
- sanitization boundaries
- disclosure constraints

---

# Canonical Principle

```text
Governed systems require governed documentation.
```
