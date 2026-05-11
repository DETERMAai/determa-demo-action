import pytest
from orchestrator.state_machine import State, StateMachine


class TestStateTransitions:
    """Test valid state transitions."""
    
    def test_proposed_to_waiting_approval(self):
        """Test transition from PROPOSED to WAITING_APPROVAL."""
        sm = StateMachine()
        assert sm.state == State.PROPOSED
        sm.transition(State.WAITING_APPROVAL)
        assert sm.state == State.WAITING_APPROVAL
    
    def test_proposed_to_rejected(self):
        """Test transition from PROPOSED to REJECTED."""
        sm = StateMachine()
        sm.transition(State.REJECTED)
        assert sm.state == State.REJECTED
    
    def test_proposed_to_blocked(self):
        """Test transition from PROPOSED to BLOCKED."""
        sm = StateMachine()
        sm.transition(State.BLOCKED)
        assert sm.state == State.BLOCKED
    
    def test_waiting_approval_to_approved(self):
        """Test transition from WAITING_APPROVAL to APPROVED."""
        sm = StateMachine()
        sm.transition(State.WAITING_APPROVAL)
        sm.transition(State.APPROVED)
        assert sm.state == State.APPROVED
    
    def test_waiting_approval_to_rejected(self):
        """Test transition from WAITING_APPROVAL to REJECTED."""
        sm = StateMachine()
        sm.transition(State.WAITING_APPROVAL)
        sm.transition(State.REJECTED)
        assert sm.state == State.REJECTED
    
    def test_waiting_approval_to_blocked(self):
        """Test transition from WAITING_APPROVAL to BLOCKED."""
        sm = StateMachine()
        sm.transition(State.WAITING_APPROVAL)
        sm.transition(State.BLOCKED)
        assert sm.state == State.BLOCKED
    
    def test_approved_to_executing(self):
        """Test transition from APPROVED to EXECUTING."""
        sm = StateMachine()
        sm.transition(State.WAITING_APPROVAL)
        sm.transition(State.APPROVED)
        sm.transition(State.EXECUTING)
        assert sm.state == State.EXECUTING
    
    def test_approved_to_rejected(self):
        """Test transition from APPROVED to REJECTED."""
        sm = StateMachine()
        sm.transition(State.WAITING_APPROVAL)
        sm.transition(State.APPROVED)
        sm.transition(State.REJECTED)
        assert sm.state == State.REJECTED
    
    def test_approved_to_blocked(self):
        """Test transition from APPROVED to BLOCKED."""
        sm = StateMachine()
        sm.transition(State.WAITING_APPROVAL)
        sm.transition(State.APPROVED)
        sm.transition(State.BLOCKED)
        assert sm.state == State.BLOCKED
    
    def test_executing_to_executed(self):
        """Test transition from EXECUTING to EXECUTED."""
        sm = StateMachine()
        sm.transition(State.WAITING_APPROVAL)
        sm.transition(State.APPROVED)
        sm.transition(State.EXECUTING)
        sm.transition(State.EXECUTED)
        assert sm.state == State.EXECUTED
    
    def test_executing_to_rejected(self):
        """Test transition from EXECUTING to REJECTED."""
        sm = StateMachine()
        sm.transition(State.WAITING_APPROVAL)
        sm.transition(State.APPROVED)
        sm.transition(State.EXECUTING)
        sm.transition(State.REJECTED)
        assert sm.state == State.REJECTED
    
    def test_executing_to_blocked(self):
        """Test transition from EXECUTING to BLOCKED."""
        sm = StateMachine()
        sm.transition(State.WAITING_APPROVAL)
        sm.transition(State.APPROVED)
        sm.transition(State.EXECUTING)
        sm.transition(State.BLOCKED)
        assert sm.state == State.BLOCKED


