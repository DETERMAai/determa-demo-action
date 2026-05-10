from src.determa_replay.severity_engine import CRITICAL, HIGH, LOW, MEDIUM, compute_severity
from src.determa_replay.surface_classifier import (
    AUTH_IAM,
    BUSINESS_LOGIC,
    CI_CD,
    DEPLOYMENT,
    DOCUMENTATION,
    INFRA_AS_CODE,
    RUNTIME_INFRA,
    SECRET_ACCESS,
    TESTS,
    UNKNOWN_OPERATIONAL,
)


def test_docs_are_low():
    assert compute_severity([DOCUMENTATION]) == LOW


def test_business_logic_is_medium():
    assert compute_severity([BUSINESS_LOGIC]) == MEDIUM


def test_ci_cd_is_high_by_default():
    assert compute_severity([CI_CD]) == HIGH


def test_deployment_is_critical():
    assert compute_severity([DEPLOYMENT]) == CRITICAL


def test_secret_access_is_critical():
    assert compute_severity([SECRET_ACCESS]) == CRITICAL


def test_auth_iam_is_critical():
    assert compute_severity([AUTH_IAM]) == CRITICAL


def test_runtime_and_infra_are_high():
    assert compute_severity([RUNTIME_INFRA]) == HIGH
    assert compute_severity([INFRA_AS_CODE]) == HIGH


def test_tests_are_medium_by_default():
    assert compute_severity([TESTS]) == MEDIUM


def test_unknown_operational_is_medium():
    assert compute_severity([UNKNOWN_OPERATIONAL]) == MEDIUM


def test_high_keyword_escalates_docs_to_high():
    assert compute_severity([DOCUMENTATION], ["disable verification instructions"]) == HIGH


def test_critical_keyword_escalates_ci_cd_to_critical():
    assert compute_severity([CI_CD], ["deploy to production rollout 100%"] ) == CRITICAL


def test_multiple_surfaces_returns_highest_severity():
    assert compute_severity([DOCUMENTATION, BUSINESS_LOGIC, SECRET_ACCESS]) == CRITICAL
