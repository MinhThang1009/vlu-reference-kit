"""Phát hiện drift khi cập nhật policy, lockfile hoặc action của repo."""

from pathlib import Path
import json
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from sync_action_pins import action_repositories
from validate_tooling import read_requirement_pins, validate_tooling


class ToolingPolicyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / ".github").mkdir()
        (self.root / "kit").mkdir()
        self.write(".github/ci-toolchain.json", {"npm-tools": {"lint": {"package": "lint", "version": "1.0.0"}}})
        self.write(".github/release-policy.json", {"default_branch": "main", "required_checks": ["ci-success", "docs-contract"], "actions_app_id": 15368})
        self.write("package.json", {"devDependencies": {"lint": "1.0.0"}})
        self.lock = {"packages": {"": {"devDependencies": {"lint": "1.0.0"}}, "node_modules/lint": {"version": "1.0.0"}}}
        self.write("package-lock.json", self.lock)
        (self.root / "requirements-docs.txt").write_text("example==1.0.0\n", encoding="utf-8")
        self.hash_option = "--hash=sha256:" + "a" * 64
        (self.root / "requirements-docs.lock").write_text("example==1.0.0 " + self.hash_option + "\n", encoding="utf-8")
        for name in ("LICENSE", "kit/LICENSE"):
            (self.root / name).write_bytes(b"Synthetic license")
        self.write("release-please-config.json", {"release-type": "simple", "version-file": "version.txt",
                                                   "skip-github-release": False, "draft": True,
                                                   "force-tag-creation": True, "initial-version": "0.1.0"})
        self.write(".release-please-manifest.json", {})
        (self.root / "version.txt").write_text("0.1.0\n", encoding="utf-8")

    def write(self, name, value):
        (self.root / name).write_text(json.dumps(value), encoding="utf-8")

    def test_matching_toolchain_passes(self):
        self.assertEqual(validate_tooling(self.root), [])

    def test_ci_rejects_release_policy_without_required_checks(self):
        self.write(".github/release-policy.json", {"default_branch": "main", "required_checks": [], "actions_app_id": 15368})
        self.assertTrue(any("required_checks" in error for error in validate_tooling(self.root)))

    def test_lock_cannot_silently_change_direct_policy_version(self):
        self.lock["packages"]["node_modules/lint"]["version"] = "2.0.0"
        self.write("package-lock.json", self.lock)
        self.assertTrue(any("sai phiên bản" in error for error in validate_tooling(self.root)))

    def test_python_direct_pin_must_be_in_lock(self):
        (self.root / "requirements-docs.lock").write_text("other==1.0.0 " + self.hash_option + "\n", encoding="utf-8")
        self.assertTrue(any("Python trực tiếp và lockfile không đồng bộ" in error for error in validate_tooling(self.root)))

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

    def test_release_please_cannot_publish_before_artifacts(self):
        for draft in (False, None, "true"):
            with self.subTest(draft=draft):
                self.write("release-please-config.json", {"release-type": "simple", "version-file": "version.txt",
                                                           "skip-github-release": False, "draft": draft,
                                                           "force-tag-creation": True, "initial-version": "0.1.0"})
                self.assertTrue(any("draft: true" in error for error in validate_tooling(self.root)))

    def test_release_please_draft_creation_cannot_be_disabled(self):
        for skip in (True, None, "false"):
            with self.subTest(skip=skip):
                self.write("release-please-config.json", {"release-type": "simple", "version-file": "version.txt",
                                                           "skip-github-release": skip, "draft": True,
                                                           "force-tag-creation": True, "initial-version": "0.1.0"})
                self.assertTrue(any("skip-github-release: false" in error for error in validate_tooling(self.root)))

    def test_release_please_must_create_tags_for_automatic_asset_upload(self):
        for force_tag in (False, None, "true"):
            with self.subTest(force_tag=force_tag):
                self.write("release-please-config.json", {"release-type": "simple", "version-file": "version.txt",
                                                           "skip-github-release": False, "draft": True,
                                                           "force-tag-creation": force_tag, "initial-version": "0.1.0"})
                self.assertTrue(any("force-tag-creation: true" in error for error in validate_tooling(self.root)))

    def test_package_override_cannot_disable_tag_creation_for_asset_upload(self):
        config = json.loads((self.root / "release-please-config.json").read_text(encoding="utf-8"))
        config["packages"] = {".": {"force-tag-creation": False}}
        self.write("release-please-config.json", config)
        self.assertTrue(any("packages[\".\"]" in error for error in validate_tooling(self.root)))

    def test_matching_invalid_versions_are_rejected(self):
        for value in ("", "not-a-version", "v0.1.0", "01.0.0", "1.2\u0662.3", "1.0.0-01", "1.0.0-rc..1", "1.0.0+", "1.0.0+" + "a" * 122):
            with self.subTest(value=value):
                (self.root / "version.txt").write_text(value + "\n", encoding="utf-8")
                self.write(".release-please-manifest.json", {".": value})
                self.assertTrue(any("SemVer" in error for error in validate_tooling(self.root)))

    def test_invalid_bootstrap_version_cannot_hide_behind_valid_manifest(self):
        self.write(".release-please-manifest.json", {".": "0.1.0"})
        self.write("release-please-config.json", {"release-type": "simple", "version-file": "version.txt",
                                                   "skip-github-release": False, "draft": True,
                                                   "force-tag-creation": True, "initial-version": "not-a-version"})
        self.assertTrue(any("initial-version" in error for error in validate_tooling(self.root)))

    def test_prerelease_and_build_metadata_remain_supported(self):
        for value in ("0.1.0-rc.1+build.001", "1.2.3+001", "1.0.0-x-y-z.--"):
            with self.subTest(value=value):
                (self.root / "version.txt").write_text(value + "\n", encoding="utf-8")
                self.write(".release-please-manifest.json", {".": value})
                self.assertEqual(validate_tooling(self.root), [])

    def test_unaccounted_requirements_cannot_be_silently_ignored(self):
        for declaration in ("new-tool>=2", "-r extra.txt", "-c constraints.txt", "other @ https://example.invalid/package.whl",
                            "example==1.*", "example[extra]==1.0.0", "example==1.0.0; python_version > '3.10'"):
            with self.subTest(declaration=declaration):
                (self.root / "requirements-docs.txt").write_text("example==1.0.0\n" + declaration + "\n", encoding="utf-8")
                self.assertTrue(any("Dependency Python không hợp lệ" in error for error in validate_tooling(self.root)))

    def test_duplicate_normalized_package_names_are_rejected(self):
        for first, second in (("example==2.0.0", "example==1.0.0"), ("Example_Tool==1.0.0", "example-tool==1.0.0")):
            with self.subTest(first=first, second=second):
                (self.root / "requirements-docs.txt").write_text(first + "\n" + second + "\n", encoding="utf-8")
                self.assertTrue(any("trùng" in error for error in validate_tooling(self.root)))

    def test_lock_hash_is_mandatory_and_must_be_sha256(self):
        for options in ("", "--hash=sha256:short", "--hash=md5:" + "a" * 32, "--no-require-hashes"):
            with self.subTest(options=options):
                (self.root / "requirements-docs.lock").write_text("example==1.0.0 " + options + "\n", encoding="utf-8")
                self.assertTrue(any("Dependency Python không hợp lệ" in error for error in validate_tooling(self.root)))

    def test_spacing_comments_continuations_and_normalized_names_are_supported(self):
        (self.root / "requirements-docs.txt").write_text("# direct\n  Example_Tool == 1.0.0  # explanation\n", encoding="utf-8")
        (self.root / "requirements-docs.lock").write_text("example-tool==1.0.0 \\\n    " + self.hash_option + "\n", encoding="utf-8")
        self.assertEqual(validate_tooling(self.root), [])

    def test_dangling_continuation_is_rejected(self):
        (self.root / "requirements-docs.txt").write_text("example==1.0.0 \\", encoding="utf-8")
        self.assertTrue(any("chưa kết thúc" in error for error in validate_tooling(self.root)))

    def test_empty_lock_and_extra_unparsed_lines_are_rejected(self):
        for text in ("# nothing\n", "example==1.0.0 " + self.hash_option + "\n--extra-index-url https://example.invalid\n"):
            with self.subTest(text=text):
                (self.root / "requirements-docs.lock").write_text(text, encoding="utf-8")
                with self.assertRaises(ValueError):
                    read_requirement_pins(self.root / "requirements-docs.lock", require_hashes=True)


if __name__ == "__main__":
    unittest.main()
