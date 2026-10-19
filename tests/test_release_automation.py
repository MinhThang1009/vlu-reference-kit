"""Regression checks for draft Release asset automation."""

from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ReleaseAutomationTests(unittest.TestCase):
    def test_release_please_config_keeps_draft_tag_creation_enabled(self):
        config = json.loads((ROOT / "release-please-config.json").read_text(encoding="utf-8"))
        self.assertFalse(config["skip-github-release"])
        self.assertTrue(config["draft"])
        self.assertTrue(config["force-tag-creation"])
        self.assertIn("release", config["pull-request-title-pattern"])
        self.assertEqual(config["changelog-sections"][2]["section"], "Bug Fixes")

    def test_release_workflow_builds_and_attaches_only_verified_assets(self):
        workflow = (ROOT / ".github/workflows/release-please.yml").read_text(encoding="utf-8")
        required_fragments = (
            "id: release",
            "release_created: ${{ steps.release.outputs.release_created }}",
            "tag_name: ${{ steps.release.outputs.tag_name }}",
            "release_sha: ${{ steps.release.outputs.sha }}",
            "name: build-release-assets",
            "name: attest-release-assets",
            "name: attach-release-assets",
            "actions/upload-artifact@cf430e030ddbb5b0abf93d22962f4752f3646cd9",
            "actions/download-artifact@9000827ccba6bdab643e8b6fd33ac0654aef8333",
            "actions/attest@1e69f48acb82d1966a394da916b4c1698aa569d6",
            "gh release upload",
            "gh release edit",
            "--draft=false",
            "vlu-reference-kit-community.zip",
            "SHA256SUMS.txt",
            "contents: write",
        )
        for fragment in required_fragments:
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, workflow)
        self.assertIn("if: ${{ needs.release-pr.outputs.release_created == 'true' }}", workflow)
        self.assertIn("gh api --hostname github.com", workflow)
        self.assertIn("releases?per_page=100", workflow)
        self.assertIn("map(select(.tag_name == env.RELEASE_TAG))[0]", workflow)
        self.assertIn(".draft // false", workflow)
        self.assertEqual(workflow.count("(cd dist && sha256sum -c SHA256SUMS.txt)"), 2)

    def test_manual_release_supports_explicit_legacy_draft_backfill(self):
        workflow = (ROOT / ".github/workflows/release.yml").read_text(encoding="utf-8")
        self.assertIn("legacy_draft:", workflow)
        self.assertIn("RELEASE_WORKFLOW_COMMIT", workflow)
        self.assertIn("RELEASE_VERSION", workflow)

    def test_release_publication_verification_retries_eventual_consistency(self):
        workflows = (
            ROOT / ".github/workflows/release-please.yml",
            ROOT / ".github/workflows/release.yml",
        )
        for path in workflows:
            workflow = path.read_text(encoding="utf-8")
            with self.subTest(workflow=path.name):
                self.assertIn("for attempt in {1..30}; do", workflow)
                self.assertIn("sleep 2", workflow)
                self.assertIn("The Release was not published after verification retries.", workflow)
                self.assertIn('"vlu-reference-kit-community.zip" and .size > 0', workflow)
                self.assertIn('"SHA256SUMS.txt" and .size > 0', workflow)
        release_please = workflows[0].read_text(encoding="utf-8")
        manual_release = workflows[1].read_text(encoding="utf-8")
        self.assertIn("id: release_state", release_please)
        self.assertIn("releases/${RELEASE_ID}", release_please)
        self.assertIn("releases/${release_id}", manual_release)
        self.assertIn("[.id, .draft, .immutable]", manual_release)


if __name__ == "__main__":
    unittest.main()
