from __future__ import annotations

from datetime import datetime, timedelta

from audit.logger import AuditLogger
from executor.capability import issue_capability
from executor.execute import execute
from executor.state_witness import validate_repository_state
from orchestrator.approval import approve_proposal
from orchestrator.proposal import Proposal, create_proposal
from orchestrator.state_machine import State, StateMachine


def _phase(title: str) -> None:
    print()
    print("=" * 72)
    print(title)
    print("=" * 72)


def _show_transition(sm: StateMachine, to_state: State) -> None:
    from_state = sm.state
    sm.transition(to_state)
    print(f"STATE TRANSITION: {from_state.name} -> {to_state.name}")


def _print_blocked() -> None:
    print("EXECUTION BLOCKED")
    print("NO MUTATION PERFORMED")


def _approved_proposal(
    proposal_id: str,
    repo_head: str,
    requested_action: str,
    created_at: datetime,
    approval_id: str,
    approved_at: datetime,
) -> tuple[Proposal, str]:
    """
    Build a proposal and explicitly narrate canonical approval transitions.
    Returns an APPROVED-state proposal (materialized for execution) and approval id.
    """
    sm = StateMachine()
    _show_transition(sm, State.WAITING_APPROVAL)

    proposal = create_proposal(
        proposal_id=proposal_id,
        repo_head=repo_head,
        patch_hash=f"sha256:{proposal_id}",
        requested_action=requested_action,
        created_at=created_at,
    )
    print(f"PROPOSAL CREATED: {proposal.proposal_id} @ {proposal.repo_head}")

    approval = approve_proposal(
        approval_id=approval_id,
        proposal=proposal,
        approved_by="deterministic-authority",
        approved_at=approved_at,
    )
    print(f"APPROVAL REGISTERED: {approval.approval_id} -> {approval.resulting_state.name}")

    _show_transition(sm, State.APPROVED)
    object.__setattr__(proposal, "status", State.APPROVED)
    print(f"PROPOSAL AUTHORITY STATE: {proposal.status.name}")
    return proposal, approval.approval_id


