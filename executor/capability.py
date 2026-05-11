from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class Capability:
    """
    Immutable single-use execution capability.
    
    Represents bounded, consumable execution authority.
    Capabilities are single-use and replay-proof.
    Consumed capabilities become permanently invalid.
    
    Attributes:
        capability_id: Unique capability identifier
        proposal_id: Reference to authorized proposal
        repo_head: Repository HEAD at capability issuance
        issued_at: Capability issuance timestamp
        consumed: Whether capability has been consumed
        consumed_at: Timestamp when capability was consumed (None if unused)
    """
    
    capability_id: str
    proposal_id: str
    repo_head: str
    issued_at: datetime
    consumed: bool
    consumed_at: Optional[datetime]
    
    def __post_init__(self) -> None:
        """
        Validate capability invariants.
        
        Raises:
            ValueError: If any invariant is violated
        """
        # Validate capability_id
        if not self.capability_id:
            raise ValueError("capability_id cannot be empty")
        if not isinstance(self.capability_id, str):
            raise ValueError("capability_id must be string")
        
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
        
        # Validate issued_at
        if not isinstance(self.issued_at, datetime):
            raise ValueError("issued_at must be datetime object")
        
        # Validate consumed
        if not isinstance(self.consumed, bool):
            raise ValueError("consumed must be boolean")
        
        # Validate consumed_at
        if self.consumed_at is not None and not isinstance(self.consumed_at, datetime):
            raise ValueError("consumed_at must be datetime object or None")
        
        # Enforce single-use semantics:
        # If capability is unconsumed, consumed_at must be None
        # If capability is consumed, consumed_at must be set
        if not self.consumed:
            if self.consumed_at is not None:
                raise ValueError(
                    "Unconsumed capability must have consumed_at=None"
                )
        else:
            if self.consumed_at is None:
                raise ValueError(
                    "Consumed capability must have consumed_at set"
                )
            if self.consumed_at < self.issued_at:
                raise ValueError(
                    "consumed_at must be after or equal to issued_at"
                )
    
    @property
    def is_valid(self) -> bool:
        """
        Check if capability is valid and unused.
        
        Returns:
            True if capability is unused, False if consumed
        """
        return not self.consumed
    
    @property
    def is_consumed(self) -> bool:
        """
        Check if capability has been consumed.
        
        Returns:
            True if capability is consumed, False if unused
        """
        return self.consumed
    
    @property
    def permits_execution(self) -> bool:
        """
        Check if capability permits execution to proceed.
        
        Execution is only permitted if capability is unused.
        Consumed capabilities block all execution.
        
        Returns:
            True only if capability is unused
        """
        return self.is_valid
    
    @property
    def replay_blocked(self) -> bool:
        """
        Check if capability blocks replay attempts.
        
        Once consumed, any attempt to reuse the capability is blocked.
        
        Returns:
            True if capability is consumed (replay blocked)
        """
        return self.is_consumed
    
    def validate_determinism(self) -> None:
        """
        Verify capability follows deterministic semantics.
        
        This is a no-op that documents the deterministic guarantee.
        The frozen dataclass enforces immutability at the Python level.
        """
        pass


def issue_capability(
    capability_id: str,
    proposal_id: str,
    repo_head: str,
    issued_at: datetime,
) -> Capability:
    """
    Issue a new single-use execution capability.
    
    Creates an unused capability that may be consumed once.
    Capability does not bypass witness validation or approval requirements.
    
    Args:
        capability_id: Unique capability identifier
        proposal_id: Reference to authorized proposal
        repo_head: Repository HEAD at issuance
        issued_at: Issuance timestamp
        
    Returns:
        Immutable unused Capability
        
    Raises:
        ValueError: If any required field is invalid
    """
    return Capability(
        capability_id=capability_id,
        proposal_id=proposal_id,
        repo_head=repo_head,
        issued_at=issued_at,
        consumed=False,
        consumed_at=None,
    )


def consume_capability(capability: Capability, consumed_at: datetime) -> Capability:
    """
    Consume a single-use capability.
    
    Marks capability as consumed, preventing replay.
    Once consumed, capability becomes permanently invalid.
    
    Args:
        capability: Capability to consume
        consumed_at: Consumption timestamp
        
    Returns:
        New immutable consumed Capability
        
    Raises:
        ValueError: If capability has already been consumed
    """
    # Replay prevention: cannot consume already-consumed capability
    if capability.is_consumed:
        raise ValueError(
            f"Capability {capability.capability_id} has already been consumed. "
            f"Replay blocked."
        )
    
    # Create new consumed capability
    return Capability(
        capability_id=capability.capability_id,
        proposal_id=capability.proposal_id,
        repo_head=capability.repo_head,
        issued_at=capability.issued_at,
        consumed=True,
        consumed_at=consumed_at,
    )
