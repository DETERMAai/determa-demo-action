"""Replay drift analysis for DETERMA Replay.

Drift analysis turns raw regression failures into operational insight:
- which scenario categories are degrading
- which check types are unstable
- where replay semantics need hardening
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

from .replay_evaluator import ReplayEvaluation


@dataclass(frozen=True)
class DriftSummary:
    total_scenarios: int
    passed_scenarios: int
    failed_scenarios: int
    failures_by_check: dict[str, int]
    failures_by_category: dict[str, int]

    @property
    def pass_rate(self) -> float:
        if self.total_scenarios == 0:
            return 1.0
        return self.passed_scenarios / self.total_scenarios


def analyze_drift(evaluations: list[ReplayEvaluation]) -> DriftSummary:
    """Analyze regression drift from replay evaluations."""
    failures_by_check: Counter[str] = Counter()
    failures_by_category: Counter[str] = Counter()

    for evaluation in evaluations:
        if evaluation.passed:
            continue

        category = _category_from_scenario(evaluation.scenario)
        failures_by_category[category] += 1

        for check in evaluation.checks:
            if not check.passed:
                failures_by_check[check.name] += 1

    total = len(evaluations)
    failed = sum(1 for evaluation in evaluations if not evaluation.passed)
    passed = total - failed

    return DriftSummary(
        total_scenarios=total,
        passed_scenarios=passed,
        failed_scenarios=failed,
        failures_by_check=dict(sorted(failures_by_check.items())),
        failures_by_category=dict(sorted(failures_by_category.items())),
    )


def render_drift_summary(summary: DriftSummary) -> str:
    """Render a deterministic drift summary."""
    lines: list[str] = []

    lines.append("# DETERMA Replay Drift Summary")
    lines.append("")
    lines.append(f"Total Scenarios: {summary.total_scenarios}")
    lines.append(f"Passed: {summary.passed_scenarios}")
    lines.append(f"Failed: {summary.failed_scenarios}")
    lines.append(f"Pass Rate: {summary.pass_rate:.2%}")
    lines.append("")

    lines.append("## Failures by Check")
    lines.extend(_render_counter(summary.failures_by_check))
    lines.append("")

    lines.append("## Failures by Category")
    lines.extend(_render_counter(summary.failures_by_category))
    lines.append("")

    return "\n".join(lines).strip() + "\n"


def _category_from_scenario(scenario: str) -> str:
    parts = Path(scenario).parts
    if "corpus" in parts:
        index = parts.index("corpus")
        if len(parts) > index + 1:
            return parts[index + 1]
    return "unknown"


def _render_counter(values: dict[str, int]) -> list[str]:
    if not values:
        return ["- none"]
    return [f"- {key}: {value}" for key, value in values.items()]
