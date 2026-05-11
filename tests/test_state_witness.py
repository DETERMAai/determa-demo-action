import pytest
from datetime import datetime, timedelta
from dataclasses import FrozenInstanceError
from executor.state_witness import StateWitness, ValidationResult, validate_repository_state


class TestValidationResult:
    """Test ValidationResult enum."""
    
    def test_valid_enum_value(self):
        """Test VALID enum value."""
        assert ValidationResult.VALID.value == "VALID"
    
    def test_invalid_enum_value(self):
        """Test INVALID enum value."""
        assert ValidationResult.INVALID.value == "INVALID"


class TestStateWitnessCreation:
    """Test state witness creation and validation."""
    
    def test_create_valid_matching_heads(self):
        """Test creating witness with matching repo heads."""
        now = datetime.now()
        head = "abc123def456"
        
        witness = StateWitness(
            approved_repo_head=head,
            current_repo_head=head,
            validation_result=ValidationResult.VALID,
            validated_at=now,
        )
        
        assert witness.approved_repo_head == head
        assert witness.current_repo_head == head
        assert witness.validation_result == ValidationResult.VALID
        assert witness.validated_at == now
    
    def test_create_invalid_mismatched_heads(self):
        """Test creating witness with mismatched repo heads."""
        now = datetime.now()
        approved = "abc123"
        current = "def456"
        
        witness = StateWitness(
            approved_repo_head=approved,
            current_repo_head=current,
            validation_result=ValidationResult.INVALID,
            validated_at=now,
        )
        
        assert witness.approved_repo_head == approved
        assert witness.current_repo_head == current
        assert witness.validation_result == ValidationResult.INVALID
        assert witness.validated_at == now


class TestStateWitnessValidation:
    """Test state witness validation semantics."""
    
    def test_matching_heads_require_valid_result(self):
        """Test that matching heads must have VALID result."""
        now = datetime.now()
        head = "abc123"
        
        # Should fail if heads match but result is INVALID
        with pytest.raises(ValueError, match="validation_result must be VALID"):
            StateWitness(
                approved_repo_head=head,
                current_repo_head=head,
                validation_result=ValidationResult.INVALID,
                validated_at=now,
            )
    
    def test_mismatched_heads_require_invalid_result(self):
        """Test that mismatched heads must have INVALID result."""
        now = datetime.now()
        
        # Should fail if heads differ but result is VALID
        with pytest.raises(ValueError, match="validation_result must be INVALID"):
            StateWitness(
                approved_repo_head="abc123",
                current_repo_head="def456",
                validation_result=ValidationResult.VALID,
                validated_at=now,
            )
    
    def test_empty_approved_repo_head_fails(self):
        """Test that empty approved_repo_head fails validation."""
        now = datetime.now()
        
        with pytest.raises(ValueError, match="approved_repo_head cannot be empty"):
            StateWitness(
                approved_repo_head="",
                current_repo_head="abc123",
                validation_result=ValidationResult.VALID,
                validated_at=now,
            )
    
    def test_non_string_approved_repo_head_fails(self):
        """Test that non-string approved_repo_head fails validation."""
        now = datetime.now()
        
        with pytest.raises(ValueError, match="approved_repo_head must be string"):
            StateWitness(
                approved_repo_head=123,  # type: ignore
                current_repo_head="abc123",
                validation_result=ValidationResult.VALID,
                validated_at=now,
            )
    
    def test_empty_current_repo_head_fails(self):
        """Test that empty current_repo_head fails validation."""
        now = datetime.now()
        
        with pytest.raises(ValueError, match="current_repo_head cannot be empty"):
            StateWitness(
                approved_repo_head="abc123",
                current_repo_head="",
                validation_result=ValidationResult.VALID,
                validated_at=now,
            )
    
    def test_non_string_current_repo_head_fails(self):
        """Test that non-string current_repo_head fails validation."""
        now = datetime.now()
        
        with pytest.raises(ValueError, match="current_repo_head must be string"):
            StateWitness(
                approved_repo_head="abc123",
                current_repo_head=456,  # type: ignore
                validation_result=ValidationResult.VALID,
                validated_at=now,
            )
    
    def test_invalid_validation_result_fails(self):
        """Test that invalid validation_result type fails validation."""
        now = datetime.now()
        
        with pytest.raises(ValueError, match="validation_result must be ValidationResult enum"):
            StateWitness(
                approved_repo_head="abc123",
                current_repo_head="abc123",
                validation_result="VALID",  # type: ignore
                validated_at=now,
            )
    
    def test_non_datetime_validated_at_fails(self):
        """Test that non-datetime validated_at fails validation."""
        with pytest.raises(ValueError, match="validated_at must be datetime object"):
            StateWitness(
                approved_repo_head="abc123",
                current_repo_head="abc123",
                validation_result=ValidationResult.VALID,
                validated_at="2024-01-01",  # type: ignore
            )


