"""GitHub Markdown renderer for DETERMA Replay v0.1.

The renderer converts a MutationReplay object into a stable,
readable GitHub comment.
"""

from __future__ import annotations

from .replay_model import MutationReplay


CHECK_TRUE = "✓"
CHECK_FALSE = "✗"


def render_markdown(replay: MutationReplay) -> str:
    """Render a canonical GitHub-ready DETERMA Replay comment."""
    lines: list[str] = []

    lines.append("# DETERMA Mutation Replay")
    lines.append("")

    lines.extend(_section("Replay ID", replay.replay_id))
    lines.extend(_section("Severity", replay.severity))
    lines.extend(_section("Trust State", replay.trust_state))
    lines.extend(_section("Mutation Surface", " / ".join(replay.mutation_surfaces)))
    lines.extend(_section("Human Summary", replay.human_summary))

    lines.append("## What Changed")
    lines.extend(_bullet_list(replay.what_changed))
    lines.append("")

    lines.append("## Potential Consequences")
    lines.extend(_bullet_list(replay.potential_consequences))
    lines.append("")

    lines.append("## Replay Timeline")
    lines.extend(_bullet_list(replay.replay_timeline))
    lines.append("")

    lines.append("## Replay Integrity")
    lines.extend(_integrity_lines(replay))
    lines.append("")

    lines.extend(_section("Recommended Action", replay.recommended_action))

    return "\n".join(lines).strip() + "\n"


def _section(title: str, value: str) -> list[str]:
    return [f"## {title}", value, ""]


def _bullet_list(values: list[str]) -> list[str]:
    if not values:
        return ["- none"]
    return [f"- {value}" for value in values]


def _integrity_lines(replay: MutationReplay) -> list[str]:
    integrity = replay.replay_integrity
    return [
        f"{_check(integrity.diff_parsed)} diff parsed",
        f"{_check(integrity.mutation_surface_classified)} mutation surface classified",
        f"{_check(integrity.deterministic_replay_generated)} deterministic replay generated",
    ]


def _check(value: bool) -> str:
    return CHECK_TRUE if value else CHECK_FALSE
