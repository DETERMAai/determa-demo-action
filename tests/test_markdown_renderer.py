from src.determa_replay.markdown_renderer import render_markdown
from src.determa_replay.replay_model import (
    MutationReplay,
    ReplayIntegrity,
    build_replay_id,
)


def _sample_replay() -> MutationReplay:
    return MutationReplay(
        replay_id=build_replay_id("replay", "deploy-workflow"),
        severity="CRITICAL",
        trust_state="REQUIRES_APPROVAL",
        mutation_surfaces=["CI/CD", "Deployment Infrastructure"],
        human_summary="AI-generated mutation changed deployment rollout behavior.",
        what_changed=[
            "Deployment rollout threshold changed from 10% to 100%.",
            "Release workflow conditions were modified.",
        ],
        potential_consequences=[
            "Production rollout behavior may be altered.",
            "Release safety controls may be reduced or bypassed.",
        ],
        replay_timeline=[
            "Diff received",
            "Files classified",
            "Risk evaluated",
            "Trust state determined",
        ],
        replay_integrity=ReplayIntegrity(
            diff_parsed=True,
            mutation_surface_classified=True,
            deterministic_replay_generated=True,
        ),
        recommended_action="Human approval required before merge.",
    )


def test_render_markdown_contains_required_sections():
    markdown = render_markdown(_sample_replay())

    assert "# DETERMA Mutation Replay" in markdown
    assert "## Replay ID" in markdown
    assert "## Severity" in markdown
    assert "## Trust State" in markdown
    assert "## Mutation Surface" in markdown
    assert "## Human Summary" in markdown
    assert "## What Changed" in markdown
    assert "## Potential Consequences" in markdown
    assert "## Replay Timeline" in markdown
    assert "## Replay Integrity" in markdown
    assert "## Recommended Action" in markdown


def test_render_markdown_contains_integrity_checks():
    markdown = render_markdown(_sample_replay())

    assert "✓ diff parsed" in markdown
    assert "✓ mutation surface classified" in markdown
    assert "✓ deterministic replay generated" in markdown


def test_render_markdown_renders_surfaces_inline():
    markdown = render_markdown(_sample_replay())

    assert "CI/CD / Deployment Infrastructure" in markdown


def test_render_markdown_renders_bullets():
    markdown = render_markdown(_sample_replay())

    assert "- Deployment rollout threshold changed from 10% to 100%." in markdown
    assert "- Production rollout behavior may be altered." in markdown


def test_render_markdown_is_deterministic():
    replay = _sample_replay()

    first = render_markdown(replay)
    second = render_markdown(replay)

    assert first == second


def test_build_replay_id_is_stable_and_readable():
    replay_id = build_replay_id("replay", "deploy-workflow")

    assert replay_id == "REPLAY-deploywork"


def test_render_markdown_has_trailing_newline():
    markdown = render_markdown(_sample_replay())

    assert markdown.endswith("\n")
