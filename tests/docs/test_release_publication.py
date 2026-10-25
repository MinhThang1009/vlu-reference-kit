"""Exercise pagination and tag changes at the actual workflow publication boundary."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[2]
EXPECTED_SHA = "a" * 40
MOVED_SHA = "b" * 40
TAG = "v9.8.7"
SHIM = r'''
import os, subprocess, sys
from urllib.parse import quote
mode, *args = sys.argv[1:]
base = os.environ["FIXTURE_API"]
env = os.environ.copy()
env["GH_TOKEN"] = "synthetic-fixture-token"
for key in ("GITHUB_TOKEN", "GH_ENTERPRISE_TOKEN", "GITHUB_ENTERPRISE_TOKEN"):
    env.pop(key, None)
if mode == "gh":
    if args[0] != "api":
        raise SystemExit("Only fixture API operations are allowed")
    if "--hostname" in args:
        index = args.index("--hostname")
        del args[index:index + 2]
    index = next(i for i, value in enumerate(args) if value.startswith("repos/"))
    args[index] = base + "/" + args[index]
    payload = None
elif mode == "jq":
    flag, expression, *files = args
    if files:
        with open(files[0], "rb") as source:
            payload = source.read()
    else:
        payload = sys.stdin.buffer.read()
    if flag == "-Rr" and expression == "@uri":
        print(quote(payload.decode().rstrip("\r\n"), safe=""))
        raise SystemExit(0)
    args = ["api", base + "/jq", "--method", "POST", "--input", "-", "--jq", expression]
else:
    raise SystemExit("Unknown fixture operation")
result = subprocess.run([env["FIXTURE_GH"], *args], input=payload,
                        capture_output=True, env=env, timeout=15)
sys.stdout.buffer.write(result.stdout)
sys.stderr.buffer.write(result.stderr)
if mode == "jq" and flag == "-e" and result.returncode == 0:
    values = result.stdout.strip().splitlines()
    if not values or values[-1] in (b"false", b"null"):
        raise SystemExit(1)
raise SystemExit(result.returncode)
'''


class FixtureHandler(BaseHTTPRequestHandler):
    def reply(self, document, status=200, next_page=None):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        if next_page is not None:
            self.send_header("Link", f'<{self.server.base}/releases?page={next_page}>; rel="next"')
        self.end_headers()
        self.wfile.write(json.dumps(document).encode())

    def do_GET(self):
        route = urlsplit(self.path)
        self.server.requests.append(route.path)
        if route.path.endswith("/releases"):
            page = int(parse_qs(route.query).get("page", ["1"])[0])
            following = page + 1 if page < len(self.server.pages) else None
            self.reply(self.server.pages[page - 1], next_page=following)
        elif "/git/ref/tags/" in route.path:
            if self.server.deleted_tag:
                self.reply({"message": "Synthetic missing tag"}, 404)
            else:
                depth = self.server.annotation_depth or int(self.server.annotated)
                self.reply({"object": {"type": "tag" if depth else "commit",
                                       "sha": f"{1:040x}" if depth else self.server.tag_sha}})
        elif "/git/tags/" in route.path:
            layer = int(route.path.rsplit("/", 1)[1], 16)
            depth = self.server.annotation_depth or int(self.server.annotated)
            self.reply({"object": {"type": "tag" if layer < depth else "commit",
                                   "sha": f"{layer + 1:040x}" if layer < depth else self.server.tag_sha}})
        elif route.path.endswith("/releases/123"):
            self.reply(self.server.release)
        else:
            self.reply({"message": "Unexpected fixture request"}, 404)

    def read_document(self):
        if self.headers.get("Transfer-Encoding", "").lower() == "chunked":
            payload = bytearray()
            while True:
                size = int(self.rfile.readline(128).split(b";", 1)[0].strip(), 16)
                if not size:
                    self.rfile.readline(128)
                    break
                if len(payload) + size > 65536:
                    raise ValueError("Oversized fixture request")
                payload.extend(self.rfile.read(size))
                if self.rfile.read(2) != b"\r\n":
                    raise ValueError("Malformed fixture chunk")
            return json.loads(payload)
        size = int(self.headers.get("Content-Length", "0"))
        if size > 65536:
            raise ValueError("Oversized fixture request")
        return json.loads(self.rfile.read(size))

    def do_POST(self):
        if self.path != "/jq":
            self.reply({"message": "Unexpected fixture POST"}, 404)
            return
        self.reply(self.read_document())

    def do_PATCH(self):
        document = self.read_document()
        if not self.path.endswith("/releases/123") or document.get("draft") is not False:
            self.reply({"message": "Unexpected fixture mutation"}, 400)
            return
        if self.server.move_during_publication:
            self.server.tag_sha = MOVED_SHA
        if self.server.retag_during_publication:
            self.server.release["tag_name"] = "v8.8.8"
        self.server.patches += 1
        self.server.release["draft"] = False
        self.reply(self.server.release)

    def log_message(self, *_args):
        pass


class WorkflowFixture(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gh = shutil.which("gh")
        if cls.gh is None:
            raise RuntimeError("Workflow boundary tests require the existing GitHub CLI")
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), FixtureHandler)
        cls.server.base = f"http://127.0.0.1:{cls.server.server_port}"
        cls.addClassCleanup(cls.server.server_close)
        thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        thread.start()
        cls.addClassCleanup(thread.join, 5)
        cls.addClassCleanup(cls.server.shutdown)

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.temp = Path(self.temporary.name)
        self.server.pages = [[]]
        self.server.requests = []
        self.server.tag_sha = EXPECTED_SHA
        self.server.deleted_tag = False
        self.server.annotated = False
        self.server.annotation_depth = 0
        self.server.move_during_publication = False
        self.server.retag_during_publication = False
        self.server.patches = 0
        self.server.release = {"id": 123, "tag_name": TAG, "draft": True, "assets": [
            {"name": "vlu-reference-kit-community.zip", "size": 100},
            {"name": "SHA256SUMS.txt", "size": 98}]}
        workflow = yaml.safe_load((ROOT / ".github/workflows/release-please.yml").read_text(encoding="utf-8"))
        self.job = workflow["jobs"]["attach-release-assets"]
        self.steps = self.job["steps"]
        self.environment = os.environ.copy()
        for key in ("GITHUB_TOKEN", "GH_ENTERPRISE_TOKEN", "GITHUB_ENTERPRISE_TOKEN"):
            self.environment.pop(key, None)
        self.environment.update(GH_TOKEN="synthetic-fixture-token", RELEASE_TAG=TAG,
                                RELEASE_SHA=EXPECTED_SHA, RELEASE_ID="123",
                                GITHUB_REPOSITORY="fixture/example", RUNNER_TEMP=self.temp.as_posix(),
                                GITHUB_OUTPUT=(self.temp / "github-output").as_posix(),
                                FIXTURE_API=self.server.base, FIXTURE_GH=self.gh,
                                GH_HOST="github.com", GH_CONFIG_DIR=(self.temp / "gh-config").as_posix(),
                                FIXTURE_PYTHON=Path(sys.executable).as_posix())


class PaginatedReleaseLookupTests(WorkflowFixture):
    def lookup(self):
        script = next(step["run"] for step in self.steps if step.get("id") == "release_state")
        expression = re.search(r"--jq '([^']+)'", script).group(1)
        result = subprocess.run([self.gh, "api", self.server.base + "/releases", "--paginate", "--jq", expression],
                                env=self.environment, capture_output=True, encoding="utf-8", timeout=15, check=True)
        return result.stdout.strip()

    def test_target_on_any_page_yields_one_release_without_null_placeholders(self):
        unrelated = [{"id": i, "tag_name": f"v0.0.{i}", "draft": False} for i in range(100)]
        for page in range(3):
            with self.subTest(page=page):
                self.server.pages = [unrelated, unrelated, unrelated]
                self.server.pages[page] = [self.server.release]
                self.assertEqual(json.loads(self.lookup()), self.server.release)

    def test_missing_release_yields_empty_output(self):
        self.server.pages = [[], []]
        self.assertEqual(self.lookup(), "")


class ReleasePublicationBoundaryTests(WorkflowFixture):
    def execute_steps(self, names):
        bash = shutil.which("bash")
        if os.name == "nt":
            installed = Path(os.environ["ProgramFiles"]) / "Git/bin/bash.exe"
            if installed.is_file():
                bash = str(installed)
        self.assertIsNotNone(bash, "Publication tests require Bash")
        shim = self.temp / "fixture_api.py"
        shim.write_text(SHIM, encoding="utf-8")
        environment = {**self.environment, "FIXTURE_SHIM": shim.as_posix()}
        preamble = 'gh() { "$FIXTURE_PYTHON" "$FIXTURE_SHIM" gh "$@"; }\njq() { "$FIXTURE_PYTHON" "$FIXTURE_SHIM" jq "$@"; }\n'
        results = []
        for step in self.steps:
            if step["name"] not in names:
                continue
            result = subprocess.run([bash, "-c", preamble + step["run"]], cwd=self.temp,
                                    env=environment, capture_output=True, encoding="utf-8",
                                    timeout=60 if self.server.annotation_depth else 30)
            results.append((step["name"], result))
            if result.returncode:
                break
        self.assertTrue(results)
        return results

    def execute_publication(self, tag_only=False):
        names = ({"Verify release tag before publication"} if tag_only else
                 {"Verify attached assets", "Verify release tag before publication", "Publish Release after assets and attestation pass",
                  "Verify release tag after publication", "Verify published Release"})
        return self.execute_steps(names)

    def test_semver_prerelease_and_build_metadata_pass_the_upload_preflight(self):
        tag = "v9.8.7-rc.1+build.001"
        self.environment["RELEASE_TAG"] = tag
        self.server.release["tag_name"] = tag
        self.server.pages = [[self.server.release]]
        state_step = next(step for step in self.steps if step.get("id") == "release_state")
        results = self.execute_steps({state_step["name"]})
        self.assertEqual(results[0][1].returncode, 0, results[0][1].stderr)
        self.assertIn("release_id=123", (self.temp / "github-output").read_text())

    def test_unchanged_tag_allows_publication(self):
        results = self.execute_publication()
        self.assertTrue(all(result.returncode == 0 for _, result in results), str(results))
        self.assertEqual(self.server.patches, 1)

    def test_tag_moved_after_upload_blocks_publication(self):
        self.server.tag_sha = MOVED_SHA
        results = self.execute_publication()
        self.assertEqual(self.server.patches, 0, "Workflow published with a tag pointing to different bytes")
        self.assertEqual(results[-1][0], "Verify release tag before publication")

    def test_move_during_publication_is_reported_as_a_failure(self):
        self.server.move_during_publication = True
        results = self.execute_publication()
        self.assertEqual(self.server.patches, 1)
        self.assertNotEqual(results[-1][1].returncode, 0, "Tag movement during PATCH was not detected")
        self.assertEqual(results[-1][0], "Verify release tag after publication")

    def test_release_reassigned_to_another_tag_blocks_publication(self):
        self.server.release["tag_name"] = "v8.8.8"
        results = self.execute_publication()
        self.assertEqual(self.server.patches, 0)
        self.assertEqual(results[-1][0], "Verify attached assets")

    def test_release_reassigned_during_patch_cannot_report_success(self):
        self.server.retag_during_publication = True
        results = self.execute_publication()
        self.assertEqual(self.server.patches, 1)
        self.assertNotEqual(results[-1][1].returncode, 0)
        self.assertEqual(results[-1][0], "Publish Release after assets and attestation pass")

    def test_annotated_tag_is_peeled_before_publication(self):
        self.server.annotated = True
        results = self.execute_publication()
        self.assertTrue(all(result.returncode == 0 for _, result in results), str(results))
        self.assertTrue(any("/git/tags/" in request for request in self.server.requests))

    def test_deleted_tag_blocks_publication(self):
        self.server.deleted_tag = True
        self.execute_publication()
        self.assertEqual(self.server.patches, 0)

    def test_final_annotation_hop_cannot_bypass_the_commit_identity_check(self):
        self.server.annotation_depth = 32
        self.server.tag_sha = MOVED_SHA
        results = self.execute_publication(tag_only=True)
        self.assertNotEqual(results[-1][1].returncode, 0,
                            "Commit reached on the final loop iteration escaped SHA comparison")
        self.assertEqual(len(self.server.requests), 33)

    def test_tag_checks_bracket_upload_and_publication_without_failure_bypasses(self):
        names = [step["name"] for step in self.steps]
        ordered = ["Verify release tag before upload", "Attach ZIP and checksum to draft Release",
                   "Verify attached assets", "Verify release tag before publication",
                   "Publish Release after assets and attestation pass", "Verify release tag after publication",
                   "Verify published Release"]
        self.assertEqual([names.index(name) for name in ordered], sorted(names.index(name) for name in ordered))
        guards = [step for step in self.steps if step["name"].startswith("Verify release tag ")]
        self.assertEqual(len(guards), 3)
        self.assertEqual(len({step["run"] for step in guards}), 1)
        for step in guards:
            self.assertFalse(step.get("continue-on-error", False))
            self.assertIn(step.get("if"), (None, "success()", "${{ success() }}"))

    def test_publication_uses_the_manual_workflow_tag_lock(self):
        manual = yaml.safe_load((ROOT / ".github/workflows/release.yml").read_text(encoding="utf-8"))
        manual_lock = manual["concurrency"]["group"].replace("${{ inputs.tag }}", TAG)
        automatic = self.job["concurrency"]
        self.assertEqual(automatic["group"].replace("${{ needs.release-pr.outputs.tag_name }}", TAG), manual_lock)
        self.assertIs(automatic["cancel-in-progress"], False)


if __name__ == "__main__":
    unittest.main()
