"""Deterministic consequence engine for DETERMA Replay v0.1.

Consequences answer: why does this mutation matter operationally?

No network access. No repository mutation. No LLM dependency.
"""

from __future__ import annotations

from typing import Iterable

from .surface_classifier import (
    AUTH_IAM,
    BUSINESS_LOGIC,
    CI_CD,
    DATABASE_MIGRATION,
    DEPLOYMENT,
    DOCUMENTATION,
    INFRA_AS_CODE,
    RUNTIME_INFRA,
    SECRET_ACCESS,
    TESTS,
    UNKNOWN_OPERATIONAL,
)

_SURFACE_CONSEQUENCES = {
    CI_CD: (
        "Build, test, release, or deployment behavior may change.",
        "Verification gates may be weakened or bypassed before merge.",
    ),
    DEPLOYMENT: (
        "Production rollout behavior may be altered.",
        "Release safety controls may be reduced or bypassed.",
    ),
    RUNTIME_INFRA: (
        "Runtime behavior, isolation, or service startup may change.",
        "Operational availability or deployment reproducibility may be affected.",
    ),
    INFRA_AS_CODE: (
        "Infrastructure resources may be created, deleted, exposed, or reconfigured.",
        "Cloud or environment state may drift from the reviewed intent.",
    ),
    SECRET_ACCESS: (
        "Credential handling or secret exposure risk may change.",
        "Sensitive runtime configuration may be exposed or weakened.",
    ),
    AUTH_IAM: (
        "Authentication, authorization, or permission behavior may change.",
        "Access boundaries may be weakened or expanded.",
    ),
    DATABASE_MIGRATION: (
        "Stored state, schema integrity, or data recoverability may change.",
        "Destructive or irreversible data effects may require explicit review.",
    ),
    BUSINESS_LOGIC: (
        "Product behavior or business rules may change.",
        "Customer-visible outcomes may be affected.",
    ),
    TESTS: (
        "Verification coverage or reviewer confidence may change.",
        "Risk may increase if tests are removed, skipped, or weakened.",
    ),
    DOCUMENTATION: (
        "No direct runtime impact detected from documentation-only paths.",
    ),
    UNKNOWN_OPERATIONAL: (
        "The operational impact could not be classified deterministically.",
        "Human review is required before trusting this mutation.",
    ),
}


def generate_consequences(surfaces: Iterable[str]) -> list[str]:
    """Generate deterministic operational consequences from surfaces."""
    consequences: list[str] = []
    seen: set[str] = set()

    for surface in surfaces:
        for consequence in _SURFACE_CONSEQUENCES.get(surface, _SURFACE_CONSEQUENCES[UNKNOWN_OPERATIONAL]):
            if consequence not in seen:
                seen.add(consequence)
                consequences.append(consequence)

    if not consequences:
        consequences.append(_SURFACE_CONSEQUENCES[UNKNOWN_OPERATIONAL][0])
        consequences.append(_SURFACE_CONSEQUENCES[UNKNOWN_OPERATIONAL][1])

    return consequences
