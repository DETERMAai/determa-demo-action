"""Factory approval queue.

Tracks executions waiting for human approval.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List


class ApprovalStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


@dataclass
class ApprovalRequest:
    task_id: str
    session_id: str | None
    reason: str
    replay: dict[str, object] | None = None
    status: ApprovalStatus = ApprovalStatus.PENDING
    decided_by: str | None = None
    decision_reason: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "task_id": self.task_id,
            "session_id": self.session_id,
            "reason": self.reason,
            "replay": self.replay,
            "status": self.status.value,
            "decided_by": self.decided_by,
            "decision_reason": self.decision_reason,
        }


@dataclass
class ApprovalQueue:
    pending: List[ApprovalRequest] = field(default_factory=list)
    completed: List[ApprovalRequest] = field(default_factory=list)

    def add_request(self, request: ApprovalRequest) -> None:
        self.pending.append(request)

    def list_pending(self) -> list[ApprovalRequest]:
        return list(self.pending)

    def approve(self, task_id: str, decided_by: str, reason: str) -> ApprovalRequest:
        request = self._pop_pending(task_id)
        request.status = ApprovalStatus.APPROVED
        request.decided_by = decided_by
        request.decision_reason = reason
        self.completed.append(request)
        return request

    def reject(self, task_id: str, decided_by: str, reason: str) -> ApprovalRequest:
        request = self._pop_pending(task_id)
        request.status = ApprovalStatus.REJECTED
        request.decided_by = decided_by
        request.decision_reason = reason
        self.completed.append(request)
        return request

    def _pop_pending(self, task_id: str) -> ApprovalRequest:
        for index, request in enumerate(self.pending):
            if request.task_id == task_id:
                return self.pending.pop(index)
        raise ValueError(f"approval request not found: {task_id}")
