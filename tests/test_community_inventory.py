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


if __name__ == "__main__":
    unittest.main()
