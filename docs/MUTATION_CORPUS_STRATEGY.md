# DETERMA Replay — Mutation Corpus Strategy

## Purpose

Define the canonical mutation corpus strategy for DETERMA Replay.

The mutation corpus exists to pressure-test replay determinism,
operational understanding, and trust-state quality.

---

# Strategic Principle

The long-term value of DETERMA is not only replay rendering.

The deeper value is:

```text
canonical operational understanding
of AI-generated mutations
```

The mutation corpus is the foundation of that capability.

---

# Why The Corpus Matters

Most systems evaluate:

- syntax,
- style,
- vulnerabilities,
- static analysis.

DETERMA must evaluate:

```text
operational mutation meaning
```

That requires replay evaluation datasets.

---

# Corpus Goals

The corpus should:

1. stress replay determinism
2. expose classifier weaknesses
3. expose trust-state weaknesses
4. expose operational blind spots
5. validate replay stability
6. support replay regression testing
7. support future replay confidence scoring

---

# Corpus Structure

```text
examples/corpus/
```

Each mutation scenario should contain:

```text
mutation.patch
expected_surfaces.json
expected_severity.json
expected_trust_state.json
expected_consequences.json
```

---

# Initial Corpus Categories

```text
deployment/
auth/
secrets/
infra/
runtime/
business_logic/
tests/
supply_chain/
observability/
data_integrity/
```

---

# Example Mutation Types

## Deployment

- rollout expansion
- region changes
- deployment gate removal
- rollback disablement

---

## Authentication / IAM

- wildcard permissions
- auth bypass
- session validation weakening
- role inheritance expansion

---

## Secrets

- plaintext credential exposure
- secret source replacement
- environment leakage

---

## Runtime

- startup script mutation
- container privilege escalation
- runtime isolation weakening

---

## Tests

- verification bypass
- skipped tests
- weakened assertions
- coverage reduction

---

# Corpus Rules

## Must remain deterministic

Expected replay outputs must remain stable.

---

## Must remain operational

Mutations should represent real operational behavior.

---

## Must avoid toy examples

The corpus should evolve toward realistic repository mutations.

---

## Must support replay regression

Replay drift should be detectable automatically.

---

# Replay Regression Loop

```text
Generate Mutation
→ Run Replay
→ Compare Expected Outputs
→ Detect Drift
→ Improve Replay Logic
→ Re-run Corpus
```

---

# Factory Responsibilities

The Factory should autonomously:

1. generate synthetic mutations
2. generate replay expectations
3. detect replay drift
4. harden classifiers
5. expand operational surfaces
6. add new mutation categories
7. validate replay determinism
8. generate replay regression reports

---

# Long-Term Strategic Value

The corpus eventually becomes:

```text
operational mutation intelligence infrastructure
```

and potentially:

```text
the canonical evaluation dataset
for AI-generated operational mutations
```
