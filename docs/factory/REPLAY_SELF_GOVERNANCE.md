# Replay Self Governance

Purpose:

Ensure every Factory-generated PR is validated by DETERMA before merge.

---

## Core Principle

The Factory must never bypass Replay validation.

Every autonomous code change must pass through governed verification.

---

## Validation Flow

```text
Worker PR
→ Replay Analysis
→ Scope Validation
→ Risk Validation
→ Test Validation
→ Merge Decision
```

---

## Replay Checks

### Scope Integrity

Verify:

- only allowed files changed
- no hidden scope expansion
- no unrelated modifications

---

### Operational Risk

Detect:

- auth mutations
- deployment escalation
- secrets exposure
- CI bypass
- rollback removal

---

### Replay Stability

Verify:

- replay output format is stable
- severity classification is deterministic
- replay explanations are consistent

---

## Automatic Block Conditions

Immediately block PR if:

- forbidden files modified
- tests fail
- replay detects critical unsafe mutation
- task scope expands unexpectedly
- replay verification fails

---

## PR Labels

Possible labels:

- replay:verified
- replay:warning
- replay:blocked
- replay:needs-review

---

## Merge Rules

PR may merge only if:

1. replay verification passed
2. required tests passed
3. scope integrity verified
4. no critical replay blocks exist

---

## Factory Principle

Autonomous execution is allowed only when:

```text
execution remains reconstructable and governable
```

Never when:

```text
autonomy becomes opaque
```
