"""Risk-aware governance decision layer.

Combines runtime risk assessment and governance policy into a required
governance action. This is the first centralized governance decision engine.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from factory.runtime.identity import ActorIdentity
from factory.runtime.policy import GovernancePolicy, PolicyResult, default_governance_policy
from factory.runtime.risk import RiskAssessment, RiskLevel


class GovernanceAction(str, Enum):
    ALLOW_AUTONOMOUS = "ALLOW_AUTONOMOUS"
    REQUIRE_REVIEW = "REQUIRE_REVIEW"
    REQUIRE_SECURITY_REVIEW = "REQUIRE_SECURITY_REVIEW"
    DENY = "DENY"


@dataclass(frozen=True)
class GovernanceDecision:
    action: GovernanceAction
    reason: str
    risk: RiskAssessment
    policy_result: PolicyResult | None = None

    @property
    def allowed(self) -> bool:
        return self.action == GovernanceAction.ALLOW_AUTONOMOUS

    @property
    def requires_human_governance(self) -> bool:
        return self.action in {
            GovernanceAction.REQUIRE_REVIEW,
            GovernanceAction.REQUIRE_SECURITY_REVIEW,
        }

    def to_dict(self) -> dict[str, object]:
        return {
            "action": self.action.value,
            "reason": self.reason,
            "allowed": self.allowed,
            "requires_human_governance": self.requires_human_governance,
            "risk": self.risk.to_dict(),
            "policy_result": self.policy_result.to_dict() if self.policy_result else None,
        }


def decide_governance_action(
    risk: RiskAssessment,
    actor: ActorIdentity | None = None,
    reason: str = "",
    policy: GovernancePolicy | None = None,
) -> GovernanceDecision:
    """Return required governance action for a risk assessment.

    Actor is optional because autonomous decisions may not have a human actor.
    If an actor is supplied, policy is evaluated for the required human decision.
    """
    governance_policy = policy or default_governance_policy()

    if risk.level == RiskLevel.LOW:
        return GovernanceDecision(
            action=GovernanceAction.ALLOW_AUTONOMOUS,
            reason="low risk execution is eligible for autonomous completion",
            risk=risk,
        )

    if risk.level == RiskLevel.MEDIUM:
        if actor is None:
            return GovernanceDecision(
                action=GovernanceAction.REQUIRE_REVIEW,
                reason="medium risk execution requires human review",
                risk=risk,
            )
        policy_result = governance_policy.evaluate_approval(actor=actor, reason=reason)
        if policy_result.allowed:
            return GovernanceDecision(
                action=GovernanceAction.REQUIRE_REVIEW,
                reason="medium risk execution may proceed after reviewer approval",
                risk=risk,
                policy_result=policy_result,
            )
        return GovernanceDecision(
            action=GovernanceAction.DENY,
            reason=policy_result.reason,
            risk=risk,
            policy_result=policy_result,
        )

    if risk.level == RiskLevel.HIGH:
        if actor is None:
            return GovernanceDecision(
                action=GovernanceAction.REQUIRE_SECURITY_REVIEW,
                reason="high risk execution requires security review",
                risk=risk,
            )
        policy_result = governance_policy.evaluate_block_override(actor=actor, reason=reason)
        if policy_result.allowed:
            return GovernanceDecision(
                action=GovernanceAction.REQUIRE_SECURITY_REVIEW,
                reason="high risk execution may proceed after security authority review",
                risk=risk,
                policy_result=policy_result,
            )
        return GovernanceDecision(
            action=GovernanceAction.DENY,
            reason=policy_result.reason,
            risk=risk,
            policy_result=policy_result,
        )

    return GovernanceDecision(
        action=GovernanceAction.DENY,
        reason="critical risk execution is denied by default governance policy",
        risk=risk,
    )