class TestRepositoryDriftDetection:
    """Test repository drift detection."""
    
    def test_matching_heads_no_drift(self):
        """Test that matching heads indicate no drift."""
        now = datetime.now()
        head = "abc123def456"
        
        witness = StateWitness(
            approved_repo_head=head,
            current_repo_head=head,
            validation_result=ValidationResult.VALID,
            validated_at=now,
        )
        
        assert witness.is_valid is True
        assert witness.repository_drift_detected is False
        assert witness.permits_execution is True
    
    def test_mismatched_heads_drift_detected(self):
        """Test that mismatched heads indicate drift."""
        now = datetime.now()
        
        witness = StateWitness(
            approved_repo_head="abc123",
            current_repo_head="def456",
            validation_result=ValidationResult.INVALID,
            validated_at=now,
        )
        
        assert witness.is_valid is False
        assert witness.repository_drift_detected is True
        assert witness.permits_execution is False


class TestExecutionPermission:
    """Test execution permission semantics."""
    
    def test_valid_witness_permits_execution(self):
        """Test that valid witness permits execution."""
        now = datetime.now()
        head = "sha256:abc123"
        
        witness = StateWitness(
            approved_repo_head=head,
            current_repo_head=head,
            validation_result=ValidationResult.VALID,
            validated_at=now,
        )
        
        assert witness.permits_execution is True
    
    def test_invalid_witness_blocks_execution(self):
        """Test that invalid witness blocks execution."""
        now = datetime.now()
        
        witness = StateWitness(
            approved_repo_head="abc123",
            current_repo_head="def456",
            validation_result=ValidationResult.INVALID,
            validated_at=now,
        )
        
        assert witness.permits_execution is False


class TestStateWitnessImmutability:
    """Test state witness immutability."""
    
    def test_witness_is_immutable_frozen_dataclass(self):
        """Test that witness cannot be modified after creation."""
        now = datetime.now()
        
        witness = StateWitness(
            approved_repo_head="abc123",
            current_repo_head="abc123",
            validation_result=ValidationResult.VALID,
            validated_at=now,
        )
        
        with pytest.raises(FrozenInstanceError):
            witness.approved_repo_head = "modified"
    
    def test_cannot_modify_current_repo_head(self):
        """Test that current_repo_head cannot be modified."""
        now = datetime.now()
        
        witness = StateWitness(
            approved_repo_head="abc123",
            current_repo_head="abc123",
            validation_result=ValidationResult.VALID,
            validated_at=now,
        )
        
        with pytest.raises(FrozenInstanceError):
            witness.current_repo_head = "modified"
    
    def test_cannot_modify_validation_result(self):
        """Test that validation_result cannot be modified."""
        now = datetime.now()
        
        witness = StateWitness(
            approved_repo_head="abc123",
            current_repo_head="abc123",
            validation_result=ValidationResult.VALID,
            validated_at=now,
        )
        
        with pytest.raises(FrozenInstanceError):
            witness.validation_result = ValidationResult.INVALID
    
    def test_cannot_modify_validated_at(self):
        """Test that validated_at cannot be modified."""
        now = datetime.now()
        
        witness = StateWitness(
            approved_repo_head="abc123",
            current_repo_head="abc123",
            validation_result=ValidationResult.VALID,
            validated_at=now,
        )
        
        with pytest.raises(FrozenInstanceError):
            witness.validated_at = datetime.now() + timedelta(hours=1)


