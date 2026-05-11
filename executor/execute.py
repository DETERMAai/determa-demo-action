from __future__ import annotations

from datetime import datetime
from typing import Callable, Optional, Tuple, TypeVar

from orchestrator.proposal import Proposal
from orchestrator.state_machine import State

from executor.capability import Capability, consume_capability
from executor.state_witness import StateWitness, ValidationResult

T = TypeVar("T")


def execute(
    proposal: Proposal,
    witness: Optional[StateWitness],
    capability: Optional[Capability],
    mutation: Callable[[], T],
    consumed_at: datetime,
) -> Tuple[T, Capability]:
    """
    Execute a mutation only when all deterministic authority checks pass.

    Gate conditions (all required):
    - proposal state is APPROVED
    - witness is present and VALID
    - capability is present, linked to proposal, and unused

    On success:
    - mutation is executed
    - capability is consumed exactly once
    - mutation result and consumed capability are returned

    On failure:
    - raises ValueError with "EXECUTION BLOCKED: ... "
    - no mutation is executed
    - capability is not consumed
    """
    _validate_execution_gate(proposal, witness, capability)

    result = mutation()
    consumed_capability = consume_capability(capability, consumed_at)
    return result, consumed_capability


def _validate_execution_gate(
    proposal: Proposal,
    witness: Optional[StateWitness],
    capability: Optional[Capability],
) -> None:
    """Validate governed execution authority. Fail closed on any violation."""
    if proposal.status != State.APPROVED:
        raise ValueError(
            "EXECUTION BLOCKED: invalid proposal state. Must be APPROVED."
        )

    if witness is None:
        raise ValueError("EXECUTION BLOCKED: missing witness.")

    if witness.validation_result != ValidationResult.VALID or not witness.is_valid:
        raise ValueError("EXECUTION BLOCKED: invalid witness.")

    if capability is None:
        raise ValueError("EXECUTION BLOCKED: missing capability.")

    if capability.proposal_id != proposal.proposal_id:
        raise ValueError(
            "EXECUTION BLOCKED: mismatched proposal/capability linkage."
        )

    if capability.repo_head != witness.approved_repo_head:
        raise ValueError(
            "EXECUTION BLOCKED: mismatched capability/witness linkage."
        )

    if capability.is_consumed:
        raise ValueError(
            "EXECUTION BLOCKED: capability already consumed (replay blocked)."
        )

    if not capability.is_valid:
        raise ValueError("EXECUTION BLOCKED: invalid capability.")
