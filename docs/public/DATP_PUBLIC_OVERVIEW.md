# DATP Public Overview

DATP (Deterministic Authority Transition Protocol) is the runtime authority model beneath DETERMA.

It defines how execution authority transitions from intent to mutation under changing runtime conditions.
The objective is operational: preserve Runtime Legitimacy when runtime state can drift between approval and execution.

## Why DATP Exists

Historical approval can survive while runtime conditions change.
When authority is reused without Runtime Legitimacy checks, mutation can occur under stale assumptions.

DATP addresses this by making Runtime Authority conditional on present-time continuity, not only past approvals.

## Public Runtime Flow

```text
Intent Generation
-> Authority Validation
-> Runtime Legitimacy Evaluation
-> Scoped Execution Grant
-> Constrained Executor
-> Verification
-> Immutable Authority Lineage
```

## Public Operational Properties

- Runtime Legitimacy is evaluated at execution time.
- Authority Continuity is required for mutation.
- Mutation Admissibility is fail-closed when continuity fails.
- Immutable Authority Lineage records execution decisions.

## Contradiction Library

Operational scenarios are documented in:
- [Runtime Legitimacy Contradiction Library](CONTRADICTION_LIBRARY.md)

## Visualization & Operational Mapping

- [Runtime Legitimacy Visualization Layer](RUNTIME_LEGITIMACY_VISUALIZATION_LAYER.md)
- [Industry Operational Mapping Layer](INDUSTRY_OPERATIONAL_MAPPING_LAYER.md)

## Scope Boundary

This document intentionally omits protocol internals, formal authority semantics, and enforcement substrate details.
