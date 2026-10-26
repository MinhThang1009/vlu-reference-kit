"""Kiểm tra công cụ hash độc lập được phân phối trong ZIP."""

from pathlib import Path
from contextlib import redirect_stdout
import hashlib
import importlib.util
import io
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1] / "kit/tools/verify-manifest.py"
SPEC = importlib.util.spec_from_file_location("offline_verifier", SOURCE)
OFFLINE = importlib.util.module_from_spec(SPEC)
with patch.object(sys, "dont_write_bytecode", True):
    SPEC.loader.exec_module(OFFLINE)


class OfflineVerifierTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "kit"
        (self.root / "target").mkdir(parents=True)
        (self.root / "target/content.txt").write_bytes(b"Synthetic reference\n")
        self.refresh()

    def refresh(self):
        files = sorted(path for path in self.root.rglob("*") if path.is_file() and path.name != "MANIFEST_SHA256.txt")
        (self.root / "MANIFEST_SHA256.txt").write_text("".join(
            hashlib.sha256(path.read_bytes()).hexdigest() + "  " + path.relative_to(self.root).as_posix() + "\n"
            for path in files), encoding="utf-8")

    def test_clean_kit_passes_without_repository_dependencies(self):
        self.assertEqual(OFFLINE.verify(self.root), ([], 1))

    def test_filesystem_aliases_cannot_add_manifest_entries_for_the_same_file(self):
        target = self.root / "target/content.txt"
        aliases = [name for name in ("TARGET/content.txt", "target/CONTENT.txt", "target/content.txt.")
                   if (self.root / name).is_file()]
        if not aliases:
            self.skipTest("Requires native case-insensitive or trailing-dot path aliases")
        digest = hashlib.sha256(target.read_bytes()).hexdigest()
        for name in aliases:
            with self.subTest(name=name):
                self.assertTrue((self.root / name).samefile(target))
                self.refresh()
                with (self.root / "MANIFEST_SHA256.txt").open("a", encoding="utf-8") as manifest:
                    manifest.write(digest + "  " + name + "\n")
                self.assertTrue(OFFLINE.verify(self.root)[0], "A second spelling of one file passed verification")

    def test_actual_mixed_case_filenames_keep_their_inventory_spelling(self):
        (self.root / "target/Mixed-Case.txt").write_bytes(b"Synthetic second file\n")
        self.refresh()
        self.assertEqual(OFFLINE.verify(self.root), ([], 2))

    def test_old_runtime_gets_actionable_message_before_filesystem_verification(self):
        output = io.StringIO()
        with patch.object(OFFLINE.sys, "version_info", (3, 11, 9)), \
                patch.object(OFFLINE, "verify", side_effect=AssertionError("Unsupported runtime must stop first")), \
                redirect_stdout(output):
            result = OFFLINE.main()
        self.assertEqual((result, "Python 3.12" in output.getvalue()), (2, True))

    def test_directory_alias_inside_kit_is_rejected(self):
        alias = self.root / "alias"
        target = self.root / "target"
        if sys.platform == "win32":
            subprocess.run(["cmd", "/c", "mklink", "/J", str(alias), str(target)],
                           check=True, capture_output=True, timeout=15)
            self.addCleanup(alias.rmdir)
        else:
            alias.symlink_to(target, target_is_directory=True)
            self.addCleanup(alias.unlink)
        digest = hashlib.sha256((target / "content.txt").read_bytes()).hexdigest()
        with (self.root / "MANIFEST_SHA256.txt").open("a", encoding="utf-8") as manifest:
            manifest.write(digest + "  alias/content.txt\n")
        self.assertTrue(any("Unsafe target" in error for error in OFFLINE.verify(self.root)[0]))

    def test_linked_directory_not_in_manifest_is_also_rejected(self):
        alias = self.root / "empty-alias"
        alias.mkdir()
        original = Path.is_junction
        with patch.object(Path, "is_junction", lambda path: path == alias or original(path)):
            self.assertTrue(any("Unsafe target" in error for error in OFFLINE.verify(self.root)[0]))

    def test_bad_manifest_encoding_is_a_validation_error(self):
        (self.root / "MANIFEST_SHA256.txt").write_bytes(b"\xff")
        self.assertTrue(any("Cannot read manifest" in error for error in OFFLINE.verify(self.root)[0]))

    def test_noncanonical_and_escaping_paths_are_rejected(self):
        for name in ("../outside.txt", "target//content.txt", "target/./content.txt", "C:outside.txt", "."):
            with self.subTest(name=name):
                with self.assertRaises(ValueError):
                    OFFLINE.checked_target(self.root, name)

    def test_hash_mismatch_and_unlisted_file_remain_detected(self):
        (self.root / "target/content.txt").write_bytes(b"modified")
        (self.root / "extra.txt").write_bytes(b"extra")
        errors, _ = OFFLINE.verify(self.root)
        self.assertTrue(any("Hash mismatch" in error for error in errors))
        self.assertTrue(any("Unlisted file" in error for error in errors))

    def test_inventory_read_error_cannot_report_pass(self):
        def denied_walk(root, **options):
            options["onerror"](PermissionError("Synthetic inaccessible subtree"))
            return iter(())

        with patch.object(OFFLINE.os, "walk", side_effect=denied_walk):
            self.assertTrue(any("Cannot inventory" in error for error in OFFLINE.verify(self.root)[0]))


if __name__ == "__main__":
    unittest.main()
