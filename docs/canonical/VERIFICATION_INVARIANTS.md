# DETERMA Verification Invariants

## Deterministic Verification

Verification must:

- produce identical outcomes for identical execution state
- preserve replay determinism
- preserve legitimacy ownership
- fail closed on ambiguity

## Replay Preservation

Replay must reconstruct:

- mutation intent
- authority boundary
- execution boundary
- approval state

## Fail-Closed Legitimacy

Verification ambiguity must:

- reject execution
- reject governed release
- reject governed PR promotion

## Canonical Verification Requirements

Verification is considered valid only if:

- authority hash stable
- mutation hash stable
- replay deterministic
- execution reproducible
- artifact chain complete
