# DETERMA

> Execution validity is not permanent. It depends on the system state at the moment of execution.

---

## A minimal runtime proof system for state-aware execution integrity

DETERMA demonstrates a simple but critical failure mode in automated systems:

> An approval made in one system state may become invalid when the system changes before execution is repeated.

---

## ⚡ The Core Insight

Most systems assume:

> “If it was approved once, it is still valid later.”

DETERMA shows why this assumption breaks in dynamic environments.

---

## 🔍 What it does (in one flow)

- A system change is approved
- The current runtime state is recorded
- The change is executed once
- The system state evolves (drift)
- The same execution is attempted again
- The system detects state mismatch
- The replay is blocked
- A verifiable proof is generated

---

## 🧠 Why it matters

In AI systems, automation pipelines, and distributed infrastructure:

- state changes constantly
- approvals are often reused
- execution is assumed to remain valid

DETERMA makes this gap visible and testable.

---

## 📦 What you get

- reproducible governed execution flow
- runtime snapshot capture
- deterministic replay invalidation
- verifiable execution proof artifacts

---

## 🧪 Try it

```bash
python scripts/demo_governed_flow.py
