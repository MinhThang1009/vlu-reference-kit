"""Execute release workflow bundle checks against synthetic local artifacts."""

from hashlib import sha256
from pathlib import Path
import os
import shutil
import subprocess
import tempfile
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[2]
ZIP = "vlu-reference-kit-community.zip"


class ReleaseBundleTests(unittest.TestCase):
    def setUp(self):
        self.workflows = {
            name: yaml.safe_load((ROOT / ".github/workflows" / filename)
                                 .read_text(encoding="utf-8"))["jobs"]
            for name, filename in (("manual", "release.yml"), ("automatic", "release-please.yml"))
        }
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.dist = self.root / "dist"
        self.dist.mkdir()
        self.payload = b"synthetic artifact bytes\n"
        (self.dist / ZIP).write_bytes(self.payload)
        self.hash = sha256(self.payload).hexdigest()
        self.checksum = self.dist / "SHA256SUMS.txt"
        self.checksum.write_text(self.hash + "  " + ZIP + "\n", encoding="utf-8", newline="\n")

    def validation_scripts(self):
        names = {"Validate release artifacts", "Validate downloaded artifacts",
                 "Validate downloaded release bundle", "Validate ZIP and checksum",
                 "Validate assets before attaching"}
        return [(f"{workflow}/{job}", step["run"]) for workflow, jobs in self.workflows.items()
                for job, value in jobs.items()
                for step in value["steps"] if step["name"] in names]

    def execute(self, script):
        bash = shutil.which("bash")
        if os.name == "nt":
            installed = Path(os.environ["ProgramFiles"]) / "Git/bin/bash.exe"
            if installed.is_file():
                bash = str(installed)
        self.assertIsNotNone(bash, "Bundle checks require Bash and sha256sum")
        return subprocess.run([bash, "-c", script], cwd=self.root, text=True,
                              capture_output=True, timeout=15, check=False)

    def assert_rejected(self):
        for job, script in self.validation_scripts():
            with self.subTest(job=job):
                result = self.execute(script)
                self.assertNotEqual(result.returncode, 0, "Invalid bundle was accepted")

    def test_valid_nonempty_bundle_is_accepted(self):
        for job, script in self.validation_scripts():
            with self.subTest(job=job):
                result = self.execute(script)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_changed_zip_fails_before_attestation_or_upload(self):
        (self.dist / ZIP).write_bytes(b"changed after checksum creation")
        self.assert_rejected()

    def test_attestation_jobs_reject_corrupt_bundle_before_signing(self):
        (self.dist / ZIP).write_bytes(b"changed after artifact transfer")
        for workflow, job in (("manual", "attest"), ("automatic", "attest-release-assets")):
            with self.subTest(workflow=workflow):
                scripts = []
                for step in self.workflows[workflow][job]["steps"]:
                    if step.get("uses", "").startswith("actions/attest@"):
                        break
                    if "run" in step:
                        scripts.append(step["run"])
                else:
                    self.fail("Attestation action is missing")
                result = self.execute("\n".join(scripts) + "\nprintf 'attestation-reached\\n'\n")
                self.assertNotIn("attestation-reached", result.stdout,
                                 "Corrupt bundle reached the signing boundary")

    def test_unexpected_top_level_or_nested_artifacts_are_rejected(self):
        for name in ("extra.txt", ".hidden"):
            with self.subTest(extra=name):
                extra = self.dist / name
                extra.write_text("unexpected", encoding="utf-8")
                self.assert_rejected()
                extra.unlink()
        (self.dist / "nested").mkdir()
        (self.dist / "nested/extra.txt").write_text("unexpected", encoding="utf-8")
        self.assert_rejected()

    def test_empty_zip_is_rejected_even_when_its_checksum_matches(self):
        (self.dist / ZIP).write_bytes(b"")
        self.checksum.write_text(sha256(b"").hexdigest() + "  " + ZIP + "\n", encoding="utf-8", newline="\n")
        self.assert_rejected()

    def test_missing_assets_are_rejected(self):
        for path in (self.checksum, self.dist / ZIP):
            with self.subTest(missing=path.name):
                content = path.read_bytes()
                path.unlink()
                self.assert_rejected()
                path.write_bytes(content)

    def test_checksum_must_cover_exactly_the_expected_zip(self):
        for text in (self.hash + "  ../outside.zip\n",
                     self.hash + "  " + ZIP + "\n" + self.hash + "  " + ZIP + "\n",
                     "not a checksum\n", self.hash + "  " + ZIP + "\nignored\n",
                     "x" * 257):
            with self.subTest(checksum=text):
                self.checksum.write_text(text, encoding="utf-8", newline="\n")
                self.assert_rejected()

    def test_every_job_checks_bundle_before_privileged_operations(self):
        guards = (
            ("manual", "build", "Validate release artifacts", "Transfer release artifacts"),
            ("manual", "attest", "Validate downloaded artifacts", "Attest release artifacts"),
            ("manual", "publish", "Validate downloaded release bundle", "Attach assets and publish the GitHub Release"),
            ("automatic", "build-release-assets", "Validate ZIP and checksum", "Transfer artifact to upload job"),
            ("automatic", "attest-release-assets", "Validate downloaded artifacts", "Attest ZIP and checksum"),
            ("automatic", "attach-release-assets", "Validate assets before attaching", "Attach ZIP and checksum to draft Release"),
        )
        for workflow, job, guard, boundary in guards:
            with self.subTest(workflow=workflow, job=job):
                steps = self.workflows[workflow][job]["steps"]
                names = [step["name"] for step in steps]
                self.assertIn(guard, names)
                step = steps[names.index(guard)]
                self.assertNotIn("continue-on-error", step)
                self.assertNotIn("if", step)
                self.assertLess(names.index(guard), names.index(boundary))


if __name__ == "__main__":
    unittest.main()
