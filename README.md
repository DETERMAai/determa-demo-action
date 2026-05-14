# DETERMA

**Governed execution control for AI-driven mutation authority.**

DETERMA is a runtime that governs whether AI-generated actions are allowed to mutate external systems.  
It separates *intent generation* from *execution authority* and enforces deterministic, fail-closed mutation control.

## NotebookLM Architecture Exploration

Use the interactive architecture notebook to explore canonical replay, lineage, governance, and execution documents:

**Open Notebook:**  
https://notebooklm.google.com/notebook/1c7fd705-9634-48e7-9249-4b06a0a6a2ef?authuser=8

### Suggested Questions

- How does deterministic replay work?
- Why are capabilities single-use?
- How does DETERMA prevent replay attacks?
- What happens if runtime state changes?
- How does append-only lineage work?
- Why govern execution instead of prompts?
- How does DETERMA differ from approval workflows?

## What Governed Execution Means

AI systems can generate actions.  
DETERMA governs whether those actions are permitted to mutate external systems *at execution time*.

Core idea:

- Approval is necessary but not sufficient.
- Authority must be valid at the moment of mutation.
- Replay and stale authority must fail closed.

## One-Command Demo

Run a complete governed execution ceremony:

```bash
python scripts/demo_governed_flow.py
```

This demo walks through proposal creation, approval, capability issuance, governed execution, replay validation, and replay attack rejection.

## Runtime Dashboard

Start the runtime shell:

```bash
uvicorn runtime.api_shell:app --host 0.0.0.0 --port 8000
```

Open the governed execution experience:

- `http://127.0.0.1:8000/demo`

Dashboard supports:

- landing + threat framing
- comparison mode: without governance vs with DETERMA
- replay attack fail-closed visualization
- post-demo architecture exploration gateway

## Threat Framing

DETERMA is built for the execution boundary where risk materializes:

- prompt-injected intent
- compromised agent behavior
- capability reuse / replay attempts
- stale execution context

It does **not** claim to detect all unsafe cognition.  
It enforces deterministic mutation authority controls before external change.

## Without Governance vs With DETERMA

| Dimension | Without Governance | With DETERMA |
|---|---|---|
| Mutation timing | Executes immediately | Intercepted behind authority checks |
| Approval semantics | Often equivalent to execution | Approval separated from authority |
| Capability reuse | Commonly reusable | Single-use and consumed |
| Replay attempts | Can succeed | Blocked fail-closed |
| Lineage guarantees | Weak / inconsistent | Append-only receipts and replay validation |
| Failure mode | Fail-open | Fail-closed |

## Runtime Principles

- Deterministic replay validation
- Append-only lineage and receipt integrity
- Single-use execution capability consumption
- Authority re-check at mutation boundary
- Fail-closed behavior on ambiguity or invalid state
- Crash-safe lifecycle recovery and reproducibility

## Documentation Map

### Core

- [Canonical Language](docs/core/CANONICAL_LANGUAGE.md)
- [MVP](docs/core/MVP.md)
- [Architecture](docs/core/ARCHITECTURE.md)
- [Governance](docs/core/GOVERNANCE.md)
- [Invariants](docs/core/INVARIANTS.md)
- [Security](docs/core/SECURITY.md)
- [Threat Scenarios](docs/core/THREAT_SCENARIOS.md)
- [Authority Ledger](docs/core/AUTHORITY_LEDGER.md)
- [Execution Convergence](docs/core/EXECUTION_CONVERGENCE.md)
- [Runtime Success Criteria](docs/core/RUNTIME_SUCCESS_CRITERIA.md)
- [Anti-Fake Implementation](docs/core/ANTI_FAKE_IMPLEMENTATION.md)
- [Canonical Stop Condition](docs/core/CANONICAL_STOP_CONDITION.md)

### Demo

- [Demo Semantics](docs/demo/DEMO.md)

## Product Direction

DETERMA is evolving as a governed execution platform narrative:

- from runtime enforcement to explainable governance demonstrations
- from standalone proofs to interactive architecture exploration
- from approval-centric workflows to deterministic execution legitimacy

The product direction remains strict: **control mutation authority, not thought content**.

## Final Runtime Exploration CTA

1. Run the ceremony: `python scripts/demo_governed_flow.py`
2. Launch dashboard: `uvicorn runtime.api_shell:app --host 0.0.0.0 --port 8000`
3. Open `/demo` and walk the fail-open vs fail-closed comparison
4. Explore canonical architecture in NotebookLM:
   https://notebooklm.google.com/notebook/1c7fd705-9634-48e7-9249-4b06a0a6a2ef?authuser=8
