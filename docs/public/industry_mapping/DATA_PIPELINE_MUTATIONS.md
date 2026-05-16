# Data Pipeline Mutations Mapping

## Typical Flow

Pipeline transformation is approved.
Execution is replayed after upstream schema or dependency changes.

## Contradiction Pattern

- historical approval remains
- runtime data assumptions diverge
- mutation side effects become uncertain

## DATP Operational Interpretation

- Mutation Admissibility depends on current Runtime Authority.
- Authority Continuity failure triggers fail-closed pipeline mutation control.
