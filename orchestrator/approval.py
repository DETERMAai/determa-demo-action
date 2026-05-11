from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from orchestrator.state_machine import State
from orchestrator.proposal import Proposal


@dataclass(frozen=True)
class Approval:
    """
    Immutable approval registration with deterministic semantics.
    
    Approval validates proposal state and registers authorization metadata.
    Approval does NOT grant execution authority or create capabilities.
    Approval alone cannot execute anything.
    
    Attributes:
        approval_id: Unique approval identifier
        proposal_id: Reference to approved proposal
        approved_by: Identifier of approver (human or system)
        approved_at: Approval timestamp
        resulting_state: Canonical state after approval (APPROVED)
    """
    
    approval_id: str
    proposal_id: str
    approved_by: str
    approved_at: datetime
    resulting_state: State
    
    def __post_init__(self) -> None:
        """
        Validate approval invariants.
        
        Raises:
            ValueError: If any invariant is violated
        """
        # Validate approval_id
        if not self.approval_id:
            raise ValueError("approval_id cannot be empty")
        if not isinstance(self.approval_id, str):
            raise ValueError("approval_id must be string")
        
        # Validate proposal_id
        if not self.proposal_id:
            raise ValueError("proposal_id cannot be empty")
        if not isinstance(self.proposal_id, str):
            raise ValueError("proposal_id must be string")
        
        # Validate approved_by
        if not self.approved_by:
            raise ValueError("approved_by cannot be empty")
        if not isinstance(self.approved_by, str):
            raise ValueError("approved_by must be string")
        
        # Validate approved_at
        if not isinstance(self.approved_at, datetime):
            raise ValueError("approved_at must be datetime object")
        
        # Validate resulting_state
        if not isinstance(self.resulting_state, State):
            raise ValueError("resulting_state must be State enum")
        
        # Enforce canonical resulting state: APPROVED
        # Approval can only result in APPROVED state
        if self.resulting_state != State.APPROVED:
            raise ValueError(
                "Approval resulting_state must be APPROVED. "
                "Cannot result in other states."
            )
    
    @property
    def has_execution_authority(self) -> bool:
        """
        Check if approval has execution authority.
        
        Approvals NEVER have execution authority.
        Execution authority must be granted through explicit state transitions.
        
        Returns:
            False - approvals cannot execute mutations
        """
        return False
    
    def validate_determinism(self) -> None:
        """
        Verify approval follows deterministic semantics.
        
        This is a no-op that documents the deterministic guarantee.
        The frozen dataclass enforces immutability at the Python level.
        """
        pass


def approve_proposal(
    approval_id: str,
    proposal: Proposal,
    approved_by: str,
    approved_at: datetime,
) -> Approval:
    """
    Register approval for a proposal.
    
    Validates that proposal is in WAITING_APPROVAL state.
    Creates immutable approval metadata.
    Does NOT execute mutations or grant execution authority.
    
    Args:
        approval_id: Unique approval identifier
        proposal: The proposal being approved (must be in WAITING_APPROVAL)
        approved_by: Identifier of approver
        approved_at: Approval timestamp
        
    Returns:
        Immutable Approval record
        
    Raises:
        ValueError: If proposal is not in WAITING_APPROVAL state
        ValueError: If any required field is invalid
    """
    # Validate proposal is in WAITING_APPROVAL state
    if proposal.status != State.WAITING_APPROVAL:
        raise ValueError(
            f"Cannot approve proposal in {proposal.status.name} state. "
            f"Must be in WAITING_APPROVAL state."
        )
    
    # Create approval record
    return Approval(
        approval_id=approval_id,
        proposal_id=proposal.proposal_id,
        approved_by=approved_by,
        approved_at=approved_at,
        resulting_state=State.APPROVED,
    )
