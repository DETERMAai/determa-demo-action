"""Deterministic severity engine for DETERMA Replay v0.1.

Severity answers: how operationally risky is this AI-generated mutation?

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

LOW = "LOW"
MEDIUM = "MEDIUM"
HIGH = "HIGH"
CRITICAL = "CRITICAL"

_SEVERITY_RANK = {
    LOW: 1,
    MEDIUM: 2,
    HIGH: 3,
    CRITICAL: 4,
}

_SURFACE_SEVERITY = {
    SECRET_ACCESS: CRITICAL,
    AUTH_IAM: CRITICAL,
    DEPLOYMENT: CRITICAL,
    DATABASE_MIGRATION: HIGH,
    INFRA_AS_CODE: HIGH,
    RUNTIME_INFRA: HIGH,
    CI_CD: HIGH,
    TESTS: MEDIUM,
    BUSINESS_LOGIC: MEDIUM,
    UNKNOWN_OPERATIONAL: MEDIUM,
    DOCUMENTATION: LOW,
}

_CRITICAL_KEYWORDS = (
    "production",
    "prod",
    "rollout",
    "deploy",
    "permission",
    "permissions",
    "role",
    "roles",
    "secret",
    "token",
    "password",
    "private_key",
    "api_key",
)

_HIGH_KEYWORDS = (
    "disable",
    "skip",
    "bypass",
    "delete",
    "drop table",
    "force",
    "allow all",
    "wildcard",
)


def compute_severity(surfaces: Iterable[str], patches: Iterable[str] | None = None) -> str:
    """Compute deterministic severity from mutation surfaces and optional patch text."""
    surface_list = list(surfaces)
    patch_text = "\n".join(patches or ()).lower()

    severity = LOW

    for surface in surface_list:
        severity = _max_severity(severity, _SURFACE_SEVERITY.get(surface, MEDIUM))

    if _contains_any(patch_text, _CRITICAL_KEYWORDS):
        if any(surface in surface_list for surface in {CI_CD, DEPLOYMENT, SECRET_ACCESS, AUTH_IAM}):
            severity = _max_severity(severity, CRITICAL)

    if _contains_any(patch_text, _HIGH_KEYWORDS):
        severity = _max_severity(severity, HIGH)

    return severity


def _max_severity(left: str, right: str) -> str:
    return left if _SEVERITY_RANK[left] >= _SEVERITY_RANK[right] else right


def _contains_any(text: str, needles: Iterable[str]) -> bool:
    return any(needle in text for needle in needles)
