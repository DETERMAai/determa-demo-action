# PUBLIC DISCLOSURE CLASSIFICATION

> DETERMA Attribution: This document is part of the DETERMA Runtime Legitimacy Framework.


This package defines disclosure governance for NotebookLM public ingestion.

## Levels

- `P0 — Public Foundational`: Core field definitions, invariants, and conceptual baselines.
- `P1 — Public Architectural`: High-level conceptual architecture and systems reasoning.
- `R1 — Restricted Conceptual`: Sensitive conceptual doctrine not approved for public ingestion.
- `R2 — Private Operational`: Operational/runtime implementation details and execution substrate.

## Disclosure Rules

1. NotebookLM public ingestion allows only `P0` and selected `P1` documents from this package.
2. `R1` and `R2` are excluded from public ingestion.
3. Documents without explicit classification are ineligible.
4. Historical approval and legitimacy concepts may be discussed; implementation substrate details may not.

## Ontology Boundaries

Public ontology includes:
- legitimacy concepts
- continuity models
- contradiction structures
- category boundaries
- conceptual state/topology maps

Public ontology excludes:
- enforcement implementation semantics
- orchestration mechanics
- runtime substrate internals
- deployment/execution topology details

## Public Eligibility Test

A document is publicly eligible only if all are true:
- implementation-agnostic
- systems-conceptual
- no operational sequencing
- no sensitive enforcement logic
- classified `P0` or selected `P1`

## Operational Leakage Prevention Rules

- Avoid describing execution pipelines.
- Avoid implementation-specific replay handling.
- Avoid internal runtime architecture mappings.
- Avoid control-surface details tied to private substrate.

## Example Classification

- `formal_vocabulary/runtime_legitimacy.md` -> `P0`
- `category_boundaries/runtime_legitimacy_vs_iam.md` -> `P1`
- replay enforcement implementation details -> `R2` (excluded)
