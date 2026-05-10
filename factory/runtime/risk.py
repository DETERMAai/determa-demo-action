"""Factory governance risk engine.

Computes governance-aware runtime risk classification using replay metadata,
execution context, and governance state.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class RiskSignal:
    name: str
    weight: int
    reason: str

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "weight": self.weight,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class RiskAssessment:
    score: int
    level: RiskLevel
    signals: tuple[RiskSignal, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "score": self.score,
            "level": self.level.value,
            "signals": [signal.to_dict() for signal in self.signals],
        }


AUTH_KEYWORDS = ("auth", "permission", "identity", "token")
DEPLOY_KEYWORDS = ("deploy", "release", "pipeline", "runtime")
SECRET_KEYWORDS = ("secret", "credential", "key", "vault")
POLICY_KEYWORDS = ("policy", "governance")


def assess_runtime_risk(
    changed_files: tuple[str, ...],
    replay_severity: str,
    trust_state: str,
    pending_approvals: int = 0,
    blocked_events: int = 0,
    orphaned_sessions: int = 0,
    override_attempted: bool = False,
    policy_violations: int = 0,
) -> RiskAssessment:
    """Compute governance runtime risk assessment."""
    signals: list[RiskSignal] = []

    severity = replay_severity.upper()
    trust = trust_state.upper()

    if severity == "HIGH":
        signals.append(RiskSignal("severity_high", 30, "high replay severity"))

    if trust != "TRUSTED":
        signals.append(RiskSignal("untrusted_state", 40, f"trust state: {trust}"))

    for path in changed_files:
        normalized = path.lower()

        if any(keyword in normalized for keyword in AUTH_KEYWORDS):
            signals.append(RiskSignal("auth_surface", 25, f"auth-related file: {path}"))

        if any(keyword in normalized for keyword in DEPLOY_KEYWORDS):
            signals.append(RiskSignal("deployment_surface", 25, f"deployment-related file: {path}"))

        if any(keyword in normalized for keyword in SECRET_KEYWORDS):
            signals.append(RiskSignal("secret_surface", 50, f"secret-related file: {path}"))

        if any(keyword in normalized for keyword in POLICY_KEYWORDS):
            signals.append(RiskSignal("policy_surface", 20, f"policy-related file: {path}"))

    if pending_approvals > 0:
        signals.append(RiskSignal("pending_approvals", 10 * pending_approvals, "pending governance approvals exist"))

    if blocked_events > 0:
        signals.append(RiskSignal("blocked_events", 20 * blocked_events, "blocked runtime events exist"))

    if orphaned_sessions > 0:
        signals.append(RiskSignal("orphaned_sessions", 15 * orphaned_sessions, "orphaned sessions detected"))

    if override_attempted:
        signals.append(RiskSignal("override_attempt", 35, "governance override attempted"))

    if policy_violations > 0:
        signals.append(RiskSignal("policy_violation", 30 * policy_violations, "policy violations detected"))

    score = sum(signal.weight for signal in signals)

    if score >= 100:
        level = RiskLevel.CRITICAL
    elif score >= 60:
        level = RiskLevel.HIGH
    elif score >= 25:
        level = RiskLevel.MEDIUM
    else:
        level = RiskLevel.LOW

    return RiskAssessment(
        score=score,
        level=level,
        signals=tuple(signals),
    )
