"""Factory runtime CLI.

Small CLI for reading runtime history, timeline, metrics, and running one
bounded factory runtime cycle.
No arbitrary shell execution.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from factory.queue.task_queue import Task, TaskQueue
from factory.runtime.coordinator import RuntimeCoordinator
from factory.runtime.metrics import compute_runtime_metrics, render_runtime_metrics
from factory.runtime.persistence import RuntimeStore
from factory.runtime.timeline import render_runtime_timeline
from factory.verification.scope_validator import ScopeContract

DEFAULT_HISTORY_PATH = Path("factory/runtime/history/runtime_events.json")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="DETERMA Factory Runtime CLI")
    parser.add_argument(
        "command",
        choices=("timeline", "metrics", "run-once"),
        help="Command to run",
    )
    parser.add_argument(
        "--history",
        default=str(DEFAULT_HISTORY_PATH),
        help="Path to runtime history JSON",
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
    store = RuntimeStore(Path(args.history))
    events = store.load()

    if args.command == "timeline":
        print(render_runtime_timeline(events), end="")
        return 0

    if args.command == "metrics":
        metrics = compute_runtime_metrics(events)
        print(render_runtime_metrics(metrics), end="")
        return 0

    if args.command == "run-once":
        return _run_once(args, store)

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


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