class TestInvalidTransitions:
    """Test that invalid transitions fail closed."""
    
    def test_proposed_to_approved_invalid(self):
        """Test that PROPOSED->APPROVED is not allowed (must go through WAITING_APPROVAL)."""
        sm = StateMachine()
        with pytest.raises(ValueError, match="Invalid transition"):
            sm.transition(State.APPROVED)
    
    def test_proposed_to_executing_invalid(self):
        """Test that PROPOSED->EXECUTING is not allowed."""
        sm = StateMachine()
        with pytest.raises(ValueError, match="Invalid transition"):
            sm.transition(State.EXECUTING)
    
    def test_proposed_to_executed_invalid(self):
        """Test that PROPOSED->EXECUTED is not allowed."""
        sm = StateMachine()
        with pytest.raises(ValueError, match="Invalid transition"):
            sm.transition(State.EXECUTED)
    
    def test_waiting_approval_to_executing_invalid(self):
        """Test that WAITING_APPROVAL->EXECUTING is not allowed (must go through APPROVED)."""
        sm = StateMachine()
        sm.transition(State.WAITING_APPROVAL)
        with pytest.raises(ValueError, match="Invalid transition"):
            sm.transition(State.EXECUTING)
    
    def test_approved_to_executed_invalid(self):
        """Test that APPROVED->EXECUTED is not allowed (must go through EXECUTING)."""
        sm = StateMachine()
        sm.transition(State.WAITING_APPROVAL)
        sm.transition(State.APPROVED)
        with pytest.raises(ValueError, match="Invalid transition"):
            sm.transition(State.EXECUTED)
    
    def test_executed_to_approved_invalid(self):
        """Test that EXECUTED->APPROVED is not allowed."""
        sm = StateMachine()
        sm.transition(State.WAITING_APPROVAL)
        sm.transition(State.APPROVED)
        sm.transition(State.EXECUTING)
        sm.transition(State.EXECUTED)
        with pytest.raises(ValueError, match="Invalid transition"):
            sm.transition(State.APPROVED)
    
    def test_rejected_to_proposed_invalid(self):
        """Test that REJECTED->PROPOSED is not allowed (terminal state)."""
        sm = StateMachine()
        sm.transition(State.REJECTED)
        with pytest.raises(ValueError, match="Cannot transition from terminal state"):
            sm.transition(State.PROPOSED)
    
    def test_rejected_to_approved_invalid(self):
        """Test that REJECTED->APPROVED is not allowed (terminal state)."""
        sm = StateMachine()
        sm.transition(State.REJECTED)
        with pytest.raises(ValueError, match="Cannot transition from terminal state"):
            sm.transition(State.APPROVED)
    
    def test_blocked_to_proposed_invalid(self):
        """Test that BLOCKED->PROPOSED is not allowed (terminal state)."""
        sm = StateMachine()
        sm.transition(State.BLOCKED)
        with pytest.raises(ValueError, match="Cannot transition from terminal state"):
            sm.transition(State.PROPOSED)


class TestExecution:
    """Test execution requirements."""
    
    def test_execution_allowed_in_approved_state(self):
        """Test that execution is allowed only in APPROVED state."""
        sm = StateMachine()
        sm.transition(State.WAITING_APPROVAL)
        sm.transition(State.APPROVED)
        assert sm.can_execute() is True
        sm.execute()  # Should not raise
    
    def test_execution_not_allowed_in_proposed_state(self):
        """Test that execution is not allowed in PROPOSED state."""
        sm = StateMachine()
        assert sm.can_execute() is False
        with pytest.raises(ValueError, match="Execution not allowed"):
            sm.execute()
    
    def test_execution_not_allowed_in_waiting_approval_state(self):
        """Test that execution is not allowed in WAITING_APPROVAL state."""
        sm = StateMachine()
        sm.transition(State.WAITING_APPROVAL)
        assert sm.can_execute() is False
        with pytest.raises(ValueError, match="Execution not allowed"):
            sm.execute()
    
    def test_execution_not_allowed_in_executing_state(self):
        """Test that execution is not allowed in EXECUTING state."""
        sm = StateMachine()
        sm.transition(State.WAITING_APPROVAL)
        sm.transition(State.APPROVED)
        sm.transition(State.EXECUTING)
        assert sm.can_execute() is False
        with pytest.raises(ValueError, match="Execution not allowed"):
            sm.execute()
    
    def test_execution_not_allowed_in_executed_state(self):
        """Test that execution is not allowed in EXECUTED state."""
        sm = StateMachine()
        sm.transition(State.WAITING_APPROVAL)
        sm.transition(State.APPROVED)
        sm.transition(State.EXECUTING)
        sm.transition(State.EXECUTED)
        assert sm.can_execute() is False
        with pytest.raises(ValueError, match="Execution not allowed"):
            sm.execute()
    
    def test_execution_not_allowed_in_rejected_state(self):
        """Test that execution is not allowed in REJECTED state."""
        sm = StateMachine()
        sm.transition(State.REJECTED)
        assert sm.can_execute() is False
        with pytest.raises(ValueError, match="Execution not allowed"):
            sm.execute()
    
    def test_execution_not_allowed_in_blocked_state(self):
        """Test that execution is not allowed in BLOCKED state."""
        sm = StateMachine()
        sm.transition(State.BLOCKED)
        assert sm.can_execute() is False
        with pytest.raises(ValueError, match="Execution not allowed"):
            sm.execute()


