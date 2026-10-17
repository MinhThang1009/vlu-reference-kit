"""Kiểm tra hồi quy cho manifest, quyền phân phối và gói ZIP."""

from pathlib import Path
import hashlib
import json
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_community_package import build_package
from refresh_manifest import refresh
from validate_kit import validate_kit


class KitToolsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "kit"
        (self.root / "data").mkdir(parents=True)
        (self.root / "assets/derived/palette").mkdir(parents=True)
        self.asset = self.root / "assets/derived/palette/colors.css"
        self.asset.write_text(":root { --red: #D72134; }\n", encoding="utf-8")
        self.ledger = [{"file": "assets/derived/palette/colors.css", "included_in_package": True,
                        "classification": "generated_palette_from_official_hex",
                        "sha256": hashlib.sha256(self.asset.read_bytes()).hexdigest()}]
        self.save_ledger()

    def save_ledger(self):
        (self.root / "data/asset-sources.json").write_text(json.dumps(self.ledger), encoding="utf-8")
        refresh(self.root)

    def test_nested_posix_paths_pass_on_supported_os(self):
        self.assertEqual(validate_kit(self.root), [])

    def test_modified_asset_fails_even_if_manifest_is_refreshed(self):
        self.asset.write_text("changed", encoding="utf-8")
        refresh(self.root)
        self.assertTrue(any("Hash sổ nguồn" in error for error in validate_kit(self.root)))

    def test_original_artwork_cannot_be_enabled_in_community_package(self):
        self.ledger[0]["classification"] = "official_vlu_original"
        self.save_ledger()
        self.assertTrue(any("phạm vi phân phối" in error for error in validate_kit(self.root)))

    def test_excluded_asset_must_not_be_present(self):
        self.ledger[0]["included_in_package"] = False
        self.save_ledger()
        self.assertTrue(any("đã loại vẫn xuất hiện" in error for error in validate_kit(self.root)))

    def test_extra_file_is_detected(self):
        (self.root / "unlisted.txt").write_text("extra", encoding="utf-8")
        self.assertTrue(any("chưa có trong manifest" in error for error in validate_kit(self.root)))

    def test_traversal_in_asset_ledger_is_rejected(self):
        self.ledger[0]["file"] = "../outside.txt"
        self.save_ledger()
        self.assertTrue(any("không an toàn" in error for error in validate_kit(self.root)))

    def test_duplicate_json_keys_are_rejected(self):
        (self.root / "data/invalid.json").write_text('{"a": 1, "a": 2}', encoding="utf-8")
        refresh(self.root)
        self.assertTrue(any("key trùng" in error for error in validate_kit(self.root)))

    def test_machine_path_is_not_published(self):
        (self.root / "note.md").write_text("C:\\Users\\Example\\private", encoding="utf-8")
        refresh(self.root)
        self.assertTrue(any("máy cá nhân" in error for error in validate_kit(self.root)))

    def test_package_is_reproducible_and_contains_verified_bytes(self):
        first = Path(self.temp.name) / "first.zip"
        second = Path(self.temp.name) / "second.zip"
        self.assertEqual(build_package(self.root, first), build_package(self.root, second))
        with zipfile.ZipFile(first) as archive:
            self.assertIsNone(archive.testzip())
            self.assertEqual(archive.read("vlu-reference-kit-community/assets/derived/palette/colors.css"), self.asset.read_bytes())

    def test_invalid_package_is_not_written(self):
        self.asset.write_text("changed", encoding="utf-8")
        destination = Path(self.temp.name) / "bad.zip"
        with self.assertRaises(ValueError):
            build_package(self.root, destination)
        self.assertFalse(destination.exists())


if __name__ == "__main__":
    unittest.main()
