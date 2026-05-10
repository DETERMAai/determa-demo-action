from src.determa_replay.replay_evaluator import (
    evaluate_consequences,
    evaluate_severity,
    evaluate_surfaces,
    evaluate_trust_state,
    summarize_results,
)


def test_surface_evaluation_passes_for_matching_surfaces():
    result = evaluate_surfaces(["CI/CD"], ["CI/CD"])

    assert result.passed is True



def test_surface_evaluation_fails_for_mismatch():
    result = evaluate_surfaces(["CI/CD"], ["Documentation"])

    assert result.passed is False



def test_severity_evaluation():
    result = evaluate_severity("CRITICAL", "CRITICAL")

    assert result.passed is True



def test_trust_state_evaluation():
    result = evaluate_trust_state("REQUIRES_APPROVAL", "REQUIRES_APPROVAL")

    assert result.passed is True



def test_consequence_evaluation_detects_missing_values():
    result = evaluate_consequences(
        ["Production rollout behavior may be altered."],
        ["Other consequence"],
    )

    assert result.passed is False



def test_summary_detects_failure():
    checks = [
        evaluate_severity("HIGH", "HIGH"),
        evaluate_trust_state("BLOCKED", "TRUSTED"),
    ]

    summary = summarize_results("scenario", checks)

    assert summary.passed is False
