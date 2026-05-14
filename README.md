# DETERMA

A minimal runtime execution integrity experiment.

---

## What this project demonstrates

DETERMA shows a simple but important idea:

> A system action approved in one runtime state may become invalid if the system changes before execution is repeated.

---

## Core Problem

In automated systems:

- decisions are made based on current system state
- execution may happen later
- the system state can change in between

This creates a mismatch between:
- what was approved
- and what is still valid

---

## What DETERMA does

This project implements a minimal, reproducible flow that demonstrates this mismatch:

1. A change is requested
2. The system captures the current state
3. The change is executed once
4. The system state changes over time (drift)
5. A replay of the same change is attempted
6. The system detects that the state has changed
7. The replay is blocked
8. A proof record is generated explaining why

---

## Key Idea

> Execution is only valid if the system state matches the state at the time of approval.

When the system changes, previous approvals may no longer apply.

---

## Output

Each run produces a simple proof record containing:

- system state at approval time
- system state at replay time
- execution identifier
- authorization reference
- invalidation reason (if applicable)

This allows verification of why an execution was accepted or rejected.

---

## Why this matters

Modern systems (automation, AI agents, distributed services) often assume:

> If something was approved, it remains valid.

This project shows why that assumption can fail in dynamic systems.

---

## How to run

```bash
python scripts/demo_governed_flow.py
