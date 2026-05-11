import pytest
from datetime import datetime, timedelta
from dataclasses import FrozenInstanceError
from orchestrator.state_machine import State
from orchestrator.proposal import create_proposal
from orchestrator.approval import Approval, approve_proposal


class TestApprovalCreation:
    """Test approval creation and validation."""
    
    def test_approve_valid_waiting_approval_proposal(self):
        """Test approving a valid proposal in WAITING_APPROVAL state."""
        now = datetime.now()
        proposal = create_proposal(
            proposal_id="prop-001",
            repo_head="abc123",
            patch_hash="hash123",
            requested_action="Deploy",
            created_at=now,
        )
        
        approval = approve_proposal(
            approval_id="appr-001",
            proposal=proposal,
            approved_by="user@example.com",
            approved_at=now,
        )
        
        assert approval.approval_id == "appr-001"
        assert approval.proposal_id == "prop-001"
        assert approval.approved_by == "user@example.com"
        assert approval.approved_at == now
        assert approval.resulting_state == State.APPROVED
    
    def test_approval_resulting_state_is_approved(self):
        """Test that approval resulting_state is always APPROVED."""
        now = datetime.now()
        proposal = create_proposal(
            proposal_id="prop-002",
            repo_head="head",
            patch_hash="hash",
            requested_action="action",
            created_at=now,
        )
        
        approval = approve_proposal(
            approval_id="appr-002",
            proposal=proposal,
            approved_by="approver",
            approved_at=now,
        )
        
        assert approval.resulting_state == State.APPROVED
    
    def test_approval_defaults_to_approved_state(self):
        """Test that approval defaults to APPROVED canonical state."""
        now = datetime.now()
        approval = Approval(
            approval_id="appr-003",
            proposal_id="prop-003",
            approved_by="user",
            approved_at=now,
            resulting_state=State.APPROVED,
        )
        
        assert approval.resulting_state == State.APPROVED


class TestApprovalValidation:
    """Test approval validation and field requirements."""
    
    def test_empty_approval_id_fails(self):
        """Test that empty approval_id fails validation."""
        now = datetime.now()
        with pytest.raises(ValueError, match="approval_id cannot be empty"):
            Approval(
                approval_id="",
                proposal_id="prop-004",
                approved_by="user",
                approved_at=now,
                resulting_state=State.APPROVED,
            )
    
    def test_non_string_approval_id_fails(self):
        """Test that non-string approval_id fails validation."""
        now = datetime.now()
        with pytest.raises(ValueError, match="approval_id must be string"):
            Approval(
                approval_id=123,  # type: ignore
                proposal_id="prop-005",
                approved_by="user",
                approved_at=now,
                resulting_state=State.APPROVED,
            )
    
    def test_empty_proposal_id_fails(self):
        """Test that empty proposal_id fails validation."""
        now = datetime.now()
        with pytest.raises(ValueError, match="proposal_id cannot be empty"):
            Approval(
                approval_id="appr-006",
                proposal_id="",
                approved_by="user",
                approved_at=now,
                resulting_state=State.APPROVED,
            )
    
    def test_non_string_proposal_id_fails(self):
        """Test that non-string proposal_id fails validation."""
        now = datetime.now()
        with pytest.raises(ValueError, match="proposal_id must be string"):
            Approval(
                approval_id="appr-007",
                proposal_id=456,  # type: ignore
                approved_by="user",
                approved_at=now,
                resulting_state=State.APPROVED,
            )
    
    def test_empty_approved_by_fails(self):
        """Test that empty approved_by fails validation."""
        now = datetime.now()
        with pytest.raises(ValueError, match="approved_by cannot be empty"):
            Approval(
                approval_id="appr-008",
                proposal_id="prop-008",
                approved_by="",
                approved_at=now,
                resulting_state=State.APPROVED,
            )
    
    def test_non_string_approved_by_fails(self):
        """Test that non-string approved_by fails validation."""
        now = datetime.now()
        with pytest.raises(ValueError, match="approved_by must be string"):
            Approval(
                approval_id="appr-009",
                proposal_id="prop-009",
                approved_by=789,  # type: ignore
                approved_at=now,
                resulting_state=State.APPROVED,
            )
    
    def test_non_datetime_approved_at_fails(self):
        """Test that non-datetime approved_at fails validation."""
        with pytest.raises(ValueError, match="approved_at must be datetime object"):
            Approval(
                approval_id="appr-010",
                proposal_id="prop-010",
                approved_by="user",
                approved_at="2024-01-01",  # type: ignore
                resulting_state=State.APPROVED,
            )
    
    def test_non_state_resulting_state_fails(self):
        """Test that non-State resulting_state fails validation."""
        now = datetime.now()
        with pytest.raises(ValueError, match="resulting_state must be State enum"):
            Approval(
                approval_id="appr-011",
                proposal_id="prop-011",
                approved_by="user",
                approved_at=now,
                resulting_state="APPROVED",  # type: ignore
            )


