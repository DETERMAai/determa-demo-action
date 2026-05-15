# Why Monitoring Is Insufficient

Post-fact observation is not governance.

Monitoring can detect and explain what happened. Governance determines what may happen before mutation occurs.

## Monitoring Versus Enforcement

Monitoring:
- observes events
- correlates signals
- reports outcomes

Enforcement:
- evaluates legitimacy before mutation
- blocks invalid execution paths
- preserves authority boundaries at action time

## Why Audit Alone Fails

Audit trails are essential for accountability, but they are retrospective. They do not prevent mutation under stale legitimacy assumptions.

## Why Rollback Is Not Legitimacy

Rollback is recovery, not prevention. It addresses aftermath, not precondition validity.

A reverted mutation can still cause:
- transient external effects
- coordination disruption
- trust damage in automation boundaries

## Pre-Mutation Enforcement Necessity

Legitimacy must be evaluated before execution commits state changes. This is where runtime-bound authorization matters.

## Three System Classes

Observability systems answer: "What happened?"
AI monitoring systems answer: "What did the model do?"
Runtime legitimacy systems answer: "Should this mutation execute now?"

These are complementary, not interchangeable.

## Core Conclusion

Without pre-mutation legitimacy enforcement, monitoring becomes high-quality narration of avoidable failures.
