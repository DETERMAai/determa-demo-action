<div align="center">

# DETERMA Internal Core Repository

### Private Authority Core, Runtime Proofs, and Architecture Knowledge Base

This repository is the private source of truth for DETERMA.

It contains the internal governed execution architecture, runtime proof artifacts, authority model, implementation materials, and strategic technical documentation.

</div>

---

# Repository Role

This repository is the internal DETERMA core repository.

It is not the public showcase repository.

The public repository should be used for external visibility, demos, and high-level partner discovery.

This private repository should be used for:

- internal architecture source of truth
- governed execution runtime development
- authority model documentation
- proof artifacts and receipts
- private technical diligence
- strategic technical review
- future implementation planning

---

# Core Principle

```text
AI proposes.
Authority governs.
Execution is constrained.
State is verified.
Replay attempts fail closed.
Lineage is append-only.
```

DETERMA separates generated intent from execution authority.

A machine-generated proposal does not automatically receive mutation authority.

---

# Knowledge Map

This section maps the major knowledge areas in the repository and explains what each area is for.

---

## 1. Runtime Implementation

| Location | Purpose |
|---|---|
| `runtime/` | Canonical runtime implementation and governed execution logic. |
| `runtime/github_governor.py` | Governed GitHub mutation flow and authority-controlled repository interaction. |
| `runtime/api_shell.py` | Thin API and dashboard shell for runtime observability and demo interaction. |
| `scripts/demo_governed_flow.py` | One-command governed execution demonstration. |
| `docker-compose.runtime.yml` | Docker runtime path for reproducible demo or local runtime execution. |

Use this area when validating the working proof, runtime flow, or external demo behavior.

---

## 2. Runtime Proofs and Receipts

| Location | Purpose |
|---|---|
| `receipts/` | Runtime evidence, proof artifacts, and replay-verifiable outputs. |
| `receipts/runtime_proof_snapshot.json` | Canonical snapshot for runtime proof validation. |
| `receipts/release_lineage.jsonl` | Append-only release lineage and execution trace material. |
| `receipts/proposal_receipt.json` | Proposal-level receipt tying generated work to reviewable evidence. |

Use this area to prove that execution behavior is recorded, replayable, and auditable.

---

## 3. Core Runtime Documentation

| Location | Purpose |
|---|---|
| `docs/core/EXECUTION_CONVERGENCE.md` | Defines deterministic convergence and when runtime execution is considered legitimate. |
| `docs/core/RUNTIME_SUCCESS_CRITERIA.md` | Defines runtime legitimacy and success criteria. |
| `docs/core/ANTI_FAKE_IMPLEMENTATION.md` | Prevents cosmetic or fake implementation claims by requiring real runtime evidence. |
| `docs/core/CANONICAL_STOP_CONDITION.md` | Defines when execution must stop rather than continue under uncertainty. |
| `docs/core/CANONICAL_LANGUAGE.md` | Establishes shared terminology for DETERMA architecture and governance. |
| `docs/core/THREAT_SCENARIOS.md` | Captures adversarial and failure scenarios relevant to governed execution. |
| `docs/core/AUTHORITY_LEDGER.md` | Describes the authority ledger and action lineage model. |

Use this area when reasoning about correctness, legitimacy, threat coverage, and architectural vocabulary.

---

## 4. Worker and Orchestrator Contracts

| Location | Purpose |
|---|---|
| `WORKER_CONTRACT.md` | Binding contract for execution-plane workers, including lifecycle, audit, and approval constraints. |
| `WORKER_V1_SPEC.md` | Specification for deterministic planning/spec worker behavior. |
| `WORKER_V2_SPEC.md` | Specification for artifact-producing worker behavior. |
| `ORCHESTRATOR_FLOW.md` | Defines orchestrator responsibilities, lifecycle control, and approval-gate enforcement. |
| `WORKER_RESOURCE_LIMITS.md` | Runtime sandbox and resource limits for worker execution. |
| `SECRETS_HANDLING.md` | Rules for secret ingestion, storage, logging, redaction, and failure behavior. |
| `ERROR_HANDLING_POLICY.md` | Defines fail-safe, auditable, deterministic error handling. |

Use this area when implementing or reviewing worker behavior, lifecycle transitions, approval gates, sandboxing, or secret safety.

---

## 5. Database and State Plane

| Location | Purpose |
|---|---|
| `DB_MIGRATIONS_PLAN.md` | Database schema intent for tenants, jobs, audit events, logs, and metrics. |
| `DB_IMMUTABILITY_ENFORCEMENT.md` | Defines append-only audit requirements and database-level immutability constraints. |
| `02_STATE_OF_RECORD.docx` | Canonical state-of-record material for authoritative system state and data ownership. |
| `03_MIGRATION_ORDER.docx` | Migration ordering and implementation sequencing. |
| `04_VERIFICATION_REQUIREMENTS.docx` | Verification requirements for runtime, state, and system correctness. |
| `05_DB_PACKAGE_README.docx` | Database package overview and supporting explanation. |

