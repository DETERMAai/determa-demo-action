"""Simple in-memory factory task queue.

Deterministic queue for governed task execution.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    BLOCKED = "BLOCKED"
    COMPLETE = "COMPLETE"


@dataclass
class Task:
    task_id: str
    name: str
    status: TaskStatus = TaskStatus.PENDING


@dataclass
class TaskQueue:
    pending: List[Task] = field(default_factory=list)
    running: List[Task] = field(default_factory=list)
    blocked: List[Task] = field(default_factory=list)
    completed: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        self.pending.append(task)

    def next_task(self) -> Task | None:
        if not self.pending:
            return None

        task = self.pending.pop(0)
        task.status = TaskStatus.RUNNING
        self.running.append(task)
        return task

    def mark_blocked(self, task: Task) -> None:
        self._remove_from_running(task)
        task.status = TaskStatus.BLOCKED
        self.blocked.append(task)

    def mark_complete(self, task: Task) -> None:
        self._remove_from_running(task)
        task.status = TaskStatus.COMPLETE
        self.completed.append(task)

    def _remove_from_running(self, task: Task) -> None:
        self.running = [t for t in self.running if t.task_id != task.task_id]
