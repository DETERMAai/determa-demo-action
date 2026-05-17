# Runtime Legitimacy Visualization Layer

This layer makes DATP visually intuitive without exposing protocol internals.

## Purpose

- visualize Runtime Legitimacy collapse paths
- make Mutation Admissibility decisions operationally readable
- reinforce Runtime Authority as infrastructure control

## Canonical State Models

Legitimacy progression:

```text
VALID
→ WEAKENING
→ STALE
→ INVALID
→ TRANSITIVELY_INVALIDATED
```

Execution lifecycle:

```text
PROPOSED
→ APPROVED
→ QUEUED
→ EXECUTING
→ REVALIDATING
→ HALTED
OR
→ FINALIZED
```

Environment flow:

```text
STAGING
→ PROMOTION
→ PRODUCTION
```

Dependency propagation:

```text
A
↓
B
↓
C
```

## Visual Maps

- [DATP Runtime Authority Flow](visualization/DATP_RUNTIME_AUTHORITY_FLOW.md)
- [Mutation Admissibility States](visualization/MUTATION_ADMISSIBILITY_STATES.md)
- [Authority Continuity Failure Map](visualization/AUTHORITY_CONTINUITY_FAILURE_MAP.md)
- [Contradiction To Outcome Map](visualization/CONTRADICTION_TO_OUTCOME_MAP.md)
- [Runtime Legitimacy Proof Map](RUNTIME_LEGITIMACY_PROOF_MAP.md)

## Public Honesty Boundary

These visuals describe deterministic sandboxed runtime legitimacy proofs.
They do not expose production control plane internals or sensitive protocol semantics.
