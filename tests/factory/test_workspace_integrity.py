from factory.runtime.branch_workspace import create_branch_workspace_snapshot
from factory.runtime.git_workspace import build_change_set
from factory.verification.workspace_integrity import verify_workspace_integrity


def test_workspace_integrity_passes_for_matching_snapshots():
    change_set = build_change_set(["src/app.py"])
    expected = create_branch_workspace_snapshot(
        base_branch="main",
        working_branch="factory/pr-103-test",
        change_set=change_set,
        diff_snapshot="diff --git a/src/app.py b/src/app.py\n",
    )
    current = create_branch_workspace_snapshot(
        base_branch="main",
        working_branch="factory/pr-103-test",
        change_set=change_set,
        diff_snapshot="diff --git a/src/app.py b/src/app.py\n",
    )

    result = verify_workspace_integrity(expected=expected, current=current)

    assert result.passed is True
    assert result.reasons == ("workspace integrity verified",)


def test_workspace_integrity_fails_on_branch_drift():
    change_set = build_change_set(["src/app.py"])
    expected = create_branch_workspace_snapshot(
        base_branch="main",
        working_branch="factory/pr-103-test",
        change_set=change_set,
    )
    current = create_branch_workspace_snapshot(
        base_branch="main",
        working_branch="factory/other-branch",
        change_set=change_set,
    )

    result = verify_workspace_integrity(expected=expected, current=current)

    assert result.passed is False
    assert any("working branch mismatch" in reason for reason in result.reasons)


def test_workspace_integrity_fails_on_changed_files_drift():
    expected = create_branch_workspace_snapshot(
        base_branch="main",
        working_branch="factory/pr-103-test",
        change_set=build_change_set(["src/app.py"]),
    )
    current = create_branch_workspace_snapshot(
        base_branch="main",
        working_branch="factory/pr-103-test",
        change_set=build_change_set(["src/app.py", "secrets/token.txt"]),
    )

    result = verify_workspace_integrity(expected=expected, current=current)

    assert result.passed is False
    assert "changed files mismatch" in result.reasons


def test_workspace_integrity_fails_on_diff_hash_drift():
    change_set = build_change_set(["src/app.py"])
    expected = create_branch_workspace_snapshot(
        base_branch="main",
        working_branch="factory/pr-103-test",
        change_set=change_set,
        diff_snapshot="old diff\n",
    )
    current = create_branch_workspace_snapshot(
        base_branch="main",
        working_branch="factory/pr-103-test",
        change_set=change_set,
        diff_snapshot="new diff\n",
    )

    result = verify_workspace_integrity(expected=expected, current=current)

    assert result.passed is False
    assert "diff hash mismatch" in result.reasons
    assert "workspace hash mismatch" in result.reasons
