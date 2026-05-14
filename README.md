<div align="center">

# DETERMA Runtime

### Public Governed Execution Demonstration

AI systems can generate actions.  
DETERMA demonstrates how execution authority can govern whether those actions are allowed to mutate real systems.

<p>
  <img src="docs/assets/determa-runtime-hero.svg" width="100%" alt="DETERMA Runtime Hero"/>
</p>

<p>
  <img src="https://img.shields.io/badge/public-demo-success"/>
  <img src="https://img.shields.io/badge/runtime-fail--closed-critical"/>
  <img src="https://img.shields.io/badge/replay-blocked-success"/>
  <img src="https://img.shields.io/badge/status-showcase-blue"/>
</p>

</div>

---

# What This Repository Is

This repository is the public DETERMA showcase.

It demonstrates a narrow governed execution loop where an AI-generated action does not receive direct mutation authority. Instead, the action must pass through an execution boundary before any governed mutation is allowed.

The goal of this repository is to prove the principle:

```text
AI proposes.
Authority governs.
Execution is constrained.
Lineage is recorded.
Replay attempts fail closed.
```

---

# What This Repository Is Not

This public repository is not the full DETERMA authority core.

It intentionally does not contain the full internal protocol specification, private architecture corpus, patent-sensitive material, partner diligence materials, roadmap, or the complete NotebookLM knowledge base.

Those materials are maintained privately and shared selectively with qualified technical, enterprise, investor, and strategic partners.

---

# Run the Governed Execution Demonstration

<div align="center">

| Demo Mode | Command |
|---|---|
| One-command demo | `python scripts/demo_governed_flow.py` |
| Interactive dashboard | `uvicorn runtime.api_shell:app --host 0.0.0.0 --port 8000` |
| Docker runtime | `docker compose -f docker-compose.runtime.yml up` |

</div>

Then open:

```text
http://localhost:8000/demo
```

The demo is designed to show the governed execution flow, including authority checks, lineage recording, and replay blocking behavior.

---

# Governed Execution Flow

```text
AI-generated proposal
        ↓
Execution boundary
        ↓
Authority check
        ↓
Single-use governed capability
        ↓
Constrained execution
        ↓
Replay verification
        ↓
Append-only lineage
```

---

# Why Govern Execution Instead of Prompts

Most AI governance systems focus on:

- prompt rules
- output filtering
- orchestration
- observability
- human approval workflows

Those controls are useful, but they do not fully answer the execution question:

```text
Should this specific machine-generated action be allowed to mutate this specific system now?
```

DETERMA focuses on that boundary.

The public demo shows how a mutation attempt can be intercepted, governed, and verified before execution is treated as legitimate.

---

# Architectural Comparison

| Category | Typical Approach | Limitation | DETERMA Public Demo |
|---|---|---|---|
| Prompt Security | Filter prompts | Cannot govern execution | Demonstrates execution boundary |
| Approval Workflows | Human approval | Approval can be reused or misapplied | Demonstrates bounded authority |
| Observability | Detect after execution | Mutation already happened | Demonstrates pre-execution control |
| Agent Frameworks | Orchestrate actions | Execution trust is assumed | Demonstrates governed execution |
| Audit Logs | Record events | May not block unsafe execution | Demonstrates lineage plus blocking |

---

# Runtime Guarantees Demonstrated

<div align="center">

| Demonstrated Property | Public Demo Status |
|---|---|
| Governed execution ceremony | ✅ Demonstrated |
| Replay blocking behavior | ✅ Demonstrated |
| Append-only lineage concept | ✅ Demonstrated |
| Fail-closed authority check | ✅ Demonstrated |
| Runtime dashboard | ✅ Included |
| Docker runtime path | ✅ Included |

</div>

---

# Public Documentation Map

| Area | Location | Purpose |
|---|---|---|
| Runtime demo | `scripts/demo_governed_flow.py` | One-command governed execution demonstration |
| Runtime implementation | `runtime/` | Public proof implementation |
| API/dashboard shell | `runtime/api_shell.py` | Thin demo and observability layer |
| Public docs | `docs/` | Showcase-level architecture and runtime notes |
| Receipts | `receipts/` | Public demo proof artifacts |

---

# Private Architecture and Partner Review

The full DETERMA architecture is maintained separately from this public showcase.

Selective access may include:

- internal authority core documentation
- deeper execution governance materials
- expanded threat model
- partner diligence package
- private NotebookLM corpus
- implementation roadmap

Access is granted manually after an introductory technical or strategic conversation.

---

# Public Product Statement

DETERMA is building governed execution authority for machine-initiated change.

This repository demonstrates one public proof slice. It should not be interpreted as the full production authority plane or the complete internal system design.

---

# Explore the Runtime

Run the governed execution ceremony:

```bash
python scripts/demo_governed_flow.py
```

Open the runtime dashboard:

```text
http://localhost:8000/demo
```

For deeper technical review, request curated private access from the DETERMA team.
