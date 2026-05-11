from datetime import datetime, timedelta

import pytest

from executor.capability import consume_capability, issue_capability
from executor.execute import execute
from executor.state_witness import validate_repository_state
from orchestrator.proposal import create_proposal
from orchestrator.state_machine import State


def _approved_proposal(proposal_id: str, repo_head: str):
    proposal = create_proposal(
        proposal_id=proposal_id,
        repo_head=repo_head,
        patch_hash="sha256:test-patch",
        requested_action="Apply deterministic mutation",
        created_at=datetime.now(),
    )
    # Proposal objects are immutable; this simulates the state-machine transition.
    object.__setattr__(proposal, "status", State.APPROVED)
    return proposal


def test_valid_execution_succeeds():
    now = datetime.now()
    proposal = _approved_proposal("prop-001", "main:abc123")
    witness = validate_repository_state("main:abc123", "main:abc123", now)
    capability = issue_capability(
        capability_id="cap-001",
        proposal_id=proposal.proposal_id,
        repo_head="main:abc123",
        issued_at=now,
    )

    result, consumed = execute(
        proposal=proposal,
        witness=witness,
        capability=capability,
        mutation=lambda: "EXECUTED",
        consumed_at=now + timedelta(seconds=1),
    )

    assert result == "EXECUTED"
    assert consumed.is_consumed is True


def test_capability_consumed_after_execution():
    now = datetime.now()
    consumed_at = now + timedelta(seconds=5)
    proposal = _approved_proposal("prop-002", "main:abc124")
    witness = validate_repository_state("main:abc124", "main:abc124", now)
    capability = issue_capability(
        capability_id="cap-002",
        proposal_id=proposal.proposal_id,
        repo_head="main:abc124",
        issued_at=now,
    )

    _, consumed = execute(
        proposal=proposal,
        witness=witness,
        capability=capability,
        mutation=lambda: {"ok": True},
        consumed_at=consumed_at,
    )

    assert consumed.is_consumed is True
    assert consumed.consumed_at == consumed_at


def test_replay_attempt_blocked():
    now = datetime.now()
    proposal = _approved_proposal("prop-003", "main:abc125")
    witness = validate_repository_state("main:abc125", "main:abc125", now)
    capability = issue_capability(
        capability_id="cap-003",
        proposal_id=proposal.proposal_id,
        repo_head="main:abc125",
        issued_at=now,
    )

    first_result, consumed = execute(
        proposal=proposal,
        witness=witness,
        capability=capability,
        mutation=lambda: "once",
        consumed_at=now + timedelta(seconds=1),
    )
    assert first_result == "once"

    mutation_calls = {"count": 0}

    def mutation():
        mutation_calls["count"] += 1
        return "should-not-run"

    with pytest.raises(ValueError, match="EXECUTION BLOCKED.*replay blocked"):
        execute(
            proposal=proposal,
            witness=witness,
            capability=consumed,
            mutation=mutation,
            consumed_at=now + timedelta(seconds=2),
        )

    assert mutation_calls["count"] == 0


def test_witness_failure_blocks_execution():
    now = datetime.now()
    proposal = _approved_proposal("prop-004", "main:abc126")
    witness = validate_repository_state("main:abc126", "main:def999", now)
    capability = issue_capability(
        capability_id="cap-004",
        proposal_id=proposal.proposal_id,
        repo_head="main:abc126",
        issued_at=now,
    )

    mutation_calls = {"count": 0}

    def mutation():
        mutation_calls["count"] += 1
        return "nope"

    with pytest.raises(ValueError, match="EXECUTION BLOCKED.*invalid witness"):
        execute(
            proposal=proposal,
            witness=witness,
            capability=capability,
            mutation=mutation,
            consumed_at=now + timedelta(seconds=1),
        )

    assert mutation_calls["count"] == 0
    assert capability.is_consumed is False


