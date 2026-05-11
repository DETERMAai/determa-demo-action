# ATTACK_001_ORDERING_DRIFT

## Goal

Detect replay instability caused by non-canonical object serialization.

## Mutation

Reorder identical RTC fields.

## Expected Result

Current vulnerable implementations using JSON.stringify directly may drift.

Replay corruption must become observable.

## Constitutional Failure

Silent replay identity mutation.
