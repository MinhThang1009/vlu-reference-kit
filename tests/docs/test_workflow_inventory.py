"""Compare Action discovery with parsed workflow structure, not source substrings."""

from pathlib import Path
import sys
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from sync_action_pins import (
    action_pin_matches, normalized_action_pin_part, normalized_uses_reference,
    workflow_uses_matches,
)


def parsed_uses(document):
    for job in document.get("jobs", {}).values():
        if "uses" in job:
            yield job["uses"]
        for step in job.get("steps", []):
            if "uses" in step:
                yield step["uses"]


class WorkflowInventoryTests(unittest.TestCase):
    def assert_inventory(self, text):
        expected = set(parsed_uses(yaml.load(text, Loader=yaml.BaseLoader)))
        references = {normalized_uses_reference(match) for match in workflow_uses_matches(text)}
        self.assertEqual(references, expected)
        pinned = {f"{normalized_action_pin_part(match, 'action')}@{normalized_action_pin_part(match, 'sha')}"
                  for match in action_pin_matches(text)}
        self.assertEqual(pinned, {value for value in expected if not value.startswith("./")})

    def test_plain_punctuation_keeps_real_steps_and_ignores_scalar_examples(self):
        reference = "actions/checkout@" + "a" * 40
        for opening, closing in (("{", "}"), ("[", "]")):
            for style in ("block", "inline", "multiline"):
                with self.subTest(opening=opening, style=style):
                    step = {
                        "block": f"      - uses: {reference}\n",
                        "inline": f"      - {{uses: {reference}}}\n",
                        "multiline": f"      - {{\n          uses: {reference}\n        }}\n",
                    }[style]
                    self.assert_inventory(
                        f"name: Review {opening}\njobs:\n  test:\n    steps:\n" + step
                        + f"      - name: Review {closing}\n        run: |\n"
                        "          uses: fixture/example@v1\n          echo [{\n")

    def test_nested_flow_nodes_and_anchored_nodes_keep_action_references(self):
        reference = "actions/checkout@" + "a" * 40
        for text in (
            f"jobs: {{test: {{steps: [{{uses: '{reference}'}}]}}}}\n",
            f"jobs:\n  test:\n    steps: [\n      {{uses: '{reference}'}}\n    ]\n",
            f"jobs:\n  test:\n    steps:\n      - &step {{uses: '{reference}'}}\n",
        ):
            with self.subTest(text=text):
                self.assert_inventory(text)

    def test_current_workflow_inventory_matches_the_yaml_parser(self):
        paths = sorted(path for path in (ROOT / ".github/workflows").iterdir()
                       if path.suffix in {".yml", ".yaml"})
        self.assertTrue(paths, "Workflow inventory must not be empty")
        for path in paths:
            with self.subTest(workflow=path.name):
                self.assert_inventory(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