class TestTerminalStates:
    """Test terminal state behavior."""
    
    def test_rejected_is_terminal(self):
        """Test that REJECTED is a terminal state."""
        sm = StateMachine()
        sm.transition(State.REJECTED)
        assert sm.is_terminal() is True
    
    def test_blocked_is_terminal(self):
        """Test that BLOCKED is a terminal state."""
        sm = StateMachine()
        sm.transition(State.BLOCKED)
        assert sm.is_terminal() is True
    
    def test_proposed_is_not_terminal(self):
        """Test that PROPOSED is not a terminal state."""
        sm = StateMachine()
        assert sm.is_terminal() is False
    
    def test_waiting_approval_is_not_terminal(self):
        """Test that WAITING_APPROVAL is not a terminal state."""
        sm = StateMachine()
        sm.transition(State.WAITING_APPROVAL)
        assert sm.is_terminal() is False
    
    def test_approved_is_not_terminal(self):
        """Test that APPROVED is not a terminal state."""
        sm = StateMachine()
        sm.transition(State.WAITING_APPROVAL)
        sm.transition(State.APPROVED)
        assert sm.is_terminal() is False
    
    def test_executing_is_not_terminal(self):
        """Test that EXECUTING is not a terminal state."""
        sm = StateMachine()
        sm.transition(State.WAITING_APPROVAL)
        sm.transition(State.APPROVED)
        sm.transition(State.EXECUTING)
        assert sm.is_terminal() is False
    
    def test_executed_is_not_terminal(self):
        """Test that EXECUTED is not a terminal state (no further transitions defined)."""
        sm = StateMachine()
        sm.transition(State.WAITING_APPROVAL)
        sm.transition(State.APPROVED)
        sm.transition(State.EXECUTING)
        sm.transition(State.EXECUTED)
        assert sm.is_terminal() is False


class TestWaitingApprovalHardStop:
    """Test WAITING_APPROVAL as explicit hard-stop state."""
    
    def test_waiting_approval_forces_explicit_resolution(self):
        """Test that WAITING_APPROVAL is explicit hard-stop requiring explicit decision."""
        sm = StateMachine()
        sm.transition(State.WAITING_APPROVAL)
        
        # Cannot proceed to EXECUTING without going through APPROVED
        with pytest.raises(ValueError, match="Invalid transition"):
            sm.transition(State.EXECUTING)
        
        # Must explicitly choose: APPROVED, REJECTED, or BLOCKED
        sm.transition(State.APPROVED)
        assert sm.state == State.APPROVED
    
    def test_waiting_approval_to_rejection_explicit(self):
        """Test explicit rejection from WAITING_APPROVAL."""
        sm = StateMachine()
        sm.transition(State.WAITING_APPROVAL)
        sm.transition(State.REJECTED)
        assert sm.state == State.REJECTED
        assert sm.is_terminal() is True
    
    def test_waiting_approval_to_blocked_explicit(self):
        """Test explicit block from WAITING_APPROVAL."""
        sm = StateMachine()
        sm.transition(State.WAITING_APPROVAL)
        sm.transition(State.BLOCKED)
        assert sm.state == State.BLOCKED
        assert sm.is_terminal() is True


