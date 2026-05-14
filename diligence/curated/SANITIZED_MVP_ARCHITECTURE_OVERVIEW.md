# Sanitized MVP Architecture Overview

## Purpose

This document provides a high-level overview of the DETERMA MVP architecture suitable for:

- investor onboarding
- design partner evaluation
- strategic technical review
- NotebookLM diligence corpora

The document intentionally omits restricted implementation semantics.

---

# MVP Goal

The DETERMA MVP demonstrates governed execution for AI-generated mutation proposals.

The core architectural objective is to separate:

```text
machine-generated intent
```

from:

```text
authorized execution
```

---

# High-Level Runtime Flow

```text
AI proposal
    ↓
Execution boundary
    ↓
Authority evaluation
    ↓
Constrained execution decision
    ↓
Verification
    ↓
Execution lineage recording
```

---

# Core MVP Properties

## Governed Execution

Mutation requests pass through a runtime governance layer before execution.

---

## Constrained Mutation Flow

Execution is treated as bounded and reviewable rather than implicitly trusted.

---

## Replay-Aware Runtime

The runtime evaluates execution legitimacy against current execution context.

---

## Fail-Closed Runtime Philosophy

Under uncertainty, invalid runtime state, or failed legitimacy checks, execution should halt rather than proceed implicitly.

---

## Runtime Lineage

Execution flow visibility is preserved through append-only lineage concepts.

---

# Intended Demonstration Outcome

The MVP is intended to demonstrate that governed execution can exist as a runtime layer independent from the AI model itself.

---

# Restricted Areas

This document intentionally excludes:

- deep governance semantics
- authority issuance mechanics
- replay invalidation internals
- cryptographic enforcement details
- internal orchestration mechanics
- moat-critical sequencing
