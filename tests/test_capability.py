import pytest
from datetime import datetime, timedelta
from dataclasses import FrozenInstanceError
from executor.capability import Capability, issue_capability, consume_capability


class TestCapabilityCreation:
    """Test capability creation and issuance."""
    
    def test_issue_valid_capability(self):
        """Test issuing a valid capability."""
        now = datetime.now()
        
        capability = issue_capability(
            capability_id="cap-001",
            proposal_id="prop-001",
            repo_head="abc123",
            issued_at=now,
        )
        
        assert capability.capability_id == "cap-001"
        assert capability.proposal_id == "prop-001"
        assert capability.repo_head == "abc123"
        assert capability.issued_at == now
        assert capability.consumed is False
        assert capability.consumed_at is None
    
    def test_capability_starts_unconsumed(self):
        """Test that new capability starts as unconsumed."""
        now = datetime.now()
        
        capability = issue_capability(
            capability_id="cap-002",
            proposal_id="prop-002",
            repo_head="head",
            issued_at=now,
        )
        
        assert capability.consumed is False
        assert capability.consumed_at is None
        assert capability.is_valid is True
    
    def test_create_consumed_capability_directly(self):
        """Test creating a consumed capability directly."""
        now = datetime.now()
        consumed_time = now + timedelta(minutes=1)
        
        capability = Capability(
            capability_id="cap-003",
            proposal_id="prop-003",
            repo_head="head",
            issued_at=now,
            consumed=True,
            consumed_at=consumed_time,
        )
        
        assert capability.consumed is True
        assert capability.consumed_at == consumed_time
        assert capability.is_valid is False


class TestCapabilityValidation:
    """Test capability validation and field requirements."""
    
    def test_empty_capability_id_fails(self):
        """Test that empty capability_id fails validation."""
        now = datetime.now()
        
        with pytest.raises(ValueError, match="capability_id cannot be empty"):
            Capability(
                capability_id="",
                proposal_id="prop-001",
                repo_head="head",
                issued_at=now,
                consumed=False,
                consumed_at=None,
            )
    
    def test_non_string_capability_id_fails(self):
        """Test that non-string capability_id fails validation."""
        now = datetime.now()
        
        with pytest.raises(ValueError, match="capability_id must be string"):
            Capability(
                capability_id=123,  # type: ignore
                proposal_id="prop-001",
                repo_head="head",
                issued_at=now,
                consumed=False,
                consumed_at=None,
            )
    
    def test_empty_proposal_id_fails(self):
        """Test that empty proposal_id fails validation."""
        now = datetime.now()
        
        with pytest.raises(ValueError, match="proposal_id cannot be empty"):
            Capability(
                capability_id="cap-001",
                proposal_id="",
                repo_head="head",
                issued_at=now,
                consumed=False,
                consumed_at=None,
            )
    
    def test_non_string_proposal_id_fails(self):
        """Test that non-string proposal_id fails validation."""
        now = datetime.now()
        
        with pytest.raises(ValueError, match="proposal_id must be string"):
            Capability(
                capability_id="cap-001",
                proposal_id=456,  # type: ignore
                repo_head="head",
                issued_at=now,
                consumed=False,
                consumed_at=None,
            )
    
    def test_empty_repo_head_fails(self):
        """Test that empty repo_head fails validation."""
        now = datetime.now()
        
        with pytest.raises(ValueError, match="repo_head cannot be empty"):
            Capability(
                capability_id="cap-001",
                proposal_id="prop-001",
                repo_head="",
                issued_at=now,
                consumed=False,
                consumed_at=None,
            )
    
    def test_non_string_repo_head_fails(self):
        """Test that non-string repo_head fails validation."""
        now = datetime.now()
        
        with pytest.raises(ValueError, match="repo_head must be string"):
            Capability(
                capability_id="cap-001",
                proposal_id="prop-001",
                repo_head=789,  # type: ignore
                issued_at=now,
                consumed=False,
                consumed_at=None,
            )
    
    def test_non_datetime_issued_at_fails(self):
        """Test that non-datetime issued_at fails validation."""
        with pytest.raises(ValueError, match="issued_at must be datetime object"):
            Capability(
                capability_id="cap-001",
                proposal_id="prop-001",
                repo_head="head",
                issued_at="2024-01-01",  # type: ignore
                consumed=False,
                consumed_at=None,
            )
    
    def test_non_boolean_consumed_fails(self):
        """Test that non-boolean consumed fails validation."""
        now = datetime.now()
        
        with pytest.raises(ValueError, match="consumed must be boolean"):
            Capability(
                capability_id="cap-001",
                proposal_id="prop-001",
                repo_head="head",
                issued_at=now,
                consumed="False",  # type: ignore
                consumed_at=None,
            )


