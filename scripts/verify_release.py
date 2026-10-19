"""Ràng buộc tag phát hành với commit main và CI thành công từ GitHub Actions."""

from pathlib import Path
import json
import os
import re
import subprocess
import sys
from urllib.parse import quote

from validate_kit import read_json


def is_valid_release_version(value: object) -> bool:
    """SemVer 2.0.0 với giới hạn 127 ký tự để tag có tiền tố v tối đa 128."""
    if not isinstance(value, str) or len(value) > 127:
        return False
    number = r"(?:0|[1-9][0-9]*)"
    prerelease = r"(?:0|[1-9][0-9]*|[0-9]*[A-Za-z-][0-9A-Za-z-]*)"
    build = r"[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*"
    return re.fullmatch(
        rf"{number}\.{number}\.{number}(?:-{prerelease}(?:\.{prerelease})*)?(?:\+{build})?", value
    ) is not None


def github_json(endpoint: str) -> object:
    result = subprocess.run(["gh", "api", "--hostname", "github.com", endpoint],
                            check=True, capture_output=True, encoding="utf-8", timeout=30)
    if len(result.stdout) > 8 * 1024 * 1024:
        raise ValueError("Phản hồi GitHub vượt giới hạn.")
    return json.loads(result.stdout)


def validate_release_policy(policy: object) -> None:
    """Không cho policy sai cấu trúc vô hiệu hóa bước đối chiếu CI."""
    if not isinstance(policy, dict):
        raise ValueError("Release policy phải là object.")
    branch = policy.get("default_branch")
    if not isinstance(branch, str) or not branch.strip():
        raise ValueError("Release policy cần default_branch không rỗng.")
    checks = policy.get("required_checks")
    if (not isinstance(checks, list) or not checks
            or any(not isinstance(name, str) or not name.strip() for name in checks)
            or len(set(checks)) != len(checks)):
        raise ValueError("Release policy cần required_checks là danh sách tên không rỗng, không trùng.")
    app_id = policy.get("actions_app_id")
    if type(app_id) is not int or app_id <= 0:
        raise ValueError("Release policy cần actions_app_id là số nguyên dương.")


def verify_release(repository: str, tag: str, commit: str, policy: dict, fetch=github_json,
                   workflow_commit: str | None = None) -> None:
    validate_release_policy(policy)
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9-]*/[A-Za-z0-9_][A-Za-z0-9_.-]*", repository):
        raise ValueError("Repository phải có dạng owner/repo.")
    if not tag.startswith("v") or not is_valid_release_version(tag[1:]):
        raise ValueError("Tag phải có dạng vMAJOR.MINOR.PATCH, có thể thêm prerelease/build.")
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("Cần SHA-1 commit đầy đủ, chữ thường.")
    if workflow_commit is not None and workflow_commit != commit:
        raise ValueError("SHA workflow dispatch phải khớp commit phát hành để provenance cùng nguồn.")
    prefix = f"repos/{repository}"
    ref = fetch(prefix + "/git/ref/tags/" + quote(tag, safe=""))
    target = ref["object"]
    for _ in range(32):
        if target["type"] == "commit":
            break
        if target["type"] != "tag" or not re.fullmatch(r"[0-9a-f]{40}", target["sha"]):
            raise ValueError("Tag không trỏ tới đối tượng Git hợp lệ.")
        target = fetch(prefix + "/git/tags/" + target["sha"])["object"]
    else:
        raise ValueError("Tag lồng quá 32 cấp.")
    if target["sha"] != commit:
        raise ValueError("Tag không trỏ đến commit đã chỉ định.")
    comparison = fetch(prefix + "/compare/" + commit + "..." + quote(policy["default_branch"], safe=""))
    if comparison["merge_base_commit"]["sha"] != commit:
        raise ValueError("Commit chưa thuộc lịch sử main hiện tại.")
    response = fetch(prefix + "/commits/" + commit + "/check-runs?filter=latest&per_page=100")
    if response["total_count"] > 100:
        raise ValueError("Quá 100 check runs, cần review thủ công thay vì bỏ sót phân trang.")
    for name in policy["required_checks"]:
        matches = [run for run in response["check_runs"] if run["name"] == name]
        if not matches or len({run["id"] for run in matches}) != len(matches):
            raise ValueError(f"Thiếu hoặc trùng check: {name}")
        if any(run["head_sha"] != commit or run["app"]["id"] != policy["actions_app_id"]
               or run["app"]["slug"] != "github-actions" for run in matches):
            raise ValueError(f"Check chưa đạt trên đúng SHA/provider: {name}")
        # API có thể giữ nhiều check suites cho cùng SHA khi PR được sửa/rerun.
        # Chỉ lần mới nhất quyết định; không dùng lần xanh cũ để vượt lần đang chạy.
        run = max(matches, key=lambda candidate: candidate["id"])
        if run["status"] != "completed" or run["conclusion"] != "success":
            raise ValueError(f"Check chưa đạt trên đúng SHA/provider: {name}")
    statuses = fetch(prefix + "/commits/" + commit + "/status?per_page=100")
    if statuses["total_count"] > 100:
        raise ValueError("Quá 100 commit statuses, cần review thủ công.")
    if any(status["context"] in policy["required_checks"] for status in statuses["statuses"]):
        raise ValueError("Tên required check đồng thời xuất hiện trong legacy statuses, cần phân xử.")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    try:
        config = read_json(Path(__file__).resolve().parents[1] / ".github/release-policy.json")
        version = os.environ.get("RELEASE_VERSION")
        if version is None:
            version = (Path(__file__).resolve().parents[1] / "version.txt").read_text(encoding="utf-8").strip()
        if os.environ["RELEASE_TAG"] != "v" + version:
            raise ValueError("Tag phải khớp version.txt của commit phát hành.")
        workflow_commit = os.environ.get("RELEASE_WORKFLOW_COMMIT") or os.environ["GITHUB_SHA"]
        verify_release(os.environ["GITHUB_REPOSITORY"], os.environ["RELEASE_TAG"],
                       os.environ["RELEASE_COMMIT_SHA"], config, workflow_commit=workflow_commit)
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        print(f"Không đủ điều kiện release: {exc}")
        raise SystemExit(1)
    print("PASS: tag, main và CI khớp commit phát hành.")
