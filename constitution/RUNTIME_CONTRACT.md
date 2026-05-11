# Deterministic Runtime Contract

The replay kernel assumes only:

- deterministic JavaScript semantics
- canonical serialization
- pure functional replay evaluation
- explicit constitutional inputs

The runtime environment is treated as adversarial.

## Replay Path Restrictions

Replay evaluation must not depend on:

- system clocks
- runtime randomness
- filesystem metadata
- network state
- locale formatting
- environment variables
- hidden mutable state

## Replay Function Shape

Replay functions must remain:

pure(input) -> output

Replay determinism takes precedence over operational convenience.
