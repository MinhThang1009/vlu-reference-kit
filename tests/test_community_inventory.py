"""Không báo community inventory hiện hành khi chưa đọc đủ template."""

from pathlib import Path
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from check_community_health import RegistryEntry, audit, inventory_entry


class ProfileClient:
    def get_json(self, endpoint):
        if endpoint != "repos/example/kit/community/profile":
            raise AssertionError("Unexpected endpoint: " + endpoint)
        return {"health_percentage": 100}


class CommunityInventoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.templates = self.root / ".github/ISSUE_TEMPLATE"
        self.nested = self.templates / "nested"
        self.nested.mkdir(parents=True)
        for name in ("example.yml", "nested/example.yml"):
            (self.templates / name).write_text("name: Synthetic fixture\n", encoding="utf-8")
        self.entry = RegistryEntry("issue_templates", "Issue templates", "github-community-health", "directory", (".github/ISSUE_TEMPLATE",), "none")
        self.scandir = os.scandir

    def test_regular_nested_files_are_inventoried_in_stable_order(self):
        result = inventory_entry(self.root, self.entry)
        self.assertEqual(result["paths"], [".github/ISSUE_TEMPLATE/example.yml", ".github/ISSUE_TEMPLATE/nested/example.yml"])

    def test_read_failure_is_indeterminate_despite_a_full_remote_profile(self):
        for blocked in (self.templates, self.nested):
            with self.subTest(blocked=blocked.name):
                def scan(path):
                    if Path(path) == blocked:
                        raise PermissionError(13, "Synthetic directory read failure", str(path))
                    return self.scandir(path)

                with patch("os.scandir", side_effect=scan):
                    report = audit(self.root, [self.entry], "example/kit", ProfileClient(), "synthetic-fixture")
                self.assertEqual(report["summary"]["status"], "indeterminate")

    def test_candidate_stat_failure_does_not_abort_other_entries(self):
        healthy = self.root / "README.md"
        healthy.write_text("Synthetic readme", encoding="utf-8")
        readme = RegistryEntry("readme", "README", "github-community-profile",
                               "file", ("README.md",), "none")
        original_stat = Path.stat
        for kind in ("file", "directory", "any"):
            with self.subTest(kind=kind):
                blocked = RegistryEntry("blocked", "Blocked", "github-community-health",
                                        kind, (".github/ISSUE_TEMPLATE",), "none")

                def denied(path, *args, **kwargs):
                    if path == self.templates and kwargs.get("follow_symlinks", True):
                        raise PermissionError(13, "Synthetic metadata read failure", str(path))
                    return original_stat(path, *args, **kwargs)

                with patch.object(Path, "stat", denied):
                    report = audit(self.root, [blocked, readme], "example/kit",
                                   ProfileClient(), "synthetic-fixture")
                self.assertEqual([item["status"] for item in report["files"]],
                                 ["indeterminate", "present"])
                self.assertEqual(report["summary"]["status"], "indeterminate")

    def test_ancestor_lstat_failure_is_indeterminate(self):
        original_lstat = Path.lstat

        def denied(path, *args, **kwargs):
            if path == self.templates.parent:
                raise PermissionError(13, "Synthetic ancestor read failure", str(path))
            return original_lstat(path, *args, **kwargs)

        with patch.object(Path, "lstat", denied):
            report = audit(self.root, [self.entry], "example/kit",
                           ProfileClient(), "synthetic-fixture")
        self.assertEqual(report["summary"]["status"], "indeterminate")

    def test_nested_file_stat_failure_is_indeterminate(self):
        original_stat = Path.stat

        def denied(path, *args, **kwargs):
            if path == self.nested / "example.yml" and kwargs.get("follow_symlinks", True):
                raise PermissionError(13, "Synthetic file metadata failure", str(path))
            return original_stat(path, *args, **kwargs)

        with patch.object(Path, "stat", denied):
            report = audit(self.root, [self.entry], "example/kit",
                           ProfileClient(), "synthetic-fixture")
        self.assertEqual(report["summary"]["status"], "indeterminate")

    def test_suppressed_predicate_errors_do_not_produce_a_current_report(self):
        # Model Python 3.14+ predicates on older runtimes as well.
        original_stat, original_exists, original_is_file = Path.stat, Path.exists, Path.is_file
        blocked_path = self.templates / "example.yml"

        def denied(path, *args, **kwargs):
            if path == blocked_path and kwargs.get("follow_symlinks", True):
                raise PermissionError(13, "Synthetic metadata read failure", str(path))
            return original_stat(path, *args, **kwargs)

        def suppress(predicate):
            def check(path, *args, **kwargs):
                try:
                    return predicate(path, *args, **kwargs)
                except OSError:
                    return False
            return check

        file_entry = RegistryEntry("file", "File", "github-community-health", "file",
                                   (".github/ISSUE_TEMPLATE/example.yml",), "none")
        for entry in (file_entry, self.entry):
            with self.subTest(kind=entry.kind):
                with patch.object(Path, "stat", denied), \
                        patch.object(Path, "exists", suppress(original_exists)), \
                        patch.object(Path, "is_file", suppress(original_is_file)):
                    report = audit(self.root, [entry], "example/kit",
                                   ProfileClient(), "synthetic-fixture")
                self.assertEqual(report["summary"]["status"], "indeterminate")

    def test_missing_candidates_remain_absent(self):
        missing = RegistryEntry("missing", "Missing", "github-community-health", "file",
                                ("missing/README.md",), "none")
        self.assertEqual(inventory_entry(self.root, missing)["status"], "absent")


if __name__ == "__main__":
    unittest.main()
