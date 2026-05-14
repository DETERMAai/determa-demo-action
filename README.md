# DETERMA

**Governed execution runtime for AI mutation authority.**

DETERMA is an execution-governance system that decides whether AI-generated actions are permitted to mutate external systems at runtime.  
It separates **intent generation** from **mutation authority** and enforces deterministic, fail-closed execution control.

## Architecture Notebook (NotebookLM)

All canonical replay, lineage, governance, and execution architecture documents are searchable in the interactive DETERMA notebook:

**Notebook Link:**  
https://notebooklm.google.com/notebook/1c7fd705-9634-48e7-9249-4b06a0a6a2ef?authuser=8

### Suggested Questions

- How does deterministic replay work?
- Why are capabilities single-use?
- How does DETERMA prevent replay attacks?
- What happens if runtime state changes?
- How does append-only lineage work?
- Why govern execution instead of prompts?
- How does DETERMA differ from approval workflows?

---

## Governed Execution, Precisely

AI systems can generate actions.  
DETERMA governs whether those actions are authorized to mutate external systems **at execution time**.

Execution invariants:

- approval is required but not sufficient
- authority must be valid at mutation boundary
- replay or stale authority must fail closed

---

## Why Existing AI Governance Is Not Enough

Most governance layers stop at policy, prompts, approvals, or workflow checkpoints.

These controls do not fully resolve execution-risk conditions:

- runtime state drift after approval
- capability reuse across attempts
- replay of previously valid authority
- ambiguity at the exact mutation boundary

DETERMA addresses this gap with deterministic execution legitimacy verification.

---

## One-Command Demo

Run the full governed execution ceremony:

```bash
python scripts/demo_governed_flow.py
```

Ceremony includes proposal, approval, capability issuance, governed mutation, replay validation, and replay attack rejection.

---

## Runtime Dashboard

Start runtime shell:

```bash
uvicorn runtime.api_shell:app --host 0.0.0.0 --port 8000
```

Open demo experience:

- `http://127.0.0.1:8000/demo`

Dashboard includes:

- landing + threat framing
- scenario narrative mode
- comparison mode (without governance vs with DETERMA)
- replay attack fail-closed visualization
- post-demo architecture exploration

---

## Threat Framing

DETERMA is built for execution-boundary risk:

- prompt-injected mutation intent
- compromised agent behavior
- capability reuse / replay attempts
- stale execution context

DETERMA does **not** claim universal unsafe-intent detection.  
It enforces deterministic authority constraints before external mutation.

---

## Without Governance vs With DETERMA

| Dimension | Without Governance | With DETERMA |
|---|---|---|
| Mutation timing | Executes immediately | Intercepted behind authority checks |
| Approval semantics | Often equivalent to execution | Approval separated from execution legitimacy |
| Capability reuse | Reusable in practice | Single-use and consumed |
| Replay attempts | May succeed | Blocked fail-closed |
| Runtime verification | Partial / workflow-bound | Deterministic replay + lifecycle verification |
| Failure mode | Fail-open | Fail-closed |

---

## Architectural Comparison

| Architecture Pattern | Control Plane Focus | Mutation Boundary Guarantees |
|---|---|---|
| Prompt / policy governance | Intent-level behavior | Weak direct mutation guarantees |
| Approval workflow governance | Human checkpointing | Vulnerable to stale/replayed authority |
| **DETERMA execution governance** | Runtime authority legitimacy | Deterministic, append-only, fail-closed mutation control |

---

## Runtime Guarantees

- deterministic replay validation
- append-only lineage + receipt integrity
- single-use capability consumption
- authority re-check at execution boundary
- fail-closed behavior on invalid/ambiguous state
- crash-safe lifecycle reconstruction and reproducibility

---

## Runtime Principles

- governance at the mutation boundary, not only at intent time
- deterministic verification over discretionary branching
- explicit authority state transitions over implicit trust
- immutable lineage over mutable runtime narratives

---

## Documentation Map

### Core Runtime

- [Canonical Language](docs/core/CANONICAL_LANGUAGE.md)
- [MVP](docs/core/MVP.md)
- [Architecture](docs/core/ARCHITECTURE.md)
- [Governance](docs/core/GOVERNANCE.md)
- [Invariants](docs/core/INVARIANTS.md)
- [Security](docs/core/SECURITY.md)
- [Threat Scenarios](docs/core/THREAT_SCENARIOS.md)
- [Authority Ledger](docs/core/AUTHORITY_LEDGER.md)

### Determinism and Recovery

- [Execution Convergence](docs/core/EXECUTION_CONVERGENCE.md)
- [Runtime Success Criteria](docs/core/RUNTIME_SUCCESS_CRITERIA.md)
- [Anti-Fake Implementation](docs/core/ANTI_FAKE_IMPLEMENTATION.md)
- [Canonical Stop Condition](docs/core/CANONICAL_STOP_CONDITION.md)

### Demo Semantics

- [Demo Semantics](docs/demo/DEMO.md)

---

## Product Direction

DETERMA is positioned as governed execution infrastructure:

- from approval-centric workflows to execution-legitimacy control
- from static policy overlays to deterministic runtime verification
- from standalone demos to explorable governed-execution platform narrative

Category thesis: **control mutation authority, not thought generation**.

---

## Final Runtime Exploration

1. Run ceremony: `python scripts/demo_governed_flow.py`
2. Launch dashboard: `uvicorn runtime.api_shell:app --host 0.0.0.0 --port 8000`
3. Open `/demo` and inspect fail-open vs fail-closed contrast
4. Explore architecture in NotebookLM:
   https://notebooklm.google.com/notebook/1c7fd705-9634-48e7-9249-4b06a0a6a2ef?authuser=8
