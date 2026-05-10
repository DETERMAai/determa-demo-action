# DETERMA Replay — Battlecard

## What DETERMA Is

DETERMA is a replay layer for AI-generated code mutations.

It explains:

- what changed,
- why it matters,
- which operational surface was touched,
- whether the mutation should be trusted before merge.

---

## What DETERMA Is Not

DETERMA is not:

- another AI coding assistant,
- another code review chatbot,
- another static security scanner,
- another observability dashboard,
- another generic governance platform.

---

## Core Insight

The core problem is not that AI writes code.

The real problem is that AI-generated mutations can change operational behavior faster than humans can reconstruct intent.

DETERMA exists to reconstruct operational meaning before trust.

---

## Core Product Reflex

```text
Before trusting an AI-generated mutation,
check the DETERMA Replay.
```

---

## Category

```text
AI Mutation Replay
```

---

## Wedge

GitHub-native pull request replay.

---

## Why This Matters

AI-generated pull requests can:

- weaken deployment safety,
- bypass tests,
- expand permissions,
- expose secrets,
- change infrastructure,
- alter production behavior.

Humans often see the code diff.

But they do not immediately see the operational consequences.

---

## DETERMA Replay Output

Every replay explains:

- Severity
- Trust State
- Mutation Surfaces
- Human Summary
- What Changed
- Potential Consequences
- Recommended Action

---

## Initial Competitor Positioning

### Traditional security scanners

Focus:

- vulnerabilities,
- CVEs,
- static analysis.

Gap:

They do not replay operational meaning.

### AI code review tools

Focus:

- style,
- bugs,
- suggestions.

Gap:

They do not create deterministic operational replay artifacts.

### Generic AI governance platforms

Focus:

- policies,
- dashboards,
- orchestration.

Gap:

They start too abstract and too enterprise-heavy.

---

## Why Replay First

Replay is:

- understandable,
- GitHub-native,
- easy to demo,
- easy to distribute,
- easy to screenshot,
- directly connected to merge behavior.

---

## Long-Term Direction

Canonical sequence:

```text
Replay
→ Replay Integrity
→ Approval Gate
→ State Witness
→ Execution Release
→ Governed Code Mutation
→ Global Action Ledger
```
