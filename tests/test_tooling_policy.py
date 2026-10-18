"""Phát hiện drift khi cập nhật policy, lockfile hoặc action của repo."""

from pathlib import Path
import json
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from sync_action_pins import action_repositories
from validate_tooling import validate_tooling


class ToolingPolicyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / ".github").mkdir()
        (self.root / "kit").mkdir()
        self.write(".github/ci-toolchain.json", {"npm-tools": {"lint": {"package": "lint", "version": "1.0.0"}}})
        self.write("package.json", {"devDependencies": {"lint": "1.0.0"}})
        self.lock = {"packages": {"": {"devDependencies": {"lint": "1.0.0"}}, "node_modules/lint": {"version": "1.0.0"}}}
        self.write("package-lock.json", self.lock)
        for name in ("requirements-docs.txt", "requirements-docs.lock"):
            (self.root / name).write_text("example==1.0.0\n", encoding="utf-8")
        for name in ("LICENSE", "kit/LICENSE"):
            (self.root / name).write_bytes(b"Synthetic license")
        self.write("release-please-config.json", {"release-type": "simple", "version-file": "version.txt",
                                                   "skip-github-release": True, "initial-version": "0.1.0"})
        self.write(".release-please-manifest.json", {})
        (self.root / "version.txt").write_text("0.1.0\n", encoding="utf-8")

    def write(self, name, value):
        (self.root / name).write_text(json.dumps(value), encoding="utf-8")

    def test_matching_toolchain_passes(self):
        self.assertEqual(validate_tooling(self.root), [])

    def test_lock_cannot_silently_change_direct_policy_version(self):
        self.lock["packages"]["node_modules/lint"]["version"] = "2.0.0"
        self.write("package-lock.json", self.lock)
        self.assertTrue(any("sai phiên bản" in error for error in validate_tooling(self.root)))

    def test_python_direct_pin_must_be_in_lock(self):
        (self.root / "requirements-docs.lock").write_text("other==1.0.0\n", encoding="utf-8")
        self.assertTrue(any("Python" in error for error in validate_tooling(self.root)))

    def test_overrides_cannot_be_omitted_from_lock(self):
        self.write("package.json", {"devDependencies": {"lint": "1.0.0"}, "overrides": {"nested": "1.1.0"}})
        self.assertTrue(any("Override" in error for error in validate_tooling(self.root)))

    def test_packaged_mit_notice_must_match_repository(self):
        (self.root / "kit/LICENSE").write_bytes(b"Wrong license")
        self.assertTrue(any("MIT" in error for error in validate_tooling(self.root)))

    def test_synchronizer_accepts_setup_node_used_by_documentation_ci(self):
        text = "jobs:\n  docs:\n    steps:\n      - uses: actions/setup-node@" + "a" * 40 + "\n"
        self.assertEqual(action_repositories(Path("fixture.yml"), text), {"actions/setup-node"})

    def test_release_pr_must_update_manifest_and_version_together(self):
        self.write(".release-please-manifest.json", {".": "0.2.0"})
        self.assertTrue(any("version.txt và manifest" in error for error in validate_tooling(self.root)))

    def test_release_please_cannot_enable_ungated_publication(self):
        self.write("release-please-config.json", {"release-type": "simple", "version-file": "version.txt",
                                                   "skip-github-release": False, "initial-version": "0.1.0"})
        self.assertTrue(any("chỉ quản lý PR" in error for error in validate_tooling(self.root)))


if __name__ == "__main__":
    unittest.main()
