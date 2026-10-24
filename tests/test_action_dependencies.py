"""Dependency metadata inspection cannot execute hooks or hide incomplete reads."""

from pathlib import Path
from hashlib import sha1
from contextlib import redirect_stdout
import base64
import io
import json
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from action_dependencies import inspect_actions, inspect_npm, inspection_complete, main, source_file


def metadata():
    package = {"dependencies": {"fixture-core": "^1.0.0"},
               "devDependencies": {"fixture-dev": "2.0.0"},
               "scripts": {"postinstall": "this hook must never be executed"}}
    lock = {"lockfileVersion": 3, "packages": {"": package,
            "node_modules/fixture-core": {"version": "1.1.0", "integrity": "sha512-fixture"},
            "node_modules/fixture-dev": {"version": "2.0.0"},
            "node_modules/fixture-transitive": {"version": "3.0.0"}}}
    return {"package.json": json.dumps(package).encode(),
            "package-lock.json": json.dumps(lock).encode(),
            "action.yml": b"name: fixture\nruns:\n  using: node24\n  main: dist/index.js\n"}


class Client:
    def __init__(self, files):
        self.files = files
        self.entries = {name: {"type": "file", "name": name, "path": name,
            "sha": sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()}
            for name, raw in files.items()}

    def get_json_list(self, path):
        return list(self.entries.values())

    def get_json(self, path):
        name = path.split("/contents/")[1].split("?")[0]
        raw = self.files[name]
        return {"encoding": "base64", "content": base64.b64encode(raw).decode(), "size": len(raw)}


class ActionDependencyTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / ".github/workflows").mkdir(parents=True)
        (self.root / ".github/workflows/test.yml").write_text(
            "jobs:\n  check:\n    steps:\n      - uses: actions/checkout@" + "a" * 40 + "\n",
            encoding="utf-8")

    def test_manifest_and_all_lock_entries_are_inventoried(self):
        record = inspect_npm(metadata())
        self.assertEqual(len(record["locked_packages"]), 3)
        self.assertEqual([(x["name"], x["kind"], x["locked"]) for x in record["direct"]],
                         [("fixture-core", "dependencies", "1.1.0"),
                          ("fixture-dev", "devDependencies", "2.0.0")])
        self.assertFalse(record["transitive_latest_versions_checked"])
        self.assertFalse(record["bundle_independently_rebuilt"])

    def test_direct_registry_lookups_do_not_include_transitive_names(self):
        looked_up = []
        def latest(name):
            looked_up.append(name)
            return "9.0.0"
        report = inspect_actions(self.root, (Path(".github/workflows"),), Client(metadata()), latest)
        self.assertEqual(set(looked_up), {"fixture-core", "fixture-dev"})
        self.assertEqual(report["actions"][0]["status"], "inspected")
        self.assertEqual(len(report["actions"][0]["metadata"]), 3)

    def test_container_references_cannot_disappear_from_complete_coverage(self):
        image = "docker://alpine@sha256:" + "b" * 64
        workflow = self.root / ".github/workflows/test.yml"
        workflow.write_text(workflow.read_text(encoding="utf-8") +
                            "      - uses: " + image + "\n", encoding="utf-8")
        report = inspect_actions(self.root, (Path(".github/workflows"),),
                                 Client(metadata()), lambda _: "1.0.0")
        statuses = {record["action"]: record["status"] for record in report["actions"]}
        self.assertEqual(statuses, {image: "indeterminate", "actions/checkout": "inspected"})
        self.assertFalse(inspection_complete(report))

    def test_aliased_container_retains_its_resolved_image_reference(self):
        image = "docker://alpine@sha256:" + "b" * 64
        (self.root / ".github/workflows/test.yml").write_text(
            "env:\n  IMAGE: &container " + image + "\njobs:\n  check:\n    steps:\n"
            "      - uses: *container\n", encoding="utf-8")
        report = inspect_actions(self.root, (Path(".github/workflows"),),
                                 Client(metadata()), lambda _: "1.0.0")
        self.assertEqual(report["actions"][0]["action"], image)
        self.assertFalse(inspection_complete(report))

    def test_container_references_count_towards_the_action_limit(self):
        (self.root / ".github/workflows/test.yml").write_text(
            "jobs:\n  check:\n    steps:\n" + "".join(
                f"      - uses: docker://fixture-{i}@sha256:" + "b" * 64 + "\n"
                for i in range(33)), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "action limit"):
            inspect_actions(self.root, (Path(".github/workflows"),),
                            Client(metadata()), lambda _: "1.0.0")

    def test_unresolved_or_ambiguous_aliases_are_retained_as_indeterminate(self):
        for definitions in ("", "env:\n  FIRST: &action ./.github/actions/one\n"
                               "  SECOND: &action ./.github/actions/two\n"):
            with self.subTest(definitions=definitions):
                (self.root / ".github/workflows/test.yml").write_text(
                    definitions + "jobs:\n  check:\n    steps:\n      - uses: *action\n", encoding="utf-8")
                report = inspect_actions(self.root, (Path(".github/workflows"),),
                                         Client(metadata()), lambda _: "1.0.0")
                self.assertEqual(report["actions"][0]["action"], "*action")
                self.assertFalse(inspection_complete(report))

    def test_content_must_match_the_exact_git_blob(self):
        client = Client(metadata())
        entry = {**client.entries["package.json"], "sha": "f" * 40}
        with self.assertRaisesRegex(ValueError, "Git object"):
            source_file(client, "fixture/example", entry, "a" * 40)

    def test_root_constraint_drift_and_missing_locks_fail_explicitly(self):
        files = metadata()
        package = json.loads(files["package.json"])
        package["dependencies"]["fixture-core"] = "^4.0.0"
        files["package.json"] = json.dumps(package).encode()
        with self.assertRaisesRegex(ValueError, "disagree"):
            inspect_npm(files)
        files.pop("package-lock.json")
        with self.assertRaisesRegex(ValueError, "No supported npm lockfile"):
            inspect_npm(files)

    def test_unsupported_runtime_is_not_silently_reported_inspected(self):
        files = metadata()
        files["action.yml"] = b"runs:\n  using: composite\n  steps: []\n"
        report = inspect_actions(self.root, (Path(".github/workflows"),), Client(files), lambda _: "1.0.0")
        self.assertEqual(report["actions"][0]["status"], "indeterminate")

    def test_additional_dependency_formats_keep_coverage_incomplete(self):
        for name in ("pnpm-lock.yaml", "yarn.lock", "pyproject.toml"):
            with self.subTest(name=name):
                files = metadata()
                files[name] = b"synthetic unsupported dependency metadata"
                report = inspect_actions(self.root, (Path(".github/workflows"),),
                                         Client(files), lambda _: "1.0.0")
                record = report["actions"][0]
                self.assertEqual(record["status"], "indeterminate")
                self.assertIn(name, record["error"])
                self.assertEqual(len(record["metadata"]), 4)
                self.assertFalse(inspection_complete(report))

    def test_declared_non_npm_manager_cannot_use_a_legacy_npm_lock(self):
        files = metadata()
        package = json.loads(files["package.json"])
        package["packageManager"] = "pnpm@9.0.0"
        files["package.json"] = json.dumps(package).encode()
        with self.assertRaisesRegex(ValueError, "packageManager"):
            inspect_npm(files)

    def test_two_npm_locks_require_explicit_resolution(self):
        files = metadata()
        files["npm-shrinkwrap.json"] = files["package-lock.json"]
        with self.assertRaisesRegex(ValueError, "Multiple lockfiles"):
            inspect_npm(files)

    def test_failed_cli_inspection_retains_the_diagnostic_report(self):
        files = metadata()
        files["pnpm-lock.yaml"] = b"lockfileVersion: '9.0'\n"
        output = self.root / "reports/action-dependencies.json"
        arguments = ["action_dependencies.py", "--repository-root", str(self.root),
                     "--json-output", str(output)]
        with patch("sys.argv", arguments), redirect_stdout(io.StringIO()), \
                patch("action_dependencies.sync_action_pins.GitHubReleaseClient", return_value=Client(files)):
            self.assertEqual(main(), 2)
        report = json.loads(output.read_text(encoding="utf-8"))
        self.assertFalse(inspection_complete(report))
        self.assertIn("pnpm-lock.yaml", report["actions"][0]["error"])

    def test_malformed_direct_lock_entries_are_rejected_before_lookup(self):
        for entry in ([], None, "invalid", 42):
            with self.subTest(entry=entry):
                files = metadata()
                lock = json.loads(files["package-lock.json"])
                lock["packages"]["node_modules/fixture-core"] = entry
                files["package-lock.json"] = json.dumps(lock).encode()
                with self.assertRaisesRegex(ValueError, "Invalid npm lock entry"):
                    inspect_npm(files)

    def test_one_malformed_action_does_not_discard_other_action_results(self):
        files = metadata()
        lock = json.loads(files["package-lock.json"])
        lock["packages"]["node_modules/fixture-core"] = []
        files["package-lock.json"] = json.dumps(lock).encode()
        malformed, valid = Client(files), Client(metadata())

        class MultiActionClient:
            def get_json_list(self, path):
                return (malformed if "/checkout/" in path else valid).get_json_list(path)

            def get_json(self, path):
                return (malformed if "/checkout/" in path else valid).get_json(path)

        workflow = self.root / ".github/workflows/test.yml"
        workflow.write_text(workflow.read_text(encoding="utf-8") +
                            "      - uses: actions/setup-node@" + "b" * 40 + "\n", encoding="utf-8")
        report = inspect_actions(self.root, (Path(".github/workflows"),),
                                 MultiActionClient(), lambda _: "1.0.0")
        self.assertEqual([(record["action"], record["status"]) for record in report["actions"]],
                         [("actions/checkout", "indeterminate"), ("actions/setup-node", "inspected")])
        self.assertIn("Invalid npm lock entry", report["actions"][0]["error"])
        self.assertFalse(inspection_complete(report))

    def test_registry_failure_is_retained_per_dependency(self):
        def unavailable(name):
            raise OSError("Synthetic registry outage")
        report = inspect_actions(self.root, (Path(".github/workflows"),), Client(metadata()), unavailable)
        self.assertTrue(all(x["registry_error"] for x in report["actions"][0]["direct"]))

    def test_local_action_metadata_and_lock_are_also_inspected(self):
        local = self.root / ".github/actions/fixture"
        local.mkdir(parents=True)
        for name, raw in metadata().items():
            (local / name).write_bytes(raw)
        workflow = self.root / ".github/workflows/test.yml"
        workflow.write_text(workflow.read_text(encoding="utf-8") + "      - uses: './.github/actions/fixture'\n", encoding="utf-8")
        report = inspect_actions(self.root, (Path(".github/workflows"),), Client(metadata()), lambda _: "1.0.0")
        self.assertEqual(len(report["actions"]), 2)
        self.assertTrue(all(x["status"] == "inspected" for x in report["actions"]))

    def test_local_aliases_inspect_the_same_metadata_as_literal_paths(self):
        local = self.root / ".github/actions/fixture"
        local.mkdir(parents=True)
        for name, raw in metadata().items():
            (local / name).write_bytes(raw)
        for declaration in ("env:\n  ACTION: &local ./.github/actions/fixture\n",
                            "env: {ACTION: &local './.github/actions/fixture'}\n"):
            with self.subTest(declaration=declaration):
                (self.root / ".github/workflows/test.yml").write_text(
                    declaration + "jobs:\n  check:\n    steps:\n      - uses: *local\n"
                    "      - uses: ./.github/actions/fixture\n", encoding="utf-8")
                report = inspect_actions(self.root, (Path(".github/workflows"),),
                                         Client(metadata()), lambda _: "1.0.0")
                self.assertEqual(len(report["actions"]), 1)
                self.assertEqual(report["actions"][0]["action"], "./.github/actions/fixture")
                self.assertEqual(len(report["actions"][0]["metadata"]), 3)
                self.assertTrue(inspection_complete(report))

    def test_local_nested_actions_are_not_silently_treated_as_complete(self):
        local = self.root / ".github/actions/fixture"
        local.mkdir(parents=True)
        for name, raw in metadata().items():
            (local / name).write_bytes(raw)
        (local / "action.yml").write_text("runs:\n  using: composite\n  steps: []\n", encoding="utf-8")
        workflow = self.root / ".github/workflows/test.yml"
        workflow.write_text("jobs:\n  check:\n    steps:\n      - uses: ./.github/actions/fixture\n", encoding="utf-8")
        report = inspect_actions(self.root, (Path(".github/workflows"),), Client(metadata()), lambda _: "1.0.0")
        self.assertEqual(report["actions"][0]["status"], "indeterminate")

    def test_non_object_metadata_is_rejected_as_a_data_error(self):
        files = metadata()
        files["package.json"] = b"[]"
        with self.assertRaisesRegex(ValueError, "must be objects"):
            inspect_npm(files)

    def test_direct_inventory_is_bounded_before_registry_lookups(self):
        files = metadata()
        package = {"dependencies": {f"package-{i}": "1.0.0" for i in range(257)}}
        files["package.json"] = json.dumps(package).encode()
        files["package-lock.json"] = json.dumps({"packages": {"": package}}).encode()
        with self.assertRaisesRegex(ValueError, "oversized direct"):
            inspect_npm(files)


if __name__ == "__main__":
    unittest.main()