class TestSingleUseSemantics:
    """Test single-use and consumption semantics."""
    
    def test_unconsumed_capability_requires_consumed_at_none(self):
        """Test that unconsumed capability must have consumed_at=None."""
        now = datetime.now()
        
        with pytest.raises(ValueError, match="consumed_at=None"):
            Capability(
                capability_id="cap-001",
                proposal_id="prop-001",
                repo_head="head",
                issued_at=now,
                consumed=False,
                consumed_at=now,  # Should be None
            )
    
    def test_consumed_capability_requires_consumed_at_set(self):
        """Test that consumed capability must have consumed_at set."""
        now = datetime.now()
        
        with pytest.raises(ValueError, match="Consumed capability must have consumed_at set"):
            Capability(
                capability_id="cap-001",
                proposal_id="prop-001",
                repo_head="head",
                issued_at=now,
                consumed=True,
                consumed_at=None,  # Should be set
            )
    
    def test_consumed_at_after_issued_at(self):
        """Test that consumed_at is after issued_at."""
        now = datetime.now()
        past = now - timedelta(hours=1)
        
        with pytest.raises(ValueError, match="consumed_at must be after"):
            Capability(
                capability_id="cap-001",
                proposal_id="prop-001",
                repo_head="head",
                issued_at=now,
                consumed=True,
                consumed_at=past,
            )
    
    def test_consumed_at_equal_to_issued_at_valid(self):
        """Test that consumed_at equal to issued_at is valid."""
        now = datetime.now()
        
        capability = Capability(
            capability_id="cap-001",
            proposal_id="prop-001",
            repo_head="head",
            issued_at=now,
            consumed=True,
            consumed_at=now,
        )
        
        assert capability.consumed is True
        assert capability.consumed_at == now


class TestCapabilityConsumption:
    """Test capability consumption mechanism."""
    
    def test_consume_valid_capability(self):
        """Test consuming a valid unused capability."""
        now = datetime.now()
        consumed_time = now + timedelta(minutes=1)
        
        capability = issue_capability(
            capability_id="cap-004",
            proposal_id="prop-004",
            repo_head="head",
            issued_at=now,
        )
        
        consumed_capability = consume_capability(capability, consumed_time)
        
        assert consumed_capability.capability_id == "cap-004"
        assert consumed_capability.consumed is True
        assert consumed_capability.consumed_at == consumed_time
    
    def test_consume_capability_once_only(self):
        """Test that capability may be consumed once only."""
        now = datetime.now()
        
        capability = issue_capability(
            capability_id="cap-005",
            proposal_id="prop-005",
            repo_head="head",
            issued_at=now,
        )
        
        # First consumption succeeds
        consumed = consume_capability(capability, now + timedelta(minutes=1))
        assert consumed.consumed is True
        
        # Second consumption fails
        with pytest.raises(ValueError, match="already been consumed"):
            consume_capability(consumed, now + timedelta(minutes=2))
    
    def test_replay_attempts_blocked(self):
        """Test that replay attempts are blocked."""
        now = datetime.now()
        
        capability = issue_capability(
            capability_id="cap-006",
            proposal_id="prop-006",
            repo_head="head",
            issued_at=now,
        )
        
        # Consume the capability
        consumed = consume_capability(capability, now + timedelta(minutes=1))
        
        # Attempting to consume same capability ID again fails
        # (simulating replay attack)
        with pytest.raises(ValueError, match="Replay blocked"):
            consume_capability(consumed, now + timedelta(minutes=2))
    
    def test_consumed_capability_invalid_forever(self):
        """Test that consumed capability is permanently invalid."""
        now = datetime.now()
        
        capability = issue_capability(
            capability_id="cap-007",
            proposal_id="prop-007",
            repo_head="head",
            issued_at=now,
        )
        
        consumed = consume_capability(capability, now + timedelta(minutes=1))
        
        # Consumed capability is invalid and blocks all operations
        assert consumed.is_valid is False
        assert consumed.is_consumed is True
        assert consumed.permits_execution is False


