"""Kiểm tra tính toàn vẹn và phạm vi phân phối của bản cộng đồng."""

from __future__ import annotations

import hashlib
import json
import os
import re
import stat
import sys
from pathlib import Path, PurePosixPath

MAX_FILES = 5000
MAX_FILE_BYTES = 16 * 1024 * 1024
MAX_TOTAL_BYTES = 128 * 1024 * 1024
ALLOWED_CLASSES = {
    "open_font_used_by_website",
    "open_font_upstream",
    "generated_palette_from_official_hex",
    "generated_font_specimen",
}
HOST_PATH = re.compile(r"(?i)\b[a-z]:[\\/]+(?:users|documents and settings)[\\/]")


def resolve_inside(root: Path, name: str) -> Path:
    """Chỉ chấp nhận đường dẫn tương đối POSIX không qua link/junction."""
    relative = PurePosixPath(name)
    if not name or relative.is_absolute() or ".." in relative.parts or "\\" in name or ":" in name:
        raise ValueError(f"Đường dẫn không an toàn: {name!r}")
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink() or current.is_junction():
            raise ValueError(f"Không theo link/junction: {name!r}")
    if not current.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"Đường dẫn vượt phạm vi: {name!r}")
    return current


def inventory(root: Path) -> dict[str, Path]:
    root = root.absolute()
    if root.is_symlink() or root.is_junction() or not root.is_dir():
        raise ValueError("Thư mục kit phải tồn tại và không phải link/junction.")
    result: dict[str, Path] = {}
    total = 0
    folded: set[str] = set()
    for parent, directories, filenames in os.walk(root, followlinks=False):
        for name in directories:
            resolve_inside(root, (Path(parent) / name).relative_to(root).as_posix())
        for filename in filenames:
            relative = (Path(parent) / filename).relative_to(root).as_posix()
            path = resolve_inside(root, relative)
            metadata = path.stat()
            if not stat.S_ISREG(metadata.st_mode):
                raise ValueError(f"Chỉ nhận tệp thông thường: {relative}")
            size = metadata.st_size
            total += size
            if size > MAX_FILE_BYTES or total > MAX_TOTAL_BYTES or len(result) >= MAX_FILES:
                raise ValueError("Kit vượt giới hạn kích thước hoặc số tệp của bộ kiểm tra.")
            if relative.casefold() in folded:
                raise ValueError(f"Tên xung đột chữ hoa/thường: {relative}")
            folded.add(relative.casefold())
            result[relative] = path
    return result


def unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"JSON có key trùng: {key}")
        result[key] = value
    return result


def read_json(path: Path) -> object:
    def reject_constant(value: str) -> object:
        raise ValueError(f"JSON có số không hợp lệ: {value}")

    return json.loads(path.read_text(encoding="utf-8-sig"), object_pairs_hook=unique_object,
                      parse_constant=reject_constant)


def validate_manifest(root: Path, files: dict[str, Path]) -> list[str]:
    errors: list[str] = []
    manifest = files.get("MANIFEST_SHA256.txt")
    if manifest is None:
        return ["Thiếu MANIFEST_SHA256.txt"]
    seen: set[str] = set()
    for line in manifest.read_text(encoding="utf-8").splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        if match is None:
            errors.append("Dòng manifest sai định dạng.")
            continue
        expected, name = match.groups()
        try:
            path = resolve_inside(root, name)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        if name in seen or name == "MANIFEST_SHA256.txt":
            errors.append(f"Manifest trùng hoặc tự tham chiếu: {name}")
        seen.add(name)
        if name not in files or not path.is_file():
            errors.append(f"Manifest trỏ tệp không tồn tại: {name}")
        elif hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            errors.append(f"Hash không khớp: {name}")
    errors.extend(f"Tệp chưa có trong manifest: {name}" for name in sorted(set(files) - seen - {"MANIFEST_SHA256.txt"}))
    return errors


def validate_assets(root: Path, files: dict[str, Path]) -> list[str]:
    errors: list[str] = []
    try:
        ledger = read_json(root / "data/asset-sources.json")
    except (OSError, ValueError, RecursionError) as exc:
        return [f"Không đọc được sổ nguồn: {exc}"]
    if not isinstance(ledger, list):
        return ["Sổ nguồn phải là danh sách."]
    seen: set[str] = set()
    for row in ledger:
        if not isinstance(row, dict) or not isinstance(row.get("file"), str):
            errors.append("Mục nguồn phải có đường dẫn file.")
            continue
        name = row["file"]
        try:
            path = resolve_inside(root, name)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        if name in seen:
            errors.append(f"Tài nguyên trùng: {name}")
        seen.add(name)
        included = row.get("included_in_package")
        if not isinstance(included, bool):
            errors.append(f"included_in_package phải là boolean: {name}")
        elif included:
            classification = row.get("classification")
            if not isinstance(classification, str) or classification not in ALLOWED_CLASSES:
                errors.append(f"Tài nguyên chưa thuộc phạm vi phân phối cộng đồng: {name}")
            if name not in files:
                errors.append(f"Thiếu tài nguyên được công bố kèm theo: {name}")
            elif hashlib.sha256(path.read_bytes()).hexdigest() != row.get("sha256"):
                errors.append(f"Hash sổ nguồn không khớp: {name}")
            if path.suffix.lower() == ".ttf" and not (path.parent / "OFL.txt").is_file():
                errors.append(f"Font thiếu OFL.txt cùng thư mục: {name}")
        elif name in files:
            errors.append(f"Tài nguyên đã loại vẫn xuất hiện: {name}")
    errors.extend(f"Tài nguyên chưa có hồ sơ nguồn: {name}" for name in files if name.startswith("assets/") and name not in seen)
    return errors


def validate_kit(root: Path) -> list[str]:
    try:
        files = inventory(root)
    except (OSError, ValueError) as exc:
        return [str(exc)]
    try:
        errors = validate_manifest(root, files) + validate_assets(root, files)
    except (OSError, UnicodeError) as exc:
        return [f"Không đọc được manifest/tài nguyên: {exc}"]
    for name in ("LICENSE", "NOTICE.md"):
        if name not in files:
            errors.append(f"Thiếu thông báo giấy phép: {name}")
    for name, path in files.items():
        if path.suffix.lower() not in {".json", ".md", ".txt", ".html", ".css", ".py", ".pb", ".gpl", ".svg"}:
            continue
        try:
            text = path.read_text(encoding="utf-8-sig")
            if "\ufffd" in text:
                errors.append(f"Ký tự thay thế Unicode: {name}")
            if HOST_PATH.search(text):
                errors.append(f"Đường dẫn máy cá nhân còn trong bản công khai: {name}")
            if path.suffix == ".json":
                read_json(path)
        except (OSError, UnicodeError, ValueError, RecursionError) as exc:
            errors.append(f"Không đọc/parse được {name}: {exc}")
    return errors


def main() -> int:
    root = Path(__file__).resolve().parents[1] / "kit"
    errors = validate_kit(root)
    if errors:
        print("FAILED: " + str(len(errors)) + " lỗi")
        print("\n".join(errors))
        return 1
    print(f"PASS: {len(inventory(root))} tệp kit khớp manifest và phạm vi bản cộng đồng.")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
