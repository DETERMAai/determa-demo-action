"""Factory runtime CLI.

Small CLI for reading runtime history, timeline, metrics, dashboard, approvals,
and running one bounded factory runtime cycle.
No arbitrary shell execution.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from factory.queue.task_queue import Task, TaskQueue
from factory.runtime.approval_store import ApprovalStore
from factory.runtime.coordinator import RuntimeCoordinator
from factory.runtime.dashboard_data import build_dashboard_data, render_dashboard_summary
from factory.runtime.metrics import compute_runtime_metrics, render_runtime_metrics
from factory.runtime.persistence import RuntimeStore
from factory.runtime.session_store import SessionStore
from factory.runtime.timeline import render_runtime_timeline
from factory.verification.scope_validator import ScopeContract

DEFAULT_HISTORY_PATH = Path("factory/runtime/history/runtime_events.json")
DEFAULT_SESSIONS_PATH = Path("factory/runtime/history/sessions.json")
DEFAULT_APPROVALS_PATH = Path("factory/runtime/history/approvals.json")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="DETERMA Factory Runtime CLI")
    parser.add_argument(
        "command",
        choices=("timeline", "metrics", "dashboard", "approvals", "run-once"),
        help="Command to run",
    )
    parser.add_argument(
        "--history",
        default=str(DEFAULT_HISTORY_PATH),
        help="Path to runtime history JSON",
    )
    parser.add_argument(
        "--sessions",
        default=str(DEFAULT_SESSIONS_PATH),
        help="Path to session history JSON",
    )
    parser.add_argument(
        "--approvals",
        default=str(DEFAULT_APPROVALS_PATH),
        help="Path to approval history JSON",
    )
    parser.add_argument("--task-id", default="manual-task", help="Task id for run-once")
    parser.add_argument("--task-name", default="manual task", help="Task name for run-once")
    parser.add_argument(
        "--changed-file",
        action="append",
        default=[],
        help="Changed file path. Can be passed multiple times.",
    )
    parser.add_argument(
        "--allowed-file",
        action="append",
        default=[],
        help="Allowed file glob. Can be passed multiple times.",
    )
    parser.add_argument(
        "--forbidden-file",
        action="append",
        default=[],
        help="Forbidden file glob. Can be passed multiple times.",
    )
    parser.add_argument(
        "--replay-json",
        default=None,
        help="Optional replay artifact JSON string for Replay Gate.",
    )

    args = parser.parse_args(argv)
    runtime_store = RuntimeStore(Path(args.history))
    events = runtime_store.load()

    if args.command == "timeline":
        print(render_runtime_timeline(events), end="")
        return 0

    if args.command == "metrics":
        metrics = compute_runtime_metrics(events)
        print(render_runtime_metrics(metrics), end="")
        return 0

    if args.command == "dashboard":
        session_store = SessionStore(Path(args.sessions))
        approval_store = ApprovalStore(Path(args.approvals))
        dashboard = build_dashboard_data(
            sessions=session_store.load(),
            events=events,
            approvals=approval_store.load(),
        )
        print(render_dashboard_summary(dashboard), end="")
        return 0

    if args.command == "approvals":
        approval_store = ApprovalStore(Path(args.approvals))
        print(_render_approvals(approval_store), end="")
        return 0

    if args.command == "run-once":
        return _run_once(args, runtime_store)

    return 1


def _run_once(args: argparse.Namespace, store: RuntimeStore) -> int:
    queue = TaskQueue()
    queue.add_task(Task(task_id=args.task_id, name=args.task_name))

    coordinator = RuntimeCoordinator(queue=queue, store=store)
    contract = ScopeContract(
        allowed_files=tuple(args.allowed_file),
        forbidden_files=tuple(args.forbidden_file),
    )
    replay = json.loads(args.replay_json) if args.replay_json else None

    result = coordinator.run_next(
        changed_files=tuple(args.changed_file),
        contract=contract,
        replay=replay,
    )

    if result is None:
        print("No task executed.")
        return 0

    print(f"Task {args.task_id}: {result.outcome()}")
    if result.replay_gate_result is not None:
        print(f"Replay Gate: {result.replay_gate_result.status.value}")
        for reason in result.replay_gate_result.reasons:
            print(f"- {reason}")

    return 0 if result.passed else 1


def _render_approvals(store: ApprovalStore) -> str:
    lines: list[str] = []
    pending = store.pending()
    completed = store.completed()

    lines.append("# DETERMA Factory Approvals")
    lines.append("")
    lines.append(f"Pending: {len(pending)}")
    lines.append(f"Completed: {len(completed)}")
    lines.append("")

    lines.append("## Pending")
    if not pending:
        lines.append("- none")
    else:
        for request in pending:
            lines.append(f"- {request.get('task_id', 'unknown-task')}: {request.get('reason', 'no reason')}")
    lines.append("")

    lines.append("## Completed")
    if not completed:
        lines.append("- none")
    else:
        for request in completed:
            lines.append(
                f"- {request.get('status', 'UNKNOWN')} — "
                f"{request.get('task_id', 'unknown-task')} — "
                f"{request.get('decision_reason', 'no decision reason')}"
            )
    lines.append("")

    return "\n".join(lines).strip() + "\n"


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
