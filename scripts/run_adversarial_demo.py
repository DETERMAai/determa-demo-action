#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import os
import sys
from pathlib import Path

try:
    import run_product_demo as product_demo
except ModuleNotFoundError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import run_product_demo as product_demo


def _blocked(name: str, reason: str) -> dict:
    return {"name": name, "blocked": True, "reason": reason}


def _run_scenarios(demo_id: str) -> dict:
    defaults = product_demo.build_default_args()
    args = argparse.Namespace(
        tenant_id=defaults["tenant_id"],
        demo_id=demo_id,
        requested_by=defaults["requested_by"],
        repo="org/not-allowed",
        branch="feature/not-allowed",
    )
    base_state = product_demo._local_seed_state(args)
    scenarios = []

    # [1] Missing Approval
    state = copy.deepcopy(base_state)
    state["approval_state"] = "MISSING"
    try:
        product_demo._local_execute(state)
        scenarios.append({"name": "Missing Approval", "blocked": False, "reason": "unexpected execution"})
    except product_demo.LocalAuthorityError as exc:
        scenarios.append(_blocked("Missing Approval", str(exc)))

    # [2] State Drift / tampered patch after approval
    state = copy.deepcopy(base_state)
    state["patch_hash"] = "sha256:tampered"
    state["witness_match"] = False
    try:
        product_demo._local_execute(state)
        scenarios.append({"name": "State Drift", "blocked": False, "reason": "unexpected execution"})
    except product_demo.LocalAuthorityError as exc:
        scenarios.append(_blocked("State Drift", str(exc)))

    # [3] Replay Attack
    state = copy.deepcopy(base_state)
    first = product_demo._local_execute(state)
    second = product_demo._local_execute(state)
    replay_detected = bool(((second.get("data") or {}).get("audit_linkage") or {}).get("replay_detected"))
    same_pr = ((first.get("data") or {}).get("github_pr_url")) == ((second.get("data") or {}).get("github_pr_url"))
    scenarios.append(
        {
            "name": "Replay Attack",
            "blocked": replay_detected and same_pr,
            "reason": "idempotent replay blocked" if replay_detected and same_pr else "replay not blocked",
            "first_pr": (first.get("data") or {}).get("github_pr_url"),
            "second_pr": (second.get("data") or {}).get("github_pr_url"),
        }
    )

    # [4] Invalid Capability
    state = copy.deepcopy(base_state)
    state["capability_id"] = ""
    try:
        product_demo._local_execute(state)
        scenarios.append({"name": "Invalid Capability", "blocked": False, "reason": "unexpected execution"})
    except product_demo.LocalAuthorityError as exc:
        scenarios.append(_blocked("Invalid Capability", str(exc)))

    # [5] Missing Release
    state = copy.deepcopy(base_state)
    state["release_id"] = ""
    try:
        product_demo._local_execute(state)
        scenarios.append({"name": "Missing Release", "blocked": False, "reason": "unexpected execution"})
    except product_demo.LocalAuthorityError as exc:
        scenarios.append(_blocked("Missing Release", str(exc)))

    # [6] Repo Violation
    env_backup = dict(os.environ)
    try:
        os.environ["DETERMA_DEMO_REAL_GITHUB"] = "1"
        os.environ["GITHUB_TOKEN"] = "demo-token"
        os.environ["DETERMA_DEMO_REPO"] = "org/sandbox-only"
        os.environ["DETERMA_DEMO_BASE_BRANCH"] = "main"
        try:
            product_demo._resolve_real_github_config(args)
            scenarios.append({"name": "Repo Violation", "blocked": False, "reason": "repo mismatch not blocked"})
        except product_demo.LocalAuthorityError as exc:
            scenarios.append(_blocked("Repo Violation", str(exc)))
    finally:
        os.environ.clear()
        os.environ.update(env_backup)

    # [7] Branch Violation
    env_backup = dict(os.environ)
    try:
        os.environ["DETERMA_DEMO_REAL_GITHUB"] = "1"
        os.environ["GITHUB_TOKEN"] = "demo-token"
        os.environ["DETERMA_DEMO_REPO"] = "org/not-allowed"
        os.environ["DETERMA_DEMO_BASE_BRANCH"] = "main"
        args_ok_repo = argparse.Namespace(
            tenant_id=defaults["tenant_id"],
            demo_id=demo_id,
            requested_by=defaults["requested_by"],
            repo="org/not-allowed",
            branch="feature/not-allowed",
        )
        try:
            product_demo._resolve_real_github_config(args_ok_repo)
            scenarios.append({"name": "Branch Violation", "blocked": False, "reason": "branch policy not enforced"})
        except product_demo.LocalAuthorityError as exc:
            scenarios.append(_blocked("Branch Violation", str(exc)))
    finally:
        os.environ.clear()
        os.environ.update(env_backup)

    all_blocked = all(bool(item.get("blocked")) for item in scenarios)
    return {"scenarios": scenarios, "all_blocked": all_blocked}


def _render_output(result: dict) -> str:
    rows = []
    labels = [
        "Missing Approval",
        "State Drift",
        "Replay Attack",
        "Invalid Capability",
        "Missing Release",
        "Repo Violation",
        "Branch Violation",
    ]
    by_name = {item["name"]: item for item in result["scenarios"]}
    for i, label in enumerate(labels, start=1):
        status = "BLOCKED" if by_name.get(label, {}).get("blocked") else "FAILED"
        rows.append(f"[{i}] {label} -> {status}")
    footer = "Result: ALL ATTACK PATHS BLOCKED (FAIL-CLOSED)" if result.get("all_blocked") else "Result: FAIL-CLOSED CHECK FAILED"
    return "\n".join(["=== DETERMA Adversarial Demo ===", "", *rows, "", footer])


def main() -> int:
    parser = argparse.ArgumentParser(description="Run adversarial fail-closed demo scenarios.")
    parser.add_argument("--demo-id", default="default")
    args = parser.parse_args()

    result = _run_scenarios(args.demo_id)
    print(_render_output(result))
    return 0 if result.get("all_blocked") else 1


if __name__ == "__main__":
    raise SystemExit(main())
