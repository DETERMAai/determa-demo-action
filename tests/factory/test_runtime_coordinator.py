from factory.queue.task_queue import Task, TaskQueue
from factory.runtime.approval_queue import ApprovalQueue
from factory.runtime.coordinator import RuntimeCoordinator
from factory.runtime.governance_decision import GovernanceAction
from factory.runtime.risk import RiskLevel
from factory.runtime.state import RuntimeState
from factory.verification.scope_validator import ScopeContract


def _queue_with_task() -> TaskQueue:
    queue = TaskQueue()
    queue.add_task(Task(task_id="PR-101-T1", name="coordinator test task"))
    return queue


def test_coordinator_completes_low_risk_passed_replay():
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
    assert result.risk_assessment is not None
    assert result.risk_assessment.level == RiskLevel.LOW
    assert result.governance_decision is not None
    assert result.governance_decision.action == GovernanceAction.ALLOW_AUTONOMOUS
    assert coordinator.state == RuntimeState.COMPLETE
    assert approval_queue.list_pending() == []


def test_coordinator_blocks_scope_violation_before_governance_decision():
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
    assert result.governance_decision is None
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
    assert result.risk_assessment is not None
    assert result.risk_assessment.level == RiskLevel.HIGH
    assert result.governance_decision is not None
    assert result.governance_decision.action == GovernanceAction.REQUIRE_SECURITY_REVIEW
    assert coordinator.state == RuntimeState.AWAITING_APPROVAL

    pending = approval_queue.list_pending()
    assert len(pending) == 1
    assert pending[0].task_id == "PR-101-T1"
    assert pending[0].reason == "approval required severity: HIGH"


def test_coordinator_routes_medium_risk_auth_surface_to_approval_queue():
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
        replay={"severity": "LOW", "trust_state": "TRUSTED"},
    )

    assert result is not None
    assert result.requires_approval is True
    assert result.outcome() == "REQUIRES_APPROVAL"
    assert result.risk_assessment is not None
    assert result.risk_assessment.level == RiskLevel.MEDIUM
    assert result.governance_decision is not None
    assert result.governance_decision.action == GovernanceAction.REQUIRE_REVIEW
    assert coordinator.state == RuntimeState.AWAITING_APPROVAL

    pending = approval_queue.list_pending()
    assert len(pending) == 1
    assert pending[0].reason == "medium risk execution requires human review"


def test_coordinator_blocks_critical_replay():
    approval_queue = ApprovalQueue()
    coordinator = RuntimeCoordinator(
        queue=_queue_with_task(),
        approval_queue=approval_queue,
    )

    result = coordinator.run_next(
        changed_files=("secrets/prod_key.txt",),
        contract=ScopeContract(
            allowed_files=("secrets/*",),
            forbidden_files=(),
        ),
        replay={"severity": "HIGH", "trust_state": "REQUIRES_APPROVAL"},
    )

    assert result is not None
    assert result.passed is False
    assert result.outcome() == "BLOCKED"
    assert result.risk_assessment is not None
    assert result.risk_assessment.level == RiskLevel.CRITICAL
    assert result.governance_decision is not None
    assert result.governance_decision.action == GovernanceAction.DENY
    assert coordinator.state == RuntimeState.BLOCKED
    assert approval_queue.list_pending() == []
