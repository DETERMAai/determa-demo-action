"""Factory runtime coordinator.

Coordinates one bounded task from queue to worker validation.
No arbitrary command execution. No Git mutation. No merge.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from factory.queue.task_queue import TaskQueue
from factory.runtime.state import RuntimeState, RuntimeTransition, transition
from factory.runtime.worker_runner import WorkerRunResult, run_worker_task
from factory.verification.scope_validator import ScopeContract


@dataclass
class RuntimeCoordinator:
    """Small deterministic coordinator for governed factory execution."""

    queue: TaskQueue
    state: RuntimeState = RuntimeState.IDLE
    transitions: list[RuntimeTransition] = field(default_factory=list)

    def run_next(
        self,
        changed_files: tuple[str, ...],
        contract: ScopeContract,
    ) -> WorkerRunResult | None:
        """Run the next queued task through bounded validation."""
        task = self.queue.next_task()
        if task is None:
            self._move(RuntimeState.IDLE, "no pending task")
            return None

        self._move(RuntimeState.DISPATCHING, f"dispatching {task.task_id}")
        self._move(RuntimeState.EXECUTING, f"executing {task.task_id}")

        result = run_worker_task(
            task=task,
            changed_files=changed_files,
            contract=contract,
        )

        self._move(RuntimeState.VERIFYING, f"verifying {task.task_id}")

        if result.status.value == "BLOCKED":
            self.queue.mark_blocked(task)
            self._move(RuntimeState.BLOCKED, f"blocked {task.task_id}")
        else:
            self.queue.mark_complete(task)
            self._move(RuntimeState.COMPLETE, f"completed {task.task_id}")

        return result

    def reset(self) -> None:
        """Reset runtime to IDLE after complete or blocked state."""
        self._move(RuntimeState.IDLE, "runtime reset")

    def _move(self, next_state: RuntimeState, reason: str) -> None:
        if self.state == next_state:
            return
        runtime_transition = transition(self.state, next_state, reason)
        self.transitions.append(runtime_transition)
        self.state = next_state
