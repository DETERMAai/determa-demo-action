"""Replay regression runner for DETERMA Replay.

Runs replay evaluation against corpus scenarios.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .drift_analyzer import analyze_drift, render_drift_summary
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
DEFAULT_REPORT_PATH = Path("reports/replay_regression/latest.md")


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

    lines.append(render_drift_summary(analyze_drift(evaluations)).strip())
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


def write_report(report: str, output_path: Path = DEFAULT_REPORT_PATH) -> Path:
    """Write a regression report to disk and return the output path."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")
    return output_path


def has_failures(evaluations: list[ReplayEvaluation]) -> bool:
    """Return True when at least one corpus scenario failed."""
    return any(not evaluation.passed for evaluation in evaluations)


def main(argv: list[str] | None = None) -> int:
    """Run the corpus regression CLI."""
    parser = argparse.ArgumentParser(description="Run DETERMA Replay corpus regression.")
    parser.add_argument("--root", default=str(CORPUS_ROOT), help="Path to corpus root")
    parser.add_argument("--report", default=str(DEFAULT_REPORT_PATH), help="Report output path")
    parser.add_argument("--no-write", action="store_true", help="Print report only")
    args = parser.parse_args(argv)

    evaluations = run_corpus(Path(args.root))
    report = render_report(evaluations)

    if args.no_write:
        print(report, end="")
    else:
        output_path = write_report(report, Path(args.report))
        print(f"DETERMA Replay regression report written to {output_path}")

    return 1 if has_failures(evaluations) else 0


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