class TestApprovalStateConstraint:
    """Test that approval can only result in APPROVED state."""
    
    def test_cannot_approve_to_proposed_state(self):
        """Test that approval cannot result in PROPOSED state."""
        now = datetime.now()
        with pytest.raises(
            ValueError,
            match="Approval resulting_state must be APPROVED"
        ):
            Approval(
                approval_id="appr-012",
                proposal_id="prop-012",
                approved_by="user",
                approved_at=now,
                resulting_state=State.PROPOSED,
            )
    
    def test_cannot_approve_to_waiting_approval_state(self):
        """Test that approval cannot result in WAITING_APPROVAL state."""
        now = datetime.now()
        with pytest.raises(
            ValueError,
            match="Approval resulting_state must be APPROVED"
        ):
            Approval(
                approval_id="appr-013",
                proposal_id="prop-013",
                approved_by="user",
                approved_at=now,
                resulting_state=State.WAITING_APPROVAL,
            )
    
    def test_cannot_approve_to_executing_state(self):
        """Test that approval cannot result in EXECUTING state."""
        now = datetime.now()
        with pytest.raises(
            ValueError,
            match="Approval resulting_state must be APPROVED"
        ):
            Approval(
                approval_id="appr-014",
                proposal_id="prop-014",
                approved_by="user",
                approved_at=now,
                resulting_state=State.EXECUTING,
            )
    
    def test_cannot_approve_to_executed_state(self):
        """Test that approval cannot result in EXECUTED state."""
        now = datetime.now()
        with pytest.raises(
            ValueError,
            match="Approval resulting_state must be APPROVED"
        ):
            Approval(
                approval_id="appr-015",
                proposal_id="prop-015",
                approved_by="user",
                approved_at=now,
                resulting_state=State.EXECUTED,
            )
    
    def test_cannot_approve_to_rejected_state(self):
        """Test that approval cannot result in REJECTED state."""
        now = datetime.now()
        with pytest.raises(
            ValueError,
            match="Approval resulting_state must be APPROVED"
        ):
            Approval(
                approval_id="appr-016",
                proposal_id="prop-016",
                approved_by="user",
                approved_at=now,
                resulting_state=State.REJECTED,
            )
    
    def test_cannot_approve_to_blocked_state(self):
        """Test that approval cannot result in BLOCKED state."""
        now = datetime.now()
        with pytest.raises(
            ValueError,
            match="Approval resulting_state must be APPROVED"
        ):
            Approval(
                approval_id="appr-017",
                proposal_id="prop-017",
                approved_by="user",
                approved_at=now,
                resulting_state=State.BLOCKED,
            )


