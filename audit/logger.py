from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Tuple


class EventType(Enum):
    """Canonical audit event types."""

    EXECUTION_SUCCESS = "EXECUTION_SUCCESS"
    EXECUTION_BLOCKED = "EXECUTION_BLOCKED"
    REPLAY_ATTEMPT = "REPLAY_ATTEMPT"


@dataclass(frozen=True)
class AuditLogEntry:
    """
    Immutable append-only audit record for authority lineage.
    """

    proposal_id: str
    approval_id: str
    capability_id: str
    repo_head: str
    witness_result: str
    execution_result: str
    timestamp: datetime
    event_type: str

    def __post_init__(self) -> None:
        if not self.proposal_id:
            raise ValueError("proposal_id cannot be empty")
        if not self.approval_id:
            raise ValueError("approval_id cannot be empty")
        if not self.capability_id:
            raise ValueError("capability_id cannot be empty")
        if not self.repo_head:
            raise ValueError("repo_head cannot be empty")
        if not self.witness_result:
            raise ValueError("witness_result cannot be empty")
        if not self.execution_result:
            raise ValueError("execution_result cannot be empty")
        if not isinstance(self.timestamp, datetime):
            raise ValueError("timestamp must be datetime object")
        if not self.event_type:
            raise ValueError("event_type cannot be empty")


class AuditLogger:
    """
    Append-only authority lineage logger.

    Guarantees:
    - records are immutable (`AuditLogEntry` is frozen)
    - append-only semantics (`entries` are exposed as tuple)
    - deterministic ordering by append sequence
    """

    def __init__(self) -> None:
        self._entries: Tuple[AuditLogEntry, ...] = tuple()

    @property
    def entries(self) -> Tuple[AuditLogEntry, ...]:
        return self._entries

    def append(
        self,
        proposal_id: str,
        approval_id: str,
        capability_id: str,
        repo_head: str,
        witness_result: str,
        execution_result: str,
        timestamp: datetime,
        event_type: str,
    ) -> AuditLogEntry:
        entry = AuditLogEntry(
            proposal_id=proposal_id,
            approval_id=approval_id,
            capability_id=capability_id,
            repo_head=repo_head,
            witness_result=witness_result,
            execution_result=execution_result,
            timestamp=timestamp,
            event_type=event_type,
        )
        # Append-only tuple growth preserves all prior records untouched.
        self._entries = self._entries + (entry,)
        return entry

    def log_successful_execution(
        self,
        proposal_id: str,
        approval_id: str,
        capability_id: str,
        repo_head: str,
        witness_result: str,
        timestamp: datetime,
    ) -> AuditLogEntry:
        return self.append(
            proposal_id=proposal_id,
            approval_id=approval_id,
            capability_id=capability_id,
            repo_head=repo_head,
            witness_result=witness_result,
            execution_result="EXECUTED",
            timestamp=timestamp,
            event_type=EventType.EXECUTION_SUCCESS.value,
        )

    def log_blocked_execution(
        self,
        proposal_id: str,
        approval_id: str,
        capability_id: str,
        repo_head: str,
        witness_result: str,
        timestamp: datetime,
    ) -> AuditLogEntry:
        return self.append(
            proposal_id=proposal_id,
            approval_id=approval_id,
            capability_id=capability_id,
            repo_head=repo_head,
            witness_result=witness_result,
            execution_result="EXECUTION BLOCKED",
            timestamp=timestamp,
            event_type=EventType.EXECUTION_BLOCKED.value,
        )

    def log_replay_attempt(
        self,
        proposal_id: str,
        approval_id: str,
        capability_id: str,
        repo_head: str,
        witness_result: str,
        timestamp: datetime,
    ) -> AuditLogEntry:
        return self.append(
            proposal_id=proposal_id,
            approval_id=approval_id,
            capability_id=capability_id,
            repo_head=repo_head,
            witness_result=witness_result,
            execution_result="REPLAY BLOCKED",
            timestamp=timestamp,
            event_type=EventType.REPLAY_ATTEMPT.value,
        )