class TestDeterministicValidation:
    """Test deterministic validation semantics."""
    
    def test_same_inputs_same_output(self):
        """Test that same inputs always produce same validation result."""
        now = datetime.now()
        approved = "abc123"
        current = "abc123"
        
        witness1 = validate_repository_state(approved, current, now)
        witness2 = validate_repository_state(approved, current, now)
        
        assert witness1.validation_result == witness2.validation_result
        assert witness1.is_valid == witness2.is_valid
    
    def test_drift_always_invalid(self):
        """Test that drift always results in INVALID."""
        now = datetime.now()
        
        # Any mismatch should always produce INVALID
        witness = validate_repository_state(
            "abc123",
            "def456",
            now,
        )
        
        assert witness.validation_result == ValidationResult.INVALID
        assert witness.is_valid is False
    
    def test_repeated_validation_same_state(self):
        """Test that repeated validation of same state is deterministic."""
        now = datetime.now()
        head = "abc123"
        
        results = []
        for _ in range(5):
            witness = validate_repository_state(head, head, now)
            results.append(witness.is_valid)
        
        # All validations should be consistent
        assert all(result is True for result in results)
    
    def test_repeated_validation_different_state(self):
        """Test that repeated validation of drift is deterministic."""
        now = datetime.now()
        
        results = []
        for _ in range(5):
            witness = validate_repository_state("abc123", "def456", now)
            results.append(witness.is_valid)
        
        # All validations should be consistent
        assert all(result is False for result in results)


class TestFailClosedSemantics:
    """Test fail-closed behavior."""
    
    def test_any_mismatch_blocks_execution(self):
        """Test that any HEAD mismatch blocks execution."""
        now = datetime.now()
        
        # Entire HEAD changed
        witness1 = validate_repository_state(
            "main:abc123",
            "main:def456",
            now,
        )
        assert witness1.permits_execution is False
        
        # Branch name matches, hash differs
        witness2 = validate_repository_state(
            "abc123",
            "abc124",  # Single character different
            now,
        )
        assert witness2.permits_execution is False
        
        # Empty mismatch should also fail
        with pytest.raises(ValueError):
            validate_repository_state("", "abc123", now)
    
    def test_whitespace_sensitive_comparison(self):
        """Test that whitespace differences block execution."""
        now = datetime.now()
        
        witness = validate_repository_state(
            "abc123",
            "abc123 ",  # Trailing space
            now,
        )
        
        assert witness.is_valid is False
        assert witness.permits_execution is False


class TestValidateRepositoryStateHelper:
    """Test the validate_repository_state helper function."""
    
    def test_matching_heads_valid_witness(self):
        """Test creating valid witness with matching heads."""
        now = datetime.now()
        head = "abc123"
        
        witness = validate_repository_state(head, head, now)
        
        assert witness.approved_repo_head == head
        assert witness.current_repo_head == head
        assert witness.validation_result == ValidationResult.VALID
        assert witness.validated_at == now
    
    def test_mismatched_heads_invalid_witness(self):
        """Test creating invalid witness with mismatched heads."""
        now = datetime.now()
        approved = "abc123"
        current = "def456"
        
        witness = validate_repository_state(approved, current, now)
        
        assert witness.approved_repo_head == approved
        assert witness.current_repo_head == current
        assert witness.validation_result == ValidationResult.INVALID
        assert witness.validated_at == now
    
    def test_helper_validates_all_fields(self):
        """Test that helper validates all required fields."""
        now = datetime.now()
        
        with pytest.raises(ValueError, match="approved_repo_head cannot be empty"):
            validate_repository_state("", "abc123", now)
        
        with pytest.raises(ValueError, match="current_repo_head cannot be empty"):
            validate_repository_state("abc123", "", now)


class TestRepositoryHeadFormats:
    """Test various repository HEAD formats."""
    
    def test_short_sha_heads(self):
        """Test with short SHA format."""
        now = datetime.now()
        head = "abc123"
        
        witness = validate_repository_state(head, head, now)
        assert witness.is_valid is True
    
    def test_full_sha_heads(self):
        """Test with full SHA format."""
        now = datetime.now()
        head = "abc123def456789abc123def456789abc12345"
        
        witness = validate_repository_state(head, head, now)
        assert witness.is_valid is True
    
    def test_branch_qualified_heads(self):
        """Test with branch:sha format."""
        now = datetime.now()
        head = "main:abc123def456"
        
        witness = validate_repository_state(head, head, now)
        assert witness.is_valid is True
    
    def test_long_ref_paths(self):
        """Test with long reference paths."""
        now = datetime.now()
        head = "refs/heads/feature/my-feature:abc123"
        
        witness = validate_repository_state(head, head, now)
        assert witness.is_valid is True
    
    def test_mismatched_formats_fail(self):
        """Test that different formats fail."""
        now = datetime.now()
        
        # Different formats should fail
        witness = validate_repository_state(
            "main:abc123",
            "abc123",
            now,
        )
        
        assert witness.is_valid is False


