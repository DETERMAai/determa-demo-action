from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta

import pytest

from audit.logger import AuditLogger, EventType


def test_append_only_enforcement():
    logger = AuditLogger()
    now = datetime.now()

    first = logger.append(
        proposal_id="prop-001",
        approval_id="appr-001",
        capability_id="cap-001",
        repo_head="main:abc123",
        witness_result="VALID",
        execution_result="EXECUTED",
        timestamp=now,
        event_type=EventType.EXECUTION_SUCCESS.value,
    )
    entries_before_second = logger.entries

    second = logger.append(
        proposal_id="prop-002",
        approval_id="appr-002",
        capability_id="cap-002",
        repo_head="main:abc124",
        witness_result="VALID",
        execution_result="EXECUTED",
        timestamp=now + timedelta(seconds=1),
        event_type=EventType.EXECUTION_SUCCESS.value,
    )

    assert len(logger.entries) == 2
    assert logger.entries[0] == first
    assert logger.entries[1] == second
    assert len(entries_before_second) == 1
    assert entries_before_second[0] == first
    assert logger.entries != entries_before_second

    with pytest.raises(AttributeError):
        logger.entries.append(first)  # type: ignore[attr-defined]


def test_immutable_records():
    logger = AuditLogger()
    entry = logger.append(
        proposal_id="prop-immut",
        approval_id="appr-immut",
        capability_id="cap-immut",
        repo_head="main:immut",
        witness_result="VALID",
        execution_result="EXECUTED",
        timestamp=datetime.now(),
        event_type=EventType.EXECUTION_SUCCESS.value,
    )

    with pytest.raises(FrozenInstanceError):
        entry.execution_result = "MUTATED"  # type: ignore[misc]


def test_deterministic_ordering():
    logger = AuditLogger()
    base = datetime.now()

    e1 = logger.append(
        proposal_id="prop-a",
        approval_id="appr-a",
        capability_id="cap-a",
        repo_head="main:a",
        witness_result="VALID",
        execution_result="EXECUTED",
        timestamp=base,
        event_type=EventType.EXECUTION_SUCCESS.value,
    )
    e2 = logger.append(
        proposal_id="prop-b",
        approval_id="appr-b",
        capability_id="cap-b",
        repo_head="main:b",
        witness_result="INVALID",
        execution_result="EXECUTION BLOCKED",
        timestamp=base + timedelta(seconds=1),
        event_type=EventType.EXECUTION_BLOCKED.value,
    )
    e3 = logger.append(
        proposal_id="prop-c",
        approval_id="appr-c",
        capability_id="cap-c",
        repo_head="main:c",
        witness_result="VALID",
        execution_result="REPLAY BLOCKED",
        timestamp=base + timedelta(seconds=2),
        event_type=EventType.REPLAY_ATTEMPT.value,
    )

    assert logger.entries == (e1, e2, e3)
    assert [entry.proposal_id for entry in logger.entries] == ["prop-a", "prop-b", "prop-c"]


def test_replay_logging():
    logger = AuditLogger()
    entry = logger.log_replay_attempt(
        proposal_id="prop-replay",
        approval_id="appr-replay",
        capability_id="cap-replay",
        repo_head="main:replay",
        witness_result="VALID",
        timestamp=datetime.now(),
    )

    assert entry.event_type == EventType.REPLAY_ATTEMPT.value
    assert entry.execution_result == "REPLAY BLOCKED"
    assert logger.entries[-1] == entry


def test_blocked_execution_logging():
    logger = AuditLogger()
    entry = logger.log_blocked_execution(
        proposal_id="prop-blocked",
        approval_id="appr-blocked",
        capability_id="cap-blocked",
        repo_head="main:blocked",
        witness_result="INVALID",
        timestamp=datetime.now(),
    )

    assert entry.event_type == EventType.EXECUTION_BLOCKED.value
    assert entry.execution_result == "EXECUTION BLOCKED"
    assert entry.witness_result == "INVALID"
    assert logger.entries[-1] == entry


def test_successful_execution_logging():
    logger = AuditLogger()
    entry = logger.log_successful_execution(
        proposal_id="prop-success",
        approval_id="appr-success",
        capability_id="cap-success",
        repo_head="main:success",
        witness_result="VALID",
        timestamp=datetime.now(),
    )

    assert entry.event_type == EventType.EXECUTION_SUCCESS.value
    assert entry.execution_result == "EXECUTED"
    assert entry.witness_result == "VALID"
    assert logger.entries[-1] == entry