class TestCapabilityValidity:
    """Test capability validity properties."""
    
    def test_unused_capability_is_valid(self):
        """Test that unused capability is valid."""
        now = datetime.now()
        
        capability = issue_capability(
            capability_id="cap-008",
            proposal_id="prop-008",
            repo_head="head",
            issued_at=now,
        )
        
        assert capability.is_valid is True
        assert capability.is_consumed is False
        assert capability.permits_execution is True
    
    def test_consumed_capability_is_invalid(self):
        """Test that consumed capability is invalid."""
        now = datetime.now()
        
        capability = issue_capability(
            capability_id="cap-009",
            proposal_id="prop-009",
            repo_head="head",
            issued_at=now,
        )
        
        consumed = consume_capability(capability, now + timedelta(minutes=1))
        
        assert consumed.is_valid is False
        assert consumed.is_consumed is True
        assert consumed.permits_execution is False
    
    def test_replay_blocked_when_consumed(self):
        """Test that replay is blocked when capability consumed."""
        now = datetime.now()
        
        capability = issue_capability(
            capability_id="cap-010",
            proposal_id="prop-010",
            repo_head="head",
            issued_at=now,
        )
        
        assert capability.replay_blocked is False
        
        consumed = consume_capability(capability, now + timedelta(minutes=1))
        
        assert consumed.replay_blocked is True


class TestCapabilityImmutability:
    """Test capability immutability."""
    
    def test_capability_is_immutable_frozen_dataclass(self):
        """Test that capability cannot be modified after creation."""
        now = datetime.now()
        
        capability = issue_capability(
            capability_id="cap-011",
            proposal_id="prop-011",
            repo_head="head",
            issued_at=now,
        )
        
        with pytest.raises(FrozenInstanceError):
            capability.capability_id = "modified"
    
    def test_cannot_modify_consumed_status(self):
        """Test that consumed status cannot be modified."""
        now = datetime.now()
        
        capability = issue_capability(
            capability_id="cap-012",
            proposal_id="prop-012",
            repo_head="head",
            issued_at=now,
        )
        
        with pytest.raises(FrozenInstanceError):
            capability.consumed = True
    
    def test_cannot_modify_consumed_at(self):
        """Test that consumed_at cannot be modified."""
        now = datetime.now()
        
        capability = issue_capability(
            capability_id="cap-013",
            proposal_id="prop-013",
            repo_head="head",
            issued_at=now,
        )
        
        with pytest.raises(FrozenInstanceError):
            capability.consumed_at = now


class TestDeterministicConsumption:
    """Test deterministic consumption semantics."""
    
    def test_same_capability_id_blocked_on_replay(self):
        """Test that same capability_id cannot be reused."""
        now = datetime.now()
        
        capability1 = issue_capability(
            capability_id="cap-014",
            proposal_id="prop-014",
            repo_head="head",
            issued_at=now,
        )
        
        consumed1 = consume_capability(capability1, now + timedelta(minutes=1))
        
        # Attempting to consume same capability again fails
        with pytest.raises(ValueError, match="already been consumed"):
            consume_capability(consumed1, now + timedelta(minutes=2))
    
    def test_repeated_consumption_attempts_fail(self):
        """Test that repeated consumption attempts always fail."""
        now = datetime.now()
        
        capability = issue_capability(
            capability_id="cap-015",
            proposal_id="prop-015",
            repo_head="head",
            issued_at=now,
        )
        
        consumed = consume_capability(capability, now + timedelta(minutes=1))
        
        # Multiple attempts to consume should all fail
        for i in range(3):
            with pytest.raises(ValueError, match="already been consumed"):
                consume_capability(consumed, now + timedelta(minutes=2+i))


class TestFailClosedSemantics:
    """Test fail-closed behavior."""
    
    def test_invalid_capability_blocks_all_execution(self):
        """Test that invalid capability blocks all execution."""
        now = datetime.now()
        
        capability = issue_capability(
            capability_id="cap-016",
            proposal_id="prop-016",
            repo_head="head",
            issued_at=now,
        )
        
        consumed = consume_capability(capability, now + timedelta(minutes=1))
        
        # Consumed capability denies all execution
        assert consumed.permits_execution is False
        assert not hasattr(consumed, 'execute')
    
    def test_consumed_capability_has_no_mutations(self):
        """Test that consumed capability has no mutation methods."""
        now = datetime.now()
        
        capability = issue_capability(
            capability_id="cap-017",
            proposal_id="prop-017",
            repo_head="head",
            issued_at=now,
        )
        
        consumed = consume_capability(capability, now + timedelta(minutes=1))
        
        # Consumed capability should have no methods to perform mutations
        assert not hasattr(consumed, 'execute')
        assert not hasattr(consumed, 'mutate')
        assert not callable(getattr(consumed, 'execute', None))


class TestCapabilityMetadata:
    """Test capability metadata preservation."""
    
    def test_consumed_capability_preserves_metadata(self):
        """Test that consuming preserves original metadata."""
        now = datetime.now()
        consumed_time = now + timedelta(minutes=5)
        
        capability = issue_capability(
            capability_id="cap-018",
            proposal_id="prop-018",
            repo_head="main:abc123",
            issued_at=now,
        )
        
        consumed = consume_capability(capability, consumed_time)
        
        # Original metadata preserved
        assert consumed.capability_id == "cap-018"
        assert consumed.proposal_id == "prop-018"
        assert consumed.repo_head == "main:abc123"
        assert consumed.issued_at == now
        
        # Consumption recorded
        assert consumed.consumed is True
        assert consumed.consumed_at == consumed_time


