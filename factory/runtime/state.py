"""Factory runtime state model.

Small, deterministic state machine for governed autonomous work.
No worker execution happens here.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class RuntimeState(str, Enum):
    IDLE = "IDLE"
    DISPATCHING = "DISPATCHING"
    EXECUTING = "EXECUTING"
    VERIFYING = "VERIFYING"
    BLOCKED = "BLOCKED"
    COMPLETE = "COMPLETE"


_ALLOWED_TRANSITIONS: dict[RuntimeState, set[RuntimeState]] = {
    RuntimeState.IDLE: {RuntimeState.DISPATCHING, RuntimeState.BLOCKED},
    RuntimeState.DISPATCHING: {RuntimeState.EXECUTING, RuntimeState.BLOCKED, RuntimeState.IDLE},
    RuntimeState.EXECUTING: {RuntimeState.VERIFYING, RuntimeState.BLOCKED},
    RuntimeState.VERIFYING: {RuntimeState.COMPLETE, RuntimeState.BLOCKED},
    RuntimeState.BLOCKED: {RuntimeState.IDLE},
    RuntimeState.COMPLETE: {RuntimeState.IDLE},
}


@dataclass(frozen=True)
class RuntimeTransition:
    previous: RuntimeState
    current: RuntimeState
    reason: str


def can_transition(previous: RuntimeState, current: RuntimeState) -> bool:
    """Return whether a runtime state transition is allowed."""
    return current in _ALLOWED_TRANSITIONS[previous]


def transition(previous: RuntimeState, current: RuntimeState, reason: str) -> RuntimeTransition:
    """Create a validated runtime transition."""
    if not can_transition(previous, current):
        raise ValueError(f"illegal runtime transition: {previous} -> {current}")
    return RuntimeTransition(previous=previous, current=current, reason=reason)
