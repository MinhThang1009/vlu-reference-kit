"""Freshness issue copy must distinguish drift from upgrade advice."""

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from audit_freshness import markdown_report


class FreshnessReportTests(unittest.TestCase):
    def report(self, findings):
        return markdown_report({
            "checked-at": "2026-10-28T00:00:00+00:00",
            "status": "attention",
            "findings": findings,
            "errors": [],
            "action-dependencies": {"actions": []},
        })

    def test_action_dependency_difference_is_not_presented_as_upgrade_advice(self):
        report = self.report([{
            "kind": "action-dependency",
            "path": "actions/example",
            "subject": "fixture-package",
            "current": "3.0.0",
            "latest": "2.2.5",
            "details": "Declared lock differs from registry latest.",
        }])
        self.assertIn("differences from tracked references for review", report)
        self.assertIn("does not mean an update is available", report)
        self.assertIn("npm `latest` dist-tag", report)
        self.assertIn("not the GitHub Action release version", report)
        self.assertIn("may even be newer than that dist-tag", report)
        self.assertIn("Configured", report)
        self.assertIn("Reference", report)
        self.assertIn("3.0.0", report)
        self.assertIn("2.2.5", report)

    def test_issue_workflow_uses_a_review_title(self):
        workflow = (ROOT / ".github/workflows/freshness.yml").read_text(encoding="utf-8")
        self.assertIn("title='Review repository freshness findings'", workflow)
        self.assertNotIn("Repository freshness update required", workflow)
        self.assertIn("# Repository freshness review", workflow)

    def test_clean_report_says_no_differences_were_found(self):
        report = markdown_report({
            "checked-at": "2026-10-28T00:00:00+00:00",
            "status": "current",
            "findings": [],
            "errors": [],
            "action-dependencies": {"actions": []},
        })
        self.assertIn("No tracked differences were found", report)
        self.assertNotIn("No stale versioned inputs", report)


if __name__ == "__main__":
    unittest.main()
