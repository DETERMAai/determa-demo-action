"""Replay lineage model for DETERMA Replay.

Lineage answers:
How did operational trust evolve across pull request mutations?

v0.1 scope:
- compare two replay artifacts
- identify severity/trust/confidence changes
- render deterministic lineage summaries

No persistence. No execution authority. No repository mutation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .replay_model import MutationReplay


@dataclass(frozen=True)
class ReplayLineageDelta:
    previous_replay_id: str
    current_replay_id: str
    severity_changed: bool
    previous_severity: str
    current_severity: str
    trust_state_changed: bool
    previous_trust_state: str
    current_trust_state: str
    confidence_changed: bool
    previous_confidence_score: int | None
    current_confidence_score: int | None
    added_surfaces: list[str]
    removed_surfaces: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "previous_replay_id": self.previous_replay_id,
            "current_replay_id": self.current_replay_id,
            "severity_changed": self.severity_changed,
            "previous_severity": self.previous_severity,
            "current_severity": self.current_severity,
            "trust_state_changed": self.trust_state_changed,
            "previous_trust_state": self.previous_trust_state,
            "current_trust_state": self.current_trust_state,
            "confidence_changed": self.confidence_changed,
            "previous_confidence_score": self.previous_confidence_score,
            "current_confidence_score": self.current_confidence_score,
            "added_surfaces": list(self.added_surfaces),
            "removed_surfaces": list(self.removed_surfaces),
        }


def compare_replays(previous: MutationReplay, current: MutationReplay) -> ReplayLineageDelta:
    """Compare two replay artifacts and return a deterministic lineage delta."""
    previous_confidence = _confidence_score(previous)
    current_confidence = _confidence_score(current)

    previous_surfaces = set(previous.mutation_surfaces)
    current_surfaces = set(current.mutation_surfaces)

    return ReplayLineageDelta(
        previous_replay_id=previous.replay_id,
        current_replay_id=current.replay_id,
        severity_changed=previous.severity != current.severity,
        previous_severity=previous.severity,
        current_severity=current.severity,
        trust_state_changed=previous.trust_state != current.trust_state,
        previous_trust_state=previous.trust_state,
        current_trust_state=current.trust_state,
        confidence_changed=previous_confidence != current_confidence,
        previous_confidence_score=previous_confidence,
        current_confidence_score=current_confidence,
        added_surfaces=sorted(current_surfaces - previous_surfaces),
        removed_surfaces=sorted(previous_surfaces - current_surfaces),
    )


def render_lineage_delta(delta: ReplayLineageDelta) -> str:
    """Render a deterministic lineage delta summary."""
    lines: list[str] = []

    lines.append("# DETERMA Replay Lineage Delta")
    lines.append("")
    lines.append(f"Previous Replay: {delta.previous_replay_id}")
    lines.append(f"Current Replay: {delta.current_replay_id}")
    lines.append("")

    lines.append("## Severity")
    lines.append(f"{delta.previous_severity} → {delta.current_severity}")
    lines.append("")

    lines.append("## Trust State")
    lines.append(f"{delta.previous_trust_state} → {delta.current_trust_state}")
    lines.append("")

    lines.append("## Confidence")
    lines.append(f"{delta.previous_confidence_score} → {delta.current_confidence_score}")
    lines.append("")

    lines.append("## Added Surfaces")
    lines.extend(_render_list(delta.added_surfaces))
    lines.append("")

    lines.append("## Removed Surfaces")
    lines.extend(_render_list(delta.removed_surfaces))
    lines.append("")

    return "\n".join(lines).strip() + "\n"


def _confidence_score(replay: MutationReplay) -> int | None:
    if not replay.confidence:
        return None
    score = replay.confidence.get("score")
    return int(score) if isinstance(score, int) else None


def _render_list(values: list[str]) -> list[str]:
    if not values:
        return ["- none"]
    return [f"- {value}" for value in values]