class TestApprovalInvalidProposalState:
    """Test that only WAITING_APPROVAL proposals can be approved."""
    
    def _create_proposal_in_state(self, proposal_id: str, state: State, now: datetime) -> "Proposal":
        """Helper to create a proposal in a specific state (for testing only)."""
        from orchestrator.proposal import Proposal
        # Create in WAITING_APPROVAL first (required by design)
        proposal = Proposal(
            proposal_id=proposal_id,
            repo_head="head",
            patch_hash="hash",
            requested_action="action",
            created_at=now,
            status=State.WAITING_APPROVAL,
        )
        # Use object.__setattr__ to bypass frozen dataclass for testing
        # This simulates a proposal that has been transitioned through state machine
        if state != State.WAITING_APPROVAL:
            object.__setattr__(proposal, 'status', state)
        return proposal
    
    def test_cannot_approve_proposed_proposal(self):
        """Test that PROPOSED proposal cannot be approved."""
        now = datetime.now()
        proposed = self._create_proposal_in_state("prop-018", State.PROPOSED, now)
        
        with pytest.raises(
            ValueError,
            match="Cannot approve proposal in PROPOSED state"
        ):
            approve_proposal(
                approval_id="appr-018",
                proposal=proposed,
                approved_by="user",
                approved_at=now,
            )
    
    def test_cannot_approve_approved_proposal(self):
        """Test that APPROVED proposal cannot be re-approved."""
        now = datetime.now()
        approved = self._create_proposal_in_state("prop-019", State.APPROVED, now)
        
        with pytest.raises(
            ValueError,
            match="Cannot approve proposal in APPROVED state"
        ):
            approve_proposal(
                approval_id="appr-019",
                proposal=approved,
                approved_by="user",
                approved_at=now,
            )
    
    def test_cannot_approve_executing_proposal(self):
        """Test that EXECUTING proposal cannot be approved."""
        now = datetime.now()
        executing = self._create_proposal_in_state("prop-020", State.EXECUTING, now)
        
        with pytest.raises(
            ValueError,
            match="Cannot approve proposal in EXECUTING state"
        ):
            approve_proposal(
                approval_id="appr-020",
                proposal=executing,
                approved_by="user",
                approved_at=now,
            )
    
    def test_cannot_approve_executed_proposal(self):
        """Test that EXECUTED proposal cannot be approved."""
        now = datetime.now()
        executed = self._create_proposal_in_state("prop-021", State.EXECUTED, now)
        
        with pytest.raises(
            ValueError,
            match="Cannot approve proposal in EXECUTED state"
        ):
            approve_proposal(
                approval_id="appr-021",
                proposal=executed,
                approved_by="user",
                approved_at=now,
            )
    
    def test_cannot_approve_rejected_proposal(self):
        """Test that REJECTED proposal cannot be approved."""
        now = datetime.now()
        rejected = self._create_proposal_in_state("prop-022", State.REJECTED, now)
        
        with pytest.raises(
            ValueError,
            match="Cannot approve proposal in REJECTED state"
        ):
            approve_proposal(
                approval_id="appr-022",
                proposal=rejected,
                approved_by="user",
                approved_at=now,
            )
    
    def test_cannot_approve_blocked_proposal(self):
        """Test that BLOCKED proposal cannot be approved."""
        now = datetime.now()
        blocked = self._create_proposal_in_state("prop-023", State.BLOCKED, now)
        
        with pytest.raises(
            ValueError,
            match="Cannot approve proposal in BLOCKED state"
        ):
            approve_proposal(
                approval_id="appr-023",
                proposal=blocked,
                approved_by="user",
                approved_at=now,
            )


class TestApprovalImmutability:
    """Test approval immutability guarantees."""
    
    def test_approval_is_immutable_frozen_dataclass(self):
        """Test that approval cannot be modified after creation."""
        now = datetime.now()
        approval = Approval(
            approval_id="appr-024",
            proposal_id="prop-024",
            approved_by="user",
            approved_at=now,
            resulting_state=State.APPROVED,
        )
        
        # Attempt to modify a field should raise FrozenInstanceError
        with pytest.raises(FrozenInstanceError):
            approval.approval_id = "modified"
    
    def test_approval_cannot_modify_proposal_id(self):
        """Test that approval proposal_id cannot be modified."""
        now = datetime.now()
        approval = Approval(
            approval_id="appr-025",
            proposal_id="prop-025",
            approved_by="user",
            approved_at=now,
            resulting_state=State.APPROVED,
        )
        
        with pytest.raises(FrozenInstanceError):
            approval.proposal_id = "modified"
    
    def test_approval_cannot_modify_approved_by(self):
        """Test that approval approved_by cannot be modified."""
        now = datetime.now()
        approval = Approval(
            approval_id="appr-026",
            proposal_id="prop-026",
            approved_by="user",
            approved_at=now,
            resulting_state=State.APPROVED,
        )
        
        with pytest.raises(FrozenInstanceError):
            approval.approved_by = "different_user"
    
    def test_approval_cannot_modify_approved_at(self):
        """Test that approval approved_at cannot be modified."""
        now = datetime.now()
        approval = Approval(
            approval_id="appr-027",
            proposal_id="prop-027",
            approved_by="user",
            approved_at=now,
            resulting_state=State.APPROVED,
        )
        
        with pytest.raises(FrozenInstanceError):
            approval.approved_at = datetime.now() + timedelta(hours=1)
    
    def test_approval_cannot_modify_resulting_state(self):
        """Test that approval resulting_state cannot be modified."""
        now = datetime.now()
        approval = Approval(
            approval_id="appr-028",
            proposal_id="prop-028",
            approved_by="user",
            approved_at=now,
            resulting_state=State.APPROVED,
        )
        
        with pytest.raises(FrozenInstanceError):
            approval.resulting_state = State.EXECUTED


