import pytest
from datetime import datetime, timedelta
from dataclasses import FrozenInstanceError
from orchestrator.state_machine import State
from orchestrator.proposal import Proposal, create_proposal


class TestProposalCreation:
    """Test proposal creation and validation."""
    
    def test_create_valid_proposal(self):
        """Test creating a valid proposal."""
        now = datetime.now()
        proposal = create_proposal(
            proposal_id="prop-001",
            repo_head="abc123def456",
            patch_hash="sha256:abc123",
            requested_action="Deploy application",
            created_at=now,
        )
        
        assert proposal.proposal_id == "prop-001"
        assert proposal.repo_head == "abc123def456"
        assert proposal.patch_hash == "sha256:abc123"
        assert proposal.requested_action == "Deploy application"
        assert proposal.created_at == now
        assert proposal.status == State.WAITING_APPROVAL
    
    def test_proposal_defaults_to_waiting_approval(self):
        """Test that proposal defaults to WAITING_APPROVAL state."""
        now = datetime.now()
        proposal = create_proposal(
            proposal_id="prop-002",
            repo_head="head",
            patch_hash="hash",
            requested_action="action",
            created_at=now,
        )
        
        assert proposal.status == State.WAITING_APPROVAL
        assert proposal.requires_approval is True
    
    def test_proposal_with_explicit_waiting_approval_state(self):
        """Test creating proposal with explicit WAITING_APPROVAL state."""
        now = datetime.now()
        proposal = Proposal(
            proposal_id="prop-003",
            repo_head="head",
            patch_hash="hash",
            requested_action="action",
            created_at=now,
            status=State.WAITING_APPROVAL,
        )
        
        assert proposal.status == State.WAITING_APPROVAL


class TestProposalImmutability:
    """Test proposal immutability guarantees."""
    
    def test_proposal_is_immutable_frozen_dataclass(self):
        """Test that proposal cannot be modified after creation."""
        now = datetime.now()
        proposal = create_proposal(
            proposal_id="prop-004",
            repo_head="head",
            patch_hash="hash",
            requested_action="action",
            created_at=now,
        )
        
        # Attempt to modify a field should raise FrozenInstanceError
        with pytest.raises(FrozenInstanceError):
            proposal.proposal_id = "prop-modified"
    
    def test_proposal_cannot_modify_status(self):
        """Test that proposal status cannot be modified."""
        now = datetime.now()
        proposal = create_proposal(
            proposal_id="prop-005",
            repo_head="head",
            patch_hash="hash",
            requested_action="action",
            created_at=now,
        )
        
        # Attempt to change status should raise FrozenInstanceError
        with pytest.raises(FrozenInstanceError):
            proposal.status = State.APPROVED
    
    def test_proposal_cannot_modify_repo_head(self):
        """Test that proposal repo_head cannot be modified."""
        now = datetime.now()
        proposal = create_proposal(
            proposal_id="prop-006",
            repo_head="original_head",
            patch_hash="hash",
            requested_action="action",
            created_at=now,
        )
        
        with pytest.raises(FrozenInstanceError):
            proposal.repo_head = "modified_head"
    
    def test_proposal_cannot_modify_patch_hash(self):
        """Test that proposal patch_hash cannot be modified."""
        now = datetime.now()
        proposal = create_proposal(
            proposal_id="prop-007",
            repo_head="head",
            patch_hash="original_hash",
            requested_action="action",
            created_at=now,
        )
        
        with pytest.raises(FrozenInstanceError):
            proposal.patch_hash = "modified_hash"
    
    def test_proposal_cannot_modify_requested_action(self):
        """Test that proposal requested_action cannot be modified."""
        now = datetime.now()
        proposal = create_proposal(
            proposal_id="prop-008",
            repo_head="head",
            patch_hash="hash",
            requested_action="original action",
            created_at=now,
        )
        
        with pytest.raises(FrozenInstanceError):
            proposal.requested_action = "modified action"
    
    def test_proposal_cannot_modify_created_at(self):
        """Test that proposal created_at cannot be modified."""
        now = datetime.now()
        proposal = create_proposal(
            proposal_id="prop-009",
            repo_head="head",
            patch_hash="hash",
            requested_action="action",
            created_at=now,
        )
        
        with pytest.raises(FrozenInstanceError):
            proposal.created_at = datetime.now() + timedelta(hours=1)
    
    def test_proposal_validate_immutability_call(self):
        """Test that validate_immutability method can be called."""
        now = datetime.now()
        proposal = create_proposal(
            proposal_id="prop-010",
            repo_head="head",
            patch_hash="hash",
            requested_action="action",
            created_at=now,
        )
        
        # Should not raise - this is a documentation method
        proposal.validate_immutability()


