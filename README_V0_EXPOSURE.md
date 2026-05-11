# DETERMA V0

Tiny deterministic replay experiment.

## Goal

Determine whether replay identity remains independently reproducible under hostile operational conditions.

## Repository Contents

- minimal replay kernel
- canonical replay vectors
- replay attack corpus
- drift harness
- local replay CLI

## Run Locally

```bash
npm install
npm run replay
npm run vectors
npm run drift
```

## Protocol

1. Obtain replay artifact
2. Distrust artifact by default
3. Replay independently
4. Compare replay identity
5. Observe:
   - identical replay
   - or observable divergence
6. Only then interpret meaning

## Core Rules

- replay evidence is not semantic truth
- silent replay mutation is constitutional failure
- observable refusal is acceptable
- reproducibility precedes trust
- semantic ignorance is intentional

## Non-Goals

DETERMA v0 does not:

- determine whether code is good
- determine whether merges are safe
- replace human judgment
- provide AI governance
- provide compliance guarantees
- provide semantic truth
- provide autonomous policy enforcement

## Attack Invitation

Please try to create replay corruption without observable replay divergence.

Suggested attacks:

- serialization drift
- timestamp leakage
- randomness injection
- environment contamination
- ordering mutation
- historical replay mutation

## Success Condition

Replay corruption either:

- reproduces identically
- or fails observably

Never silently.
