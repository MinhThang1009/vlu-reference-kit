"""Kiểm tra hồi quy cho manifest, quyền phân phối và gói ZIP."""

from pathlib import Path
import hashlib
import json
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_community_package import build_package
from refresh_manifest import refresh
from validate_kit import inventory, resolve_inside, validate_kit


class KitToolsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "kit"
        (self.root / "data").mkdir(parents=True)
        (self.root / "assets/derived/palette").mkdir(parents=True)
        self.asset = self.root / "assets/derived/palette/colors.css"
        self.asset.write_text(":root { --red: #D72134; }\n", encoding="utf-8")
        (self.root / "LICENSE").write_text("Synthetic license notice", encoding="utf-8")
        (self.root / "NOTICE.md").write_text("Synthetic scope notice", encoding="utf-8")
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

    def test_host_platform_metadata_does_not_change_archive_bytes(self):
        original_info = zipfile.ZipInfo
        digests = []
        for system in (0, 3):
            class HostZipInfo(original_info):
                creator_system = system

                def __init__(self, *args, **kwargs):
                    super().__init__(*args, **kwargs)
                    self.create_system = self.creator_system

            destination = Path(self.temp.name) / f"host-{system}" / "package.zip"
            with patch("build_community_package.zipfile.ZipInfo", HostZipInfo):
                digests.append(build_package(self.root, destination))
        self.assertEqual(digests[0], digests[1])

    def test_invalid_package_is_not_written(self):
        self.asset.write_text("changed", encoding="utf-8")
        destination = Path(self.temp.name) / "bad.zip"
        with self.assertRaises(ValueError):
            build_package(self.root, destination)
        self.assertFalse(destination.exists())

    def test_nonstandard_json_numbers_are_rejected(self):
        for value in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(value=value):
                (self.root / "data/invalid.json").write_text('{"a": ' + value + '}', encoding="utf-8")
                refresh(self.root)
                self.assertTrue(any("số không hợp lệ" in error for error in validate_kit(self.root)))

    def test_invalid_utf8_manifest_returns_validation_error(self):
        (self.root / "MANIFEST_SHA256.txt").write_bytes(b"\xff")
        self.assertTrue(any("Không đọc được" in error for error in validate_kit(self.root)))

    def test_classification_with_wrong_type_returns_validation_error(self):
        self.ledger[0]["classification"] = []
        self.save_ledger()
        self.assertTrue(any("phạm vi phân phối" in error for error in validate_kit(self.root)))

    def test_failed_build_preserves_previous_artifact_and_checksum(self):
        destination = Path(self.temp.name) / "package.zip"
        digest = build_package(self.root, destination)
        with patch("zipfile.ZipFile.writestr", side_effect=OSError("synthetic failure")):
            with self.assertRaises(OSError):
                build_package(self.root, destination)
        self.assertEqual(hashlib.sha256(destination.read_bytes()).hexdigest(), digest)
        self.assertEqual((destination.parent / "SHA256SUMS.txt").read_text(), digest + "  package.zip\n")

    def test_source_change_during_snapshot_cannot_publish_invalid_zip(self):
        from validate_kit import inventory

        destination = Path(self.temp.name) / "package.zip"

        def changed_inventory(root):
            files = inventory(root)
            self.asset.write_text("changed during build", encoding="utf-8")
            return files

        with patch("build_community_package.inventory", side_effect=changed_inventory):
            with self.assertRaises(ValueError):
                build_package(self.root, destination)
        self.assertFalse(destination.exists())

    def test_license_notice_is_required_in_download(self):
        (self.root / "LICENSE").unlink()
        refresh(self.root)
        self.assertTrue(any("Thiếu thông báo giấy phép" in error for error in validate_kit(self.root)))

    def test_destination_inside_kit_is_rejected(self):
        with self.assertRaises(ValueError):
            build_package(self.root, self.root / "package.zip")

    def test_output_cannot_collide_with_checksum_filename(self):
        with self.assertRaisesRegex(ValueError, ".zip"):
            build_package(self.root, Path(self.temp.name) / "SHA256SUMS.txt")

    def test_snapshot_total_limit_is_enforced_before_publishing(self):
        destination = Path(self.temp.name) / "package.zip"
        with patch("build_community_package.MAX_TOTAL_BYTES", 1):
            with self.assertRaisesRegex(ValueError, "tổng dung lượng"):
                build_package(self.root, destination)
        self.assertFalse(destination.exists())

    def test_nonportable_and_noncanonical_paths_are_rejected(self):
        for name in ("assets/CON.txt", "assets/nul", "assets/COM¹.txt", "assets/LPT2", "assets/item.",
                     "assets/item ", "assets/bad?.txt", "assets//alias.txt", "assets/./alias.txt", "."):
            with self.subTest(name=name):
                with self.assertRaises(ValueError):
                    resolve_inside(self.root, name)

    def test_portable_unicode_and_nonreserved_device_like_paths_are_allowed(self):
        for name in ("assets/đồng-phục.txt", "assets/connection.txt", "assets/com10.txt", ".cache/file.txt"):
            with self.subTest(name=name):
                self.assertEqual(resolve_inside(self.root, name), self.root / name)

    def test_unreadable_subtree_cannot_be_silently_omitted(self):
        def denied_walk(directory, **options):
            options["onerror"](PermissionError("Synthetic inaccessible subtree"))
            return iter(())

        with patch("validate_kit.os.walk", side_effect=denied_walk):
            self.assertTrue(any("inaccessible subtree" in error for error in validate_kit(self.root)))

    def test_case_colliding_directories_are_rejected_even_with_different_children(self):
        entries = [(str(self.root), ["Images", "images"], [])]
        with patch("validate_kit.os.walk", return_value=iter(entries)):
            with self.assertRaisesRegex(ValueError, "chữ hoa/thường"):
                inventory(self.root)


if __name__ == "__main__":
    unittest.main()