class TestProposalValidation:
    """Test proposal validation and invariants."""
    
    def test_empty_proposal_id_fails(self):
        """Test that empty proposal_id fails validation."""
        now = datetime.now()
        with pytest.raises(ValueError, match="proposal_id cannot be empty"):
            Proposal(
                proposal_id="",
                repo_head="head",
                patch_hash="hash",
                requested_action="action",
                created_at=now,
                status=State.WAITING_APPROVAL,
            )
    
    def test_none_proposal_id_fails(self):
        """Test that None proposal_id fails validation."""
        now = datetime.now()
        with pytest.raises(ValueError, match="proposal_id cannot be empty"):
            Proposal(
                proposal_id=None,  # type: ignore
                repo_head="head",
                patch_hash="hash",
                requested_action="action",
                created_at=now,
                status=State.WAITING_APPROVAL,
            )
    
    def test_non_string_proposal_id_fails(self):
        """Test that non-string proposal_id fails validation."""
        now = datetime.now()
        with pytest.raises(ValueError, match="proposal_id must be string"):
            Proposal(
                proposal_id=123,  # type: ignore
                repo_head="head",
                patch_hash="hash",
                requested_action="action",
                created_at=now,
                status=State.WAITING_APPROVAL,
            )
    
    def test_empty_repo_head_fails(self):
        """Test that empty repo_head fails validation."""
        now = datetime.now()
        with pytest.raises(ValueError, match="repo_head cannot be empty"):
            Proposal(
                proposal_id="prop-011",
                repo_head="",
                patch_hash="hash",
                requested_action="action",
                created_at=now,
                status=State.WAITING_APPROVAL,
            )
    
    def test_non_string_repo_head_fails(self):
        """Test that non-string repo_head fails validation."""
        now = datetime.now()
        with pytest.raises(ValueError, match="repo_head must be string"):
            Proposal(
                proposal_id="prop-012",
                repo_head=456,  # type: ignore
                patch_hash="hash",
                requested_action="action",
                created_at=now,
                status=State.WAITING_APPROVAL,
            )
    
    def test_empty_patch_hash_fails(self):
        """Test that empty patch_hash fails validation."""
        now = datetime.now()
        with pytest.raises(ValueError, match="patch_hash cannot be empty"):
            Proposal(
                proposal_id="prop-013",
                repo_head="head",
                patch_hash="",
                requested_action="action",
                created_at=now,
                status=State.WAITING_APPROVAL,
            )
    
    def test_non_string_patch_hash_fails(self):
        """Test that non-string patch_hash fails validation."""
        now = datetime.now()
        with pytest.raises(ValueError, match="patch_hash must be string"):
            Proposal(
                proposal_id="prop-014",
                repo_head="head",
                patch_hash=789,  # type: ignore
                requested_action="action",
                created_at=now,
                status=State.WAITING_APPROVAL,
            )
    
    def test_empty_requested_action_fails(self):
        """Test that empty requested_action fails validation."""
        now = datetime.now()
        with pytest.raises(ValueError, match="requested_action cannot be empty"):
            Proposal(
                proposal_id="prop-015",
                repo_head="head",
                patch_hash="hash",
                requested_action="",
                created_at=now,
                status=State.WAITING_APPROVAL,
            )
    
    def test_non_string_requested_action_fails(self):
        """Test that non-string requested_action fails validation."""
        now = datetime.now()
        with pytest.raises(ValueError, match="requested_action must be string"):
            Proposal(
                proposal_id="prop-016",
                repo_head="head",
                patch_hash="hash",
                requested_action=999,  # type: ignore
                created_at=now,
                status=State.WAITING_APPROVAL,
            )
    
    def test_non_datetime_created_at_fails(self):
        """Test that non-datetime created_at fails validation."""
        with pytest.raises(ValueError, match="created_at must be datetime object"):
            Proposal(
                proposal_id="prop-017",
                repo_head="head",
                patch_hash="hash",
                requested_action="action",
                created_at="2024-01-01",  # type: ignore
                status=State.WAITING_APPROVAL,
            )
    
    def test_non_state_status_fails(self):
        """Test that non-State status fails validation."""
        now = datetime.now()
        with pytest.raises(ValueError, match="status must be State enum"):
            Proposal(
                proposal_id="prop-018",
                repo_head="head",
                patch_hash="hash",
                requested_action="action",
                created_at=now,
                status="WAITING_APPROVAL",  # type: ignore
            )


