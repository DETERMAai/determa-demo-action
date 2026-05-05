from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PublicDemoPackageTests(unittest.TestCase):
    def test_private_core_files_not_included(self) -> None:
        self.assertFalse((ROOT / "app" / "orchestrator" / "app.py").exists())
        self.assertFalse((ROOT / "init.sql").exists())

    def test_readme_contains_public_core_exclusion_statement(self) -> None:
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("production DETERMA authority core is not included", text)

    def test_action_and_entrypoint_exist(self) -> None:
        self.assertTrue((ROOT / "action.yml").exists())
        self.assertTrue((ROOT / "entrypoint.sh").exists())

    def test_demo_scripts_exist(self) -> None:
        self.assertTrue((ROOT / "scripts" / "run_product_demo.py").exists())
        self.assertTrue((ROOT / "scripts" / "run_adversarial_demo.py").exists())
        self.assertTrue((ROOT / "scripts" / "fake_agent_loop.py").exists())

    def test_no_internal_patent_or_v6_docs(self) -> None:
        blocked_tokens = ("patent", "provisional", "v6")
        for file in ROOT.rglob("*"):
            if not file.is_file():
                continue
            rel = str(file.relative_to(ROOT)).lower()
            if rel.startswith("tests/"):
                continue
            for token in blocked_tokens:
                self.assertNotIn(token, rel)

    def test_zero_setup_mock_mode_runs(self) -> None:
        proc = subprocess.run(
            [sys.executable, "scripts/run_product_demo.py", "--operator-token", "demo-token"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        output = (proc.stdout or "") + (proc.stderr or "")
        self.assertEqual(proc.returncode, 0, msg=output)
        self.assertIn("Result: GOVERNED EXECUTION ENFORCED", output)


if __name__ == "__main__":
    unittest.main()
