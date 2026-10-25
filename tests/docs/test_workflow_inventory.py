"""Compare Action discovery with parsed workflow structure, not source substrings."""

from pathlib import Path
import json
import sys
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from sync_action_pins import (
    action_pin_matches, normalized_action_pin_part, normalized_uses_reference,
    auditable_action_repositories, workflow_uses_matches,
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

    def test_block_scalar_quotes_do_not_hide_real_or_promote_example_actions(self):
        reference = "actions/checkout@" + "a" * 40
        for style in ("|", "|-", "|+", ">", ">-", ">+"):
            for script in ('''echo 'note: "hello' ''', '''echo "note: 'hello" '''):
                with self.subTest(style=style, script=script):
                    self.assert_inventory(
                        "jobs:\n  test:\n    steps:\n      - run: " + style + "\n"
                        "          " + script + "\n          uses: fixture/fake@v1\n"
                        "      - uses: " + reference + "\n")

    def test_quoted_names_with_nested_colons_preserve_action_inventory(self):
        reference = "actions/checkout@" + "a" * 40
        for name in ('''"Doc: 'hello"''', "'Doc: \"hello'",
                     '''"Example\n  note: 'hello\n  end"''', "'Example\n  note: \"hello\n  end'"):
            with self.subTest(name=name):
                self.assert_inventory("name: " + name + "\njobs:\n  test:\n    steps:\n      - uses: " + reference + "\n")

    def test_block_like_text_inside_quotes_does_not_hide_real_actions(self):
        reference = "actions/checkout@" + "a" * 40
        for quote in ("'", '"'):
            for indentation in (0, 2, 4, 6):
                with self.subTest(quote=quote, indentation=indentation):
                    self.assert_inventory(
                        "jobs:\n  test:\n    name: " + quote + "Example\n"
                        + " " * indentation + "fake: |\n      end" + quote
                        + "\n    steps:\n      - uses: " + reference + "\n")

    def test_quotes_inside_plain_flow_scalars_do_not_hide_actions(self):
        reference = "actions/checkout@" + "a" * 40
        for name in ("O'Reilly", 'Build "fast', 'Two "quoted" words', "quote:inside'plain"):
            for style in ("root", "step", "multiline"):
                with self.subTest(name=name, style=style):
                    text = {
                        "root": "jobs: {test: {name: " + name + ", steps: [{uses: " + reference + "}]}}\n",
                        "step": "jobs:\n  test:\n    steps: [{name: " + name + ", uses: " + reference + "}]\n",
                        "multiline": "jobs:\n  test:\n    steps:\n      - {name: " + name + ",\n         uses: " + reference + "}\n",
                    }[style]
                    self.assert_inventory(text)

    def test_plain_flow_quotes_cannot_suppress_unpinned_rejection(self):
        for name in ("O'Reilly", 'Build "fast', "quote:inside'plain"):
            with self.subTest(name=name):
                text = "jobs: {test: {name: " + name + ", steps: [{uses: actions/checkout@v7}]}}\n"
                parsed = yaml.load(text, Loader=yaml.BaseLoader)
                self.assertEqual(set(parsed_uses(parsed)), {"actions/checkout@v7"})
                with self.assertRaisesRegex(ValueError, "not pinned"):
                    auditable_action_repositories(Path("fixture.yml"), text)

    def test_true_quoted_scalars_keep_embedded_action_examples_hidden(self):
        reference = "actions/checkout@" + "a" * 40
        example = 'It\'s an "example", {uses: fixture/fake@v1}'
        for value in (json.dumps(example), "'" + example.replace("'", "''") + "'"):
            with self.subTest(value=value):
                self.assert_inventory("jobs: {test: {steps: [{name: " + value + ", uses: " + reference + "}]}}\n")

    def test_emitted_quote_styles_preserve_the_action_inventory(self):
        reference = "actions/checkout@" + "a" * 40
        for name in ("O'Reilly", 'Build "fast', 'Two "quoted" words', "quote:inside'plain"):
            document = {"jobs": {"test": {"name": name, "steps": [{"uses": reference}]}}}
            for flow in (True, False):
                for style in (None, "'", '"'):
                    with self.subTest(name=name, flow=flow, style=style):
                        self.assert_inventory(yaml.safe_dump(
                            document, default_flow_style=flow, default_style=style, width=60))


if __name__ == "__main__":
    unittest.main()
