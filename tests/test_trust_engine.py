from src.determa_replay.severity_engine import CRITICAL, HIGH, LOW, MEDIUM
from src.determa_replay.surface_classifier import (
    AUTH_IAM,
    BUSINESS_LOGIC,
    CI_CD,
    DEPLOYMENT,
    DOCUMENTATION,
    SECRET_ACCESS,
    UNKNOWN_OPERATIONAL,
)
from src.determa_replay.trust_engine import (
    BLOCKED,
    REQUIRES_APPROVAL,
    TRUSTED,
    UNEXPLAINABLE,
    determine_trust_state,
    recommended_action_for_trust_state,
)


def test_docs_low_is_trusted():
    assert determine_trust_state(LOW, [DOCUMENTATION]) == TRUSTED


def test_secret_access_is_blocked():
    assert determine_trust_state(CRITICAL, [SECRET_ACCESS]) == BLOCKED


def test_critical_deployment_requires_approval():
    assert determine_trust_state(CRITICAL, [DEPLOYMENT]) == REQUIRES_APPROVAL


def test_high_ci_cd_requires_approval():
    assert determine_trust_state(HIGH, [CI_CD]) == REQUIRES_APPROVAL


def test_medium_business_logic_requires_approval():
    assert determine_trust_state(MEDIUM, [BUSINESS_LOGIC]) == REQUIRES_APPROVAL


def test_unknown_medium_is_unexplainable():
    assert determine_trust_state(MEDIUM, [UNKNOWN_OPERATIONAL]) == UNEXPLAINABLE


def test_incomplete_integrity_is_unexplainable():
    assert determine_trust_state(
        HIGH,
        [AUTH_IAM],
        replay_integrity_complete=False,
    ) == UNEXPLAINABLE


def test_blocking_patch_patterns_block():
    assert determine_trust_state(
        HIGH,
        [CI_CD],
        patches=["approval_required: false"],
    ) == BLOCKED


def test_recommended_action_for_trusted():
    assert recommended_action_for_trust_state(TRUSTED) == "Safe to review normally."


def test_recommended_action_for_requires_approval():
    assert recommended_action_for_trust_state(REQUIRES_APPROVAL) == "Human approval required before merge."


def test_recommended_action_for_blocked():
    assert recommended_action_for_trust_state(BLOCKED) == "Do not merge until the mutation is explicitly reviewed and corrected."


def test_recommended_action_for_unexplainable():
    assert recommended_action_for_trust_state(UNEXPLAINABLE) == "Replay could not be reconstructed. Treat this mutation as untrusted."
