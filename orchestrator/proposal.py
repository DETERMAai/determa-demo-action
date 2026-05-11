from dataclasses import dataclass
from datetime import datetime
from typing import Tuple
from orchestrator.state_machine import State


@dataclass(frozen=True)
class Proposal:
    """
    Immutable execution proposal with WAITING_APPROVAL hard-stop semantics.
    
    Proposal creation grants NO execution authority.
    Proposal cannot auto-transition or bypass WAITING_APPROVAL.
    Proposal is read-only after creation.
    
    Attributes:
        proposal_id: Unique proposal identifier
        repo_head: Git repository HEAD reference
        patch_hash: Deterministic hash of proposed patch
        requested_action: Human-readable action description
        created_at: Proposal creation timestamp
        status: Canonical state (always WAITING_APPROVAL at creation)
    """
    
    proposal_id: str
    repo_head: str
    patch_hash: str
    requested_action: str
    created_at: datetime
    status: State
    
    def __post_init__(self) -> None:
        """
        Validate proposal invariants.
        
        Raises:
            ValueError: If any invariant is violated
        """
        # Validate proposal_id
        if not self.proposal_id:
            raise ValueError("proposal_id cannot be empty")
        if not isinstance(self.proposal_id, str):
            raise ValueError("proposal_id must be string")
        
        # Validate repo_head
        if not self.repo_head:
            raise ValueError("repo_head cannot be empty")
        if not isinstance(self.repo_head, str):
            raise ValueError("repo_head must be string")
        
        # Validate patch_hash
        if not self.patch_hash:
            raise ValueError("patch_hash cannot be empty")
        if not isinstance(self.patch_hash, str):
            raise ValueError("patch_hash must be string")
        
        # Validate requested_action
        if not self.requested_action:
            raise ValueError("requested_action cannot be empty")
        if not isinstance(self.requested_action, str):
            raise ValueError("requested_action must be string")
        
        # Validate created_at
        if not isinstance(self.created_at, datetime):
            raise ValueError("created_at must be datetime object")
        
        # Validate status
        if not isinstance(self.status, State):
            raise ValueError("status must be State enum")
        
        # Enforce WAITING_APPROVAL hard-stop: proposal can only be created
        # in WAITING_APPROVAL state. Cannot bypass or auto-transition.
        if self.status != State.WAITING_APPROVAL:
            raise ValueError(
                "Proposal must be created in WAITING_APPROVAL state. "
                "Cannot bypass hard-stop or auto-transition."
            )
    
    @property
    def requires_approval(self) -> bool:
        """
        Check if proposal requires approval.
        
        Returns:
            True if proposal is in WAITING_APPROVAL state
        """
        return self.status == State.WAITING_APPROVAL
    
    @property
    def has_execution_authority(self) -> bool:
        """
        Check if proposal has execution authority.
        
        Proposals NEVER have execution authority.
        Execution authority must be granted through explicit state transitions.
        
        Returns:
            False - proposals cannot execute mutations
        """
        return False
    
    def validate_immutability(self) -> None:
        """
        Verify proposal is immutable.
        
        This is a no-op that documents the immutability guarantee.
        The frozen dataclass enforces immutability at the Python level.
        """
        pass


def create_proposal(
    proposal_id: str,
    repo_head: str,
    patch_hash: str,
    requested_action: str,
    created_at: datetime,
) -> Proposal:
    """
    Create an immutable proposal in WAITING_APPROVAL state.
    
    Proposal creation grants NO execution authority.
    Proposal cannot auto-transition or bypass WAITING_APPROVAL.
    
    Args:
        proposal_id: Unique proposal identifier
        repo_head: Git repository HEAD reference
        patch_hash: Deterministic hash of proposed patch
        requested_action: Human-readable action description
        created_at: Proposal creation timestamp
        
    Returns:
        Immutable Proposal in WAITING_APPROVAL state
        
    Raises:
        ValueError: If any required field is invalid
    """
    return Proposal(
        proposal_id=proposal_id,
        repo_head=repo_head,
        patch_hash=patch_hash,
        requested_action=requested_action,
        created_at=created_at,
        status=State.WAITING_APPROVAL,
    )
