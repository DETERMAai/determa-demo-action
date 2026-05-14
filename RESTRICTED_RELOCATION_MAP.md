# DETERMA Restricted Relocation Map

## Purpose

This document tracks the migration of sensitive materials into the canonical restricted archive structure.

The objective is to:

- preserve continuity
- avoid accidental exposure
- support governed repository restructuring
- maintain canonical references during migration

---

# Migration Rules

## Rule 1

Copy before removing originals.

---

## Rule 2

Create sanitized derivatives before external exposure.

---

## Rule 3

Preserve canonical references during relocation.

---

# Restricted Relocation Table

| Original Document | Classification | Target Archive Location | Sanitized Replacement |
|---|---|---|---|
| `PROVISIONAL PATENT APPLICATION DRAFT.docx` | RESTRICTED | `/internal_archive/patents/` | None |
| `הפיזיקה של המערכת – המפרט המתמטי והקריפטוגרפי של DATP_.docx` | RESTRICTED | `/internal_archive/cryptography/` | None |
| `DETERMA V6.2.docx` | RESTRICTED | `/internal_archive/governance/` | Future sanitized governance overview |
| `DETERMA V6.3.docx` | RESTRICTED | `/internal_archive/governance/` | Future sanitized governance overview |
| `DETERMA V6.4.docx` | RESTRICTED | `/internal_archive/governance/` | Future sanitized governance overview |
| `DETERMA V6 Architecture.docx` | RESTRICTED | `/internal_archive/architecture/` | `SANITIZED_MVP_ARCHITECTURE_OVERVIEW.md` |
| `DETERMA_Canonical_System_Contract_v1_EN.pdf` | RESTRICTED | `/internal_archive/contracts/` | Future public-safe canonical overview |
| `01_DETERMA_Governed_Core_v1.docx` | RESTRICTED | `/internal_archive/governed_core/` | Future sanitized governed execution overview |

---

# Archive Directory Model

```text
/internal_archive/
    /patents/
    /cryptography/
    /governance/
    /architecture/
    /contracts/
    /governed_core/
```

---

# Canonical Principle

```text
Sensitive knowledge should remain structured, discoverable, and governed.
```
