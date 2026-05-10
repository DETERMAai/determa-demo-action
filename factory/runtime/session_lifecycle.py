"""Factory session lifecycle manager.

Creates, updates, and persists autonomous execution sessions.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from factory.runtime.git_workspace import WorkspaceChangeSet
from factory.runtime.session import FactorySession, create_session, with_runtime_result
from factory.runtime.session_store import SessionStore


@dataclass
class SessionLifecycleManager:
    """Manage reconstructable factory session lifecycle."""

    store: SessionStore

    def start_session(
        self,
        task_id: str,
        task_name: str,
        change_set: WorkspaceChangeSet,
    ) -> FactorySession:
        """Create and persist a new session."""
        session = create_session(
            task_id=task_id,
            task_name=task_name,
            change_set=change_set,
        )
        self.store.append(session)
        return session

    def complete_session(
        self,
        session: FactorySession,
        replay: dict[str, Any] | None,
    ) -> FactorySession:
        """Mark a session as complete and persist it."""
        updated = with_runtime_result(
            session=session,
            replay=replay,
            outcome="PASSED",
            state="COMPLETE",
        )
        self.store.append(updated)
        return updated

    def block_session(
        self,
        session: FactorySession,
        replay: dict[str, Any] | None,
    ) -> FactorySession:
        """Mark a session as blocked and persist it."""
        updated = with_runtime_result(
            session=session,
            replay=replay,
            outcome="BLOCKED",
            state="BLOCKED",
        )
        self.store.append(updated)
        return updated
