"""Factory runtime coordinator.

Coordinates one bounded task from queue to worker validation, replay gating,
and optional runtime persistence.
No arbitrary command execution. No Git mutation. No merge.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from factory.queue.task_queue import TaskQueue
from factory.runtime.persistence import RuntimeEvent, RuntimeStore, build_event_id
from factory.runtime.state import RuntimeState, RuntimeTransition, transition
from factory.runtime.worker_runner import WorkerRunResult, run_worker_task
from factory.verification.replay_gate import ReplayGateResult, evaluate_replay_gate
from factory.verification.scope_validator import ScopeContract


@dataclass(frozen=True)
class RuntimeRunResult:
    """Result of one coordinated factory runtime cycle."""

    worker_result: WorkerRunResult
    replay_gate_result: ReplayGateResult | None

    @property
    def passed(self) -> bool:
        if self.worker_result.status.value == "BLOCKED":
            return False
        if self.replay_gate_result is None:
            return True
        return self.replay_gate_result.passed

    def outcome(self) -> str:
        return "PASSED" if self.passed else "BLOCKED"


@dataclass
class RuntimeCoordinator:
    """Small deterministic coordinator for governed factory execution."""

    queue: TaskQueue
    state: RuntimeState = RuntimeState.IDLE
    transitions: list[RuntimeTransition] = field(default_factory=list)
    store: RuntimeStore | None = None

    def run_next(
        self,
        changed_files: tuple[str, ...],
        contract: ScopeContract,
        replay: dict[str, object] | None = None,
    ) -> RuntimeRunResult | None:
        """Run the next queued task through scope validation and optional replay gate."""
        task = self.queue.next_task()
        if task is None:
            self._move(RuntimeState.IDLE, "no pending task")
            return None

        self._move(RuntimeState.DISPATCHING, f"dispatching {task.task_id}")
        self._move(RuntimeState.EXECUTING, f"executing {task.task_id}")

        worker_result = run_worker_task(
            task=task,
            changed_files=changed_files,
            contract=contract,
        )

        self._move(RuntimeState.VERIFYING, f"verifying {task.task_id}")

        replay_gate_result: ReplayGateResult | None = None
        if worker_result.status.value != "BLOCKED" and replay is not None:
            replay_gate_result = evaluate_replay_gate(replay)

        runtime_result = RuntimeRunResult(
            worker_result=worker_result,
            replay_gate_result=replay_gate_result,
        )

        if not runtime_result.passed:
            self.queue.mark_blocked(task)
            self._move(RuntimeState.BLOCKED, f"blocked {task.task_id}")
        else:
            self.queue.mark_complete(task)
            self._move(RuntimeState.COMPLETE, f"completed {task.task_id}")

        self._persist_result(
            task_id=task.task_id,
            runtime_result=runtime_result,
            changed_files=changed_files,
            replay=replay,
        )

        return runtime_result

    def reset(self) -> None:
        """Reset runtime to IDLE after complete or blocked state."""
        self._move(RuntimeState.IDLE, "runtime reset")

    def _persist_result(
        self,
        task_id: str,
        runtime_result: RuntimeRunResult,
        changed_files: tuple[str, ...],
        replay: dict[str, object] | None,
    ) -> None:
        if self.store is None:
            return

        existing_events = self.store.load()
        event = RuntimeEvent(
            event_id=build_event_id(task_id, self.state.value, len(existing_events)),
            task_id=task_id,
            state=self.state.value,
            outcome=runtime_result.outcome(),
            reason=self._reason_for(runtime_result),
            replay=replay,
            changed_files=changed_files,
        )
        self.store.append(event)

    def _reason_for(self, runtime_result: RuntimeRunResult) -> str:
        if runtime_result.worker_result.status.value == "BLOCKED":
            return "; ".join(runtime_result.worker_result.notes)
        if runtime_result.replay_gate_result is not None and not runtime_result.replay_gate_result.passed:
            return "; ".join(runtime_result.replay_gate_result.reasons)
        if runtime_result.replay_gate_result is not None:
            return "; ".join(runtime_result.replay_gate_result.reasons)
        return "runtime completed without replay gate"

    def _move(self, next_state: RuntimeState, reason: str) -> None:
        if self.state == next_state:
            return
        runtime_transition = transition(self.state, next_state, reason)
        self.transitions.append(runtime_transition)
        self.state = next_state