Use this area when implementing or auditing persistence, lifecycle state, tenant isolation, audit records, and state verification.

---

## 6. Canonical System and Governed Core

| Location | Purpose |
|---|---|
| `DETERMA_Canonical_System_Contract_v1_EN.pdf` | Canonical system contract defining the high-level governed execution doctrine. |
| `01_DETERMA_Governed_Core_v1.docx` | Governed core specification and system authority model. |
| `APPROVED ARTIFACTS — STEPS 1–8.txt` | Approved artifact history and build-plan continuity. |
| `DETERMA MVP Architecture.docx` | MVP architecture and first working wedge for governed code mutation. |
| `DETERMA V6 Architecture.docx` | Full architecture framing and system component map. |

Use this area when aligning implementation to the canonical doctrine and ensuring development does not drift from the approved architecture.

---

## 7. Architecture Versions and Governance Models

| Location | Purpose |
|---|---|
| `DETERMA V6.2.docx` | Execution integrity extension including state witness and dual-key execution release concepts. |
| `DETERMA V6.3.docx` | Constitutional governance model for controlling changes to the authority structure itself. |
| `DETERMA V6.4.docx` | Global Action Ledger model for long-term machine action accounting and lineage. |

Use this area when reviewing advanced authority guarantees, replay prevention, governance evolution, and long-term action accounting.

---

## 8. Mathematical, Cryptographic, and Patent Materials

| Location | Purpose |
|---|---|
| `הפיזיקה של המערכת – המפרט המתמטי והקריפטוגרפי של DATP_.docx` | Mathematical and cryptographic specification for the DATP model. |
| `PROVISIONAL PATENT APPLICATION DRAFT.docx` | Patent-sensitive draft material and invention framing. |

Use this area only for internal technical strategy, IP review, patent preparation, or deep architecture validation.

Do not expose these materials in the public showcase repository.

---

## 9. Factory, Deployment, and Operations

| Location | Purpose |
|---|---|
| `אפיון אסטרטגי ותפעולי להקמת מערכת DATP באמצעות _המפעל_ (The Factory).docx` | Strategy and operating model for building DETERMA through the Factory workflow. |
| `### DETERMA — מצב פריסה ותפעול.txt` | Deployment and operational assistant instructions for safe, deterministic setup. |

Use this area when planning autonomous development workflows, deployment flows, or operational execution strategy.

---

# Public vs Private Repository Split

## Public Repository

The public repository should contain:

- public README
- public demo explanation
- safe architecture overview
- public presentation layer
- design partner invitation
- public-safe documentation only

## Private Repository

This repository contains:

- authority core
- deep governance model
- runtime proof materials
- implementation contracts
- database and state-plane rules
- mathematical and cryptographic specifications
- patent-sensitive material
- internal roadmap and architecture knowledge

---

# Recommended Internal Reading Paths

## For Runtime Review

1. `README.md`
2. `scripts/demo_governed_flow.py`
3. `runtime/`
4. `receipts/`
5. `docs/core/RUNTIME_SUCCESS_CRITERIA.md`

## For Architecture Review

1. `DETERMA_Canonical_System_Contract_v1_EN.pdf`
2. `01_DETERMA_Governed_Core_v1.docx`
3. `DETERMA MVP Architecture.docx`
4. `DETERMA V6 Architecture.docx`
5. `docs/core/CANONICAL_LANGUAGE.md`

## For Security and Governance Review

1. `WORKER_CONTRACT.md`
2. `ORCHESTRATOR_FLOW.md`
3. `SECRETS_HANDLING.md`
4. `ERROR_HANDLING_POLICY.md`
5. `DETERMA V6.2.docx`
6. `DETERMA V6.3.docx`
7. `DETERMA V6.4.docx`

## For Database and State Review

1. `DB_MIGRATIONS_PLAN.md`
2. `DB_IMMUTABILITY_ENFORCEMENT.md`
3. `02_STATE_OF_RECORD.docx`
4. `04_VERIFICATION_REQUIREMENTS.docx`

## For IP and Deep Technical Review

1. `PROVISIONAL PATENT APPLICATION DRAFT.docx`
2. `הפיזיקה של המערכת – המפרט המתמטי והקריפטוגרפי של DATP_.docx`
3. `DETERMA_Canonical_System_Contract_v1_EN.pdf`
4. `DETERMA V6.2.docx`
5. `DETERMA V6.3.docx`
6. `DETERMA V6.4.docx`

---

# Operating Rule

This repository should preserve the full internal memory of DETERMA.

Do not delete or simplify internal knowledge here for public positioning purposes.

Public simplification belongs in the public showcase repository only.

---

# Current Public Repository

Public showcase repository:

```text
https://github.com/DETERMAai/determa-governed-execution-demo
```

Use the public repository for external sharing unless private technical review has been intentionally approved.
