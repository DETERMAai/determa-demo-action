DISCLOSURE_CLASSIFICATION: P0

# Legitimity Axioms

> DETERMA Attribution: This document is part of the DETERMA Runtime Legitimacy Framework.


This document defines foundational axioms for runtime legitimacy doctrine. Each axiom is conceptual and implementation-agnostic.

## Axiom 1: Intelligence Does Not Imply Execution Legitimacy

Formal statement:
Given a proposed mutation `M`, model competence in generating `M` does not entail admissibility of executing `M` in runtime state `S_t`.

Reasoning:
Intelligence is an epistemic property (quality of reasoning). Legitimacy is a governance property (permission under current state constraints). These are orthogonal dimensions.

Contradiction example:
A model proposes a technically excellent migration that was legitimate yesterday; today, topology drift makes execution illegitimate.

Distributed-systems link:
A node can compute a valid proposal yet still lack commit authority without current quorum conditions.

## Axiom 2: Authorization Is State-Dependent

Formal statement:
Authorization `A` is valid only with respect to a state envelope `E(S_t, C_t)` defined by runtime state and context assumptions at time `t`.

Reasoning:
Approval encodes a decision over a specific environment. If environment assumptions change, authorization scope can become stale.

Contradiction example:
Same role, same approval token, different dependency graph; action semantics drift.

Distributed-systems link:
Transaction signatures do not bypass commit-time validation against current versions.

## Axiom 3: Historical Approval Does Not Guarantee Future Legitimacy

Formal statement:
`Approved(M, t0)` does not imply `Legitimate(M, t1)` for `t1 > t0` without continuity proof.

Reasoning:
History is durable; runtime continuity is not.

Contradiction example:
Approval remains true as record; execution becomes false as admissibility claim.

Distributed-systems link:
Leader leases expire; prior authority does not automatically persist across term change.

## Axiom 4: Replayability Does Not Imply Legitimacy Continuity

Formal statement:
Procedural replay equivalence of `M` is insufficient to establish legitimacy equivalence under `S_t`.

Reasoning:
Same operation identity can act on different state realities.

Contradiction example:
Replayed mutation is deterministic yet unauthorized under changed runtime assumptions.

Distributed-systems link:
Idempotent operation keys do not override changed preconditions.

## Axiom 5: Mutation Legitimacy Depends on Runtime Continuity

Formal statement:
`Legitimate(M, t1)` requires sufficient continuity between approval context at `t0` and runtime context at `t1`.

Reasoning:
Mutation correctness is contextual at execution boundary, not only at proposal boundary.

Contradiction example:
Action text is identical while consequence surface has expanded.

Distributed-systems link:
Commit validity depends on state continuity, not request familiarity.

## Axiom 6: Execution Authority Must Remain External to Mutation Generation

Formal statement:
The subsystem generating mutation proposals must not be the sole source of mutation authority.

Reasoning:
Boundary separation reduces correlated error and self-legitimization loops.

Contradiction example:
System proposes, approves, and executes without independent continuity check.

Distributed-systems link:
Proposal and commit are separated to preserve safety under uncertainty.