def test_invalid_proposal_state_blocks_execution():
    now = datetime.now()
    proposal = create_proposal(
        proposal_id="prop-005",
        repo_head="main:abc127",
        patch_hash="sha256:test",
        requested_action="blocked action",
        created_at=now,
    )
    witness = validate_repository_state("main:abc127", "main:abc127", now)
    capability = issue_capability(
        capability_id="cap-005",
        proposal_id=proposal.proposal_id,
        repo_head="main:abc127",
        issued_at=now,
    )

    mutation_calls = {"count": 0}

    def mutation():
        mutation_calls["count"] += 1
        return "nope"

    with pytest.raises(ValueError, match="EXECUTION BLOCKED.*proposal state"):
        execute(
            proposal=proposal,
            witness=witness,
            capability=capability,
            mutation=mutation,
            consumed_at=now + timedelta(seconds=1),
        )

    assert mutation_calls["count"] == 0
    assert capability.is_consumed is False


def test_consumed_capability_blocks_execution():
    now = datetime.now()
    proposal = _approved_proposal("prop-006", "main:abc128")
    witness = validate_repository_state("main:abc128", "main:abc128", now)
    capability = issue_capability(
        capability_id="cap-006",
        proposal_id=proposal.proposal_id,
        repo_head="main:abc128",
        issued_at=now,
    )
    consumed = consume_capability(capability, now + timedelta(seconds=1))

    mutation_calls = {"count": 0}

    def mutation():
        mutation_calls["count"] += 1
        return "nope"

    with pytest.raises(ValueError, match="EXECUTION BLOCKED.*consumed"):
        execute(
            proposal=proposal,
            witness=witness,
            capability=consumed,
            mutation=mutation,
            consumed_at=now + timedelta(seconds=2),
        )

    assert mutation_calls["count"] == 0


def test_execution_deterministic_under_repeated_validation():
    now = datetime.now()
    consumed_at = now + timedelta(seconds=5)
    proposal = _approved_proposal("prop-007", "main:abc129")
    witness = validate_repository_state("main:abc129", "main:abc129", now)

    capability_1 = issue_capability(
        capability_id="cap-007-a",
        proposal_id=proposal.proposal_id,
        repo_head="main:abc129",
        issued_at=now,
    )
    capability_2 = issue_capability(
        capability_id="cap-007-b",
        proposal_id=proposal.proposal_id,
        repo_head="main:abc129",
        issued_at=now,
    )

    result_1, consumed_1 = execute(
        proposal=proposal,
        witness=witness,
        capability=capability_1,
        mutation=lambda: "stable-result",
        consumed_at=consumed_at,
    )
    result_2, consumed_2 = execute(
        proposal=proposal,
        witness=witness,
        capability=capability_2,
        mutation=lambda: "stable-result",
        consumed_at=consumed_at,
    )

    assert result_1 == result_2
    assert consumed_1.is_consumed is True
    assert consumed_2.is_consumed is True
    assert consumed_1.consumed_at == consumed_2.consumed_at == consumed_at


def test_fail_closed_semantics_preserved():
    now = datetime.now()
    proposal = _approved_proposal("prop-008", "main:abc130")
    witness = validate_repository_state("main:abc130", "main:abc130", now)
    capability = issue_capability(
        capability_id="cap-008",
        proposal_id=proposal.proposal_id,
        repo_head="main:abc130",
        issued_at=now,
    )

    mutation_calls = {"count": 0}

    def mutation():
        mutation_calls["count"] += 1
        return "nope"

    with pytest.raises(ValueError, match="EXECUTION BLOCKED.*missing witness"):
        execute(
            proposal=proposal,
            witness=None,
            capability=capability,
            mutation=mutation,
            consumed_at=now + timedelta(seconds=1),
        )

    with pytest.raises(ValueError, match="EXECUTION BLOCKED.*missing capability"):
        execute(
            proposal=proposal,
            witness=witness,
            capability=None,
            mutation=mutation,
            consumed_at=now + timedelta(seconds=1),
        )

    mismatched_capability = issue_capability(
        capability_id="cap-008-mismatch",
        proposal_id="different-proposal",
        repo_head="main:abc130",
        issued_at=now,
    )
    with pytest.raises(ValueError, match="EXECUTION BLOCKED.*mismatched proposal/capability linkage"):
        execute(
            proposal=proposal,
            witness=witness,
            capability=mismatched_capability,
            mutation=mutation,
            consumed_at=now + timedelta(seconds=1),
        )

    assert mutation_calls["count"] == 0
    assert capability.is_consumed is False
