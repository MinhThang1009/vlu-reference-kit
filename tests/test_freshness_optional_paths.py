"""Optional freshness inputs must distinguish missing paths from access errors."""

from dataclasses import replace
from pathlib import Path
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from audit_freshness import AuditError, FreshnessTrackers, audit, existing_optional_paths
from sync_action_pins import ActionRelease


class OptionalFreshnessPathTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.blocked = Path("blocked.json")
        self.healthy = Path("healthy.json")
        for name in (self.blocked, self.healthy):
            (self.root / name).write_text("{}", encoding="utf-8")
        self.original_lstat = os.lstat

    def denied_metadata(self, path, *args, **kwargs):
        if Path(path) == self.root / self.blocked:
            raise PermissionError(13, "Synthetic optional metadata failure", str(path))
        return self.original_lstat(path, *args, **kwargs)

    def test_missing_paths_are_skipped_and_readable_paths_keep_input_order(self):
        paths = (Path("missing.json"), self.healthy, self.blocked)
        self.assertEqual(existing_optional_paths(self.root, paths),
                         (self.healthy, self.blocked))

    def test_metadata_failure_raises_when_no_error_collector_is_supplied(self):
        with patch("os.lstat", side_effect=self.denied_metadata):
            with self.assertRaises(AuditError):
                existing_optional_paths(self.root, (self.blocked,))

    def test_metadata_failure_is_recorded_without_hiding_other_optional_paths(self):
        errors = []
        with patch("os.lstat", side_effect=self.denied_metadata):
            paths = existing_optional_paths(
                self.root, (self.blocked, Path("missing.json"), self.healthy), errors=errors)
        self.assertEqual(paths, (self.healthy,))
        self.assertEqual(len(errors), 1)
        self.assertIn(self.blocked.as_posix(), errors[0])

    def test_audit_marks_both_optional_groups_indeterminate_and_continues(self):
        empty = FreshnessTrackers((), (), (), (), (), (), (), (Path("runtime"),))
        for group in ("optional_release_please_configs", "optional_code_scanning_allowlists"):
            with self.subTest(group=group):
                trackers = replace(empty, **{group: (self.blocked, self.healthy)})
                with patch("os.lstat", side_effect=self.denied_metadata), \
                        patch("audit_freshness.load_trackers", return_value=trackers), \
                        patch("audit_freshness.sync_action_pins.GitHubReleaseClient") as client, \
                        patch("audit_freshness.action_dependencies.inspect_actions",
                              return_value={"actions": []}), \
                        patch("audit_freshness.release_please_findings", return_value=[]) as schema, \
                        patch("audit_freshness.release_please_core_findings", return_value=[]) as core, \
                        patch("audit_freshness.code_scanning_allowlist_findings",
                              return_value=[]) as allowlist:
                    client.return_value.latest_release.return_value = ActionRelease("v1.0.0", "a" * 40)
                    report = audit(self.root, "synthetic-token")
                self.assertEqual(report["status"], "indeterminate")
                self.assertEqual(len(report["errors"]), 1)
                core.assert_called_once()
                check = schema if group == "optional_release_please_configs" else allowlist
                self.assertEqual(check.call_args.args[1], (self.healthy,))


if __name__ == "__main__":
    unittest.main()