def run_demo() -> None:
    base_time = datetime(2026, 1, 1, 12, 0, 0)
    audit = AuditLogger()

    _phase("DETERMA PROOF KERNEL DEMO")
    print("Deterministic local execution only.")

    # FLOW A: valid approved execution succeeds
    _phase("FLOW A: VALID APPROVED EXECUTION SUCCEEDS")
    proposal_a, approval_id_a = _approved_proposal(
        proposal_id="prop-A",
        repo_head="main:abc123",
        requested_action="Apply approved mutation A",
        created_at=base_time + timedelta(seconds=1),
        approval_id="appr-A",
        approved_at=base_time + timedelta(seconds=2),
    )

    witness_a = validate_repository_state(
        approved_repo_head="main:abc123",
        current_repo_head="main:abc123",
        validated_at=base_time + timedelta(seconds=3),
    )
    print(f"WITNESS VALIDATION: {witness_a.validation_result.value}")

    capability_a = issue_capability(
        capability_id="cap-A",
        proposal_id=proposal_a.proposal_id,
        repo_head="main:abc123",
        issued_at=base_time + timedelta(seconds=4),
    )
    print(
        f"CAPABILITY ISSUED: {capability_a.capability_id} "
        f"(consumed={capability_a.consumed})"
    )

    result_a, consumed_capability_a = execute(
        proposal=proposal_a,
        witness=witness_a,
        capability=capability_a,
        mutation=lambda: "MUTATION_APPLIED",
        consumed_at=base_time + timedelta(seconds=5),
    )
    print("EXECUTION AUTHORIZED")
    print(f"EXECUTION RESULT: {result_a}")
    print(
        f"CAPABILITY CONSUMED: {consumed_capability_a.capability_id} "
        f"(consumed={consumed_capability_a.consumed})"
    )

    audit.log_successful_execution(
        proposal_id=proposal_a.proposal_id,
        approval_id=approval_id_a,
        capability_id=consumed_capability_a.capability_id,
        repo_head=proposal_a.repo_head,
        witness_result=witness_a.validation_result.value,
        timestamp=base_time + timedelta(seconds=6),
    )

    # FLOW B: replay attempt blocked
    _phase("FLOW B: REPLAY ATTEMPT BLOCKED")
    print(
        f"REPLAY ATTEMPT WITH CAPABILITY: {consumed_capability_a.capability_id} "
        f"(consumed={consumed_capability_a.consumed})"
    )
    replay_mutation_performed = {"value": False}

    def replay_mutation() -> str:
        replay_mutation_performed["value"] = True
        return "SHOULD_NOT_EXECUTE"

    try:
        execute(
            proposal=proposal_a,
            witness=witness_a,
            capability=consumed_capability_a,
            mutation=replay_mutation,
            consumed_at=base_time + timedelta(seconds=7),
        )
    except ValueError:
        print("REPLAY DETECTED")
        _print_blocked()
        audit.log_replay_attempt(
            proposal_id=proposal_a.proposal_id,
            approval_id=approval_id_a,
            capability_id=consumed_capability_a.capability_id,
            repo_head=proposal_a.repo_head,
            witness_result=witness_a.validation_result.value,
            timestamp=base_time + timedelta(seconds=8),
        )

    print(f"MUTATION INVOKED: {replay_mutation_performed['value']}")

    # FLOW C: repository drift blocks execution
    _phase("FLOW C: REPOSITORY DRIFT BLOCKS EXECUTION")
    proposal_c, approval_id_c = _approved_proposal(
        proposal_id="prop-C",
        repo_head="main:xyz111",
        requested_action="Apply approved mutation C",
        created_at=base_time + timedelta(seconds=9),
        approval_id="appr-C",
        approved_at=base_time + timedelta(seconds=10),
    )

    witness_c = validate_repository_state(
        approved_repo_head="main:xyz111",
        current_repo_head="main:xyz222",
        validated_at=base_time + timedelta(seconds=11),
    )
    print(f"WITNESS VALIDATION: {witness_c.validation_result.value}")
    print("STATE DRIFT DETECTED")

    capability_c = issue_capability(
        capability_id="cap-C",
        proposal_id=proposal_c.proposal_id,
        repo_head="main:xyz111",
        issued_at=base_time + timedelta(seconds=12),
    )
    print(
        f"CAPABILITY ISSUED: {capability_c.capability_id} "
        f"(consumed={capability_c.consumed})"
    )

    drift_mutation_performed = {"value": False}

    def drift_mutation() -> str:
        drift_mutation_performed["value"] = True
        return "SHOULD_NOT_EXECUTE"

    try:
        execute(
            proposal=proposal_c,
            witness=witness_c,
            capability=capability_c,
            mutation=drift_mutation,
            consumed_at=base_time + timedelta(seconds=13),
        )
    except ValueError:
        _print_blocked()
        audit.log_blocked_execution(
            proposal_id=proposal_c.proposal_id,
            approval_id=approval_id_c,
            capability_id=capability_c.capability_id,
            repo_head=proposal_c.repo_head,
            witness_result=witness_c.validation_result.value,
            timestamp=base_time + timedelta(seconds=14),
        )

    print(f"MUTATION INVOKED: {drift_mutation_performed['value']}")

    # FLOW D: immutable audit lineage displayed
    _phase("FLOW D: IMMUTABLE AUDIT LINEAGE DISPLAYED")
    print("APPEND-ONLY AUTHORITY LINEAGE:")
    for index, entry in enumerate(audit.entries, start=1):
        print(
            f"{index}. "
            f"proposal_id={entry.proposal_id}, "
            f"approval_id={entry.approval_id}, "
            f"capability_id={entry.capability_id}, "
            f"repo_head={entry.repo_head}, "
            f"witness_result={entry.witness_result}, "
            f"execution_result={entry.execution_result}, "
            f"timestamp={entry.timestamp.isoformat()}, "
            f"event_type={entry.event_type}"
        )
    print(f"TOTAL AUDIT EVENTS: {len(audit.entries)}")


if __name__ == "__main__":
    run_demo()
