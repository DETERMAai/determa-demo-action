# First Contradiction

This is the operational contradiction that motivates DATP and Runtime Legitimacy.

## Sequence

T0:
Patch approved.

T1:
Runtime state changes.

T2:
Historical approval still exists.

T3:
Execution occurs.

T4:
Failure emerges.

## Core Conclusion

The approval survived.
The legitimacy did not.

## What Failed

- Stale authority was reused after Runtime Divergence.
- Authority Continuity did not hold from approval-time state to execution-time state.
- Mutation Admissibility should have failed-closed before execution.

## Why Traditional Approval Models Fail Here

Traditional models preserve approval records, but do not reliably reevaluate Runtime Legitimacy at mutation time.
In autonomous systems with delay and drift, this creates legitimacy collapse even when historical approvals look valid.
