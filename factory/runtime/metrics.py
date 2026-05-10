"""Factory runtime metrics.

Computes simple operational metrics from persisted runtime events.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RuntimeMetrics:
    total_events: int
    passed_events: int
    blocked_events: int
    pass_rate: float
    blocked_rate: float
    severity_distribution: dict[str, int]
    trust_state_distribution: dict[str, int]

    def to_dict(self) -> dict[str, object]:
        return {
            "total_events": self.total_events,
            "passed_events": self.passed_events,
            "blocked_events": self.blocked_events,
            "pass_rate": self.pass_rate,
            "blocked_rate": self.blocked_rate,
            "severity_distribution": dict(self.severity_distribution),
            "trust_state_distribution": dict(self.trust_state_distribution),
        }


def compute_runtime_metrics(events: list[dict[str, Any]]) -> RuntimeMetrics:
    """Compute deterministic runtime metrics from persisted events."""
    total = len(events)
    passed = sum(1 for event in events if event.get("outcome") == "PASSED")
    blocked = sum(1 for event in events if event.get("outcome") == "BLOCKED")

    severity_counter: Counter[str] = Counter()
    trust_counter: Counter[str] = Counter()

    for event in events:
        replay = event.get("replay") or {}
        if replay:
            severity_counter[str(replay.get("severity", "unknown"))] += 1
            trust_counter[str(replay.get("trust_state", "unknown"))] += 1

    return RuntimeMetrics(
        total_events=total,
        passed_events=passed,
        blocked_events=blocked,
        pass_rate=_rate(passed, total),
        blocked_rate=_rate(blocked, total),
        severity_distribution=dict(sorted(severity_counter.items())),
        trust_state_distribution=dict(sorted(trust_counter.items())),
    )


def render_runtime_metrics(metrics: RuntimeMetrics) -> str:
    """Render runtime metrics as deterministic Markdown."""
    lines: list[str] = []

    lines.append("# DETERMA Factory Runtime Metrics")
    lines.append("")
    lines.append(f"Total Events: {metrics.total_events}")
    lines.append(f"Passed Events: {metrics.passed_events}")
    lines.append(f"Blocked Events: {metrics.blocked_events}")
    lines.append(f"Pass Rate: {metrics.pass_rate:.2%}")
    lines.append(f"Blocked Rate: {metrics.blocked_rate:.2%}")
    lines.append("")

    lines.append("## Severity Distribution")
    lines.extend(_render_distribution(metrics.severity_distribution))
    lines.append("")

    lines.append("## Trust State Distribution")
    lines.extend(_render_distribution(metrics.trust_state_distribution))
    lines.append("")

    return "\n".join(lines).strip() + "\n"


def _rate(value: int, total: int) -> float:
    if total == 0:
        return 0.0
    return value / total


def _render_distribution(values: dict[str, int]) -> list[str]:
    if not values:
        return ["- none"]
    return [f"- {key}: {value}" for key, value in values.items()]
