# DETERMA Replay MVP Spec

Status: Canonical v0.1 implementation spec  
Date: 2026-05-10  
Authority: `docs/canonical/DETERMA_REPLAY_MVP_FACTORY_PLAN.md`

---

## 1. Purpose

DETERMA Replay MVP creates a deterministic GitHub pull request replay artifact for AI-generated code mutations.

The MVP does not execute, merge, approve, or mutate repositories.

It observes a pull request diff and produces a replay comment that helps a human reviewer understand:

1. what changed,
2. why it matters,
3. which mutation surface was touched,
4. whether the mutation should be trusted,
5. what action should be taken before merge.

---

## 2. Product Boundary

### In Scope

- pull request diff parsing
- deterministic normalization of changed files
- mutation surface classification
- severity classification
- consequence generation
- trust state classification
- replay integrity signals
- GitHub Markdown replay rendering
- GitHub pull request comment creation/update
- deterministic demo scenarios

### Out of Scope

- repository mutation
- automatic merge
- execution release
- executor implementation
- cloud/IAM/payment/browser adapters
- SaaS dashboard
- user management
- billing
- MCP gateway
- full policy DSL
- Global Action Ledger
- Constitutional Governance runtime

---

## 3. Core Flow

```text
Pull Request Opened or Updated
↓
Diff Collected
↓
Diff Parsed
↓
Mutation Surfaces Classified
↓
Severity Computed
↓
Consequences Generated
↓
Trust State Determined
↓
Replay Integrity Signals Added
↓
DETERMA Mutation Replay Comment Posted or Updated
```

---

## 4. Required Replay Fields

Every replay MUST include:

- Replay ID
- Severity
- Trust State
- Mutation Surface
- Human Summary
- What Changed
- Potential Consequences
- Replay Timeline
- Replay Integrity
- Recommended Action

---

## 5. Determinism Requirement

Given the same PR diff and the same rule set, the system MUST produce the same replay result.

v0.1 MUST be rule-based and deterministic.

LLM-generated classification is out of scope for v0.1 core behavior.

---

## 6. Fail-Closed Requirement

If the diff cannot be parsed or the mutation cannot be explained deterministically, the replay MUST use:

```text
Trust State: UNEXPLAINABLE
```

If the mutation appears operationally risky and cannot be safely interpreted, the replay SHOULD use:

```text
Trust State: BLOCKED
```

---

## 7. GitHub Comment Behavior

The GitHub integration MUST:

- post one DETERMA Replay comment per PR,
- update an existing DETERMA comment when the PR changes,
- avoid duplicate comment spam,
- avoid repository mutation,
- avoid auto-merge,
- fail safely when permissions are missing.

---

## 8. v0.1 Definition of Done

v0.1 is complete when a PR can trigger a DETERMA Replay comment that includes all required fields and correctly handles the required demo scenarios.

Required demos:

1. production rollout changed,
2. CI tests removed,
3. auth middleware changed,
4. business logic changed,
5. documentation-only change.
