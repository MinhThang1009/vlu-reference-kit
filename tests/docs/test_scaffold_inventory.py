"""Kiểm tra tài liệu phải báo lỗi nếu chưa duyệt được toàn bộ phạm vi."""

from pathlib import Path
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from validate_scaffold import validate_markdown_sources


class ScaffoldInventoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.guides = self.root / "guides"
        self.guides.mkdir()
        (self.guides / "guide.md").write_text("# Fixture\n\n[Missing](absent.md)\n", encoding="utf-8")
        self.scandir = os.scandir

    def test_nested_markdown_is_checked_when_inventory_succeeds(self):
        self.assertTrue(any("relative link is missing" in error for error in validate_markdown_sources(self.root)))

    def test_directory_read_failure_cannot_return_a_partial_pass(self):
        for blocked in (self.root, self.guides):
            with self.subTest(blocked=blocked.name):
                def scan(path):
                    if Path(path) == blocked:
                        raise PermissionError(13, "Synthetic directory read failure", str(path))
                    return self.scandir(path)

                with patch("os.scandir", side_effect=scan):
                    problems = validate_markdown_sources(self.root)
                self.assertTrue(any("Markdown inventory incomplete" in error for error in problems))

    def test_intentionally_excluded_dependency_directory_is_not_scanned(self):
        dependency = self.root / "node_modules"
        dependency.mkdir()

        def scan(path):
            if Path(path) == dependency:
                self.fail("Dependency directory should be outside the Markdown inventory")
            return self.scandir(path)

        with patch("os.scandir", side_effect=scan):
            problems = validate_markdown_sources(self.root)
        self.assertTrue(any("relative link is missing" in error for error in problems))


if __name__ == "__main__":
    unittest.main()
