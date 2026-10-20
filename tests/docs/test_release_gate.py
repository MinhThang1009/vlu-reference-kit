"""Exercise the automatic release gate with synthetic verifier outcomes."""

from pathlib import Path
import os
import shutil
import subprocess
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[2]
GATE_NAME = "Wait for exact release commit CI"


class AutomaticReleaseGateTests(unittest.TestCase):
    def setUp(self):
        workflow = yaml.safe_load((ROOT / ".github/workflows/release-please.yml")
                                  .read_text(encoding="utf-8"))
        self.jobs = workflow["jobs"]
        self.build = self.jobs["build-release-assets"]
        gates = [step for step in self.build["steps"] if step.get("name") == GATE_NAME]
        self.assertEqual(len(gates), 1, "Automatic publication needs an exact-commit CI gate")
        self.gate = gates[0]

    def run_gate(self, failures):
        bash = shutil.which("bash")
        if os.name == "nt":
            git_bash = Path(os.environ["ProgramFiles"]) / "Git/bin/bash.exe"
            if git_bash.is_file():
                bash = str(git_bash)
        self.assertIsNotNone(bash, "Release gate tests require Bash")
        environment = os.environ.copy()
        environment["FIXTURE_FAILURES"] = str(failures)
        # Replace only external operations; execute the workflow's actual control flow.
        fixture = """
        calls=0
        python() {
          [[ "$*" == "scripts/verify_release.py" ]] || return 97
          calls=$((calls + 1))
          printf 'guard:%s\\n' "$calls"
          (( calls > FIXTURE_FAILURES ))
        }
        sleep() {
          [[ "$*" == "10" ]] || return 98
          printf 'retry\\n'
        }
        """
        return subprocess.run([bash, "-c", fixture + self.gate["run"]],
                              cwd=ROOT, env=environment, text=True, capture_output=True,
                              timeout=15, check=False)

    def test_gate_binds_release_outputs_and_blocks_publication_jobs(self):
        self.assertEqual(self.build["env"]["RELEASE_TAG"],
                         "${{ needs.release-pr.outputs.tag_name }}")
        self.assertEqual(self.build["env"]["RELEASE_COMMIT_SHA"],
                         "${{ needs.release-pr.outputs.release_sha }}")
        self.assertEqual(self.gate["env"]["GH_TOKEN"], "${{ github.token }}")
        self.assertEqual(self.build["permissions"],
                         {"contents": "read", "checks": "read", "statuses": "read"})
        self.assertFalse(self.gate.get("continue-on-error", False))
        self.assertGreater(self.gate["timeout-minutes"], 0)
        self.assertLessEqual(self.gate["timeout-minutes"], 10)
        names = [step["name"] for step in self.build["steps"]]
        self.assertLess(names.index(GATE_NAME), names.index("Transfer artifact to upload job"))
        for name in ("attest-release-assets", "attach-release-assets"):
            self.assertIn("build-release-assets", self.jobs[name]["needs"])
            self.assertEqual(self.jobs[name]["if"],
                             "${{ needs.release-pr.outputs.release_created == 'true' }}")

    def test_success_requires_no_retry(self):
        result = self.run_gate(0)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.count("guard:"), 1)
        self.assertNotIn("retry", result.stdout)

    def test_pending_checks_are_rechecked_before_success(self):
        result = self.run_gate(2)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.count("guard:"), 3)
        self.assertEqual(result.stdout.count("retry"), 2)

    def test_persistent_failure_stops_at_retry_limit(self):
        result = self.run_gate(100)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout.count("guard:"), 30)
        self.assertEqual(result.stdout.count("retry"), 29)
        self.assertIn("::error::", result.stdout)


if __name__ == "__main__":
    unittest.main()
