# ATTACK_002_TIMESTAMP_LEAK

## Goal

Detect replay nondeterminism introduced through runtime time access.

## Forbidden Surfaces

- Date.now()
- new Date()

## Expected Result

Replay drift must become observable.

Silent replay mutation is constitutional failure.
