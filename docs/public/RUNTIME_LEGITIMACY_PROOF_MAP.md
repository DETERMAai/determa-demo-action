# Runtime Legitimacy Proof Map

This document is the canonical map of DETERMA public runtime legitimacy proofs.

It explains how the repository progresses from single-mutation legitimacy checks to dependency-graph propagation.

## Purpose

- keep demo/docs/runtime behavior synchronized
- prevent conceptual drift across repository surfaces
- provide one consistent progression for public review

## Proof Progression

### 1. Runtime Legitimacy Simulator

Reference: [RUNTIME_LEGITIMACY_SIMULATOR.html](RUNTIME_LEGITIMACY_SIMULATOR.html)

What it demonstrates:
- deterministic Runtime Witness evolution
- live Mutation Admissibility transitions
- fail-closed execution decisions with Append-Only Lineage output

### 2. Controlled Real Mutation Proof

Reference: [CONTROLLED_REAL_MUTATION_PROOF.md](CONTROLLED_REAL_MUTATION_PROOF.md)

What it demonstrates:
- same mutation proposal
- same approval structure
- different runtime continuity
- different execution outcome

Core result:
- `EXECUTION_ALLOWED` when continuity is preserved
- `EXECUTION_DENIED` when continuity diverges

### 3. Governed Repository Mutation Proof

Reference: [GOVERNED_REPOSITORY_MUTATION_PROOF.md](GOVERNED_REPOSITORY_MUTATION_PROOF.md)

What it demonstrates:
- real sandbox git runtime state governance
- execution boundary legitimacy re-evaluation
- deterministic admissibility outcomes

### 4. Continuous Runtime Revalidation

Governed proof paths:
- Path C (mid-execution collapse)

What it demonstrates:
- legitimacy is not a one-time pre-check
- execution may begin legitimately and still be halted before finalization

### 5. Async Runtime Governance

Governed proof paths:
- Path E (delayed execution decay)
- Path F (retry under diverged runtime)

What it demonstrates:
- Authority Continuity decays over waiting horizons
- retry does not preserve legitimacy under evolved runtime state

### 6. Cross-Environment Governance

Governed proof paths:
- Path G (staging to production divergence)
- Path H (delegated environment transfer)

What it demonstrates:
- approval continuity across environments requires Runtime Witness continuity
- delegation does not preserve legitimacy across diverged execution contexts

### 7. Graph-Structured Legitimacy Propagation

Governed proof path:
- Path I (cascading collapse `A -> B -> C`)

What it demonstrates:
- legitimacy is dependency-graph structured
- upstream invalidation propagates downstream
- dependent mutations become `TRANSITIVELY_INVALIDATED`

## Capability Alignment Matrix

| Capability Class | Public Proof Surface |
|---|---|
| Execution-boundary legitimacy | simulator + controlled proof |
| Continuous revalidation | governed proof Path C |
| Async decay/retry invalidation | governed proof Paths E/F |
| Cross-environment continuity | governed proof Paths G/H |
| Transitive dependency invalidation | governed proof Path I |
| Deterministic evidence and lineage | simulator + controlled proof + governed proof |

## Maturity Framing

Current public scope is:
- deterministic sandboxed runtime legitimacy proofs
- operationally believable governed mutation behavior

Current public scope is not:
- production control plane infrastructure
- distributed consensus substrate
- sensitive protocol internal disclosure

## Public Honesty Boundary

The repository demonstrates deterministic sandboxed runtime legitimacy proofs.
It does not expose production infrastructure control, distributed consensus internals, or sensitive protocol implementation details.