class TestExecutionBlockingSemantics:
    """Test execution blocking on drift."""
    
    def test_no_execution_on_drift(self):
        """Test that execution is blocked on any drift."""
        now = datetime.now()
        
        witness = validate_repository_state(
            "approved_version",
            "current_version",
            now,
        )
        
        # Execution must be blocked
        assert witness.permits_execution is False
        
        # Drift must be detected
        assert witness.repository_drift_detected is True
    
    def test_no_mutation_authority_on_invalid_witness(self):
        """Test that invalid witness has no mutation authority."""
        now = datetime.now()
        
        witness = validate_repository_state(
            "abc123",
            "def456",
            now,
        )
        
        # Invalid witness should not permit any operations
        assert witness.permits_execution is False
        
        # Should have no methods that could mutate
        assert not hasattr(witness, 'execute')
        assert not hasattr(witness, 'approve')
        assert not callable(getattr(witness, 'execute', None))


class TestDeterminismProperties:
    """Test determinism properties."""
    
    def test_validate_determinism_method(self):
        """Test that validate_determinism method can be called."""
        now = datetime.now()
        
        witness = StateWitness(
            approved_repo_head="abc123",
            current_repo_head="abc123",
            validation_result=ValidationResult.VALID,
            validated_at=now,
        )
        
        # Should not raise - this is a documentation method
        witness.validate_determinism()
    
    def test_witness_properties_deterministic(self):
        """Test that witness properties are deterministic."""
        now = datetime.now()
        
        witness1 = validate_repository_state("abc123", "abc123", now)
        witness2 = validate_repository_state("abc123", "abc123", now)
        
        # Properties should be identical
        assert witness1.is_valid == witness2.is_valid
        assert witness1.repository_drift_detected == witness2.repository_drift_detected
        assert witness1.permits_execution == witness2.permits_execution


class TestStateWitnessIntegration:
    """Test state witness integration scenarios."""
    
    def test_approved_execution_with_valid_witness(self):
        """Test execution flow with valid witness."""
        now = datetime.now()
        repo_head = "main:abc123def456"
        
        # At approval time, HEAD is recorded
        approved_head = repo_head
        
        # At execution time, HEAD is checked
        current_head = repo_head
        
        # Validate witness
        witness = validate_repository_state(approved_head, current_head, now)
        
        # Execution should be permitted
        assert witness.is_valid is True
        assert witness.permits_execution is True
    
    def test_execution_blocked_with_repository_drift(self):
        """Test that execution is blocked when repository has drifted."""
        now = datetime.now()
        
        # Approved at this HEAD
        approved_head = "main:abc123"
        
        # But HEAD has changed
        current_head = "main:def456"
        
        # Validate witness
        witness = validate_repository_state(approved_head, current_head, now)
        
        # Execution must be blocked
        assert witness.is_valid is False
        assert witness.repository_drift_detected is True
        assert witness.permits_execution is False
    
    def test_witness_timestamps(self):
        """Test witness timestamps."""
        now1 = datetime.now()
        now2 = datetime.now() + timedelta(minutes=5)
        
        witness1 = validate_repository_state("abc123", "abc123", now1)
        witness2 = validate_repository_state("abc123", "abc123", now2)
        
        assert witness1.validated_at == now1
        assert witness2.validated_at == now2
        assert witness1.validated_at < witness2.validated_at
    
    def test_witness_preserves_repo_information(self):
        """Test that witness preserves repository information."""
        now = datetime.now()
        approved = "feature:abc123"
        current = "feature:abc123"
        
        witness = validate_repository_state(approved, current, now)
        
        assert witness.approved_repo_head == approved
        assert witness.current_repo_head == current
        assert "feature" in witness.approved_repo_head
        assert "abc123" in witness.current_repo_head
