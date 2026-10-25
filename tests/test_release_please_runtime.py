"""The editor schema and Action tag cannot stand in for the owned core lock."""

from pathlib import Path
import json
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from audit_freshness import release_please_core_findings, release_please_findings


class ReleasePleaseRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.runtime = Path(".github/actions/release-please")
        (self.root / self.runtime).mkdir(parents=True)

    def write_runtime(self, version="17.6.0", locked=None):
        package = {"dependencies": {"release-please": version}}
        lock = {"packages": {"": package, "node_modules/release-please": {"version": locked or version}}}
        for name, value in [("package.json", package), ("package-lock.json", lock)]:
            (self.root / self.runtime / name).write_text(json.dumps(value), encoding="utf-8")

    def test_current_schema_does_not_hide_old_core(self):
        self.write_runtime()
        (self.root / "release-please-config.json").write_text(json.dumps({
            "$schema": "https://raw.githubusercontent.com/googleapis/release-please/v17.11.2/schemas/config.json"
        }), encoding="utf-8")
        self.assertEqual(release_please_findings(self.root, (Path("release-please-config.json"),), "v17.11.2"), [])
        errors = []
        findings = release_please_core_findings(self.root, (self.runtime,), "v17.11.2", errors)
        self.assertEqual([(x["kind"], x["current"], x["latest"]) for x in findings],
                         [("release-please-core", "17.6.0", "v17.11.2")])
        self.assertEqual(errors, [])

    def test_matching_core_and_lock_are_current(self):
        self.write_runtime("17.11.2")
        errors = []
        self.assertEqual(release_please_core_findings(self.root, (self.runtime,), "v17.11.2", errors), [])
        self.assertEqual(errors, [])

    def test_lock_mismatch_is_an_error_even_when_manifest_is_latest(self):
        self.write_runtime("17.11.2", "17.6.0")
        errors = []
        release_please_core_findings(self.root, (self.runtime,), "v17.11.2", errors)
        self.assertTrue(any("disagree" in x for x in errors))

    def test_range_or_missing_lock_cannot_be_reported_current(self):
        self.write_runtime("^17.11.2")
        errors = []
        release_please_core_findings(self.root, (self.runtime,), "v17.11.2", errors)
        self.assertTrue(errors)
        (self.root / self.runtime / "package-lock.json").unlink()
        errors = []
        release_please_core_findings(self.root, (self.runtime,), "v17.11.2", errors)
        self.assertTrue(errors)


if __name__ == "__main__":
    unittest.main()