class TestCapabilityProperties:
    """Test capability properties and queries."""
    
    def test_capability_fields_accessible(self):
        """Test that all capability fields are readable."""
        now = datetime.now()
        
        capability = issue_capability(
            capability_id="cap-019",
            proposal_id="prop-019",
            repo_head="head",
            issued_at=now,
        )
        
        assert capability.capability_id == "cap-019"
        assert capability.proposal_id == "prop-019"
        assert capability.repo_head == "head"
        assert capability.issued_at == now
        assert capability.consumed is False
        assert capability.consumed_at is None
    
    def test_consumed_capability_fields_accessible(self):
        """Test that consumed capability fields are accessible."""
        now = datetime.now()
        consumed_time = now + timedelta(minutes=1)
        
        capability = issue_capability(
            capability_id="cap-020",
            proposal_id="prop-020",
            repo_head="head",
            issued_at=now,
        )
        
        consumed = consume_capability(capability, consumed_time)
        
        assert consumed.capability_id == "cap-020"
        assert consumed.proposal_id == "prop-020"
        assert consumed.consumed is True
        assert consumed.consumed_at == consumed_time


class TestDeterminismProperties:
    """Test determinism properties."""
    
    def test_validate_determinism_method(self):
        """Test that validate_determinism method can be called."""
        now = datetime.now()
        
        capability = issue_capability(
            capability_id="cap-021",
            proposal_id="prop-021",
            repo_head="head",
            issued_at=now,
        )
        
        # Should not raise - this is a documentation method
        capability.validate_determinism()


class TestCapabilityIntegration:
    """Test capability integration scenarios."""
    
    def test_capability_lifecycle(self):
        """Test complete capability lifecycle."""
        now = datetime.now()
        
        # Issue capability
        capability = issue_capability(
            capability_id="cap-022",
            proposal_id="prop-022",
            repo_head="main:abc123",
            issued_at=now,
        )
        
        # Capability is valid and unused
        assert capability.is_valid is True
        assert capability.permits_execution is True
        
        # Consume capability
        consumed_time = now + timedelta(minutes=5)
        consumed = consume_capability(capability, consumed_time)
        
        # Capability is now consumed
        assert consumed.is_valid is False
        assert consumed.is_consumed is True
        assert consumed.permits_execution is False
        assert consumed.replay_blocked is True
        
        # Cannot consume again
        with pytest.raises(ValueError, match="already been consumed"):
            consume_capability(consumed, now + timedelta(minutes=10))
    
    def test_multiple_capabilities_independent(self):
        """Test that multiple capabilities are independent."""
        now = datetime.now()
        
        cap1 = issue_capability(
            capability_id="cap-023",
            proposal_id="prop-023",
            repo_head="head",
            issued_at=now,
        )
        
        cap2 = issue_capability(
            capability_id="cap-024",
            proposal_id="prop-024",
            repo_head="head",
            issued_at=now + timedelta(seconds=1),
        )
        
        # Both are valid
        assert cap1.is_valid is True
        assert cap2.is_valid is True
        
        # Consume first
        consumed1 = consume_capability(cap1, now + timedelta(minutes=1))
        
        # First is consumed, second is still valid
        assert consumed1.is_valid is False
        assert cap2.is_valid is True
        
        # Can consume second independently
        consumed2 = consume_capability(cap2, now + timedelta(minutes=2))
        assert consumed2.is_valid is False
    
    def test_capability_does_not_bypass_witness_validation(self):
        """Test that capability alone doesn't bypass witness validation."""
        now = datetime.now()
        
        capability = issue_capability(
            capability_id="cap-025",
            proposal_id="prop-025",
            repo_head="approved_head",
            issued_at=now,
        )
        
        # Capability records repo_head but doesn't validate it
        # Witness validation is separate and must be performed
        assert capability.repo_head == "approved_head"
        
        # Capability itself has no witness validation method
        assert not hasattr(capability, 'validate_witness')
    
    def test_capability_does_not_bypass_approval(self):
        """Test that capability doesn't bypass approval requirements."""
        now = datetime.now()
        
        capability = issue_capability(
            capability_id="cap-026",
            proposal_id="prop-026",
            repo_head="head",
            issued_at=now,
        )
        
        # Capability references proposal but doesn't validate approval
        assert capability.proposal_id == "prop-026"
        
        # Capability has no approval validation method
        assert not hasattr(capability, 'validate_approval')
