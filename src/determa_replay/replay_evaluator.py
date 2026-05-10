"""Replay evaluation utilities for DETERMA Replay.

Evaluates replay outputs against expected corpus artifacts.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EvaluationResult:
    name: str
    passed: bool
    expected: object
    actual: object


@dataclass(frozen=True)
class ReplayEvaluation:
    scenario: str
    passed: bool
    checks: list[EvaluationResult]


def evaluate_surfaces(expected: list[str], actual: list[str]) -> EvaluationResult:
    return EvaluationResult(
        name="surfaces",
        passed=sorted(expected) == sorted(actual),
        expected=expected,
        actual=actual,
    )


def evaluate_severity(expected: str, actual: str) -> EvaluationResult:
    return EvaluationResult(
        name="severity",
        passed=expected == actual,
        expected=expected,
        actual=actual,
    )


def evaluate_trust_state(expected: str, actual: str) -> EvaluationResult:
    return EvaluationResult(
        name="trust_state",
        passed=expected == actual,
        expected=expected,
        actual=actual,
    )


def evaluate_consequences(expected: list[str], actual: list[str]) -> EvaluationResult:
    missing = [value for value in expected if value not in actual]
    return EvaluationResult(
        name="consequences",
        passed=not missing,
        expected=expected,
        actual=actual,
    )


def summarize_results(scenario: str, checks: list[EvaluationResult]) -> ReplayEvaluation:
    return ReplayEvaluation(
        scenario=scenario,
        passed=all(check.passed for check in checks),
        checks=checks,
    )
