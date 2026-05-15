DISCLOSURE_CLASSIFICATION: P0

# Mutation Legitimacy Lifecycle

Conceptual lifecycle for mutation legitimacy.

```text
PROPOSED
↓
APPROVED (historical)
↓
RUNTIME CONTINUITY CHECK
↓
LEGITIMATE NOW    |    LEGITIMACY UNCERTAIN
↓                         ↓
EXECUTABLE                REVALIDATION REQUIRED
                          ↓
                    REVALIDATED | INVALIDATED
```

State meanings:
- `APPROVED (historical)`: approval artifact exists.
- `LEGITIMATE NOW`: continuity holds at execution boundary.
- `LEGITIMACY UNCERTAIN`: drift signals unresolved admissibility.
- `INVALIDATED`: execution authority does not carry forward.

Key invalidation conditions:
- critical runtime divergence
- capability envelope shift
- temporal decay beyond tolerance

