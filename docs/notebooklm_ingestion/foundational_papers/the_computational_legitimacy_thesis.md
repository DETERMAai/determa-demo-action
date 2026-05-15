DISCLOSURE_CLASSIFICATION: P1

# The Computational Legitimacy Thesis

> This paper is part of the DETERMA Runtime Legitimacy Doctrine.


## Abstract

Autonomous systems are crossing a critical boundary: from generating recommendations to mutating shared runtime state. This transition exposes a structural gap in current governance models. Existing systems preserve historical approvals, identity permissions, and post-fact observability, yet often lack a rigorous mechanism for execution-time legitimacy under runtime evolution. This paper argues that computational legitimacy is an emerging infrastructure primitive: a formal layer that determines whether execution still belongs to current runtime reality.

## 1. Problem Statement

Classical approval-centric systems assume that if a task was approved once, it can be executed later. In mutable distributed environments, this assumption fails. Repository state changes, dependency graphs evolve, policy defaults shift, capabilities expand, and execution may be delayed. Historical authorization can remain true while present execution legitimacy becomes uncertain or false.

The core contradiction is simple:
- approval continuity may persist
- state continuity may not

When these diverge, historical authorization cannot be treated as unconditional execution authority.

## 2. Conceptual Foundations

### 2.1 Runtime Legitimacy
Runtime legitimacy is present-time admissibility of mutation under current state constraints.

### 2.2 Authority Continuity
Authority continuity is the persistence of coherent control boundaries from approval to execution.

### 2.3 Temporal Decay
Legitimacy decays as unverified runtime divergence accumulates.

### 2.4 Replay Legitimacy
Replayability does not imply replay admissibility under changed runtime context.

### 2.5 Bounded Execution
Mutation authority must remain bounded by continuity-aware legitimacy constraints.

## 3. Distributed Systems Parallel

Computational legitimacy is not a novelty category detached from systems theory. It is continuous with established distributed-systems principles:
- proposal is distinct from commit
- commit requires current-state validity
- stale snapshots invalidate execution assumptions
- temporal correctness matters under asynchronous evolution

Approval maps conceptually to proposal. Execution maps to commit. Runtime legitimacy maps to commit admissibility under continuity constraints.

## 4. Why Existing Layers Are Necessary but Insufficient

- IAM proves identity scope, not present mutation admissibility.
- Audit proves historical action evidence, not prior admissibility correctness.
- Monitoring and observability explain events, not pre-mutation permissibility.
- Replay tooling proves reproducibility, not authority continuity.

These layers are essential. None replaces runtime legitimacy.

## 5. Legitimacy Invalidation Dynamics

Legitimacy invalidation can arise through:
- stale authorization under delay
- replay divergence
- capability-context misalignment
- cross-system state divergence
- mutation reinterpretation under environment drift

Invalidation does not erase approval history. It updates execution admissibility.

## 6. Mutation Governance Implications

A governance architecture for autonomous mutation must separate:
- historical truth (what was approved)
- present truth (what may execute now)

This separation preserves accountability while preventing stale-authority execution.

## 7. Field Definition

Computational legitimacy infrastructure is the systems layer that computes execution admissibility under current runtime continuity conditions. Its purpose is not to optimize prompt quality or provide post-fact explanation. Its purpose is to maintain correctness at the mutation boundary.

## 8. Theoretical Claims

1. Authorization is state-dependent.
2. Historical approval is not sufficient for future execution legitimacy.
3. Legitimacy decays with unverified divergence.
4. Replay and legitimacy are non-equivalent dimensions.
5. Execution authority must remain external to mutation generation.
6. Runtime legitimacy is a distributed-correctness requirement for autonomous mutation.

## 9. Consequences for System Design

As autonomous systems scale, legitimacy evaluation must become explicit and formalized. The future discipline is not approval accumulation. It is continuity-aware execution governance.

This implies a conceptual stack:
- intelligence infrastructure (proposal generation)
- identity/policy infrastructure (static scope)
- observability/audit infrastructure (evidence)
- computational legitimacy infrastructure (execution admissibility)

## 10. Conclusion

Autonomous mutation without runtime legitimacy is equivalent to commit without current-state validation. It can function temporarily under low divergence and fail predictably under normal evolution.

Computational legitimacy is therefore not optional refinement. It is the next infrastructure primitive required to align execution authority with present runtime reality.


