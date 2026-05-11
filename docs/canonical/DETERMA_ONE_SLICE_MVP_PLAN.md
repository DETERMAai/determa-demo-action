# DETERMA ONE-SLICE MVP PLAN
## Canonical Official Execution Plan — May 2026

Status:

```text
ACTIVE CANONICAL MVP PLAN
```

---

# Purpose

This document defines the single canonical MVP strategy for DETERMA.

Its purpose is to prevent:

- premature platform expansion
- infrastructure recursion
- generalized orchestration drift
- governance overengineering
- roadmap fragmentation

The current mission is:

```text
Build one undeniable governed execution slice.
```

---

# Canonical Definition

DETERMA is not:

- a generic AI orchestration platform
- an AI observability dashboard
- a multi-agent mesh
- an autonomous swarm framework
- a generalized governance protocol

DETERMA is:

```text
Governed replayable authority for AI-generated code mutations.
```

Or operationally:

```text
Observe, replay, and govern AI-generated code mutations.
```

---

# Core Problem

The core problem is not:

```text
Can AI generate code?
```

The real problem is:

```text
Can organizations trust, reconstruct, and govern AI-generated mutations?
```

---

# Foundational Principle

AI may propose.

AI may not independently mutate operational systems.

Every mutation must pass through:

```text
Authority
→ Verification
→ Controlled Execution
→ Replayability
```

---

# MVP Goal

The MVP proves only one thing:

```text
Governed code mutation.
```

The MVP is NOT a complete authority plane.

The MVP is one live governed execution slice.

---

# Canonical MVP Flow

```text
Evidence detected
→ Supervisor creates task
→ Worker v2 generates artifacts
→ WAITING_APPROVAL
→ Human approval
→ Capability issued
→ State witness validated
→ Constrained executor applies patch
→ Tests run
→ Verification
→ Draft PR created
→ Replay generated
→ Audit finalized
```

---

# MVP Components

## 1. Supervisor

Responsibilities:

- detect evidence
- create governed task
- initialize runtime state

Examples:

- failing tests
- lint failures
- TODO/FIXME findings
- static analysis findings

---

## 2. Worker v2

Worker v2 performs:

```text
artifact generation only
```

Outputs:

```text
spec.md
patch.diff
test_plan.md
risk_report.md
score_report.json
```

Worker v2 MUST NOT:

- push directly
- deploy
- mutate repositories directly
- open PRs independently
- execute unrestricted shell commands

---

## 3. Authority Core

Responsibilities:

- runtime governance
- replay evaluation
- approval lifecycle
- policy checks
- capability issuance
- audit continuity
- fail-closed enforcement

---

## 4. Approval Layer

The MVP approval layer remains intentionally minimal.

Allowed surfaces:

- CLI
- minimal web UI
- HTTP endpoint

Operations:

```text
approve
reject
```

---

## 5. Policy Engine

Minimal policies only.

```text
LOW → REVIEW
HIGH → SECURITY_REVIEW
CRITICAL → ADMIN
```

No policy DSL.

No generalized policy framework.

---

## 6. State Witness

Before execution:

```text
repository state must match approved state
```

Otherwise execution halts.

---

## 7. Capability Release

Execution requires:

```text
single-use constrained authorization
```

Capability requirements:

- TTL
- executor binding
- exact scope
- replay protection
- revocation support

---

## 8. Constrained Executor

Canonical first executor:

```text
Git Patch Executor
```

Allowed operations only:

- apply patch
- run tests
- commit
- open draft PR

No arbitrary execution.

---

## 9. Verification

After execution:

- validate actual mutation surface
- validate approval alignment
- validate tests
- validate replay reconstruction

---

## 10. Replay Artifact

The replay artifact IS the product.

Not the dashboard.

Not orchestration complexity.

Not governance abstractions.

The replay itself.

Canonical replay sections:

```text
Repository
Agent
Severity
Mutation Surface
Intent
Human Summary
What Changed
Potential Consequences
Replay Timeline
Trust Analysis
Replay Integrity
```

---

# Canonical Demo Story

```text
Claude Code modifies deployment workflow
→ touches release policy
→ DETERMA reconstructs replay
→ analyzes consequences
→ blocks unsafe mutation
→ explains trust decision
```

This is the canonical MVP demonstration.

---

# Existing Implemented Foundations

Already implemented:

- runtime governance
- replay gate
- approval queue
- approval persistence
- recovery engine
- resume planner
- identity layer
- authority hierarchy
- governance CLI
- governance testing

---

# Remaining Critical Work

## 1. Minimal Policy Engine

Target:

```text
1 day
```

---

## 2. Real Git Patch Executor

Target:

```text
2–4 days
```

---

## 3. Replay Artifact Hardening

Target:

```text
2 days
```

---

## 4. Canonical Demo Packaging

Target:

```text
2–3 days
```

---

# Factory Strategy

The Factory is not an autonomous architect.

The Factory is:

```text
bounded implementation acceleration
```

---

# Factory Operational Rules

## Rule 1 — Tiny PRs

```text
one responsibility per PR
```

---

## Rule 2 — Hard Boundaries

Every task must define:

- allowed files
- forbidden files
- expected outputs
- execution limits

---

## Rule 3 — Test-Gated Execution

```text
No execution without tests.
```

---

## Rule 4 — No Recursive Expansion

If work drifts toward:

- generalized frameworks
- broad abstractions
- platformization
- infrastructure recursion

Stop.

Return to governed execution delivery.

---

# Real KPI

The KPI is not governance complexity.

The KPI is:

```text
Did replay change merge behavior?
```

---

# MVP Delivery Goal

Target delivery:

```text
7–14 days
```

Deliverable:

```text
working governed execution slice
```

Capabilities:

- receive task
- generate bounded patch
- evaluate replay
- evaluate trust
- require authority
- receive approval
- open governed draft PR
- generate replay artifact

---

# Canonical Status Statement

The correct current statement is:

```text
DETERMA has one live governed execution slice,
not yet a complete authority plane.
```

---

# Victory Condition

Victory is NOT:

```text
building the biggest governance platform
```

Victory is:

```text
making AI-generated mutations operationally replayable
before they become operationally dangerous
```
