# Deployment Verification Protocol

This protocol defines deployment legitimacy for the public DETERMA runtime surface.

## Canonical Lifecycle

```text
Implementation
    ↓
Commit
    ↓
Push
    ↓
Pages Propagation
    ↓
Runtime Verification
    ↓
Public Convergence
    ↓
Deployment Legitimacy Achieved
```

## Required Validation Checks

1. Git state
- commit exists and is attributable to intended change scope
- branch is correct
- push completed to remote

2. Pages propagation
- GitHub Pages URL resolves
- root routing resolves to demo surface
- static assets resolve without 404

3. Runtime integrity
- session initialization generates execution/evidence/session IDs
- event stream appends in temporal order
- evidence generation progresses and finalizes
- replay and new-scenario controls operate

4. Public convergence
- README links reflect deployed paths
- demo links match public URL behavior
- NotebookLM public URL is reachable
- screenshot and visual paths are valid

## Propagation Requirements

- Do not mark deployment legitimate before Pages propagation is verified.
- Validate both repository state and public Pages state.
- If propagation is stale, classify deployment as pending and rerun checks.

## Runtime Integrity Rules

- Runtime status must be derived from active session state.
- Evidence output must be reconstructable from runtime flow.
- Session history persistence must not break replay continuity.

## Evidence Verification Expectations

- Evidence export must include session identity and runtime epochs.
- Finalized records must indicate immutable completion state.
- Historical records must remain accessible for comparison.
