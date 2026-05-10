"""Replay confidence engine for DETERMA Replay.

Confidence answers:
How reliable is this replay artifact as a basis for human review?

Important:
Confidence is not a safety guarantee.
It is a measured reliability signal derived from replay integrity,
classification clarity, severity, trust state, and optional regression context.
"""

from __future__ import annotations

from dataclasses import dataclass

from .replay_model import MutationReplay
from .trust_engine import BLOCKED, REQUIRES_APPROVAL, TRUSTED, UNEXPLAINABLE
from .surface_classifier import UNKNOWN_OPERATIONAL


@dataclass(frozen=True)
class ReplayConfidence:
    score: int
    band: str
    reasons: list[str]

    def to_dict(self) -> dict[str, object]:
        return {
            "score": self.score,
            "band": self.band,
            "reasons": list(self.reasons),
        }


def compute_replay_confidence(replay: MutationReplay) -> ReplayConfidence:
    """Compute a deterministic replay confidence score from 0 to 100."""
    score = 100
    reasons: list[str] = []

    if not replay.replay_integrity.diff_parsed:
        score -= 40
        reasons.append("diff could not be parsed")

    if not replay.replay_integrity.mutation_surface_classified:
        score -= 30
        reasons.append("mutation surface could not be classified")

    if not replay.replay_integrity.deterministic_replay_generated:
        score -= 30
        reasons.append("deterministic replay was not generated")

    if UNKNOWN_OPERATIONAL in replay.mutation_surfaces:
        score -= 20
        reasons.append("unknown operational surface detected")

    if replay.trust_state == UNEXPLAINABLE:
        score -= 35
        reasons.append("trust state is unexplainable")
    elif replay.trust_state == BLOCKED:
        score -= 15
        reasons.append("mutation is blocked and requires investigation")
    elif replay.trust_state == REQUIRES_APPROVAL:
        score -= 5
        reasons.append("human approval is required")
    elif replay.trust_state == TRUSTED:
        reasons.append("replay is trusted for normal review")
    else:
        score -= 35
        reasons.append("unknown trust state")

    if not replay.what_changed:
        score -= 10
        reasons.append("no concrete changed items were recorded")

    if not replay.potential_consequences:
        score -= 10
        reasons.append("no consequences were generated")

    bounded_score = max(0, min(100, score))
    return ReplayConfidence(
        score=bounded_score,
        band=_band_for_score(bounded_score),
        reasons=reasons or ["no confidence degradation detected"],
    )


def _band_for_score(score: int) -> str:
    if score >= 90:
        return "HIGH"
    if score >= 70:
        return "MEDIUM"
    if score >= 40:
        return "LOW"
    return "UNTRUSTED"
