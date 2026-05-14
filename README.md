# DETERMA

Runtime execution integrity system for verifying whether actions remain valid as system state changes.

---

## What this system is

DETERMA is a governed execution runtime that ensures:

> Actions are only valid if system state has not changed since approval.

---

## Core Idea

Modern systems execute actions based on prior approval.

But between approval and execution:

- system state changes
- dependencies shift
- assumptions become outdated

DETERMA makes this mismatch explicit, reproducible, and verifiable.

---

## What it does (simplified flow)

- A change is proposed
- The system records current state (snapshot)
- The change is executed once
- The system evolves over time (drift)
- A replay attempt is made
- The system detects mismatch
- The replay is blocked
- A proof artifact is generated

---

## Key Principle

> Execution validity must match current system state, not historical approval.

---

## What you can inspect

Each execution produces a proof containing:

- state at approval time
- state at replay time
- execution identifier
- authorization reference
- invalidation reason

All outputs are reproducible and verifiable.

---

## How to run

```bash
python scripts/demo_governed_flow.py
