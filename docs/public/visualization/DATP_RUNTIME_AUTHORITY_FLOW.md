# DATP Runtime Authority Flow

```text
Intent Generation
    ↓
Authority Validation
    ↓
Runtime Legitimacy Evaluation
    ↓
Mutation Admissibility Decision
    ↓
Scoped Execution Grant (or Deny)
    ↓
Constrained Executor
    ↓
Verification
    ↓
Immutable Authority Lineage
```

Cross-environment flow:

```text
STAGING
    ↓
PROMOTION_REVALIDATION
    ↓
PRODUCTION
```

Dependency propagation:

```text
A
↓
B
↓
C
```

## Operational Reading

- Runtime Authority is evaluated before mutation.
- Mutation Admissibility is continuously revalidated during execution.
- Mutation Admissibility fails-closed when Authority Continuity breaks.
- Transitive Invalidation propagates from upstream to downstream dependencies.