class TestCanonicalWorkflows:
    """Test canonical DETERMA Proof Kernel workflows."""
    
    def test_successful_authorized_execution_flow(self):
        """Test successful execution: PROPOSED -> WAITING_APPROVAL -> APPROVED -> EXECUTING -> EXECUTED."""
        sm = StateMachine()
        assert sm.state == State.PROPOSED
        
        sm.transition(State.WAITING_APPROVAL)
        assert sm.state == State.WAITING_APPROVAL
        assert sm.can_execute() is False
        
        sm.transition(State.APPROVED)
        assert sm.state == State.APPROVED
        assert sm.can_execute() is True
        
        sm.execute()
        sm.transition(State.EXECUTING)
        assert sm.state == State.EXECUTING
        assert sm.can_execute() is False
        
        sm.transition(State.EXECUTED)
        assert sm.state == State.EXECUTED
        assert sm.can_execute() is False
    
    def test_direct_rejection_from_proposed(self):
        """Test direct rejection: PROPOSED -> REJECTED."""
        sm = StateMachine()
        sm.transition(State.REJECTED)
        assert sm.state == State.REJECTED
        assert sm.is_terminal() is True
        assert sm.can_execute() is False
    
    def test_rejection_during_approval(self):
        """Test rejection during approval: PROPOSED -> WAITING_APPROVAL -> REJECTED."""
        sm = StateMachine()
        sm.transition(State.WAITING_APPROVAL)
        sm.transition(State.REJECTED)
        assert sm.state == State.REJECTED
        assert sm.is_terminal() is True
    
    def test_rejection_after_approval(self):
        """Test rejection after approval: PROPOSED -> WAITING_APPROVAL -> APPROVED -> REJECTED."""
        sm = StateMachine()
        sm.transition(State.WAITING_APPROVAL)
        sm.transition(State.APPROVED)
        sm.execute()
        sm.transition(State.REJECTED)
        assert sm.state == State.REJECTED
        assert sm.is_terminal() is True
    
    def test_failure_during_execution(self):
        """Test failure during execution: PROPOSED -> WAITING_APPROVAL -> APPROVED -> EXECUTING -> REJECTED."""
        sm = StateMachine()
        sm.transition(State.WAITING_APPROVAL)
        sm.transition(State.APPROVED)
        sm.transition(State.EXECUTING)
        sm.transition(State.REJECTED)
        assert sm.state == State.REJECTED
        assert sm.is_terminal() is True
    
    def test_direct_block_from_proposed(self):
        """Test direct block: PROPOSED -> BLOCKED."""
        sm = StateMachine()
        sm.transition(State.BLOCKED)
        assert sm.state == State.BLOCKED
        assert sm.is_terminal() is True
    
    def test_block_during_approval(self):
        """Test block during approval: PROPOSED -> WAITING_APPROVAL -> BLOCKED."""
        sm = StateMachine()
        sm.transition(State.WAITING_APPROVAL)
        sm.transition(State.BLOCKED)
        assert sm.state == State.BLOCKED
        assert sm.is_terminal() is True
    
    def test_block_after_approval(self):
        """Test block after approval: PROPOSED -> WAITING_APPROVAL -> APPROVED -> BLOCKED."""
        sm = StateMachine()
        sm.transition(State.WAITING_APPROVAL)
        sm.transition(State.APPROVED)
        sm.transition(State.BLOCKED)
        assert sm.state == State.BLOCKED
        assert sm.is_terminal() is True
    
    def test_block_during_execution(self):
        """Test block during execution: PROPOSED -> WAITING_APPROVAL -> APPROVED -> EXECUTING -> BLOCKED."""
        sm = StateMachine()
        sm.transition(State.WAITING_APPROVAL)
        sm.transition(State.APPROVED)
        sm.transition(State.EXECUTING)
        sm.transition(State.BLOCKED)
        assert sm.state == State.BLOCKED
        assert sm.is_terminal() is True


class TestInitialState:
    """Test initial state behavior."""
    
    def test_initial_state_is_proposed(self):
        """Test that initial state is PROPOSED."""
        sm = StateMachine()
        assert sm.state == State.PROPOSED
    
    def test_initial_state_is_not_terminal(self):
        """Test that initial state is not terminal."""
        sm = StateMachine()
        assert sm.is_terminal() is False
    
    def test_cannot_execute_in_initial_state(self):
        """Test that execution is not allowed in initial state."""
        sm = StateMachine()
        assert sm.can_execute() is False
        with pytest.raises(ValueError, match="Execution not allowed"):
            sm.execute()

