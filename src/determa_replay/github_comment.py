"""GitHub PR comment integration for DETERMA Replay v0.1.

This module is the integration boundary.
Core replay logic remains deterministic and network-free; this file is allowed to
communicate with GitHub when executed inside GitHub Actions.

Behavior:
- read pull_request event payload
- fetch PR diff
- build a DETERMA Mutation Replay
- post or update a single PR comment

No repository mutation. No merge. No execution authority.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from hashlib import sha256
from typing import Any

from .consequence_engine import generate_consequences
from .diff_parser import ParsedFileChange, parse_unified_diff
from .markdown_renderer import render_markdown
from .replay_model import MutationReplay, ReplayIntegrity
from .severity_engine import compute_severity
from .surface_classifier import aggregate_surfaces
from .trust_engine import determine_trust_state, recommended_action_for_trust_state

COMMENT_MARKER = "<!-- DETERMA_REPLAY_COMMENT_V0 -->"
USER_AGENT = "DETERMA-Replay/0.1"


@dataclass(frozen=True)
class PullRequestContext:
    owner: str
    repo: str
    pr_number: int
    api_url: str

    @property
    def repo_full_name(self) -> str:
        return f"{self.owner}/{self.repo}"


def main() -> int:
    token = os.environ.get("GITHUB_TOKEN")
    event_path = os.environ.get("GITHUB_EVENT_PATH")

    if not token:
        print("DETERMA Replay: missing GITHUB_TOKEN", file=sys.stderr)
        return 1
    if not event_path:
        print("DETERMA Replay: missing GITHUB_EVENT_PATH", file=sys.stderr)
        return 1

    with open(event_path, "r", encoding="utf-8") as handle:
        event = json.load(handle)

    context = _context_from_event(event)
    diff_text = _fetch_pr_diff(context, token)
    replay = build_replay_from_diff(diff_text, stable_value=f"{context.repo_full_name}-{context.pr_number}")
    comment_body = COMMENT_MARKER + "\n" + render_markdown(replay)

    existing_comment_id = _find_existing_comment_id(context, token)
    if existing_comment_id is None:
        _create_comment(context, token, comment_body)
        print(f"DETERMA Replay: created comment on PR #{context.pr_number}")
    else:
        _update_comment(context, token, existing_comment_id, comment_body)
        print(f"DETERMA Replay: updated comment {existing_comment_id} on PR #{context.pr_number}")

    return 0


def build_replay_from_diff(diff_text: str, stable_value: str) -> MutationReplay:
    """Build a canonical MutationReplay from diff text."""
    changes = parse_unified_diff(diff_text)
    diff_parsed = bool(changes)
    surfaces = aggregate_surfaces(changes) if changes else []
    patches = [change.patch for change in changes]
    severity = compute_severity(surfaces, patches)
    consequences = generate_consequences(surfaces)

    integrity = ReplayIntegrity(
        diff_parsed=diff_parsed,
        mutation_surface_classified=bool(surfaces),
        deterministic_replay_generated=True,
    )

    trust_state = determine_trust_state(
        severity=severity,
        surfaces=surfaces,
        patches=patches,
        replay_integrity_complete=integrity.is_complete(),
    )

    replay_id = _replay_id_from_diff(stable_value=stable_value, diff_text=diff_text)

    return MutationReplay(
        replay_id=replay_id,
        severity=severity,
        trust_state=trust_state,
        mutation_surfaces=surfaces or ["Unknown Operational Surface"],
        human_summary=_human_summary(severity, trust_state, surfaces, changes),
        what_changed=_what_changed(changes),
        potential_consequences=consequences,
        replay_timeline=[
            "Diff received",
            "Files classified",
            "Risk evaluated",
            "Trust state determined",
        ],
        replay_integrity=integrity,
        recommended_action=recommended_action_for_trust_state(trust_state),
        metadata={"changed_file_count": len(changes)},
    )


def _context_from_event(event: dict[str, Any]) -> PullRequestContext:
    pr = event.get("pull_request") or {}
    repo = event.get("repository") or {}
    owner = (repo.get("owner") or {}).get("login")
    repo_name = repo.get("name")
    pr_number = pr.get("number")
    api_url = pr.get("url")

    if not owner or not repo_name or not pr_number or not api_url:
        raise ValueError("event payload is not a supported pull_request event")

    return PullRequestContext(owner=owner, repo=repo_name, pr_number=int(pr_number), api_url=api_url)


def _fetch_pr_diff(context: PullRequestContext, token: str) -> str:
    request = urllib.request.Request(
        context.api_url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3.diff",
            "User-Agent": USER_AGENT,
        },
    )
    return _urlopen_text(request)


def _find_existing_comment_id(context: PullRequestContext, token: str) -> int | None:
    url = f"https://api.github.com/repos/{context.repo_full_name}/issues/{context.pr_number}/comments"
    request = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": USER_AGENT,
        },
    )
    comments = json.loads(_urlopen_text(request))
    for comment in comments:
        if COMMENT_MARKER in comment.get("body", ""):
            return int(comment["id"])
    return None


def _create_comment(context: PullRequestContext, token: str, body: str) -> None:
    url = f"https://api.github.com/repos/{context.repo_full_name}/issues/{context.pr_number}/comments"
    request = _json_request(url, token, {"body": body}, method="POST")
    _urlopen_text(request)


def _update_comment(context: PullRequestContext, token: str, comment_id: int, body: str) -> None:
    url = f"https://api.github.com/repos/{context.repo_full_name}/issues/comments/{comment_id}"
    request = _json_request(url, token, {"body": body}, method="PATCH")
    _urlopen_text(request)


def _json_request(url: str, token: str, payload: dict[str, Any], method: str) -> urllib.request.Request:
    data = json.dumps(payload, sort_keys=True).encode("utf-8")
    return urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "User-Agent": USER_AGENT,
        },
    )


def _urlopen_text(request: urllib.request.Request) -> str:
    try:
        with urllib.request.urlopen(request, timeout=20) as response:  # noqa: S310 - GitHub API only via constructed URLs.
            return response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub API request failed: {exc.code} {body}") from exc


def _replay_id_from_diff(stable_value: str, diff_text: str) -> str:
    digest = sha256((stable_value + "\n" + diff_text).encode("utf-8")).hexdigest()[:12]
    return f"REPLAY-{digest}"


def _human_summary(
    severity: str,
    trust_state: str,
    surfaces: list[str],
    changes: list[ParsedFileChange],
) -> str:
    if not changes:
        return "DETERMA could not reconstruct this pull request mutation deterministically."
    surface_text = ", ".join(surfaces) if surfaces else "unknown operational surface"
    return (
        f"This pull request changes {len(changes)} file(s) touching {surface_text}. "
        f"DETERMA classified the mutation as {severity} with trust state {trust_state}."
    )


def _what_changed(changes: list[ParsedFileChange]) -> list[str]:
    if not changes:
        return ["No parseable file changes were found in the pull request diff."]
    return [
        f"{change.status}: {change.path} (+{change.additions}/-{change.deletions})"
        for change in changes
    ]


if __name__ == "__main__":
    raise SystemExit(main())
