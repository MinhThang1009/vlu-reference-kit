"""Đối soát policy, dependency trực tiếp và lockfile của công cụ tài liệu."""

from pathlib import Path
import re
import sys

from validate_kit import read_json
from verify_release import is_valid_release_version


def validate_tooling(root: Path) -> list[str]:
    policy = read_json(root / ".github/ci-toolchain.json")
    package = read_json(root / "package.json")
    lock = read_json(root / "package-lock.json")
    expected = {entry["package"]: entry["version"] for entry in policy["npm-tools"].values()}
    errors = []
    if package.get("devDependencies") != expected or lock["packages"][""].get("devDependencies") != expected:
        errors.append("Policy npm và dependency trực tiếp/lockfile không đồng bộ.")
    for name, version in expected.items():
        if lock["packages"].get("node_modules/" + name, {}).get("version") != version:
            errors.append(f"Lock npm sai phiên bản policy: {name}")
    for name, version in package.get("overrides", {}).items():
        matches = [entry for path, entry in lock["packages"].items()
                   if path.endswith("node_modules/" + name)]
        if not matches or any(entry.get("version") != version for entry in matches):
            errors.append(f"Override npm chưa được khóa: {name}")
    direct = dict(re.findall(r"(?m)^([\w.-]+)==([^\s\\]+)", (root / "requirements-docs.txt").read_text(encoding="utf-8")))
    locked = dict(re.findall(r"(?m)^([\w.-]+)==([^\s\\]+)", (root / "requirements-docs.lock").read_text(encoding="utf-8")))
    if not direct or any(locked.get(name) != version for name, version in direct.items()):
        errors.append("Dependency Python trực tiếp và lockfile không đồng bộ.")
    if (root / "LICENSE").read_bytes() != (root / "kit/LICENSE").read_bytes():
        errors.append("Thông báo MIT trong ZIP phải khớp LICENSE của repo.")
    release = read_json(root / "release-please-config.json")
    manifest = read_json(root / ".release-please-manifest.json")
    version = (root / "version.txt").read_text(encoding="utf-8").strip()
    if not is_valid_release_version(version):
        errors.append("version.txt phải chứa SemVer ASCII hợp lệ, không có tiền tố v.")
    initial_version = release.get("initial-version")
    if initial_version is not None and not is_valid_release_version(initial_version):
        errors.append("initial-version phải là SemVer ASCII hợp lệ.")
    if release.get("release-type") != "simple" or release.get("version-file") != "version.txt":
        errors.append("Release Please phải quản lý phiên bản kit bằng version.txt, không dùng package tooling.")
    if release.get("skip-github-release") is not True:
        errors.append("Release Please chỉ quản lý PR; phát hành artifact phải qua workflow riêng.")
    if not isinstance(manifest, dict) or set(manifest) - {"."}:
        errors.append("Manifest release chỉ được chứa package gốc của kit.")
    else:
        if "." in manifest and not is_valid_release_version(manifest["."]):
            errors.append("Phiên bản trong manifest phải là SemVer ASCII hợp lệ.")
        if version != manifest.get(".", initial_version):
            errors.append("version.txt và manifest/phiên bản đề xuất ban đầu không đồng bộ.")
    return errors


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    try:
        problems = validate_tooling(Path(__file__).resolve().parents[1])
    except (OSError, ValueError, KeyError, TypeError) as exc:
        problems = [f"Không đọc được policy/lockfile: {exc}"]
    print("\n".join(problems) if problems else "PASS: policy và lockfile đồng bộ.")
    raise SystemExit(bool(problems))
