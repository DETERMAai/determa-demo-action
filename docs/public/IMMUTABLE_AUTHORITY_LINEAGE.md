# Immutable Authority Lineage

Immutable Authority Lineage is the execution authority record produced by governed runtime decisions.

It is not a marketing artifact.
It is an operational trace of authority state, continuity outcome, and execution decision.

## What It Captures

- execution identity
- authority context at decision time
- Runtime Legitimacy outcome
- fail-closed or admitted mutation decision
- ordering continuity across events

## Why It Matters

When runtime conditions evolve, teams need a durable record of why execution was permitted or denied.
Immutable Authority Lineage supports reconstruction without exposing internal enforcement semantics.

## DATP Relationship

DATP uses lineage as a public-safe verification surface:
- authority transitioned under continuity, or
- mutation was denied due to continuity failure.
