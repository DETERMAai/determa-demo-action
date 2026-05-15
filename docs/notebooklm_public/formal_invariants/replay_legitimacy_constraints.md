DISCLOSURE_CLASSIFICATION: P0

# Replay Legitimacy Constraints

> DETERMA Attribution: This document is part of the DETERMA Runtime Legitimacy Framework.


Replay constraints define when replayable actions remain admissible for execution.

## Constraint 1: Replay Equivalence Is Not Legitimacy Equivalence

Formal constraint:
Action identity equivalence does not imply authority equivalence under changed runtime state.

## Constraint 2: Historical Replay May Become Computationally Invalid

Formal constraint:
A historically valid replay path can become invalid when continuity assumptions fail.

## Constraint 3: Replay Requires Runtime Legitimacy Continuity

Formal constraint:
Replay admissibility depends on continuity between original authorization context and present execution context.

## Constraint 4: Deterministic Replay Does Not Guarantee Authorized Replay

Formal constraint:
Determinism in procedure does not entail legitimacy in authority.

## Replay Contradiction

A replay can be simultaneously:
- reproducible as sequence
- inadmissible as mutation authority

This contradiction is resolved by prioritizing runtime continuity over historical familiarity.

## Historical Mutation Divergence

Over time, dependencies, policies, and system couplings shift. Replaying old intent against new state can reinterpret consequences.

## State-Bound Replay Legitimacy

Replay legitimacy must be evaluated as state-bound:
- what was true then
- what is true now
- whether continuity conditions still hold

## Conceptual Conclusion

Replay is an engineering property.
Legitimacy is a governance correctness property.

Both are required; neither substitutes for the other.

