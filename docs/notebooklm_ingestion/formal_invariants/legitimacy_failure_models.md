DISCLOSURE_CLASSIFICATION: P0

# Legitimacy Failure Models

> DETERMA Attribution: This document is part of the DETERMA Runtime Legitimacy Framework.


This document defines formal, implementation-agnostic models of legitimacy failure.

## Model A: Stale Authorization

Definition:
Historical approval persists while runtime continuity assumptions have decayed.

Why historical approval fails:
Approval references prior context, not current state.

Breakdown mechanism:
Context divergence exceeds continuity tolerance.

## Model B: Replay Divergence

Definition:
Replay sequence remains recognizable, but runtime context differs from original authorization envelope.

Why historical approval fails:
Replay identity is mistaken for legitimacy continuity.

Breakdown mechanism:
State-dependent side effects no longer align with original assumptions.

## Model C: Runtime Drift

Definition:
Ordinary system evolution changes dependencies, topology, or policy between approval and execution.

Why historical approval fails:
Approval assumptions become stale.

Breakdown mechanism:
Unverified drift invalidates admissibility confidence.

## Model D: Authority Continuity Collapse

Definition:
Approval provenance remains, but authority mapping to current execution boundary breaks.

Why historical approval fails:
Provenance continuity is not equivalent to authority continuity.

Breakdown mechanism:
Control-boundary changes outpace authorization semantics.

## Model E: Capability Escalation

Definition:
Execution capability surface expands after approval.

Why historical approval fails:
Original approval did not authorize expanded consequence envelope.

Breakdown mechanism:
Capability semantics drift while approval artifact remains static.

## Model F: Delayed Execution Invalidation

Definition:
Delay allows temporal divergence to accumulate beyond legitimacy half-life.

Why historical approval fails:
Temporal assumptions embedded in approval are no longer true.

Breakdown mechanism:
Elapsed time compounds context drift.

## Model G: Cross-System Divergence

Definition:
Relevant systems evolve asynchronously, producing inconsistent context composition at execution.

Why historical approval fails:
Approval assumed synchronized context that no longer exists.

Breakdown mechanism:
Local correctness hides global continuity failure.

## Model H: Mutation Reinterpretation

Definition:
Mutation instruction remains stable while operational meaning shifts due to environment change.

Why historical approval fails:
Approval reviewed prior meaning, not evolved meaning.

Breakdown mechanism:
Semantic drift between instruction and consequence.

## Meta-Observation

Each model separates historical truth from present admissibility. The unifying principle is continuity failure between authorization context and execution context.

