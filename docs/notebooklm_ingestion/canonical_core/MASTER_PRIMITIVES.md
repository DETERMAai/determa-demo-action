DISCLOSURE_CLASSIFICATION: P0

# Master Primitives

This file defines the canonical primitive set for the runtime legitimacy field.

Use rule:
All higher-order doctrine should reduce to these primitives and their relationships.

## Primitive Set (24)

### P01 Legitimacy
- Definition: Present-time admissibility of a state-changing action.
- Role: Root field concept.
- Depends on: runtime context, authority context.
- Contradicts: historical-record sufficiency.
- Invariants: admissibility is contextual.

### P02 Runtime Legitimacy
- Definition: Legitimacy evaluated at execution boundary.
- Role: Core execution predicate.
- Depends on: P04, P05, P06.
- Contradicts: approval-only execution.
- Invariants: evaluated at mutation time.

### P03 Mutation Legitimacy
- Definition: Legitimacy specific to state mutation actions.
- Role: Narrows P01 to mutable operations.
- Depends on: P02, P11.
- Contradicts: descriptive-only governance.
- Invariants: requires commit-time admissibility.

### P04 Authority Continuity
- Definition: Persistence of coherent authority assumptions from approval to execution.
- Role: Authority bridge primitive.
- Depends on: P07, P08.
- Contradicts: static authority inheritance.
- Invariants: continuity can weaken over time.

### P05 State Continuity
- Definition: Coherence between approval-time and execution-time relevant state.
- Role: Context bridge primitive.
- Depends on: P09, P10.
- Contradicts: state-agnostic authorization.
- Invariants: continuity is required for stable admissibility.

### P06 Temporal Validity
- Definition: Time-bounded validity of authority claims.
- Role: Temporal constraint primitive.
- Depends on: P12.
- Contradicts: timeless approval semantics.
- Invariants: delay increases uncertainty.

### P07 Execution Authority
- Definition: Present right to execute mutation under current constraints.
- Role: Execution gate primitive.
- Depends on: P02, P04.
- Contradicts: capability-only execution.
- Invariants: authority is state-dependent.

### P08 Authority Externalization
- Definition: Separation between mutation generation and mutation authorization.
- Role: Boundary integrity primitive.
- Depends on: P07.
- Contradicts: self-legitimizing agents.
- Invariants: independent control boundary required.

### P09 Runtime Divergence
- Definition: Material difference between approval context and execution context.
- Role: Primary destabilizer primitive.
- Depends on: elapsed time, system change.
- Contradicts: context stability assumption.
- Invariants: divergence accumulates under change.

### P10 State Witness
- Definition: Conceptual evidence of relevant runtime state at a moment.
- Role: Continuity reference primitive.
- Depends on: state observability abstractions.
- Contradicts: context-free approvals.
- Invariants: witness mismatch implies uncertainty.

### P11 Bounded Execution
- Definition: Controlled mutation scope under legitimacy constraints.
- Role: Containment primitive.
- Depends on: P07, P14.
- Contradicts: unconstrained mutation authority.
- Invariants: scope must remain explicit.

### P12 Legitimity Half-Life
- Definition: Conceptual interval over which legitimacy confidence materially decays.
- Role: Decay calibration primitive.
- Depends on: P09, volatility.
- Contradicts: constant trust over time.
- Invariants: decay is environment-sensitive.

### P13 Mutation Trust Decay
- Definition: Decreasing confidence in mutation safety under unverified drift.
- Role: Risk pressure primitive.
- Depends on: P09, P12.
- Contradicts: immutable trust assumptions.
- Invariants: trust is contextual and temporal.

### P14 Legitimacy Revalidation
- Definition: Re-check of admissibility under current runtime state.
- Role: Continuity repair primitive.
- Depends on: P02, P04, P05.
- Contradicts: one-time approval sufficiency.
- Invariants: required after meaningful divergence.

### P15 Historical Authorization
- Definition: Recorded approval under prior context.
- Role: Accountability primitive.
- Depends on: authorization workflows.
- Contradicts: present-time authority equivalence.
- Invariants: historical truth can coexist with present invalidity.

### P16 Static Authorization
- Definition: Context-light permission model with durable grants.
- Role: Baseline comparison primitive.
- Depends on: role/policy assignment.
- Contradicts: runtime-aware authority.
- Invariants: degrades under high drift + delay.

### P17 Replayability
- Definition: Ability to reproduce procedural action sequence.
- Role: Reproducibility primitive.
- Depends on: deterministic reconstruction.
- Contradicts: replay legitimacy equivalence.
- Invariants: reproducibility != admissibility.

### P18 Replay Legitimacy
- Definition: Admissibility of replay under current continuity conditions.
- Role: Replay authority primitive.
- Depends on: P02, P05, P09.
- Contradicts: historical success sufficiency.
- Invariants: each replay is a fresh legitimacy event.

### P19 Computational Invalidation
- Definition: Formal outcome that prior authority no longer applies.
- Role: Fail-closed outcome primitive.
- Depends on: P14, contradiction detection.
- Contradicts: forced continuity assumptions.
- Invariants: invalidation preserves history, blocks inadmissible execution.

### P20 Mutation Reinterpretation
- Definition: Change in operational meaning of unchanged mutation instruction.
- Role: Semantic drift primitive.
- Depends on: P09, coupling evolution.
- Contradicts: instruction-text permanence assumptions.
- Invariants: semantics can drift without syntax drift.

### P21 Contradiction Primitive
- Definition: Persistent mismatch between historical truth and present admissibility.
- Role: Diagnostic primitive.
- Depends on: P15 + P02 mismatch.
- Contradicts: single-truth governance framing.
- Invariants: contradiction propagation is systemic.

### P22 Drift Accumulation
- Definition: Cumulative mutation-relevant divergence over time.
- Role: Dynamics primitive.
- Depends on: change rate, coupling.
- Contradicts: independent-change neutrality.
- Invariants: accumulation can be non-linear.

### P23 Authority Collapse Path
- Definition: Sequence through which continuity weakens into invalidation.
- Role: Failure progression primitive.
- Depends on: P04, P09, P12.
- Contradicts: abrupt-failure-only models.
- Invariants: collapse usually unfolds in stages.

### P24 Runtime Governance
- Definition: Discipline of evaluating execution admissibility at runtime.
- Role: Field synthesis primitive.
- Depends on: P02, P14, P19.
- Contradicts: approval-centric governance only.
- Invariants: governance quality is judged at execution boundary.

## Dependency Spine

```text
Legitimacy
  -> Runtime Legitimacy
    -> Authority Continuity + State Continuity + Temporal Validity
      -> Revalidation
        -> Invalidation or Executable Authority
```

## Canonical Contradiction Spine

```text
Historical Authorization TRUE
+ Runtime Divergence HIGH
= Legitimacy Uncertain
-> Revalidation Required
-> Invalidation (if continuity fails)
```

