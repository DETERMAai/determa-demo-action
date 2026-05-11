from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class ValidationResult(Enum):
    """Deterministic witness validation outcomes."""
    VALID = "VALID"
    INVALID = "INVALID"


@dataclass(frozen=True)
class StateWitness:
    """
    Immutable runtime repository integrity witness.
    
    Validates that current repository HEAD matches the approved HEAD at the time
    of execution authorization. Repository drift blocks execution.
    
    Attributes:
        approved_repo_head: Repository HEAD when approval was granted
        current_repo_head: Current repository HEAD at validation time
        validation_result: VALID if heads match, INVALID if drift detected
        validated_at: Witness validation timestamp
    """
    
    approved_repo_head: str
    current_repo_head: str
    validation_result: ValidationResult
    validated_at: datetime
    
    def __post_init__(self) -> None:
        """
        Validate witness invariants.
        
        Raises:
            ValueError: If any invariant is violated
        """
        # Validate approved_repo_head
        if not self.approved_repo_head:
            raise ValueError("approved_repo_head cannot be empty")
        if not isinstance(self.approved_repo_head, str):
            raise ValueError("approved_repo_head must be string")
        
        # Validate current_repo_head
        if not self.current_repo_head:
            raise ValueError("current_repo_head cannot be empty")
        if not isinstance(self.current_repo_head, str):
            raise ValueError("current_repo_head must be string")
        
        # Validate validation_result
        if not isinstance(self.validation_result, ValidationResult):
            raise ValueError("validation_result must be ValidationResult enum")
        
        # Validate validated_at
        if not isinstance(self.validated_at, datetime):
            raise ValueError("validated_at must be datetime object")
        
        # Enforce deterministic validation semantics:
        # If heads match, result must be VALID
        # If heads differ, result must be INVALID
        if self.approved_repo_head == self.current_repo_head:
            if self.validation_result != ValidationResult.VALID:
                raise ValueError(
                    "When repo heads match, validation_result must be VALID"
                )
        else:
            if self.validation_result != ValidationResult.INVALID:
                raise ValueError(
                    "When repo heads differ, validation_result must be INVALID"
                )
    
    @property
    def is_valid(self) -> bool:
        """
        Check if witness validation passed.
        
        Returns:
            True if validation_result is VALID, False otherwise
        """
        return self.validation_result == ValidationResult.VALID
    
    @property
    def repository_drift_detected(self) -> bool:
        """
        Check if repository drift was detected.
        
        Repository drift blocks execution.
        
        Returns:
            True if validation_result is INVALID, False otherwise
        """
        return self.validation_result == ValidationResult.INVALID
    
    @property
    def permits_execution(self) -> bool:
        """
        Check if witness permits execution to proceed.
        
        Execution is only permitted if witness is valid and no drift detected.
        
        Returns:
            True only if validation passed (heads match)
        """
        return self.is_valid
    
    def validate_determinism(self) -> None:
        """
        Verify witness follows deterministic semantics.
        
        This is a no-op that documents the deterministic guarantee.
        The frozen dataclass enforces immutability at the Python level.
        """
        pass


def validate_repository_state(
    approved_repo_head: str,
    current_repo_head: str,
    validated_at: datetime,
) -> StateWitness:
    """
    Validate current repository state matches approved state.
    
    Deterministic validation: if repository HEAD has changed, execution is blocked.
    Fails closed on any mismatch or invalid input.
    
    Args:
        approved_repo_head: Repository HEAD when approval was granted
        current_repo_head: Current repository HEAD
        validated_at: Validation timestamp
        
    Returns:
        Immutable StateWitness with validation result
        
    Raises:
        ValueError: If any required field is invalid
    """
    # Determine validation result
    if approved_repo_head == current_repo_head:
        result = ValidationResult.VALID
    else:
        result = ValidationResult.INVALID
    
    # Create witness record
    return StateWitness(
        approved_repo_head=approved_repo_head,
        current_repo_head=current_repo_head,
        validation_result=result,
        validated_at=validated_at,
    )
