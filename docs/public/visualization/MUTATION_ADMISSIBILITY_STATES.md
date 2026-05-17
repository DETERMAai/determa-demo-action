# Mutation Admissibility States

```text
PROPOSED
    ↓
APPROVED
    ↓
QUEUED
    ↓
EXECUTING
    ↓
REVALIDATING
    ↓
ADMISSIBLE ? ------ no ------> HALTED (FAIL_CLOSED)
     |
    yes
     ↓
FINALIZED
```

## Authority Continuity Progression

```text
VALID
→ WEAKENING
→ STALE
→ INVALID
→ TRANSITIVELY_INVALIDATED
```

## Operational Reading

- Historical approval is not final authority.
- Mutation Admissibility is recomputed at the Execution Boundary.
- Downstream admissibility may be transitively invalidated by upstream collapse.
