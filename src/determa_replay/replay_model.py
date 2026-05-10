"""Canonical DETERMA Replay model for v0.1.

The replay object is the product-facing artifact.
It must remain simple, deterministic, and GitHub-comment friendly.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ReplayIntegrity:
    """Basic replay integrity signals for v0.1."""

    diff_parsed: bool
    mutation_surface_classified: bool
    deterministic_replay_generated: bool

    def is_complete(self) -> bool:
        return (
            self.diff_parsed
            and self.mutation_surface_classified
            and self.deterministic_replay_generated
        )

    def to_dict(self) -> dict[str, bool]:
        return {
            "diff_parsed": self.diff_parsed,
            "mutation_surface_classified": self.mutation_surface_classified,
            "deterministic_replay_generated": self.deterministic_replay_generated,
        }


@dataclass(frozen=True)
class MutationReplay:
    """Canonical DETERMA Mutation Replay object."""

    replay_id: str
    severity: str
    trust_state: str
    mutation_surfaces: list[str]
    human_summary: str
    what_changed: list[str]
    potential_consequences: list[str]
    replay_timeline: list[str]
    replay_integrity: ReplayIntegrity
    recommended_action: str
    confidence: dict[str, Any] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return a stable JSON-serializable representation."""
        return {
            "replay_id": self.replay_id,
            "severity": self.severity,
            "trust_state": self.trust_state,
            "mutation_surfaces": list(self.mutation_surfaces),
            "human_summary": self.human_summary,
            "what_changed": list(self.what_changed),
            "potential_consequences": list(self.potential_consequences),
            "replay_timeline": list(self.replay_timeline),
            "replay_integrity": self.replay_integrity.to_dict(),
            "recommended_action": self.recommended_action,
            "confidence": dict(self.confidence or {}),
            "metadata": dict(self.metadata),
        }


def build_replay_id(prefix: str, stable_value: str) -> str:
    """Build a readable deterministic replay identifier for v0.1.

    v0.2 should bind this to a canonical diff hash.
    """
    clean_prefix = prefix.strip().upper() or "REPLAY"
    clean_value = "".join(ch for ch in stable_value.strip() if ch.isalnum())[:12]
    if not clean_value:
        clean_value = "LOCAL"
    return f"{clean_prefix}-{clean_value}"
