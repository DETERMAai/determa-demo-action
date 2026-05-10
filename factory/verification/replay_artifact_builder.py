"""Factory replay artifact builder.

Builds a minimal replay artifact from changed files so the Factory Runtime can
self-govern without manually supplied replay JSON.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from src.determa_replay.consequence_engine import generate_consequences
from src.determa_replay.severity_engine import compute_severity
from src.determa_replay.surface_classifier import classify_path
from src.determa_replay.trust_engine import determine_trust_state, recommended_action_for_trust_state


@dataclass(frozen=True)
class FactoryReplayArtifact:
    severity: str
    trust_state: str
    mutation_surfaces: tuple[str, ...]
    changed_files: tuple[str, ...]
    consequences: tuple[str, ...]
    recommended_action: str

    def to_dict(self) -> dict[str, object]:
        return {
            "severity": self.severity,
            "trust_state": self.trust_state,
            "mutation_surfaces": list(self.mutation_surfaces),
            "changed_files": list(self.changed_files),
            "consequences": list(self.consequences),
            "recommended_action": self.recommended_action,
        }


def build_factory_replay_artifact(changed_files: Iterable[str]) -> FactoryReplayArtifact:
    """Build a deterministic replay artifact from changed file paths."""
    files = tuple(changed_files)
    surfaces = _aggregate_surfaces(files)
    severity = compute_severity(surfaces)
    consequences = tuple(generate_consequences(surfaces))
    trust_state = determine_trust_state(
        severity=severity,
        surfaces=surfaces,
        replay_integrity_complete=bool(files) and bool(surfaces),
    )

    return FactoryReplayArtifact(
        severity=severity,
        trust_state=trust_state,
        mutation_surfaces=tuple(surfaces),
        changed_files=files,
        consequences=consequences,
        recommended_action=recommended_action_for_trust_state(trust_state),
    )


def _aggregate_surfaces(changed_files: Iterable[str]) -> list[str]:
    surfaces: list[str] = []
    seen: set[str] = set()

    for path in changed_files:
        for surface in classify_path(path):
            if surface not in seen:
                seen.add(surface)
                surfaces.append(surface)

    return surfaces
