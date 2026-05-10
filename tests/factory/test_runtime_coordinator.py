from factory.queue.task_queue import Task, TaskQueue
from factory.runtime.approval_queue import ApprovalQueue
from factory.runtime.coordinator import RuntimeCoordinator
from factory.runtime.state import RuntimeState
from factory.verification.scope_validator import ScopeContract


def _queue_with_task() -> TaskQueue:
    queue = TaskQueue()
    queue.add_task(Task(task_id="PR-101-T1", name="coordinator test task"))
    return queue


def test_coordinator_completes_passed_replay():
    approval_queue = ApprovalQueue()
    coordinator = RuntimeCoordinator(
        queue=_queue_with_task(),
        approval_queue=approval_queue,
    )

    result = coordinator.run_next(
        changed_files=("docs/example.md",),
        contract=ScopeContract(
            allowed_files=("docs/*",),
            forbidden_files=("secrets/*",),
        ),
        replay={"severity": "LOW", "trust_state": "TRUSTED"},
    )

    assert result is not None
    assert result.passed is True
    assert result.outcome() == "PASSED"
    assert coordinator.state == RuntimeState.COMPLETE
    assert approval_queue.list_pending() == []


def test_coordinator_blocks_scope_violation():
    coordinator = RuntimeCoordinator(queue=_queue_with_task())

    result = coordinator.run_next(
        changed_files=("secrets/token.txt",),
        contract=ScopeContract(
            allowed_files=("docs/*",),
            forbidden_files=("secrets/*",),
        ),
        replay={"severity": "LOW", "trust_state": "TRUSTED"},
    )

    assert result is not None
    assert result.passed is False
    assert result.outcome() == "BLOCKED"
    assert coordinator.state == RuntimeState.BLOCKED


def test_coordinator_routes_high_severity_to_approval_queue():
    approval_queue = ApprovalQueue()
    coordinator = RuntimeCoordinator(
        queue=_queue_with_task(),
        approval_queue=approval_queue,
    )

    result = coordinator.run_next(
        changed_files=("src/auth.py",),
        contract=ScopeContract(
            allowed_files=("src/*",),
            forbidden_files=("secrets/*",),
        ),
        replay={"severity": "HIGH", "trust_state": "TRUSTED"},
    )

    assert result is not None
    assert result.requires_approval is True
    assert result.outcome() == "REQUIRES_APPROVAL"
    assert coordinator.state == RuntimeState.AWAITING_APPROVAL

    pending = approval_queue.list_pending()
    assert len(pending) == 1
    assert pending[0].task_id == "PR-101-T1"
    assert pending[0].reason == "approval required severity: HIGH"


def test_coordinator_blocks_critical_replay():
    approval_queue = ApprovalQueue()
    coordinator = RuntimeCoordinator(
        queue=_queue_with_task(),
        approval_queue=approval_queue,
    )

    result = coordinator.run_next(
        changed_files=("src/deploy.py",),
        contract=ScopeContract(
            allowed_files=("src/*",),
            forbidden_files=("secrets/*",),
        ),
        replay={"severity": "CRITICAL", "trust_state": "TRUSTED"},
    )

    assert result is not None
    assert result.passed is False
    assert result.outcome() == "BLOCKED"
    assert coordinator.state == RuntimeState.BLOCKED
    assert approval_queue.list_pending() == []
