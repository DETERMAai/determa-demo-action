# Mutation Admissibility States

```text
APPROVAL_PRESENT
    ↓
RUNTIME_MATCH_CHECK
    ↓
AUTHORITY_CONTINUITY_VALID ? ---- no ----> FAIL_CLOSED_EXECUTION
          |
         yes
          ↓
MUTATION_ADMISSIBLE
    ↓
SCOPED_EXECUTION
    ↓
LINEAGE_RECORDED
```

## Operational Reading

- Historical approval is not final authority.
- Admissibility depends on present Runtime Legitimacy.
