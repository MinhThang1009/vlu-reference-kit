"""Dependency metadata inspection cannot execute hooks or hide incomplete reads."""

from pathlib import Path
from hashlib import sha1
import base64
import json
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from action_dependencies import inspect_actions, inspect_npm, source_file


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
