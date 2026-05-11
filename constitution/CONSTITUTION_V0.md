# DETERMA Constitution v0

Status: Frozen for empirical replay testing.

## Purpose

DETERMA v0 is a tiny deterministic replay experiment.

It tests whether replay identity can be independently reproduced under hostile operational conditions.

## Frozen Surfaces

The following are frozen for v0:

- replay artifact schema
- equivalence law
- admissibility semantics
- replay hash semantics
- stable serialization semantics
- failure visibility semantics

## Allowed During Freeze

The following may evolve without changing the constitution:

- attack corpus
- drift harness
- CLI ergonomics
- README clarity
- packaging
- external reproducibility instructions

## Forbidden During Freeze

The following are out of scope for v0:

- AI interpretation
- policy reasoning
- risk scoring
- governance semantics
- semantic equivalence
- approximate replay matching
- automatic drift healing

## Core Rule

Equivalent replay inputs must produce equivalent replay evidence.

Silent replay mutation is constitutional failure.

Observable refusal is acceptable.

## Non-Goals

DETERMA v0 does not prove code quality, merge safety, policy correctness, compliance, malicious intent, or semantic truth.

It only tests deterministic replay evidence reproduction.
