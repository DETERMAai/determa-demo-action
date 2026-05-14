# DETERMA Document Classification Matrix

## Purpose

This document classifies the major DETERMA documents according to the canonical disclosure doctrine.

The goal is to:

- separate public-safe material from restricted internals
- guide future migration work
- prevent accidental exposure
- support NotebookLM corpus construction
- define canonical disclosure boundaries

---

# Classification Levels

| Classification | Meaning |
|---|---|
| PUBLIC_SAFE | May appear in public showcase or sanitized onboarding flows |
| DILIGENCE | Suitable for curated investor and partner review |
| INTERNAL_CORE | Internal operational and architectural material |
| RESTRICTED | Highly sensitive implementation or strategic material |

---

# Public-Safe Candidates

| Document | Classification | Notes |
|---|---|---|
| `docs/FAQ.md` | PUBLIC_SAFE | Public onboarding and explanation layer |
| `docs/DEMO_OVERVIEW.md` | PUBLIC_SAFE | Safe conceptual demo explanation |
| `docs/PUBLIC_ARCHITECTURE.md` | PUBLIC_SAFE | High-level architecture only |
| `docs/PRESENTATION.md` | PUBLIC_SAFE | Public presentation layer |
| `docs/GETTING_STARTED.md` | PUBLIC_SAFE | Public onboarding material |
| `docs/SPLIT_DEMONSTRATION.md` | PUBLIC_SAFE | Fail-open vs fail-closed framing |

---

# Curated Diligence Candidates

| Document | Classification | Notes |
|---|---|---|
| `docs/core/THREAT_SCENARIOS.md` | DILIGENCE | Strong strategic framing, sanitize if needed |
| `docs/core/RUNTIME_SUCCESS_CRITERIA.md` | DILIGENCE | Valuable for enterprise credibility |
| `docs/core/CANONICAL_LANGUAGE.md` | DILIGENCE | Safe if reviewed before sharing |
| `DETERMA MVP Architecture.docx` | DILIGENCE | Sanitized version recommended |
| `docs/SECURITY_MODEL.md` | DILIGENCE | Public-safe security framing |
| `docs/core/EXECUTION_CONVERGENCE.md` | DILIGENCE | Useful for advanced technical review |

---

# Internal Core Documents

| Document | Classification | Notes |
|---|---|---|
| `WORKER_CONTRACT.md` | INTERNAL_CORE | Internal execution semantics |
| `ORCHESTRATOR_FLOW.md` | INTERNAL_CORE | Runtime lifecycle semantics |
| `ERROR_HANDLING_POLICY.md` | INTERNAL_CORE | Internal runtime enforcement logic |
| `SECRETS_HANDLING.md` | INTERNAL_CORE | Internal operational policy |
| `DB_MIGRATIONS_PLAN.md` | INTERNAL_CORE | Internal system structure |
| `DB_IMMUTABILITY_ENFORCEMENT.md` | INTERNAL_CORE | Deep state and audit mechanics |
| `02_STATE_OF_RECORD.docx` | INTERNAL_CORE | Canonical operational state material |
| `03_MIGRATION_ORDER.docx` | INTERNAL_CORE | Internal sequencing material |
| `04_VERIFICATION_REQUIREMENTS.docx` | INTERNAL_CORE | Internal verification semantics |
| `05_DB_PACKAGE_README.docx` | INTERNAL_CORE | Internal database implementation knowledge |

---

# Restricted Documents

| Document | Classification | Notes |
|---|---|---|
| `PROVISIONAL PATENT APPLICATION DRAFT.docx` | RESTRICTED | Patent-sensitive invention material |
| `הפיזיקה של המערכת – המפרט המתמטי והקריפטוגרפי של DATP_.docx` | RESTRICTED | Deep mathematical and cryptographic internals |
| `DETERMA V6.2.docx` | RESTRICTED | Advanced replay and authority semantics |
| `DETERMA V6.3.docx` | RESTRICTED | Governance mutation semantics |
| `DETERMA V6.4.docx` | RESTRICTED | Long-term authority ledger mechanics |
| `DETERMA V6 Architecture.docx` | RESTRICTED | Deep architecture and moat structure |
| `DETERMA_Canonical_System_Contract_v1_EN.pdf` | RESTRICTED | Canonical authority doctrine |
| `01_DETERMA_Governed_Core_v1.docx` | RESTRICTED | Deep governed core semantics |

---

# Migration Guidance

## Public Repository

Only PUBLIC_SAFE material should migrate directly.

---

## Curated NotebookLM Corpus

Should primarily contain:

- PUBLIC_SAFE
- selected DILIGENCE

materials.

---

## Internal Repository

Must retain:

- INTERNAL_CORE
- RESTRICTED

materials.

---

# Canonical Rule

When uncertain:

```text
Do not expose mechanism details through convenience.
```
