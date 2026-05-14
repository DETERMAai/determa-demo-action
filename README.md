<div align="center">

# DETERMA

### Runtime Execution Integrity System

---

### Execution validity is not permanent.  
### It depends on current system state.

---

</div>

---

## ⚡ HERO — The Core Problem

Modern automated systems assume:

> If an action was approved once, it remains valid later.

But in reality:

- system state changes continuously
- dependencies evolve
- runtime conditions drift

👉 This creates a gap between **approval time** and **execution time**

---

## 🧠 HERO — The Insight

> An approval is only valid within the system state in which it was created.

If the system changes, the approval may no longer apply.

---

## 🔄 VISUAL FLOW (What the system does)

```text id="f1m8qx"
[ REQUEST ]
     ↓
[ SNAPSHOT STATE ]
     ↓
[ EXECUTION (ONCE) ]
     ↓
[ SYSTEM DRIFT ]
     ↓
[ REPLAY ATTEMPT ]
     ↓
[ STATE MISMATCH DETECTED ]
     ↓
[ EXECUTION BLOCKED ]
     ↓
[ PROOF GENERATED ]
📦 WHAT THIS DEMO SHOWS
governed execution flow
immutable runtime snapshot capture
single-use execution authority
deterministic replay invalidation
verifiable proof artifacts
🔍 INTERACTIVE IDEA (how it feels)

You see:

1. Approval

A system change is approved

2. Execution

Change is executed successfully

3. Time passes

System state evolves

4. Replay attempt

Same action is executed again

5. Block

Execution is stopped

6. Explanation

The system state has changed since approval

📊 WHY THIS MATTERS

In real-world systems:

AI agents execute actions
automation pipelines reuse approvals
infrastructure changes continuously

DETERMA makes a key failure mode visible:

execution assumptions become invalid over time

🧪 RUN LOCALLY
python scripts/demo_governed_flow.py

or:

docker compose up
🧩 SYSTEM COMPONENTS (Minimal View)
runtime/    execution + snapshot + validation
scripts/    demo flows
receipts/   proof artifacts
tests/      replay + drift validation
⚠️ WHAT THIS IS NOT

This project is NOT:

a governance platform
a distributed orchestration system
a security product
a blockchain or consensus layer

It is a minimal runtime experiment that demonstrates execution validity under change.

🎯 CORE PRINCIPLE

Execution must be validated against current system state, not past authorization.

💡 ONE-LINE SUMMARY

DETERMA shows why approvals can silently become invalid when systems change.

<div align="center">
⭐ If this resonates, explore the runtime demo
</div> ```
