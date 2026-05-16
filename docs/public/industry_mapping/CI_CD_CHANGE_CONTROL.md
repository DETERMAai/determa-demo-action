# CI/CD Change Control Mapping

## Typical Flow

Build approved in one environment.
Deployment executes later under shifted runtime conditions.

## Contradiction Pattern

- approval token exists
- runtime package graph changed
- execution context differs from approval context

## DATP Operational Interpretation

- Runtime Legitimacy must be re-evaluated at deploy time.
- If Authority Continuity fails, deployment mutation is denied fail-closed.
