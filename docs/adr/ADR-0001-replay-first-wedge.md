# ADR-0001 — Replay First Wedge

Status: Accepted  
Date: 2026-05-10

---

## Context

DETERMA has a broader authority architecture covering governed execution, state witness, execution release, constrained executors, immutable lineage, and future global action ledger behavior.

However, building the full authority plane first creates product, market, and implementation risk.

The market-facing entry point must be small, understandable, and demonstrable.

---

## Decision

DETERMA will begin with a GitHub-native Replay wedge.

The first product is:

```text
DETERMA Replay for AI-generated Pull Requests
```

The first implementation will produce deterministic Mutation Replay comments on GitHub pull requests.

It will explain:

- what changed,
- why it matters,
- which mutation surface was touched,
- whether the mutation should be trusted,
- what action a human reviewer should take.

---

## Rationale

Replay is the fastest path from deep architecture to visible product value.

Replay creates a human review reflex before DETERMA expands into approval, witness, release, and execution authority.

The product should first make engineers uncomfortable merging AI-generated code without replayability.

---

## Consequences

### Positive

- Faster MVP delivery
- Clearer demo
- Stronger market readability
- Lower implementation risk
- Better GitHub-native distribution
- Direct bridge to future authority features

### Negative

- v0.1 does not prove the full authority plane
- v0.1 does not enforce execution release
- v0.1 does not include the Global Action Ledger
- v0.1 may look lighter than the full DETERMA vision

These tradeoffs are accepted.

---

## Explicit Non-Goals

This ADR rejects starting with:

- universal agent governance,
- full MCP gateway,
- enterprise dashboard,
- production executor,
- full constitutional governance,
- full global action ledger.

---

## Canonical Sequence

```text
Replay
→ Replay Integrity
→ Approval Gate
→ State Witness
→ Execution Release
→ Governed Code Mutation
→ Global Action Ledger
```

Any work that does not strengthen the first GitHub-native Replay loop should be deferred.
