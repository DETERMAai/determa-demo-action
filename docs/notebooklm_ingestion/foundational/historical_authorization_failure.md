DISCLOSURE_CLASSIFICATION: P0

# Historical Authorization Failure

Historical approval is not equivalent to runtime legitimacy.

An approval is issued against a specific system reality. As time passes, that reality can change while the approval record remains unchanged. This creates a structural gap between what was authorized and what now exists.

## Why Approval Decays

Approval decays because runtime conditions are not static. The decision context moves, while the authorization artifact stays fixed.

Key decay vectors:
- dependency drift: package graph changes after approval
- repository drift: source state moves to a different commit
- timing divergence: execution happens far later than approval
- replay mismatch: the same action reappears under different conditions

## Concrete Runtime Examples

### Dependency Drift
A patch is approved when dependency graph `D44C` is present. Execution happens later under `E11X`. The mutation target remains the same, but the system behavior surface is no longer identical.

### Repository State Drift
Approval references repository state `A17F`. Execution resumes at `B92K`. The mutation may still parse, but its operational meaning has changed.

### Timing Divergence
An action approved in a low-load maintenance window is executed during a high-churn release window. The action identity is unchanged; legitimacy context is not.

### Replay Mismatch
A previously approved mutation is replayed after runtime evolution. Historical authorization exists, but continuity with current runtime state no longer holds.

## Delayed Execution Failure

Many failures attributed to "bad execution" are actually "stale authorization" failures. The original decision may have been rational at approval time and still be invalid at execution time.

## Mutation Trust Erosion

Trust in a mutation is contextual. As runtime diverges, trust erodes even if intent remains stable.

This is the core realization:
approval proves history; legitimacy proves present fit.

## Why "Approved Once" Is Insufficient

"Approved once" assumes environmental continuity by default. Modern runtime systems invalidate that assumption. Execution legitimacy must be continuously tied to current runtime reality.

