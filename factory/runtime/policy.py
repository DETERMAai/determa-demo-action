"""Factory governance policy layer.

Centralizes authority decisions so runtime governance does not rely on scattered
role checks. This is the first policy substrate for approval and override rules.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from factory.runtime.identity import ActorIdentity, can_make_approval_decision, can_override_block


class PolicyDecision(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"


@dataclass(frozen=True)
class PolicyResult:
    decision: PolicyDecision
    reason: str

    @property
    def allowed(self) -> bool:
        return self.decision == PolicyDecision.ALLOW

    def to_dict(self) -> dict[str, str | bool]:
        return {
            "decision": self.decision.value,
            "reason": self.reason,
            "allowed": self.allowed,
        }


@dataclass(frozen=True)
class GovernancePolicy:
    """Minimal governance policy for approval and override decisions."""

    require_reason: bool = True

    def evaluate_approval(self, actor: ActorIdentity, reason: str) -> PolicyResult:
        if not can_make_approval_decision(actor):
            return PolicyResult(
                decision=PolicyDecision.DENY,
                reason=f"actor lacks approval authority: {actor.actor_id}",
            )
        if self.require_reason and not reason.strip():
            return PolicyResult(
                decision=PolicyDecision.DENY,
                reason="approval reason is required",
            )
        return PolicyResult(
            decision=PolicyDecision.ALLOW,
            reason=f"approval allowed for {actor.actor_id}",
        )

    def evaluate_block_override(self, actor: ActorIdentity, reason: str) -> PolicyResult:
        if not can_override_block(actor):
            return PolicyResult(
                decision=PolicyDecision.DENY,
                reason=f"actor lacks block override authority: {actor.actor_id}",
            )
        if self.require_reason and not reason.strip():
            return PolicyResult(
                decision=PolicyDecision.DENY,
                reason="override reason is required",
            )
        return PolicyResult(
            decision=PolicyDecision.ALLOW,
            reason=f"block override allowed for {actor.actor_id}",
        )


def default_governance_policy() -> GovernancePolicy:
    return GovernancePolicy(require_reason=True)
