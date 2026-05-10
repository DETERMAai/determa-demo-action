"""Deterministic trust-state engine for DETERMA Replay v0.1.

Trust state answers: what should a reviewer do with this mutation before merge?

No network access. No repository mutation. No LLM dependency.
"""

from __future__ import annotations

from typing import Iterable

from .severity_engine import CRITICAL, HIGH, LOW, MEDIUM
from .surface_classifier import (
    AUTH_IAM,
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

TRUSTED = "TRUSTED"
REQUIRES_APPROVAL = "REQUIRES_APPROVAL"
BLOCKED = "BLOCKED"
UNEXPLAINABLE = "UNEXPLAINABLE"

_BLOCKING_PATCH_PATTERNS = (
    "skip tests",
    "disable tests",
    "bypass approval",
    "allow all",
    "chmod 777",
    "verify=false",
    "approval_required: false",
    "required_approval: false",
)

_BLOCKING_SURFACES = {
    SECRET_ACCESS,
}

_APPROVAL_SURFACES = {
    AUTH_IAM,
    CI_CD,
    DATABASE_MIGRATION,
    DEPLOYMENT,
    INFRA_AS_CODE,
    RUNTIME_INFRA,
    TESTS,
    UNKNOWN_OPERATIONAL,
}


def determine_trust_state(
    severity: str,
    surfaces: Iterable[str],
    patches: Iterable[str] | None = None,
    replay_integrity_complete: bool = True,
) -> str:
    """Determine a deterministic trust state.

    Fail-closed rule:
    If replay integrity is incomplete, return UNEXPLAINABLE.
    """
    if not replay_integrity_complete:
        return UNEXPLAINABLE

    surface_set = set(surfaces)
    patch_text = "\n".join(patches or ()).lower()

    if _contains_any(patch_text, _BLOCKING_PATCH_PATTERNS):
        return BLOCKED

    if surface_set & _BLOCKING_SURFACES:
        return BLOCKED

    if severity == CRITICAL:
        return REQUIRES_APPROVAL

    if severity == HIGH:
        if surface_set & _APPROVAL_SURFACES:
            return REQUIRES_APPROVAL
        return REQUIRES_APPROVAL

    if severity == MEDIUM:
        if UNKNOWN_OPERATIONAL in surface_set:
            return UNEXPLAINABLE
        if surface_set & _APPROVAL_SURFACES:
            return REQUIRES_APPROVAL
        return REQUIRES_APPROVAL

    if severity == LOW:
        if surface_set == {DOCUMENTATION} or DOCUMENTATION in surface_set:
            return TRUSTED
        return REQUIRES_APPROVAL

    return UNEXPLAINABLE


def recommended_action_for_trust_state(trust_state: str) -> str:
    """Return the canonical recommended action for a trust state."""
    if trust_state == TRUSTED:
        return "Safe to review normally."
    if trust_state == REQUIRES_APPROVAL:
        return "Human approval required before merge."
    if trust_state == BLOCKED:
        return "Do not merge until the mutation is explicitly reviewed and corrected."
    if trust_state == UNEXPLAINABLE:
        return "Replay could not be reconstructed. Treat this mutation as untrusted."
    return "Unknown trust state. Treat this mutation as untrusted."


def _contains_any(text: str, needles: Iterable[str]) -> bool:
    return any(needle in text for needle in needles)
