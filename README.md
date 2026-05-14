# DETERMA Runtime

> Deterministic Governed Execution for Autonomous AI Systems.

AI systems can generate actions. DETERMA governs whether those actions are allowed to mutate real systems.

DETERMA verifies whether AI-driven execution is authorized, replayable, recoverable, append-only traceable, and deterministically reproducible.

---

## What DETERMA Demonstrates

DETERMA demonstrates a governed execution runtime where:

- AI-generated mutations are intercepted before execution
- execution authority is explicitly issued
- execution capabilities are single-use
- replay attacks fail closed
- runtime lineage remains append-only
- deterministic replay verifies execution legitimacy

This repository demonstrates governed execution for AI-driven mutations under deterministic replay validation and fail-closed authority control.

---

## Run the Governed Execution Demonstration

### One-command demo

```bash
python scripts/demo_governed_flow.py
```

### Interactive runtime dashboard

```bash
uvicorn runtime.api_shell:app --host 0.0.0.0 --port 8000
```

Then open:

```text
http://localhost:8000/demo
```

### Docker runtime

```bash
docker compose -f docker-compose.runtime.yml up
```

Then open:

```text
http://localhost:8000/demo
```

---

## What the Demonstration Shows

The governed execution ceremony demonstrates:

1. AI proposes a mutation
2. Execution is intercepted
3. Authority approval is required
4. Single-use capability is issued
5. Governed mutation executes
6. Replay validation succeeds
7. Replay attack is blocked

---

## Explore the DETERMA Runtime Architecture

All canonical replay, lineage, governance, runtime, and threat-model documents are searchable through the interactive DETERMA architecture notebook.

### Interactive Architecture Notebook

[Open the DETERMA Architecture Notebook](https://notebooklm.google.com/notebook/1c7fd705-9634-48e7-9249-4b06a0a6a2ef?authuser=8)

### Suggested Questions

- How does deterministic replay work?
- Why are capabilities single-use?
- How does DETERMA prevent replay attacks?
- What happens if runtime state changes?
- How does append-only lineage work?
- Why govern execution instead of prompts?
- How does DETERMA differ from approval workflows?

---

## Governed Execution Flow

```text
AI
 ↓
Proposal
 ↓
Authority Boundary
 ↓
Capability Issuance
 ↓
Governed Execution
 ↓
Replay Verification
 ↓
Replay Attack Blocked
```

---

## Documentation Map

### Core Runtime

| Document | Purpose |
|---|---|
| `README.md` | Product overview and governed execution entrypoint |
| `runtime/` | Canonical runtime implementation |
| `runtime/github_governor.py` | Governed GitHub mutation flow |
| `runtime/api_shell.py` | Thin observability/API layer |

### Replay and Integrity

| Document | Purpose |
|---|---|
| `docs/core/AUTHORITY_LEDGER.md` | Append-only lineage model |
| `docs/core/EXECUTION_CONVERGENCE.md` | Deterministic replay guarantees |
| `docs/core/CANONICAL_STOP_CONDITION.md` | Fail-closed execution semantics |
| `docs/core/ANTI_FAKE_IMPLEMENTATION.md` | Runtime legitimacy constraints |

### Threat and Governance

| Document | Purpose |
|---|---|
| `docs/core/THREAT_SCENARIOS.md` | Attack and compromise scenarios |
| `docs/core/CANONICAL_LANGUAGE.md` | Canonical governance terminology |
| `docs/core/RUNTIME_SUCCESS_CRITERIA.md` | Runtime legitimacy conditions |

### Runtime Proofs and Receipts

| Document | Purpose |
|---|---|
| `receipts/` | Replay-verifiable runtime artifacts |
| `receipts/runtime_proof_snapshot.json` | Canonical replay proof snapshot |
| `receipts/release_lineage.jsonl` | Append-only release lineage |

### Operational Demo

| Document | Purpose |
|---|---|
| `scripts/demo_governed_flow.py` | One-command governed execution ceremony |
| `ui/runtime_dashboard.html` | Runtime observability and demo experience |
| `docker-compose.runtime.yml` | Reproducible runtime demo environment |

---

## Why Governed Execution Matters

AI systems increasingly generate actions capable of mutating:

- repositories
- infrastructure
- CI/CD pipelines
- operational systems
- cloud environments
- production workflows

Traditional AI safety approaches focus on prompts, model behavior, and output filtering.

DETERMA focuses on the execution boundary itself.

Even compromised or manipulated AI systems cannot mutate governed systems without explicitly issued execution authority.

---

## Comparison

| Without Governance | With DETERMA |
|---|---|
| execution occurs immediately | execution is intercepted |
| replay attempts can succeed | replay attacks fail closed |
| authority is implicit | authority is explicit |
| fail-open behavior | fail-closed behavior |
| mutation trust is assumed | mutation trust is verified |

---

## What DETERMA Is Not

DETERMA is not:

- an AI model
- a prompt firewall
- a jailbreak detector
- a generalized orchestration platform
- an approval workflow tool
- an alignment system

DETERMA governs whether AI-generated actions are allowed to mutate external systems.

---

## Status

```text
Runtime validation: 60 passed, 1 skipped
Replay subset: 18 passed
Corruption subset: 1 passed
Multi-process subset: 2 passed
```

The skipped test is the credential-gated remote GitHub API governance validation.

---

## Runtime Guarantees Verified

| Guarantee | Status |
|---|---|
| Deterministic replay | Verified |
| Append-only lineage | Verified |
| Replay prevention | Verified |
| Fail-closed authority checks | Verified |
| Crash recovery | Verified |
| Cross-process coordination | Verified |
| Corruption detection | Verified |
| Restoration equivalence | Verified |
| Container parity | Verified |

---

## Runtime API Shell

The FastAPI shell is intentionally thin. It delegates to the existing runtime functions and does not reimplement governance semantics.

Available endpoints:

```text
GET  /health
GET  /demo
GET  /demo/status
GET  /demo/autoplay
POST /demo/run
POST /demo/replay-attack
GET  /runtime/replay
GET  /runtime/lifecycle/replay
POST /runtime/orchestrator/run-once
POST /runtime/recovery/recover
```

---

## Runtime Principles

```text
AI proposes.
Authority decides.
Execution is verified.
Replay is reproducible.
Lineage is append-only.
```

The runtime preserves:

- deterministic replay
- append-only lineage
- fail-closed execution
- replay digest consistency
- restoration equivalence
- single-use capability semantics
- authority-bound execution

---

## Public Scope

This repository demonstrates a governed execution runtime kernel.

It does not yet claim:

- production-scale infrastructure guarantees
- universal agent orchestration
- full distributed authority federation
- complete multi-system governance coverage

The current focus is a strict, executable governed runtime baseline.

---

## Product Direction

DETERMA is evolving toward deterministic governed execution infrastructure focused on:

- governed AI mutations
- replay-verifiable execution
- append-only lineage
- authority-bound execution
- recoverable runtime workflows
- fail-closed mutation governance

---

## Explore the Runtime

Run the governed execution ceremony:

```bash
python scripts/demo_governed_flow.py
```

Open the runtime dashboard:

```text
http://localhost:8000/demo
```

Explore the architecture notebook:

[Open the DETERMA Architecture Notebook](https://notebooklm.google.com/notebook/1c7fd705-9634-48e7-9249-4b06a0a6a2ef?authuser=8)
