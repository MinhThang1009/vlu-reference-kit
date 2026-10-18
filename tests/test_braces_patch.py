"""Bản vá dependency phải dừng khi phiên bản hoặc byte upstream đã đổi."""

from pathlib import Path
import json
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from patch_braces import patch_dependencies


class BracesPatchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.package = self.root / "node_modules/braces"
        (self.package / "lib").mkdir(parents=True)
        self.source = self.package / "lib/parse.js"
        self.source.write_bytes(b"Synthetic unreviewed dependency source\n")
        self.write_metadata("3.0.3")

    def write_metadata(self, version):
        (self.package / "package.json").write_text(json.dumps({"version": version}), encoding="utf-8")
        (self.root / "package-lock.json").write_text(json.dumps({"packages": {"node_modules/braces": {"version": version}}}), encoding="utf-8")

    def test_unknown_source_is_refused_without_modifying_installed_bytes(self):
        original = self.source.read_bytes()
        with self.assertRaisesRegex(ValueError, "Hash parser"):
            patch_dependencies(self.root)
        self.assertEqual(self.source.read_bytes(), original)

    def test_upstream_version_change_requires_review(self):
        self.write_metadata("3.0.4")
        with self.assertRaisesRegex(ValueError, "Phiên bản braces đã đổi"):
            patch_dependencies(self.root)

    def test_missing_dependency_is_not_silently_treated_as_mitigated(self):
        (self.root / "package-lock.json").write_text('{"packages": {}}', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Không còn braces"):
            patch_dependencies(self.root)


if __name__ == "__main__":
    unittest.main()
