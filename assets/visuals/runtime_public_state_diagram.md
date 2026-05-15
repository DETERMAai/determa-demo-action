# Runtime Public State Diagram

```text
Local Runtime State
    ↓
Repository Commit State
    ↓
Repository Push State
    ↓
Pages Deployment State
    ↓
Public Runtime State
```

## Divergence Possibilities

- local runtime updated but commit missing
- commit exists but push not completed
- push completed but Pages propagation stale
- Pages updated but static assets unresolved
- demo session logic updated but public runtime still old

## Stale Deployment Risk

When public runtime state lags repository intent, users observe outdated legitimacy behavior and stale evidence logic.

## Public Legitimacy Alignment

Deployment legitimacy is achieved only when local, repository, Pages, and runtime states converge.
