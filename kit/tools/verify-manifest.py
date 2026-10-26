from __future__ import annotations

from pathlib import Path, PurePosixPath
import hashlib
import os
import re
import sys


def checked_target(root: Path, name: str) -> Path:
    relative = PurePosixPath(name)
    if (not relative.parts or relative.is_absolute() or ".." in relative.parts
            or "\\" in name or ":" in name or relative.as_posix() != name):
        raise ValueError(f"Unsafe path: {name}")
    target = root
    for part in relative.parts:
        target = target / part
        # Kiểm tra từng thành phần trước resolve để không làm mất dấu link.
        if target.is_symlink() or target.is_junction():
            raise ValueError(f"Unsafe target: {name}")
    if not target.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"Unsafe target: {name}")
    return target


def verify(root: Path) -> tuple[list[str], int]:
    errors = []
    seen = set()
    if root.is_symlink() or root.is_junction() or not root.is_dir():
        return ["Unsafe or missing kit root"], 0
    try:
        manifest = checked_target(root, "MANIFEST_SHA256.txt")
        lines = manifest.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError, ValueError) as exc:
        return [f"Cannot read manifest: {exc}"], 0
    for number, line in enumerate(lines, 1):
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        if not match:
            errors.append(f"Malformed manifest line: {number}")
            continue
        expected, name = match.groups()
        try:
            target = checked_target(root, name)
            if name in seen or name == "MANIFEST_SHA256.txt":
                errors.append(f"Duplicate or self-referencing entry: {name}")
            seen.add(name)
            if not target.is_file():
                errors.append(f"Missing file: {name}")
            elif hashlib.sha256(target.read_bytes()).hexdigest() != expected:
                errors.append(f"Hash mismatch: {name}")
        except (OSError, ValueError) as exc:
            errors.append(f"Cannot verify {name}: {exc}")

    def walk_error(error: OSError) -> None:
        errors.append(f"Cannot inventory kit: {error}")

    actual = set()
    for parent, directories, filenames in os.walk(root, followlinks=False, onerror=walk_error):
        for directory in directories[:]:
            name = (Path(parent) / directory).relative_to(root).as_posix()
            try:
                checked_target(root, name)
            except (OSError, ValueError) as exc:
                errors.append(str(exc))
                directories.remove(directory)
        for filename in filenames:
            name = (Path(parent) / filename).relative_to(root).as_posix()
            try:
                checked_target(root, name)
            except (OSError, ValueError) as exc:
                errors.append(str(exc))
            if name != "MANIFEST_SHA256.txt":
                actual.add(name)
    errors.extend(f"Unlisted file: {name}" for name in sorted(actual - seen))
    # Kiểm tra cả chiều ngược lại để alias filesystem không tạo thêm mục hợp lệ.
    errors.extend(f"Manifest path not in file inventory: {name}" for name in sorted(seen - actual))
    return errors, len(seen)


def main() -> int:
    if sys.version_info < (3, 12):
        print("FAILED: Python 3.12 or newer is required. Upgrade Python, then rerun this verifier.")
        return 2
    errors, count = verify(Path(__file__).absolute().parents[1])
    if errors:
        print("FAILED: " + str(len(errors)) + " issue(s)")
        print("\n".join(errors))
        return 1
    print(f"PASS: {count} files match the manifest.")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
