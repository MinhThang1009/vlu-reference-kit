"""Execute workflow publication predicates against JSON release states."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import os
import re
import shutil
import subprocess
import threading
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[2]


class ReleaseStateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.jq = shutil.which("jq")
        cls.gh = shutil.which("gh")
        if cls.jq:
            return
        if not cls.gh:
            raise RuntimeError("Release predicate tests require jq or GitHub CLI's jq engine")

        class FixtureHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(self.server.document)

            def log_message(self, *_args):
                pass

        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), FixtureHandler)
        cls.addClassCleanup(cls.server.server_close)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.addClassCleanup(cls.thread.join, 5)
        cls.addClassCleanup(cls.server.shutdown)

    def evaluate(self, expression, document):
        payload = json.dumps(document)
        if self.jq:
            command = [self.jq, "-r", expression]
        else:
            self.server.document = payload.encode("utf-8")
            command = [self.gh, "api", f"http://127.0.0.1:{self.server.server_port}/fixture",
                       "--jq", expression]
        environment = os.environ.copy()
        # The fallback contacts only the local synthetic fixture server.
        environment["GH_TOKEN"] = "synthetic-fixture-token"
        environment.pop("GITHUB_TOKEN", None)
        result = subprocess.run(command, input=payload, text=True, capture_output=True,
                                env=environment, timeout=15, check=True)
        return result.stdout.strip()

    def test_publication_checks_accept_only_explicit_false(self):
        states = (({"draft": False}, True), ({"draft": True}, False),
                  ({"draft": None}, False), ({}, False),
                  ({"draft": "false"}, False), ({"draft": 0}, False))
        for filename in ("release-please.yml", "release.yml"):
            document = yaml.safe_load((ROOT / ".github/workflows" / filename)
                                      .read_text(encoding="utf-8"))
            scripts = [step["run"] for job in document["jobs"].values()
                       for step in job["steps"] if "run" in step]
            checks = re.findall(r"jq -r '([^']+)' <<<\"\$\{release_json\}\"\)\" == \"([^\"]+)\"",
                                "\n".join(scripts))
            self.assertTrue(checks, f"No publication state check found in {filename}")
            for expression, expected in checks:
                for state, accepted in states:
                    with self.subTest(workflow=filename, state=state):
                        self.assertEqual(self.evaluate(expression, state) == expected, accepted)

    def test_publication_response_requires_both_nonempty_assets(self):
        assets = [{"name": "vlu-reference-kit-community.zip", "size": 100},
                  {"name": "SHA256SUMS.txt", "size": 98}]
        for filename in ("release-please.yml", "release.yml"):
            document = yaml.safe_load((ROOT / ".github/workflows" / filename)
                                      .read_text(encoding="utf-8"))
            scripts = "\n".join(step["run"] for job in document["jobs"].values()
                                for step in job["steps"] if "run" in step)
            expressions = [expression for expression in re.findall(r"jq -e '([^']+)'", scripts)
                           if ".draft == false" in expression]
            self.assertTrue(expressions, f"No publication response check found in {filename}")
            fixtures = (({"draft": False, "assets": assets}, True),
                        ({"draft": True, "assets": assets}, False),
                        ({"draft": False, "assets": assets[:1]}, False),
                        ({"draft": False, "assets": assets[1:]}, False),
                        ({"draft": False, "assets": [assets[0], {**assets[1], "size": 0}]}, False))
            for expression in expressions:
                for release, accepted in fixtures:
                    with self.subTest(workflow=filename, release=release):
                        self.assertEqual(self.evaluate(expression, release) == "true", accepted)


if __name__ == "__main__":
    unittest.main()
