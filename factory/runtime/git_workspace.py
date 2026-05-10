"""Git workspace adapter for the Factory Runtime.

This module normalizes changed-file inputs from a Git workspace.
It intentionally does not execute shell commands in v0.1.
External CI may pass the output of `git diff --name-only` through a file or stdin.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class WorkspaceChangeSet:
    """Normalized changed file set for runtime verification."""

    changed_files: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {"changed_files": list(self.changed_files)}


def build_change_set(paths: Iterable[str]) -> WorkspaceChangeSet:
    """Build a deterministic changed-file set from raw path strings."""
    normalized = sorted({_normalize_path(path) for path in paths if _normalize_path(path)})
    return WorkspaceChangeSet(changed_files=tuple(normalized))


def build_change_set_from_file(path: Path) -> WorkspaceChangeSet:
    """Load newline-delimited changed files from a file.

    This lets CI or a future Git adapter provide changed files without letting
    the runtime execute arbitrary shell commands.
    """
    if not path.exists():
        return WorkspaceChangeSet(changed_files=())

    return build_change_set(path.read_text(encoding="utf-8").splitlines())


def build_change_set_from_git_name_only_output(output: str) -> WorkspaceChangeSet:
    """Build a change set from `git diff --name-only` style output."""
    return build_change_set(output.splitlines())


def build_change_set_from_status_output(output: str) -> WorkspaceChangeSet:
    """Build a change set from simple `git status --short` style output.

    Supports lines like:
    - M path.py
    - A new.py
    - D old.py
    - R old.py -> new.py
    """
    paths: list[str] = []

    for line in output.splitlines():
        stripped = line.strip()
        if not stripped:
            continue

        path_part = stripped[2:].strip() if len(stripped) > 2 else stripped
        if " -> " in path_part:
            path_part = path_part.split(" -> ", 1)[1]
        paths.append(path_part)

    return build_change_set(paths)


def _normalize_path(path: str) -> str:
    return path.strip().replace("\\", "/").lstrip("/")
