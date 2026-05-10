"""Factory scope validator.

Validates that worker changes stay inside the task contract.
"""

from __future__ import annotations

from dataclasses import dataclass
from fnmatch import fnmatch
from typing import Iterable


@dataclass(frozen=True)
class ScopeContract:
    allowed_files: tuple[str, ...]
    forbidden_files: tuple[str, ...]


@dataclass(frozen=True)
class ScopeViolation:
    path: str
    reason: str


@dataclass(frozen=True)
class ScopeValidationResult:
    passed: bool
    violations: list[ScopeViolation]


def validate_scope(changed_files: Iterable[str], contract: ScopeContract) -> ScopeValidationResult:
    """Validate changed files against allowed and forbidden file patterns."""
    violations: list[ScopeViolation] = []

    for path in changed_files:
        normalized = _normalize(path)

        if _matches_any(normalized, contract.forbidden_files):
            violations.append(ScopeViolation(path=normalized, reason="forbidden file modified"))
            continue

        if contract.allowed_files and not _matches_any(normalized, contract.allowed_files):
            violations.append(ScopeViolation(path=normalized, reason="file outside allowed scope"))

    return ScopeValidationResult(passed=not violations, violations=violations)


def _normalize(path: str) -> str:
    return path.strip().replace("\\", "/").lstrip("/")


def _matches_any(path: str, patterns: tuple[str, ...]) -> bool:
    return any(fnmatch(path, pattern) for pattern in patterns)