class TestExecutionAuthority:
    """Test that approvals have no execution authority."""
    
    def test_approval_has_no_execution_authority(self):
        """Test that approval never has execution authority."""
        now = datetime.now()
        approval = Approval(
            approval_id="appr-029",
            proposal_id="prop-029",
            approved_by="user",
            approved_at=now,
            resulting_state=State.APPROVED,
        )
        
        assert approval.has_execution_authority is False
    
    def test_approval_cannot_execute_anything(self):
        """Test that approval has no execution methods."""
        now = datetime.now()
        approval = Approval(
            approval_id="appr-030",
            proposal_id="prop-030",
            approved_by="user",
            approved_at=now,
            resulting_state=State.APPROVED,
        )
        
        # Approval should have no methods to execute or modify state
        assert not hasattr(approval, 'execute')
        assert not hasattr(approval, 'transition')
        assert not hasattr(approval, 'auto_execute')
        assert not callable(getattr(approval, 'execute', None))


class TestApprovalDeterminism:
    """Test approval follows deterministic semantics."""
    
    def test_approval_validates_determinism(self):
        """Test that validate_determinism method can be called."""
        now = datetime.now()
        approval = Approval(
            approval_id="appr-031",
            proposal_id="prop-031",
            approved_by="user",
            approved_at=now,
            resulting_state=State.APPROVED,
        )
        
        # Should not raise - this is a documentation method
        approval.validate_determinism()
    
    def test_approval_does_not_auto_execute(self):
        """Test that approval alone does not execute anything."""
        now = datetime.now()
        proposal = create_proposal(
            proposal_id="prop-032",
            repo_head="head",
            patch_hash="hash",
            requested_action="Deploy",
            created_at=now,
        )
        
        approval = approve_proposal(
            approval_id="appr-032",
            proposal=proposal,
            approved_by="user",
            approved_at=now,
        )
        
        # After approval, proposal is still in WAITING_APPROVAL
        # (approval doesn't transition state - that's the state machine's job)
        assert proposal.status == State.WAITING_APPROVAL
        assert approval.resulting_state == State.APPROVED


class TestApprovalProperties:
    """Test approval properties and metadata."""
    
    def test_approval_fields_accessible(self):
        """Test that all approval fields are readable."""
        now = datetime.now()
        approval = Approval(
            approval_id="appr-033",
            proposal_id="prop-033",
            approved_by="reviewer@example.com",
            approved_at=now,
            resulting_state=State.APPROVED,
        )
        
        assert approval.approval_id == "appr-033"
        assert approval.proposal_id == "prop-033"
        assert approval.approved_by == "reviewer@example.com"
        assert approval.approved_at == now
        assert approval.resulting_state == State.APPROVED


