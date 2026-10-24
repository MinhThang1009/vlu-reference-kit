"""Đối soát policy, dependency trực tiếp và lockfile của công cụ tài liệu."""

from pathlib import Path
import re
import sys

from validate_kit import read_json
from verify_release import is_valid_release_version, validate_release_policy


def read_requirement_pins(path: Path, *, require_hashes: bool = False) -> dict[str, str]:
    """Đọc subset name==version của repo; cú pháp pip khác phải được review riêng."""
    pins: dict[str, str] = {}
    pending = ""
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        pending += " " + line.strip()
        if pending.endswith("\\"):
            pending = pending[:-1]
            continue
        logical = re.split(r"\s+#", pending, maxsplit=1)[0].strip()
        pending = ""
        if not logical or logical.startswith("#"):
            continue
        match = re.fullmatch(r"([A-Za-z0-9](?:[A-Za-z0-9._-]*[A-Za-z0-9])?)\s*==\s*([A-Za-z0-9][A-Za-z0-9.+!_-]*)(.*)", logical)
        if match is None:
            raise ValueError(f"{path.name}:{number}: chỉ hỗ trợ dependency ghim name==version.")
        name, version, options = match.groups()
        name = re.sub(r"[-_.]+", "-", name).lower()
        if name in pins:
            raise ValueError(f"{path.name}:{number}: dependency trùng sau chuẩn hóa: {name}")
        hashes = options.split()
        if any(re.fullmatch(r"--hash=sha256:[0-9a-f]{64}", value) is None for value in hashes):
            raise ValueError(f"{path.name}:{number}: tùy chọn hoặc hash không được hỗ trợ.")
        if require_hashes and not hashes:
            raise ValueError(f"{path.name}:{number}: dependency trong lock phải có hash SHA-256.")
        pins[name] = version
    if pending.strip():
        raise ValueError(f"{path.name}: dòng nối tiếp chưa kết thúc.")
    if not pins:
        raise ValueError(f"{path.name}: phải có ít nhất một dependency ghim.")
    return pins


def validate_tooling(root: Path) -> list[str]:
    policy = read_json(root / ".github/ci-toolchain.json")
    package = read_json(root / "package.json")
    lock = read_json(root / "package-lock.json")
    expected = {entry["package"]: entry["version"] for entry in policy["npm-tools"].values()}
    errors = []
    try:
        validate_release_policy(read_json(root / ".github/release-policy.json"))
    except ValueError as exc:
        errors.append(f"Policy phát hành không hợp lệ: {exc}")
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
    try:
        direct = read_requirement_pins(root / "requirements-docs.txt")
        locked = read_requirement_pins(root / "requirements-docs.lock", require_hashes=True)
    except ValueError as exc:
        errors.append(f"Dependency Python không hợp lệ: {exc}")
    else:
        if any(locked.get(name) != version for name, version in direct.items()):
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
    packages = release.get("packages")
    release_configs = [("root", release)]
    if (not isinstance(packages, dict) or set(packages) != {"."}
            or not isinstance(packages.get("."), dict)):
        errors.append('Release Please packages phải chỉ chứa object "." của kit.')
    else:
        # Release Please ưu tiên cấu hình theo path hơn giá trị root.
        release_configs.append(('packages["."]', {**release, **packages["."]}))
    for scope, effective in release_configs:
        if effective.get("release-type") != "simple" or effective.get("version-file") != "version.txt":
            errors.append(f"{scope}: Release Please phải quản lý phiên bản kit bằng version.txt, không dùng package tooling.")
        if effective.get("skip-github-release") is not False:
            errors.append(f"{scope}: Release Please phải bật tạo GitHub Release nháp bằng skip-github-release: false.")
        if effective.get("draft") is not True:
            errors.append(f"{scope}: Release Please phải dùng draft: true; công khai sau khi workflow kèm artifact.")
        if effective.get("force-tag-creation") is not True:
            errors.append(f"{scope}: Release Please phải dùng force-tag-creation: true để job tự động có thể kiểm tra tag và kèm asset cho draft.")
        if (effective.get("include-component-in-tag") is not False
                or effective.get("include-v-in-tag", True) is not True):
            errors.append(f"{scope}: Tag phải có dạng v<SemVer>, dùng include-component-in-tag: false và giữ include-v-in-tag: true.")
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
