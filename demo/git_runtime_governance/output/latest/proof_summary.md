# Governed Repository Mutation Proof

Same patch. Same authority model. Different repository runtime state. Different execution outcome.

## Path A — Patch Allowed

- status: EXECUTION_ALLOWED
- reason: authority continuity preserved

## Path B — Patch Denied

- status: EXECUTION_DENIED
- reason: repository runtime state diverged after approval

## Replay Invalidation

- replay attempt status: DENIED
- replay reason: repository HEAD diverged; target file hash diverged; runtime epoch changed; single-use authority grant replay detected

## Runtime Divergence

- path_a: LOW (0)
- path_b: HIGH (64)

## State Visualization

Authority Continuity
VALID -> WEAKENING -> STALE -> INVALID

Mutation Admissibility
ADMISSIBLE -> REQUIRES_REVALIDATION -> DENIED

Runtime Divergence
LOW -> MEDIUM -> HIGH -> CRITICAL
