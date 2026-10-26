"""Malformed issue forms should produce diagnostics without aborting the scan."""

from pathlib import Path
import json
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from validate_scaffold import validate_issue_forms, validate_markdown_issue_templates


def form():
    return {"name": "Synthetic report", "description": "Synthetic description",
            "body": [{"type": "input", "id": "summary",
                      "attributes": {"label": "Summary"}}]}


class IssueFormValidationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.directory = self.root / ".github/ISSUE_TEMPLATE"
        self.directory.mkdir(parents=True)

    def write_form(self, document, name="report.yml"):
        (self.directory / name).write_text(json.dumps(document), encoding="utf-8")

    def test_missing_required_labels_are_reported_without_key_errors(self):
        for field in ("name", "description"):
            with self.subTest(field=field):
                document = form()
                del document[field]
                self.write_form(document)
                problems = validate_issue_forms(self.root)
                self.assertTrue(any("name and description must be nonempty" in p for p in problems))

    def test_collection_input_types_are_rejected_without_type_errors(self):
        for value in ([], {}):
            with self.subTest(value=value):
                document = form()
                document["body"][0]["type"] = value
                self.write_form(document)
                self.assertTrue(any("supported input type" in p for p in validate_issue_forms(self.root)))

    def test_collection_checkbox_required_values_are_rejected(self):
        for value in ([], {}):
            with self.subTest(value=value):
                document = form()
                document["body"][0].update(type="checkboxes", attributes={
                    "label": "Consent", "options": [{"label": "Confirm", "required": value}]})
                self.write_form(document)
                self.assertTrue(any("nonempty checkbox list" in p for p in validate_issue_forms(self.root)))

    def test_collection_validation_required_values_are_rejected(self):
        for value in ([], {}):
            with self.subTest(value=value):
                document = form()
                document["body"][0]["validations"] = {"required": value}
                self.write_form(document)
                self.assertTrue(any("required must be a boolean" in p for p in validate_issue_forms(self.root)))

    def test_valid_boolean_requirements_remain_accepted(self):
        for required in (True, False):
            with self.subTest(required=required):
                document = form()
                document["body"][0].update(type="checkboxes", attributes={
                    "label": "Consent", "options": [{"label": "Confirm", "required": required}]},
                    validations={"required": required})
                self.write_form(document)
                self.assertEqual(validate_issue_forms(self.root), [])

    def test_nonstring_scalar_fields_are_rejected(self):
        for value in (True, False, 42, 1.5, None):
            for field in ("name", "description", "id", "label"):
                with self.subTest(value=value, field=field):
                    document = form()
                    if field in ("name", "description"):
                        document[field] = value
                    elif field == "id":
                        document["body"][0][field] = value
                    else:
                        document["body"][0]["attributes"][field] = value
                    self.write_form(document)
                    self.assertNotEqual(validate_issue_forms(self.root), [])

    def test_duplicate_dropdown_options_are_rejected(self):
        document = form()
        document["body"][0].update(type="dropdown", attributes={
            "label": "Choice", "options": ["Alpha", "Beta", "Alpha"]})
        self.write_form(document)
        self.assertTrue(any("options must be unique" in p
                            for p in validate_issue_forms(self.root)))

    def test_nonstring_dropdown_options_are_rejected(self):
        for value in (True, False, 42, 1.5, None, [], {}):
            with self.subTest(value=value):
                document = form()
                document["body"][0].update(type="dropdown", attributes={
                    "label": "Choice", "options": ["Alpha", value]})
                self.write_form(document)
                self.assertTrue(any("nonempty string list" in p
                                    for p in validate_issue_forms(self.root)))

    def test_distinct_quoted_boolean_choices_remain_strings(self):
        document = form()
        document["body"][0].update(type="dropdown", attributes={
            "label": "Choice", "options": ["true", "false", "42"]})
        self.write_form(document)
        self.assertEqual(validate_issue_forms(self.root), [])

    def test_nonboolean_required_values_are_rejected(self):
        for value in ("true", "false", 0, 1, None):
            for target in ("checkbox", "validation"):
                with self.subTest(value=value, target=target):
                    document = form()
                    item = document["body"][0]
                    if target == "checkbox":
                        item.update(type="checkboxes", attributes={
                            "label": "Consent", "options": [
                                {"label": "Confirm", "required": value}]})
                        expected = "nonempty checkbox list"
                    else:
                        item["validations"] = {"required": value}
                        expected = "required must be a boolean"
                    self.write_form(document)
                    self.assertTrue(any(expected in p for p in validate_issue_forms(self.root)))

    def test_duplicate_yaml_keys_remain_rejected(self):
        path = self.directory / "report.yml"
        path.write_text("name: First\nname: Second\ndescription: Report\nbody: []\n",
                        encoding="utf-8")
        self.assertTrue(any("found duplicate key" in p
                            for p in validate_issue_forms(self.root)))

    def test_legacy_frontmatter_preserves_scalar_types(self):
        path = self.directory / "legacy.md"
        for value, valid in (("true", False), ("42", False), ('"true"', True)):
            with self.subTest(value=value):
                path.write_text(f"---\nname: {value}\nabout: Report\n---\nDescribe the issue.\n",
                                encoding="utf-8")
                problems = validate_markdown_issue_templates(self.root)
                if valid:
                    self.assertEqual(problems, [])
                else:
                    self.assertTrue(any("values must be strings" in p for p in problems))

    def test_an_invalid_form_does_not_hide_diagnostics_from_other_forms(self):
        first = form()
        del first["name"]
        self.write_form(first, "first.yml")
        second = form()
        second["body"][0]["type"] = []
        self.write_form(second, "second.yml")
        problems = validate_issue_forms(self.root)
        self.assertEqual({p.split(":", 1)[0] for p in problems},
                         {".github/ISSUE_TEMPLATE/first.yml", ".github/ISSUE_TEMPLATE/second.yml"})


if __name__ == "__main__":
    unittest.main()