class TestWaitingApprovalHardStop:
    """Test WAITING_APPROVAL hard-stop semantics."""
    
    def test_cannot_create_in_proposed_state(self):
        """Test that proposal cannot be created in PROPOSED state."""
        now = datetime.now()
        with pytest.raises(
            ValueError,
            match="Proposal must be created in WAITING_APPROVAL state"
        ):
            Proposal(
                proposal_id="prop-019",
                repo_head="head",
                patch_hash="hash",
                requested_action="action",
                created_at=now,
                status=State.PROPOSED,
            )
    
    def test_cannot_create_in_approved_state(self):
        """Test that proposal cannot be created in APPROVED state."""
        now = datetime.now()
        with pytest.raises(
            ValueError,
            match="Proposal must be created in WAITING_APPROVAL state"
        ):
            Proposal(
                proposal_id="prop-020",
                repo_head="head",
                patch_hash="hash",
                requested_action="action",
                created_at=now,
                status=State.APPROVED,
            )
    
    def test_cannot_create_in_executing_state(self):
        """Test that proposal cannot be created in EXECUTING state."""
        now = datetime.now()
        with pytest.raises(
            ValueError,
            match="Proposal must be created in WAITING_APPROVAL state"
        ):
            Proposal(
                proposal_id="prop-021",
                repo_head="head",
                patch_hash="hash",
                requested_action="action",
                created_at=now,
                status=State.EXECUTING,
            )
    
    def test_cannot_create_in_executed_state(self):
        """Test that proposal cannot be created in EXECUTED state."""
        now = datetime.now()
        with pytest.raises(
            ValueError,
            match="Proposal must be created in WAITING_APPROVAL state"
        ):
            Proposal(
                proposal_id="prop-022",
                repo_head="head",
                patch_hash="hash",
                requested_action="action",
                created_at=now,
                status=State.EXECUTED,
            )
    
    def test_cannot_create_in_rejected_state(self):
        """Test that proposal cannot be created in REJECTED state."""
        now = datetime.now()
        with pytest.raises(
            ValueError,
            match="Proposal must be created in WAITING_APPROVAL state"
        ):
            Proposal(
                proposal_id="prop-023",
                repo_head="head",
                patch_hash="hash",
                requested_action="action",
                created_at=now,
                status=State.REJECTED,
            )
    
    def test_cannot_create_in_blocked_state(self):
        """Test that proposal cannot be created in BLOCKED state."""
        now = datetime.now()
        with pytest.raises(
            ValueError,
            match="Proposal must be created in WAITING_APPROVAL state"
        ):
            Proposal(
                proposal_id="prop-024",
                repo_head="head",
                patch_hash="hash",
                requested_action="action",
                created_at=now,
                status=State.BLOCKED,
            )


class TestExecutionAuthority:
    """Test that proposals have no execution authority."""
    
    def test_proposal_has_no_execution_authority(self):
        """Test that proposal never has execution authority."""
        now = datetime.now()
        proposal = create_proposal(
            proposal_id="prop-025",
            repo_head="head",
            patch_hash="hash",
            requested_action="action",
            created_at=now,
        )
        
        assert proposal.has_execution_authority is False
    
    def test_proposal_cannot_execute_mutations(self):
        """Test that proposal cannot execute mutations."""
        now = datetime.now()
        proposal = create_proposal(
            proposal_id="prop-026",
            repo_head="head",
            patch_hash="hash",
            requested_action="action",
            created_at=now,
        )
        
        # Proposal has no methods to execute or transition state
        # It is purely a data container
        assert not hasattr(proposal, 'execute')
        assert not hasattr(proposal, 'transition')
        assert not hasattr(proposal, 'approve')
        assert not hasattr(proposal, 'reject')
        assert not hasattr(proposal, 'block')


