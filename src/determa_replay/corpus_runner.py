"""Replay regression runner for DETERMA Replay.

Runs replay evaluation against corpus scenarios.
"""

from __future__ import annotations

import json
from pathlib import Path

from .github_comment import build_replay_from_diff
from .replay_evaluator import (
    ReplayEvaluation,
    evaluate_consequences,
    evaluate_severity,
    evaluate_surfaces,
    evaluate_trust_state,
    summarize_results,
)

CORPUS_ROOT = Path("examples/corpus")


def run_corpus(root: Path = CORPUS_ROOT) -> list[ReplayEvaluation]:
    """Run replay evaluation across the mutation corpus."""
    evaluations: list[ReplayEvaluation] = []

    for scenario_dir in sorted(root.rglob("mutation.patch")):
        scenario_path = scenario_dir.parent
        evaluations.append(run_scenario(scenario_path))

    return evaluations


def run_scenario(scenario_path: Path) -> ReplayEvaluation:
    """Run replay evaluation for a single scenario."""
    diff_text = _read_text(scenario_path / "mutation.patch")

    replay = build_replay_from_diff(
        diff_text=diff_text,
        stable_value=str(scenario_path),
    )

    expected_surfaces = _read_json(scenario_path / "expected_surfaces.json")
    expected_severity = _read_json(scenario_path / "expected_severity.json")["severity"]
    expected_trust_state = _read_json(scenario_path / "expected_trust_state.json")["trust_state"]
    expected_consequences = _read_json(scenario_path / "expected_consequences.json")

    checks = [
        evaluate_surfaces(expected_surfaces, replay.mutation_surfaces),
        evaluate_severity(expected_severity, replay.severity),
        evaluate_trust_state(expected_trust_state, replay.trust_state),
        evaluate_consequences(expected_consequences, replay.potential_consequences),
    ]

    return summarize_results(str(scenario_path), checks)


def render_report(evaluations: list[ReplayEvaluation]) -> str:
    """Render a deterministic regression report."""
    lines: list[str] = []

    passed = sum(1 for evaluation in evaluations if evaluation.passed)
    failed = len(evaluations) - passed

    lines.append("# DETERMA Replay Regression Report")
    lines.append("")
    lines.append(f"Total Scenarios: {len(evaluations)}")
    lines.append(f"Passed: {passed}")
    lines.append(f"Failed: {failed}")
    lines.append("")

    for evaluation in evaluations:
        status = "PASS" if evaluation.passed else "FAIL"
        lines.append(f"## {status} — {evaluation.scenario}")

        for check in evaluation.checks:
            marker = "✓" if check.passed else "✗"
            lines.append(f"- {marker} {check.name}")

            if not check.passed:
                lines.append(f"  expected: {check.expected}")
                lines.append(f"  actual: {check.actual}")

        lines.append("")

    return "\n".join(lines).strip() + "\n"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))
