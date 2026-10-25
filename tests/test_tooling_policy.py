"""Phát hiện drift khi cập nhật policy, lockfile hoặc action của repo."""

from contextlib import redirect_stderr
from pathlib import Path
import io
import json
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from sync_action_pins import ActionRelease, action_repositories, synchronize_action_pins, workflow_paths
from audit_freshness import AuditError, RequirementSource, action_findings, pinned_requirements, requirement_findings
from validate_tooling import read_requirement_pins, validate_tooling
import ci_toolchain


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
                                                   "force-tag-creation": True, "initial-version": "0.1.0",
                                                   "include-component-in-tag": False,
                                                   "packages": {".": {}}})
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

    def test_script_quotes_cannot_hide_unpinned_actions(self):
        for style in ("|", "|-", "|+", ">", ">-", ">+"):
            for script in ('''echo 'note: "hello' ''', '''echo "note: 'hello" '''):
                with self.subTest(style=style, script=script):
                    text = ("jobs:\n  test:\n    steps:\n      - run: " + style + "\n"
                            "          " + script + "\n      - uses: actions/checkout@v7\n")
                    with self.assertRaisesRegex(ValueError, "not pinned"):
                        action_repositories(Path("fixture.yml"), text)

    def test_plain_continuations_cannot_hide_unpinned_actions(self):
        for text in ('"quoted text', "'quoted text", "{uses:fixture/fake@v1}"):
            for prefix in ("name: Workflow\n  " + text + "\njobs:\n  test:\n    steps:\n      - ",
                           "jobs:\n  test:\n    steps:\n      - name: Workflow\n          " + text + "\n        "):
                with self.subTest(prefix=prefix):
                    with self.assertRaisesRegex(ValueError, "not pinned"):
                        action_repositories(Path("fixture.yml"), prefix + "uses: actions/checkout@v7\n")

    def test_blank_lines_after_scalars_cannot_hide_unpinned_actions(self):
        for scalar in ("run: |\n          echo done\n", "run: >-\n          echo done\n",
                       "run: echo\n          done\n"):
            for blank in ("\n", "  \n"):
                with self.subTest(scalar=scalar, blank=blank):
                    source = ("jobs:\n  test:\n    steps:\n      - " + scalar + blank
                              + "      - uses: actions/checkout@v7\n")
                    with self.assertRaisesRegex(ValueError, "not pinned"):
                        action_repositories(Path("fixture.yml"), source)

    def test_synchronization_preserves_plain_continuations_and_blank_lines(self):
        directory = self.root / ".github/workflows"
        directory.mkdir()
        workflow = directory / "example.yml"
        original = ('name: Workflow\n  "quoted text\njobs:\n  test:\n    steps:\n'
                    '      - run: |\n          echo done\n\n'
                    '      - uses: actions/checkout@' + 'a' * 40 + ' # v1.0.0\n')
        workflow.write_bytes(original.encode())
        synchronize_action_pins(self.root, lambda _: ActionRelease(tag="v2.0.0", sha="b" * 40), write=True)
        self.assertEqual(workflow.read_bytes().decode(),
                         original.replace("a" * 40 + " # v1.0.0", "b" * 40 + " # v2.0.0"))

    def test_continued_plain_reference_is_not_treated_as_a_single_sha(self):
        source = ("jobs:\n  test:\n    steps:\n      - uses: actions/checkout@" + "a" * 40
                  + "\n          extra-text\n")
        with self.assertRaisesRegex(ValueError, "not pinned"):
            action_repositories(Path("fixture.yml"), source)

    def test_quoted_name_colons_cannot_hide_unpinned_actions(self):
        for name in ('''"Doc: 'hello"''', "'Doc: \"hello'",
                     '''"Example\n  note: 'hello\n  end"''', "'Example\n  note: \"hello\n  end'"):
            with self.subTest(name=name):
                text = "name: " + name + "\njobs:\n  test:\n    steps:\n      - uses: actions/checkout@v7\n"
                with self.assertRaisesRegex(ValueError, "not pinned"):
                    action_repositories(Path("fixture.yml"), text)

    def test_synchronization_preserves_script_quotes_before_real_actions(self):
        directory = self.root / ".github/workflows"
        directory.mkdir()
        workflow = directory / "example.yml"
        original = ("jobs:\n  test:\n    steps:\n      - run: |\n"
                    '''          echo 'note: "hello'\n'''
                    "          uses: fixture/fake@v1\n"
                    "      - uses: actions/checkout@" + "a" * 40 + " # v1.0.0\n")
        workflow.write_bytes(original.encode("utf-8"))
        synchronize_action_pins(
            self.root, lambda _: ActionRelease(tag="v2.0.0", sha="b" * 40), write=True)
        self.assertEqual(workflow.read_bytes().decode("utf-8"),
                         original.replace("a" * 40 + " # v1.0.0", "b" * 40 + " # v2.0.0"))

    def test_freshness_finds_stale_actions_after_script_quotes(self):
        directory = self.root / ".github/workflows"
        directory.mkdir()
        (directory / "example.yml").write_text(
            "jobs:\n  test:\n    steps:\n      - run: |\n"
            '''          echo "note: 'hello"\n'''
            "      - uses: actions/checkout@" + "a" * 40 + "\n", encoding="utf-8")
        findings = action_findings(self.root, (Path(".github/workflows"),),
                                   lambda _: ActionRelease(tag="v2.0.0", sha="b" * 40))
        self.assertEqual([finding["subject"] for finding in findings], ["actions/checkout"])

    def test_plain_scalar_delimiters_cannot_hide_unpinned_actions(self):
        for opening, closing in (("{", "}"), ("[", "]")):
            with self.subTest(opening=opening):
                text = (f"name: Review {opening}\njobs:\n  test:\n    steps:\n"
                        "      - uses: actions/checkout@v7\n"
                        f"      - name: Review {closing}\n        run: echo done\n")
                with self.assertRaisesRegex(ValueError, "not pinned"):
                    action_repositories(Path("fixture.yml"), text)

    def test_plain_scalar_delimiters_preserve_pinned_action_inventory(self):
        for opening, closing in (("{", "}"), ("[", "]")):
            with self.subTest(opening=opening):
                text = (f"name: Review {opening}\njobs:\n  test:\n    steps:\n"
                        "      - uses: actions/checkout@" + "a" * 40 + "\n"
                        f"      - name: Review {closing}\n        run: echo done\n")
                self.assertEqual(action_repositories(Path("fixture.yml"), text), {"actions/checkout"})

    def test_synchronization_updates_actions_between_plain_scalar_delimiters(self):
        directory = self.root / ".github/workflows"
        directory.mkdir()
        workflow = directory / "example.yml"
        for opening, closing in (("{", "}"), ("[", "]")):
            with self.subTest(opening=opening):
                original = (f"name: Review {opening}\njobs:\n  test:\n    steps:\n"
                            "      - uses: actions/checkout@" + "a" * 40 + " # v1.0.0\n"
                            f"      - name: Review {closing}\n        run: echo done\n")
                workflow.write_text(original, encoding="utf-8")
                changed = synchronize_action_pins(
                    self.root, lambda _: ActionRelease(tag="v2.0.0", sha="b" * 40), write=True)
                self.assertEqual(changed, [workflow])
                self.assertEqual(workflow.read_text(encoding="utf-8"),
                                 original.replace("a" * 40 + " # v1.0.0", "b" * 40 + " # v2.0.0"))

    def test_workflow_inventory_collects_both_extensions_once(self):
        directory = self.root / ".github/workflows"
        directory.mkdir()
        for name in ("second.yml", "first.yaml", "upper.YML"):
            (directory / name).write_text("name: Synthetic fixture\n", encoding="utf-8")
        expected = [directory / "first.yaml", directory / "second.yml"]
        if os.name == "nt":
            expected.append(directory / "upper.YML")
        self.assertEqual(workflow_paths(self.root, (Path(".github/workflows"),)), expected)

    def test_flow_plain_quotes_cannot_hide_unpinned_actions(self):
        for name in ("O'Reilly", 'Build "fast', "quote:inside'plain"):
            with self.subTest(name=name):
                text = "jobs: {test: {name: " + name + ", steps: [{uses: actions/checkout@v7}]}}\n"
                with self.assertRaisesRegex(ValueError, "not pinned"):
                    action_repositories(Path("fixture.yml"), text)

    def test_synchronization_updates_actions_after_plain_flow_quotes(self):
        directory = self.root / ".github/workflows"
        directory.mkdir()
        workflow = directory / "example.yml"
        for name in ("O'Reilly", 'Build "fast', "quote:inside'plain"):
            with self.subTest(name=name):
                original = "jobs: {test: {name: " + name + ", steps: [{uses: actions/checkout@" + "a" * 40 + "}]}}\n"
                workflow.write_text(original, encoding="utf-8")
                changed = synchronize_action_pins(
                    self.root, lambda _: ActionRelease(tag="v2.0.0", sha="b" * 40), write=True)
                self.assertEqual(changed, [workflow])
                self.assertEqual(workflow.read_text(encoding="utf-8"), original.replace("a" * 40, "b" * 40))

    def test_default_workflow_scope_uses_this_repository_layout(self):
        directory = self.root / ".github/workflows"
        directory.mkdir()
        workflow = directory / "example.yml"
        workflow.write_text("name: Synthetic fixture\n", encoding="utf-8")
        self.assertEqual(workflow_paths(self.root), [workflow])

    def test_workflow_read_error_cannot_return_a_partial_inventory(self):
        directory = self.root / ".github/workflows"
        directory.mkdir()
        for name in ("first.yml", "second.yaml"):
            (directory / name).write_text("name: Synthetic fixture\n", encoding="utf-8")
        scandir = os.scandir
        failed = False

        def interrupted_scan(path):
            nonlocal failed
            if Path(path) == directory and not failed:
                failed = True
                raise PermissionError("Synthetic transient directory read failure")
            return scandir(path)

        with patch("os.scandir", side_effect=interrupted_scan):
            with self.assertRaisesRegex(ValueError, "could not enumerate workflow directory"):
                workflow_paths(self.root, (Path(".github/workflows"),))

    def test_freshness_records_unreadable_workflow_scope_as_indeterminate(self):
        directory = self.root / ".github/workflows"
        directory.mkdir()
        for name, sha in (("outdated.yml", "b" * 40), ("current.yaml", "a" * 40)):
            (directory / name).write_text("jobs:\n  test:\n    steps:\n      - uses: actions/checkout@"
                                          + sha + "\n", encoding="utf-8")
        scandir = os.scandir
        failed = False

        def interrupted_scan(path):
            nonlocal failed
            if Path(path) == directory and not failed:
                failed = True
                raise PermissionError("Synthetic transient directory read failure")
            return scandir(path)

        errors = []
        with patch("os.scandir", side_effect=interrupted_scan):
            action_findings(self.root, (Path(".github/workflows"),),
                            lambda _: ActionRelease(tag="v1.0.0", sha="a" * 40), errors)
        self.assertTrue(any("could not enumerate workflow directory" in error for error in errors))

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

    def test_root_and_package_tag_options_cannot_break_the_release_pipeline(self):
        config = json.loads((self.root / "release-please-config.json").read_text(encoding="utf-8"))
        for location in ("root", "package"):
            for override in ({"include-component-in-tag": True}, {"include-component-in-tag": None},
                             {"include-v-in-tag": False}, {"include-v-in-tag": None},
                             {"include-v-in-tag": "true"}):
                with self.subTest(location=location, override=override):
                    candidate = ({**config, **override} if location == "root" else
                                 {**config, "packages": {".": override}})
                    self.write("release-please-config.json", candidate)
                    errors = validate_tooling(self.root)
                    self.assertTrue(any("v<SemVer>" in error for error in errors))
        self.write("release-please-config.json", {**config, "include-v-in-tag": True})
        self.assertEqual(validate_tooling(self.root), [])

    def test_package_settings_cannot_override_release_guards(self):
        config = json.loads((self.root / "release-please-config.json").read_text(encoding="utf-8"))
        for override in ({"draft": False}, {"skip-github-release": True},
                         {"release-type": "node"}, {"version-file": "unreviewed-version.txt"}):
            with self.subTest(override=override):
                self.write("release-please-config.json", {**config, "packages": {".": override}})
                self.assertTrue(any('packages["."]' in error for error in validate_tooling(self.root)))

    def test_matching_package_settings_remain_supported(self):
        config = json.loads((self.root / "release-please-config.json").read_text(encoding="utf-8"))
        config["packages"] = {".": {"draft": True, "skip-github-release": False,
                                     "release-type": "simple", "version-file": "version.txt"}}
        self.write("release-please-config.json", config)
        self.assertEqual(validate_tooling(self.root), [])

    def test_release_config_requires_single_root_package_mapping(self):
        config = json.loads((self.root / "release-please-config.json").read_text(encoding="utf-8"))
        for packages in (None, [], {}, {".": None}, {".": {}, "extra": {}}):
            with self.subTest(packages=packages):
                self.write("release-please-config.json", {**config, "packages": packages})
                self.assertTrue(any("packages phải" in error for error in validate_tooling(self.root)))

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

    def test_comment_backslashes_do_not_consume_the_next_requirement(self):
        source = self.root / "requirements-docs.txt"
        for prefix in ("# note", "  # note", "\t# note"):
            for tail in ("\nother==2.0.0\n", ""):
                with self.subTest(prefix=prefix, tail=tail):
                    source.write_text("example==1.0.0\n" + prefix + "\\" + tail, encoding="utf-8")
                    expected = {"example": "1.0.0", **({"other": "2.0.0"} if tail else {})}
                    self.assertEqual(read_requirement_pins(source), expected)
                    self.assertEqual(pinned_requirements(source),
                                     {name: (name, version) for name, version in expected.items()})

    def test_comment_backslashes_cannot_hide_unsupported_requirements(self):
        source = self.root / "requirements-docs.txt"
        for declaration in ("-r extra.txt", "-c constraints.txt", "other>=2",
                            "--extra-index-url https://example.invalid"):
            with self.subTest(declaration=declaration):
                source.write_text("example==1.0.0\n# note\\\n" + declaration + "\n", encoding="utf-8")
                with self.assertRaises(ValueError):
                    read_requirement_pins(source)
                with self.assertRaises(AuditError):
                    pinned_requirements(source)

    def test_comment_ends_a_pending_logical_requirement(self):
        source = self.root / "requirements-docs.lock"
        source.write_text("example==1.0.0 \\\n    " + self.hash_option + " \\\n# note\\\n"
                          "other==2.0.0 " + self.hash_option + "\n", encoding="utf-8")
        self.assertEqual(read_requirement_pins(source, require_hashes=True),
                         {"example": "1.0.0", "other": "2.0.0"})
        source.write_text("example==1.0.0 \\\n# note\\\n    " + self.hash_option + "\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            read_requirement_pins(source, require_hashes=True)

    def test_whitespace_after_a_backslash_does_not_create_a_continuation(self):
        source = self.root / "requirements-docs.lock"
        for whitespace in (" ", "\t", " \t"):
            with self.subTest(whitespace=whitespace):
                source.write_text("example==1.0.0 \\" + whitespace + "\n    " + self.hash_option + "\n", encoding="utf-8")
                with self.assertRaises(ValueError):
                    read_requirement_pins(source, require_hashes=True)

    def test_dependency_after_comment_still_requires_a_matching_lock_entry(self):
        (self.root / "requirements-docs.txt").write_text(
            "example==1.0.0\n# note\\\nother==2.0.0\n", encoding="utf-8")
        self.assertTrue(any("Python trực tiếp và lockfile không đồng bộ" in error
                            for error in validate_tooling(self.root)))

    def test_comment_backslashes_cannot_hide_hashless_lock_entries(self):
        source = self.root / "requirements-docs.lock"
        source.write_text("example==1.0.0 " + self.hash_option + "\n# note\\\nother==2.0.0\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "hash SHA-256"):
            read_requirement_pins(source, require_hashes=True)

    def test_inline_comments_are_stripped_after_line_continuation(self):
        source = self.root / "requirements-docs.txt"
        source.write_text("example==1.0.0 # inline\\\nignored==9.0.0\nother==2.0.0\n", encoding="utf-8")
        self.assertEqual(read_requirement_pins(source), {"example": "1.0.0", "other": "2.0.0"})

    def test_freshness_accepts_the_same_supported_requirement_formats(self):
        source = self.root / "requirements-docs.txt"
        for text in ("# direct\n Example_Tool == 1.0.0  # explanation\n",
                     "example-tool==1.0.0 " + self.hash_option + "\n",
                     "example-tool==1.0.0 \\" + "\n    " + self.hash_option + "\n"):
            with self.subTest(text=text):
                source.write_text(text, encoding="utf-8")
                self.assertEqual(read_requirement_pins(source), {"example-tool": "1.0.0"})
                self.assertEqual(pinned_requirements(source),
                                 {"example-tool": ("example-tool", "1.0.0")})

    def test_freshness_rejects_unsupported_or_incomplete_requirement_inputs(self):
        source = self.root / "requirements-docs.txt"
        for tail in ("-r extra.txt\n", "--requirement extra.txt\n",
                     "Example==1.0.0\n", "other==1.0.0 \\"):
            with self.subTest(tail=tail):
                source.write_text("example==1.0.0\n" + tail, encoding="utf-8")
                with self.assertRaises(AuditError):
                    pinned_requirements(source)

    def test_freshness_detects_drift_with_single_line_hashes_and_rejects_hashless_lock(self):
        source = self.root / "requirements-docs.txt"
        lock = self.root / "requirements-docs.lock"
        source.write_text("Example == 1.0.0\n", encoding="utf-8")
        scope = (RequirementSource(Path(source.name), (Path(lock.name),)),)
        lock.write_text("example==2.0.0 " + self.hash_option + "\n", encoding="utf-8")
        errors = []
        findings = requirement_findings(self.root, scope, lambda _: "1.0.0", errors)
        self.assertEqual(errors, [])
        self.assertTrue(any(finding["kind"] == "lock-consistency"
                            and finding["current"] == "2.0.0" for finding in findings))
        source.write_text("example==1.0.0\n", encoding="utf-8")
        lock.write_text("example==1.0.0\n", encoding="utf-8")
        errors = []
        requirement_findings(self.root, scope, lambda _: "1.0.0", errors)
        self.assertTrue(errors, "Hashless locks must not produce a current freshness report")

    def test_dangling_continuation_is_rejected(self):
        (self.root / "requirements-docs.txt").write_text("example==1.0.0 \\", encoding="utf-8")
        self.assertTrue(any("chưa kết thúc" in error for error in validate_tooling(self.root)))

    def test_empty_lock_and_extra_unparsed_lines_are_rejected(self):
        for text in ("# nothing\n", "example==1.0.0 " + self.hash_option + "\n--extra-index-url https://example.invalid\n"):
            with self.subTest(text=text):
                (self.root / "requirements-docs.lock").write_text(text, encoding="utf-8")
                with self.assertRaises(ValueError):
                    read_requirement_pins(self.root / "requirements-docs.lock", require_hashes=True)


class ToolchainRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.policy_path = Path(__file__).resolve().parents[1] / ".github/ci-toolchain.json"

    def test_policy_cannot_advertise_a_runtime_without_junction_checks(self):
        document = json.loads(self.policy_path.read_text(encoding="utf-8"))
        for minimum in ("3.10", "3.11"):
            with self.subTest(minimum=minimum):
                with self.assertRaises(ci_toolchain.ToolchainError):
                    ci_toolchain.parse_policy({**document, "tooling-python-minimum": minimum})

    def test_old_runtime_stops_before_lint_and_explains_upgrade(self):
        error = io.StringIO()
        with patch.object(ci_toolchain.sys, "version_info", (3, 11, 9)), \
                patch.object(ci_toolchain, "run_markdownlint", return_value=0) as lint, \
                redirect_stderr(error):
            result = ci_toolchain.main(["--policy", str(self.policy_path), "run-markdownlint"])
        self.assertEqual((result, "Python 3.12" in error.getvalue(), lint.called),
                         (1, True, False))

    def test_supported_runtime_preserves_the_linter_exit_code(self):
        with patch.object(ci_toolchain.sys, "version_info", (3, 12, 0)), \
                patch.object(ci_toolchain, "run_markdownlint", return_value=7) as lint:
            result = ci_toolchain.main(["--policy", str(self.policy_path), "run-markdownlint"])
        self.assertEqual((result, lint.call_count), (7, 1))


if __name__ == "__main__":
    unittest.main()
