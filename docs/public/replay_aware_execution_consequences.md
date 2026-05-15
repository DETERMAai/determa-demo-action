# Replay-Aware Execution Consequences

Replay-aware execution means historical authorization is not automatically reusable across changed runtime conditions.

Category outcome:
- replay of previously authorized intent can be invalid when runtime context diverges.

Public framing:
- this is an execution-boundary consistency problem
- the system protects mutation legitimacy under temporal drift
