"""Factory governance identity layer.

Defines actor identity and authority roles for governed runtime decisions.
This is intentionally lightweight and deterministic for the first implementation.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class GovernanceRole(str, Enum):
    SYSTEM = "SYSTEM"
    AI_WORKER = "AI_WORKER"
    HUMAN_REVIEWER = "HUMAN_REVIEWER"
    SECURITY_REVIEWER = "SECURITY_REVIEWER"
    ADMIN = "ADMIN"


class DecisionAuthority(str, Enum):
    NONE = "NONE"
    REVIEW = "REVIEW"
    SECURITY_REVIEW = "SECURITY_REVIEW"
    ADMIN = "ADMIN"


@dataclass(frozen=True)
class ActorIdentity:
    actor_id: str
    display_name: str
    role: GovernanceRole
    authority: DecisionAuthority

    def to_dict(self) -> dict[str, str]:
        return {
            "actor_id": self.actor_id,
            "display_name": self.display_name,
            "role": self.role.value,
            "authority": self.authority.value,
        }


def system_actor() -> ActorIdentity:
    return ActorIdentity(
        actor_id="system",
        display_name="DETERMA Factory Runtime",
        role=GovernanceRole.SYSTEM,
        authority=DecisionAuthority.NONE,
    )


def human_reviewer(actor_id: str, display_name: str | None = None) -> ActorIdentity:
    return ActorIdentity(
        actor_id=_clean_actor_id(actor_id),
        display_name=display_name or actor_id,
        role=GovernanceRole.HUMAN_REVIEWER,
        authority=DecisionAuthority.REVIEW,
    )


def security_reviewer(actor_id: str, display_name: str | None = None) -> ActorIdentity:
    return ActorIdentity(
        actor_id=_clean_actor_id(actor_id),
        display_name=display_name or actor_id,
        role=GovernanceRole.SECURITY_REVIEWER,
        authority=DecisionAuthority.SECURITY_REVIEW,
    )


def admin_actor(actor_id: str, display_name: str | None = None) -> ActorIdentity:
    return ActorIdentity(
        actor_id=_clean_actor_id(actor_id),
        display_name=display_name or actor_id,
        role=GovernanceRole.ADMIN,
        authority=DecisionAuthority.ADMIN,
    )


def can_make_approval_decision(actor: ActorIdentity) -> bool:
    return actor.authority in {
        DecisionAuthority.REVIEW,
        DecisionAuthority.SECURITY_REVIEW,
        DecisionAuthority.ADMIN,
    }


def can_override_block(actor: ActorIdentity) -> bool:
    return actor.authority in {
        DecisionAuthority.SECURITY_REVIEW,
        DecisionAuthority.ADMIN,
    }


def _clean_actor_id(actor_id: str) -> str:
    clean = actor_id.strip()
    if not clean:
        raise ValueError("actor_id is required")
    return clean
