"""Minimal governed worker runner.

This runner coordinates a bounded task execution result.
It does not execute arbitrary shell commands.
It validates scope before a task can be marked complete.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from factory.queue.task_queue import Task, TaskStatus
from factory.verification.scope_validator import (
    ScopeContract,
    ScopeValidationResult,
    validate_scope,
)


class WorkerRunStatus(str, Enum):
    PASSED = "PASSED"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class WorkerRunResult:
    task_id: str
    status: WorkerRunStatus
    changed_files: tuple[str, ...]
    scope_result: ScopeValidationResult
    notes: tuple[str, ...] = field(default_factory=tuple)


def run_worker_task(
    task: Task,
    changed_files: tuple[str, ...],
    contract: ScopeContract,
) -> WorkerRunResult:
    """Validate a worker task result against its scope contract.

    The actual code-writing worker is intentionally outside this function.
    This function gates whether the produced file set is acceptable.
    """
    scope_result = validate_scope(changed_files, contract)

    if not scope_result.passed:
        task.status = TaskStatus.BLOCKED
        return WorkerRunResult(
            task_id=task.task_id,
            status=WorkerRunStatus.BLOCKED,
            changed_files=changed_files,
            scope_result=scope_result,
            notes=("scope validation failed",),
        )

    task.status = TaskStatus.COMPLETE
    return WorkerRunResult(
        task_id=task.task_id,
        status=WorkerRunStatus.PASSED,
        changed_files=changed_files,
        scope_result=scope_result,
        notes=("scope validation passed",),
    )
