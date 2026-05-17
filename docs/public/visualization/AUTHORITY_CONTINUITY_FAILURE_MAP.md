# Authority Continuity Failure Map

```text
Historical Approval
    ↓
Execution Delay / Environment Transition / Upstream Drift
    ↓
Runtime Divergence
    ↓
Authority Continuity Pressure
    ↓
Continuity Failure
    ↓
Mutation Admissibility = DENIED or TRANSITIVELY_INVALIDATED
    ↓
Fail-Closed Execution
```

## Failure Inputs

- dependency graph shift
- runtime patch after approval
- capability scope escalation
- replay under changed context
- staging-to-production witness mismatch
- delegated runtime continuity mismatch
- upstream dependency invalidation propagation (`A -> B -> C`)
