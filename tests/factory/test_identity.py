import pytest

from factory.runtime.identity import (
    DecisionAuthority,
    GovernanceRole,
    admin_actor,
    can_make_approval_decision,
    can_override_block,
    human_reviewer,
    security_reviewer,
    system_actor,
)


def test_system_actor_has_no_decision_authority():
    actor = system_actor()

    assert actor.actor_id == "system"
    assert actor.role == GovernanceRole.SYSTEM
    assert actor.authority == DecisionAuthority.NONE
    assert can_make_approval_decision(actor) is False
    assert can_override_block(actor) is False


def test_human_reviewer_can_make_approval_decision_but_cannot_override_block():
    actor = human_reviewer("reviewer-1", display_name="Reviewer One")

    assert actor.actor_id == "reviewer-1"
    assert actor.display_name == "Reviewer One"
    assert actor.role == GovernanceRole.HUMAN_REVIEWER
    assert actor.authority == DecisionAuthority.REVIEW
    assert can_make_approval_decision(actor) is True
    assert can_override_block(actor) is False


def test_security_reviewer_can_approve_and_override_block():
    actor = security_reviewer("security-1")

    assert actor.role == GovernanceRole.SECURITY_REVIEWER
    assert actor.authority == DecisionAuthority.SECURITY_REVIEW
    assert can_make_approval_decision(actor) is True
    assert can_override_block(actor) is True


def test_admin_can_approve_and_override_block():
    actor = admin_actor("admin-1")

    assert actor.role == GovernanceRole.ADMIN
    assert actor.authority == DecisionAuthority.ADMIN
    assert can_make_approval_decision(actor) is True
    assert can_override_block(actor) is True


def test_actor_identity_serializes_authority_context():
    actor = security_reviewer("security-2", display_name="Security Two")

    assert actor.to_dict() == {
        "actor_id": "security-2",
        "display_name": "Security Two",
        "role": "SECURITY_REVIEWER",
        "authority": "SECURITY_REVIEW",
    }


def test_actor_id_is_required():
    with pytest.raises(ValueError, match="actor_id is required"):
        human_reviewer("   ")
