from factory.verification.replay_gate import ReplayGateStatus, evaluate_replay_gate


def test_replay_gate_passes_low_risk_replay():
    result = evaluate_replay_gate({"severity": "LOW", "trust_state": "TRUSTED"})

    assert result.status == ReplayGateStatus.PASS
    assert result.passed is True


def test_replay_gate_requires_approval_for_high_severity():
    result = evaluate_replay_gate({"severity": "HIGH", "trust_state": "TRUSTED"})

    assert result.status == ReplayGateStatus.REQUIRES_APPROVAL
    assert result.requires_approval is True
    assert result.passed is False


def test_replay_gate_blocks_critical_severity():
    result = evaluate_replay_gate({"severity": "CRITICAL", "trust_state": "TRUSTED"})

    assert result.status == ReplayGateStatus.BLOCK
    assert result.passed is False


def test_replay_gate_blocks_blocked_trust_state():
    result = evaluate_replay_gate({"severity": "LOW", "trust_state": "BLOCKED"})

    assert result.status == ReplayGateStatus.BLOCK
    assert result.passed is False