class TestProposalProperties:
    """Test proposal properties and queries."""
    
    def test_requires_approval_in_waiting_approval_state(self):
        """Test that requires_approval is True in WAITING_APPROVAL state."""
        now = datetime.now()
        proposal = create_proposal(
            proposal_id="prop-027",
            repo_head="head",
            patch_hash="hash",
            requested_action="action",
            created_at=now,
        )
        
        assert proposal.requires_approval is True
    
    def test_proposal_fields_accessible(self):
        """Test that all proposal fields are accessible."""
        now = datetime.now()
        proposal = create_proposal(
            proposal_id="prop-028",
            repo_head="main:abc123",
            patch_hash="sha256:def456",
            requested_action="Deploy to production",
            created_at=now,
        )
        
        # All fields should be readable
        assert proposal.proposal_id == "prop-028"
        assert proposal.repo_head == "main:abc123"
        assert proposal.patch_hash == "sha256:def456"
        assert proposal.requested_action == "Deploy to production"
        assert proposal.created_at == now
        assert proposal.status == State.WAITING_APPROVAL


class TestProposalNoAutoTransition:
    """Test that proposals cannot auto-transition."""
    
    def test_proposal_has_no_transition_method(self):
        """Test that proposal has no automatic transition mechanism."""
        now = datetime.now()
        proposal = create_proposal(
            proposal_id="prop-029",
            repo_head="head",
            patch_hash="hash",
            requested_action="action",
            created_at=now,
        )
        
        # Proposal should have no methods that change state
        # State transitions happen through StateMachine, not Proposal
        assert not callable(getattr(proposal, 'transition', None))
    
    def test_proposal_cannot_bypass_waiting_approval(self):
        """Test that proposal cannot be created bypassing WAITING_APPROVAL."""
        now = datetime.now()
        
        # Can only create in WAITING_APPROVAL
        proposal = create_proposal(
            proposal_id="prop-030",
            repo_head="head",
            patch_hash="hash",
            requested_action="action",
            created_at=now,
        )
        
        assert proposal.status == State.WAITING_APPROVAL
        
        # Cannot modify status to bypass
        with pytest.raises(FrozenInstanceError):
            proposal.status = State.APPROVED


class TestCreateProposalHelper:
    """Test the create_proposal helper function."""
    
    def test_create_proposal_helper_returns_waiting_approval(self):
        """Test that create_proposal helper returns WAITING_APPROVAL state."""
        now = datetime.now()
        proposal = create_proposal(
            proposal_id="prop-031",
            repo_head="head",
            patch_hash="hash",
            requested_action="action",
            created_at=now,
        )
        
        assert isinstance(proposal, Proposal)
        assert proposal.status == State.WAITING_APPROVAL
    
    def test_create_proposal_helper_validates_all_fields(self):
        """Test that create_proposal helper validates all fields."""
        now = datetime.now()
        
        with pytest.raises(ValueError, match="proposal_id cannot be empty"):
            create_proposal(
                proposal_id="",
                repo_head="head",
                patch_hash="hash",
                requested_action="action",
                created_at=now,
            )
    
    def test_create_proposal_with_various_timestamps(self):
        """Test creating proposals with various timestamps."""
        past = datetime.now() - timedelta(hours=1)
        now = datetime.now()
        
        proposal_past = create_proposal(
            proposal_id="prop-032",
            repo_head="head",
            patch_hash="hash",
            requested_action="action",
            created_at=past,
        )
        
        proposal_now = create_proposal(
            proposal_id="prop-033",
            repo_head="head",
            patch_hash="hash",
            requested_action="action",
            created_at=now,
        )
        
        assert proposal_past.created_at == past
        assert proposal_now.created_at == now
        assert proposal_past.created_at < proposal_now.created_at
