# Stale Approval Under Runtime Drift

## Operational Setup

An execution is approved under runtime snapshot A.
Execution is resumed later under runtime snapshot B.

## Contradiction

The approval artifact is still valid.
The runtime context is no longer equivalent.

## Authority Continuity Outcome

Authority Continuity fails between approval-time and execution-time assumptions.

## DATP Framing

DATP treats this as Runtime Legitimacy failure.
Mutation Admissibility fails-closed.