class TestApprovalCannotBypassFlow:
    """Test that approval cannot bypass deterministic flow."""
    
    def test_approval_respects_proposal_immutability(self):
        """Test that approval cannot modify original proposal."""
        now = datetime.now()
        proposal = create_proposal(
            proposal_id="prop-034",
            repo_head="original",
            patch_hash="hash",
            requested_action="action",
            created_at=now,
        )
        
        approval = approve_proposal(
            approval_id="appr-034",
            proposal=proposal,
            approved_by="user",
            approved_at=now,
        )
        
        # Proposal should remain unchanged and immutable
        assert proposal.proposal_id == "prop-034"
        assert proposal.repo_head == "original"
        assert proposal.status == State.WAITING_APPROVAL
        
        # Cannot modify proposal through approval
        assert approval.resulting_state == State.APPROVED
        assert proposal.status == State.WAITING_APPROVAL
    
    def test_approval_references_proposal_not_mutates(self):
        """Test that approval references proposal without mutating."""
        now = datetime.now()
        proposal = create_proposal(
            proposal_id="prop-035",
            repo_head="head",
            patch_hash="hash",
            requested_action="action",
            created_at=now,
        )
        
        approval = approve_proposal(
            approval_id="appr-035",
            proposal=proposal,
            approved_by="user",
            approved_at=now,
        )
        
        # Approval contains proposal_id reference only
        assert approval.proposal_id == proposal.proposal_id
        # But cannot modify the proposal
        with pytest.raises(FrozenInstanceError):
            proposal.status = State.APPROVED


class TestApproveProposalHelper:
    """Test the approve_proposal helper function."""
    
    def test_approve_proposal_validates_waiting_approval(self):
        """Test that approve_proposal validates WAITING_APPROVAL state."""
        now = datetime.now()
        proposal = create_proposal(
            proposal_id="prop-036",
            repo_head="head",
            patch_hash="hash",
            requested_action="action",
            created_at=now,
        )
        
        # Should succeed with WAITING_APPROVAL proposal
        approval = approve_proposal(
            approval_id="appr-036",
            proposal=proposal,
            approved_by="user",
            approved_at=now,
        )
        
        assert approval.approval_id == "appr-036"
        assert approval.resulting_state == State.APPROVED
    
    def test_approve_proposal_validates_all_fields(self):
        """Test that approve_proposal validates all fields."""
        now = datetime.now()
        proposal = create_proposal(
            proposal_id="prop-037",
            repo_head="head",
            patch_hash="hash",
            requested_action="action",
            created_at=now,
        )
        
        with pytest.raises(ValueError, match="approval_id cannot be empty"):
            approve_proposal(
                approval_id="",
                proposal=proposal,
                approved_by="user",
                approved_at=now,
            )
    
    def test_approve_proposal_with_various_approvers(self):
        """Test approving with different approver identifiers."""
        now = datetime.now()
        
        proposal1 = create_proposal(
            proposal_id="prop-038",
            repo_head="head",
            patch_hash="hash",
            requested_action="action",
            created_at=now,
        )
        
        proposal2 = create_proposal(
            proposal_id="prop-039",
            repo_head="head",
            patch_hash="hash",
            requested_action="action",
            created_at=now,
        )
        
        approval1 = approve_proposal(
            approval_id="appr-038",
            proposal=proposal1,
            approved_by="user@example.com",
            approved_at=now,
        )
        
        approval2 = approve_proposal(
            approval_id="appr-039",
            proposal=proposal2,
            approved_by="system:auto-approver",
            approved_at=now,
        )
        
        assert approval1.approved_by == "user@example.com"
        assert approval2.approved_by == "system:auto-approver"


class TestApprovalIntegration:
    """Test approval integration with proposal and state machine."""
    
    def test_approval_flow_with_proposal(self):
        """Test complete approval flow with proposal."""
        now = datetime.now()
        
        # Create proposal
        proposal = create_proposal(
            proposal_id="prop-040",
            repo_head="main:abc123",
            patch_hash="sha256:def456",
            requested_action="Deploy service",
            created_at=now,
        )
        
        # Proposal starts in WAITING_APPROVAL
        assert proposal.status == State.WAITING_APPROVAL
        assert proposal.requires_approval is True
        
        # Register approval
        approval = approve_proposal(
            approval_id="appr-040",
            proposal=proposal,
            approved_by="admin@example.com",
            approved_at=now + timedelta(minutes=5),
        )
        
        # Approval records the authorization
        assert approval.approval_id == "appr-040"
        assert approval.proposal_id == "prop-040"
        assert approval.approved_by == "admin@example.com"
        assert approval.resulting_state == State.APPROVED
        
        # Proposal remains unchanged (approval doesn't transition)
        assert proposal.status == State.WAITING_APPROVAL
