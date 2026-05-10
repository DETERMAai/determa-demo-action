"""Factory Replay Gate.

Validates whether a DETERMA Replay result allows a factory task to complete.
This is a lightweight gate for self-governed factory execution.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ReplayGateStatus(str, Enum):
    PASS = "PASS"
    REQUIRES_APPROVAL = "REQUIRES_APPROVAL"
    BLOCK = "BLOCK"


@dataclass(frozen=True)
class ReplayGatePolicy:
    block_trust_states: tuple[str, ...] = ("BLOCKED", "UNEXPLAINABLE")
    approval_trust_states: tuple[str, ...] = ("REQUIRES_APPROVAL",)
    block_severities: tuple[str, ...] = ("CRITICAL",)
    approval_severities: tuple[str, ...] = ("HIGH",)


@dataclass(frozen=True)
class ReplayGateResult:
    status: ReplayGateStatus
    reasons: tuple[str, ...]

    @property
    def passed(self) -> bool:
        return self.status == ReplayGateStatus.PASS

    @property
    def requires_approval(self) -> bool:
        return self.status == ReplayGateStatus.REQUIRES_APPROVAL


def evaluate_replay_gate(
    replay: dict[str, object],
    policy: ReplayGatePolicy | None = None,
) -> ReplayGateResult:
    """Evaluate a replay artifact against a factory gate policy."""
    gate_policy = policy or ReplayGatePolicy()
    severity = str(replay.get("severity", ""))
    trust_state = str(replay.get("trust_state", ""))

    reasons: list[str] = []

    if trust_state in gate_policy.block_trust_states:
        reasons.append(f"blocked trust state: {trust_state}")

    if severity in gate_policy.block_severities:
        reasons.append(f"blocked severity: {severity}")

    if reasons:
        return ReplayGateResult(status=ReplayGateStatus.BLOCK, reasons=tuple(reasons))

    if trust_state in gate_policy.approval_trust_states:
        reasons.append(f"approval required trust state: {trust_state}")

    if severity in gate_policy.approval_severities:
        reasons.append(f"approval required severity: {severity}")

    if reasons:
        return ReplayGateResult(status=ReplayGateStatus.REQUIRES_APPROVAL, reasons=tuple(reasons))

    return ReplayGateResult(status=ReplayGateStatus.PASS, reasons=("replay gate passed",))
