from enum import Enum, auto
from typing import Set, Tuple, Optional


class State(Enum):
    """Canonical DETERMA Proof Kernel states."""
    PROPOSED = auto()
    WAITING_APPROVAL = auto()
    APPROVED = auto()
    EXECUTING = auto()
    EXECUTED = auto()
    BLOCKED = auto()
    REJECTED = auto()


class StateMachine:
    """
    Canonical DETERMA Proof Kernel state machine with deterministic authority semantics.
    
    States:
    - PROPOSED: Initial proposed action
    - WAITING_APPROVAL: Explicit hard-stop awaiting authorization
    - APPROVED: Authorization granted, ready for execution
    - EXECUTING: Execution in progress
    - EXECUTED: Execution completed successfully
    - BLOCKED: Terminal state - action blocked
    - REJECTED: Terminal state - action rejected
    
    Rules:
    - Only explicit transitions allowed (fail closed on invalid)
    - WAITING_APPROVAL is explicit hard-stop state
    - Execution requires APPROVED state
    - BLOCKED and REJECTED are terminal states
    - No implicit execution
    """
    
    # Define all valid transitions as (from_state, to_state) tuples
    VALID_TRANSITIONS: Set[Tuple[State, State]] = {
        # From PROPOSED
        (State.PROPOSED, State.WAITING_APPROVAL),
        (State.PROPOSED, State.BLOCKED),
        (State.PROPOSED, State.REJECTED),
        # From WAITING_APPROVAL (explicit hard-stop state)
        (State.WAITING_APPROVAL, State.APPROVED),
        (State.WAITING_APPROVAL, State.REJECTED),
        (State.WAITING_APPROVAL, State.BLOCKED),
        # From APPROVED
        (State.APPROVED, State.EXECUTING),
        (State.APPROVED, State.REJECTED),
        (State.APPROVED, State.BLOCKED),
        # From EXECUTING
        (State.EXECUTING, State.EXECUTED),
        (State.EXECUTING, State.REJECTED),
        (State.EXECUTING, State.BLOCKED),
    }
    
    # Terminal states that cannot transition further
    TERMINAL_STATES: Set[State] = {
        State.BLOCKED,
        State.REJECTED,
    }
    
    def __init__(self):
        """Initialize state machine in PROPOSED state."""
        self._state = State.PROPOSED
    
    @property
    def state(self) -> State:
        """Get current state."""
        return self._state
    
    def transition(self, to_state: State) -> None:
        """
        Transition to a new state.
        
        Args:
            to_state: Target state to transition to
            
        Raises:
            ValueError: If transition is invalid or state is terminal
        """
        # Check if current state is terminal
        if self._state in self.TERMINAL_STATES:
            raise ValueError(
                f"Cannot transition from terminal state {self._state.name}"
            )
        
        # Check if transition is explicitly allowed
        transition = (self._state, to_state)
        if transition not in self.VALID_TRANSITIONS:
            raise ValueError(
                f"Invalid transition: {self._state.name} -> {to_state.name}"
            )
        
        self._state = to_state
    
    def can_execute(self) -> bool:
        """
        Check if execution is allowed in current state.
        
        Execution is only allowed in APPROVED state.
        
        Returns:
            True if state is APPROVED, False otherwise
        """
        return self._state == State.APPROVED
    
    def execute(self) -> None:
        """
        Execute in the current state.
        
        Raises:
            ValueError: If not in APPROVED state
        """
        if not self.can_execute():
            raise ValueError(
                f"Execution not allowed in {self._state.name} state. "
                f"Must be in APPROVED state."
            )
    
    def is_terminal(self) -> bool:
        """Check if current state is terminal."""
        return self._state in self.TERMINAL_STATES
