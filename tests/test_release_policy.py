"""Kiểm tra điều kiện từ chối phát hành trước mọi quyền ghi."""

from copy import deepcopy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from verify_release import verify_release


class ReleasePolicyTests(unittest.TestCase):
    def setUp(self):
        self.commit = "a" * 40
        self.policy = {"default_branch": "main", "required_checks": ["ci-success", "docs-contract"], "actions_app_id": 15368}
        self.ref = {"object": {"type": "tag", "sha": "b" * 40}}
        self.tag = {"object": {"type": "commit", "sha": self.commit}}
        self.comparison = {"merge_base_commit": {"sha": self.commit}}
        self.checks = {"total_count": 2, "check_runs": [
            {"name": name, "head_sha": self.commit, "status": "completed", "conclusion": "success",
             "app": {"id": 15368, "slug": "github-actions"}} for name in self.policy["required_checks"]]}
        self.statuses = {"total_count": 0, "statuses": []}

    def fetch(self, endpoint):
        if "/git/ref/tags/" in endpoint:
            return deepcopy(self.ref)
        if "/git/tags/" in endpoint:
            return deepcopy(self.tag)
        if "/compare/" in endpoint:
            return deepcopy(self.comparison)
        if "/check-runs?" in endpoint:
            return deepcopy(self.checks)
        if "/status?" in endpoint:
            return deepcopy(self.statuses)
        raise AssertionError("Unexpected endpoint: " + endpoint)

    def verify(self):
        verify_release("example/kit", "v0.1.0", self.commit, self.policy, self.fetch)

    def test_annotated_tag_and_successful_exact_sha_checks_pass(self):
        self.verify()

    def test_moved_tag_is_rejected(self):
        self.tag["object"]["sha"] = "c" * 40
        with self.assertRaisesRegex(ValueError, "Tag không trỏ"):
            self.verify()

    def test_dispatch_provenance_must_match_release_commit(self):
        with self.assertRaisesRegex(ValueError, "provenance"):
            verify_release("example/kit", "v0.1.0", self.commit, self.policy, self.fetch,
                           workflow_commit="c" * 40)

    def test_commit_outside_main_is_rejected(self):
        self.comparison["merge_base_commit"]["sha"] = "c" * 40
        with self.assertRaisesRegex(ValueError, "lịch sử main"):
            self.verify()

    def test_wrong_sha_provider_or_skipped_check_is_rejected(self):
        for field, value in [("head_sha", "c" * 40), ("app", {"id": 1, "slug": "github-actions"}),
                             ("conclusion", "skipped"), ("status", "in_progress")]:
            with self.subTest(field=field):
                original = deepcopy(self.checks)
                self.checks["check_runs"][0][field] = value
                with self.assertRaisesRegex(ValueError, "SHA/provider"):
                    self.verify()
                self.checks = original

    def test_missing_duplicate_or_truncated_checks_are_rejected(self):
        for change in ("missing", "duplicate", "truncated"):
            with self.subTest(change=change):
                original = deepcopy(self.checks)
                if change == "missing":
                    self.checks["check_runs"].pop()
                elif change == "duplicate":
                    self.checks["check_runs"].append(deepcopy(self.checks["check_runs"][0]))
                else:
                    self.checks["total_count"] = 101
                with self.assertRaises(ValueError):
                    self.verify()
                self.checks = original

    def test_legacy_status_name_collision_is_rejected(self):
        self.statuses = {"total_count": 1, "statuses": [{"context": "ci-success", "state": "success"}]}
        with self.assertRaisesRegex(ValueError, "legacy statuses"):
            self.verify()

    def test_unbounded_annotated_tag_chain_is_rejected(self):
        self.tag["object"] = deepcopy(self.ref["object"])
        with self.assertRaisesRegex(ValueError, "32 cấp"):
            self.verify()

    def test_invalid_inputs_are_rejected_before_network(self):
        for repository, tag, commit in [("../escape", "v0.1.0", self.commit),
                                        ("example/kit", "v$(command)", self.commit),
                                        ("example/kit", "v01.0.0", self.commit),
                                        ("example/kit", "v1.0.0-01", self.commit),
                                        ("example/kit", "v1.0.0-rc..1", self.commit),
                                        ("example/kit", "v0.1.0", "short")]:
            with self.subTest(repository=repository, tag=tag, commit=commit):
                with self.assertRaises(ValueError):
                    verify_release(repository, tag, commit, self.policy,
                                   lambda endpoint: self.fail("Unexpected network request"))


if __name__ == "__main__":
    unittest.main()
