from factory.runtime.governance_decision import GovernanceAction, decide_governance_action
from factory.runtime.identity import human_reviewer, security_reviewer, system_actor
from factory.runtime.risk import RiskLevel, assess_runtime_risk


def test_risk_engine_classifies_low_risk_execution():
    assessment = assess_runtime_risk(
        changed_files=("docs/readme.md",),
        replay_severity="LOW",
        trust_state="TRUSTED",
    )

    assert assessment.level == RiskLevel.LOW
    assert assessment.score == 0
    assert assessment.signals == ()


def test_risk_engine_detects_medium_auth_surface():
    assessment = assess_runtime_risk(
        changed_files=("src/auth.py",),
        replay_severity="LOW",
        trust_state="TRUSTED",
    )

    assert assessment.level == RiskLevel.MEDIUM
    assert assessment.score == 25
    assert assessment.signals[0].name == "auth_surface"


def test_risk_engine_detects_high_risk_from_severity_and_auth_surface():
    assessment = assess_runtime_risk(
        changed_files=("src/auth.py",),
        replay_severity="HIGH",
        trust_state="TRUSTED",
        pending_approvals=1,
    )

    assert assessment.level == RiskLevel.HIGH
    assert assessment.score == 65
    assert {signal.name for signal in assessment.signals} == {
        "severity_high",
        "auth_surface",
        "pending_approvals",
    }


def test_risk_engine_detects_critical_secret_and_untrusted_state():
    assessment = assess_runtime_risk(
        changed_files=("secrets/prod_key.txt",),
        replay_severity="HIGH",
        trust_state="REQUIRES_APPROVAL",
        policy_violations=1,
    )

    assert assessment.level == RiskLevel.CRITICAL
    assert assessment.score >= 100


def test_governance_decision_allows_low_risk_autonomous_execution():
    risk = assess_runtime_risk(
        changed_files=("docs/readme.md",),
        replay_severity="LOW",
        trust_state="TRUSTED",
    )

    decision = decide_governance_action(risk)

    assert decision.action == GovernanceAction.ALLOW_AUTONOMOUS
    assert decision.allowed is True
    assert decision.requires_human_governance is False


def test_governance_decision_requires_review_for_medium_risk_without_actor():
    risk = assess_runtime_risk(
        changed_files=("src/auth.py",),
        replay_severity="LOW",
        trust_state="TRUSTED",
    )

    decision = decide_governance_action(risk)

    assert decision.action == GovernanceAction.REQUIRE_REVIEW
    assert decision.requires_human_governance is True


def test_governance_decision_allows_medium_risk_after_reviewer_policy_check():
    risk = assess_runtime_risk(
        changed_files=("src/auth.py",),
        replay_severity="LOW",
        trust_state="TRUSTED",
    )

    decision = decide_governance_action(
        risk=risk,
        actor=human_reviewer("reviewer-1"),
        reason="reviewed and accepted",
    )

    assert decision.action == GovernanceAction.REQUIRE_REVIEW
    assert decision.policy_result is not None
    assert decision.policy_result.allowed is True


def test_governance_decision_denies_medium_risk_for_actor_without_authority():
    risk = assess_runtime_risk(
        changed_files=("src/auth.py",),
        replay_severity="LOW",
        trust_state="TRUSTED",
    )

    decision = decide_governance_action(
        risk=risk,
        actor=system_actor(),
        reason="system tried to approve",
    )

    assert decision.action == GovernanceAction.DENY
    assert decision.policy_result is not None
    assert decision.policy_result.allowed is False


def test_governance_decision_requires_security_review_for_high_risk_without_actor():
    risk = assess_runtime_risk(
        changed_files=("src/auth.py",),
        replay_severity="HIGH",
        trust_state="TRUSTED",
        pending_approvals=1,
    )

    decision = decide_governance_action(risk)

    assert decision.action == GovernanceAction.REQUIRE_SECURITY_REVIEW
    assert decision.requires_human_governance is True


def test_governance_decision_allows_high_risk_after_security_policy_check():
    risk = assess_runtime_risk(
        changed_files=("src/auth.py",),
        replay_severity="HIGH",
        trust_state="TRUSTED",
        pending_approvals=1,
    )

    decision = decide_governance_action(
        risk=risk,
        actor=security_reviewer("security-1"),
        reason="security review approved",
    )

    assert decision.action == GovernanceAction.REQUIRE_SECURITY_REVIEW
    assert decision.policy_result is not None
    assert decision.policy_result.allowed is True


def test_governance_decision_denies_critical_risk_by_default():
    risk = assess_runtime_risk(
        changed_files=("secrets/prod_key.txt",),
        replay_severity="HIGH",
        trust_state="REQUIRES_APPROVAL",
        policy_violations=1,
    )

    decision = decide_governance_action(risk)

    assert decision.action == GovernanceAction.DENY
    assert decision.allowed is False
