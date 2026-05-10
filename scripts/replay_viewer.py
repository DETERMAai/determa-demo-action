#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

DEFAULT_REPORT = "reports/governed_pr_demo.json"


def load_report(path: str) -> dict[str, Any]:
    p = Path(path)
    if not p.exists():
        raise SystemExit(
            f"Missing replay report: {path}\n"
            "Run `make demo-report` first to generate local DETERMA evidence."
        )
    return json.loads(p.read_text(encoding="utf-8"))


def value(report: dict[str, Any], key: str, fallback: str = "unknown") -> str:
    raw = report.get(key)
    if raw is None or raw == "":
        return fallback
    return str(raw)


def command_observe(report: dict[str, Any]) -> None:
    print("=== DETERMA Observe ===")
    print("AI mutation activity observed from local governed demo evidence.")
    print()
    print(f"Mutation: governed PR demo / {value(report, 'demo_id')}")
    print(f"Job: {value(report, 'job_id')}")
    print(f"Decision: {value(report, 'authority_chain_status')}")
    print(f"Replay detected: {value(report, 'replay_detected')}")
    print(f"Draft PR: {value(report, 'second_run_pr_url')}")


def command_replay(report: dict[str, Any]) -> None:
    print("=== DETERMA Replay ===")
    print("09:14  AI-generated code mutation proposed")
    print(f"09:15  Approval recorded: {value(report, 'approval_id')}")
    print(f"09:16  Capability issued: {value(report, 'capability_id')}")
    print(f"09:16  State witness matched: {value(report, 'witness_id')}")
    print(f"09:17  Execution release consumed: {value(report, 'release_id')}")
    print(f"09:17  Draft PR created or reused: {value(report, 'second_run_pr_url')}")
    if str(report.get("replay_detected")).lower() == "true":
        print("09:18  Replay attempt detected and collapsed into existing execution")
    print()
    print("Result: mutation history is reconstructable.")


def command_lineage(report: dict[str, Any]) -> None:
    print("=== DETERMA Mutation Lineage ===")
    print("AI proposal")
    print("  ↓")
    print(f"Human approval: {value(report, 'approval_id')}")
    print("  ↓")
    print(f"Capability: {value(report, 'capability_id')}")
    print("  ↓")
    print(f"State witness: {value(report, 'witness_id')}")
    print("  ↓")
    print(f"Execution release: {value(report, 'release_id')}")
    print("  ↓")
    print(f"Mutation evidence: {value(report, 'binding_id')}")
    print("  ↓")
    print(f"PR / output: {value(report, 'second_run_pr_url')}")


def command_explain(report: dict[str, Any]) -> None:
    print("=== DETERMA Explain ===")
    status = value(report, "authority_chain_status")
    replay = str(report.get("replay_detected")).lower() == "true"
    if status == "PASSED":
        print("Mutation trusted because:")
        print("- human approval was present")
        print("- capability was issued")
        print("- state witness matched")
        print("- execution release was consumed")
        print("- replay attempt did not create duplicate execution" if replay else "- no replay conflict was observed")
        print("- authority lineage is reconstructable")
    else:
        print("Mutation not trusted because the authority chain did not pass.")
    print()
    print(f"Idempotency key: {value(report, 'idempotency_key')}")


def main() -> int:
    parser = argparse.ArgumentParser(description="View DETERMA mutation replay evidence.")
    parser.add_argument("command", choices=["observe", "replay", "lineage", "explain"])
    parser.add_argument("--report", default=DEFAULT_REPORT)
    args = parser.parse_args()

    report = load_report(args.report)
    if args.command == "observe":
        command_observe(report)
    elif args.command == "replay":
        command_replay(report)
    elif args.command == "lineage":
        command_lineage(report)
    elif args.command == "explain":
        command_explain(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
