# README Public Positioning Policy

## Purpose
Ensure the public README remains a conceptual field gateway and never an implementation disclosure surface.

## README Must Explain
- runtime legitimacy as a systems problem
- historical authorization failure under runtime evolution
- why runtime governance emerges
- category boundaries (what this field is and is not)
- public demo purpose and conceptual interpretation

## README Must Not Expose
- operational evolution details
- implementation sequencing
- runtime substrate internals
- orchestration/control-plane mechanics
- replay enforcement semantics
- private runtime architecture

## Content Constraints
- high signal, low operational detail
- conceptual language over implementation language
- no runbook-style operational guidance for private runtime internals
- no topology/flow descriptions that enable reconstruction of enforcement behavior

## Boundary Phrases
Allowed:
- "why runtime legitimacy matters"
- "historical authorization can become stale"

Disallowed:
- "how replay invalidation is implemented"
- "exact capability issuance or enforcement sequence"
- "internal runtime authority mechanics"

## Enforcement
README changes require disclosure check against `DISCLOSURE_DECISION_MATRIX.md` before publication.
