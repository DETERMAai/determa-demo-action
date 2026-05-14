STATUS: SANITIZED_DERIVATIVE
EXPOSURE: PUBLIC_SAFE
CANONICAL_SOURCE: /docs/core/THREAT_SCENARIOS.md

# Sanitized Threat Scenarios

## Purpose

This document presents public-safe examples of the operational risks DETERMA is designed to address.

The focus is on:

- execution legitimacy
- runtime governance
- mutation safety
- replay awareness
- operational trust boundaries

without exposing restricted implementation mechanics.

---

# Threat Scenario 1 — Stale Execution State

## Description

An AI system generates an execution request using outdated environmental assumptions.

The surrounding system state has already changed.

---

## Risk

Without runtime governance, stale assumptions may authorize mutations against systems that no longer match the original execution context.

---

## Governed Goal

Execution legitimacy should be re-evaluated before mutation proceeds.

---

# Threat Scenario 2 — Replay Attempt

## Description

An execution request or approval flow is reused after its original context has already completed.

---

## Risk

Without replay-aware governance, prior authority may be reused in unintended ways.

---

## Governed Goal

Execution authority should remain bounded, contextual, and runtime-aware.

---

# Threat Scenario 3 — Direct Mutation Without Governance

## Description

AI-generated actions execute immediately without a governed execution boundary.

---

## Risk

Mutation legitimacy becomes implicitly trusted rather than externally validated.

---

## Governed Goal

Machine-generated actions should pass through constrained execution controls before real mutation occurs.

---

# Threat Scenario 4 — Runtime Drift

## Description

Runtime conditions change between proposal generation and execution.

---

## Risk

Execution may proceed under assumptions that are no longer valid.

---

## Governed Goal

Execution legitimacy should remain tied to current runtime conditions rather than historical assumptions.

---

# Canonical Principle

```text
Execution legitimacy should be evaluated at execution time, not assumed from generation time.
```
