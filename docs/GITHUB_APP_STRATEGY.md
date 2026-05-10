# DETERMA Replay — GitHub App Strategy

## Strategic Goal

Turn DETERMA Replay into a GitHub-native trust layer for AI-generated pull requests.

The GitHub App is the distribution wedge.

The long-term moat remains governed execution authority.

---

# Why GitHub First

GitHub is where:

- AI-generated pull requests appear,
- human reviewers already work,
- trust decisions already happen,
- operational mutations already enter production.

DETERMA should appear directly inside that flow.

---

# Core Product Reflex

```text
Before trusting an AI-generated pull request,
check the DETERMA Replay.
```

---

# Initial Product Shape

The GitHub App should:

1. listen to pull_request events
2. fetch diffs
3. generate deterministic replay artifacts
4. classify operational surfaces
5. compute trust states
6. publish replay comments
7. update replay comments on synchronization

---

# MVP Installation Flow

## Step 1

Install GitHub App.

## Step 2

Select repositories.

## Step 3

Open a pull request.

## Step 4

Receive DETERMA Replay automatically.

---

# MVP UX Principle

The replay must be understandable in under 30 seconds.

The reviewer should immediately understand:

- what changed,
- why it matters,
- whether the mutation should be trusted.

---

# Replay UX Rules

## Must be deterministic

Replay artifacts should remain stable across executions.

## Must fail closed

Unknown operational meaning should reduce trust.

## Must avoid hallucinated claims

Replay output should only derive from deterministic evidence.

## Must remain operational

The focus is operational meaning, not generic code review.

---

# Initial Operational Surfaces

```text
CI/CD
Deployment Infrastructure
Runtime Infrastructure
Infrastructure as Code
Secret Access
Authentication / IAM
Database Migration
Business Logic
Tests
Documentation
```

---

# Initial Trust States

```text
TRUSTED
REQUIRES_APPROVAL
BLOCKED
UNEXPLAINABLE
```

---

# Recommended Adoption Motion

## Phase 1 — Open Source Replay

Goal:

Developer awareness.

Focus:

- screenshots
- demos
- GitHub comments
- social distribution
- technical explainability

---

## Phase 2 — Team Replay

Goal:

Engineering team adoption.

Focus:

- org-wide policies
- replay persistence
- reviewer analytics
- mutation trend analysis

---

## Phase 3 — Governed Mutation Authority

Goal:

Execution control.

Focus:

```text
Replay
→ Approval Gate
→ State Witness
→ Execution Release
→ Governed Mutation
```

---

# Long-Term Moat

Replay itself is not the moat.

The moat is:

```text
deterministic operational trust infrastructure
```

and eventually:

```text
governed execution authority
```

---

# Factory Execution Plan

The Factory should autonomously:

1. expand mutation surface classifiers
2. add replay snapshots
3. improve replay rendering
4. add GitHub App infrastructure
5. generate synthetic replay scenarios
6. harden deterministic behavior
7. validate replay stability
8. expand trust-state logic

---

# Canonical Direction

Externally:

```text
Replay-first product
```

Internally:

```text
Authority-first architecture
```
