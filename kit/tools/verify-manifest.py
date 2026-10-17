from pathlib import Path, PurePosixPath
import hashlib
import re
import sys

root = Path(__file__).resolve().parents[1]
manifest = root / "MANIFEST_SHA256.txt"
errors = []
seen = set()
for number, line in enumerate(manifest.read_text(encoding="utf-8").splitlines(), 1):
    match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
    if not match:
        errors.append(f"Malformed manifest line: {number}")
        continue
    expected, name = match.groups()
    relative = PurePosixPath(name)
    if relative.is_absolute() or ".." in relative.parts or "\\" in name:
        errors.append(f"Unsafe path: {name}")
        continue
    target = root.joinpath(*relative.parts).resolve()
    if not target.is_relative_to(root.resolve()) or target.is_symlink():
        errors.append(f"Unsafe target: {name}")
        continue
    if name in seen:
        errors.append(f"Duplicate entry: {name}")
    seen.add(name)
    if not target.is_file():
        errors.append(f"Missing file: {name}")
    elif hashlib.sha256(target.read_bytes()).hexdigest() != expected:
        errors.append(f"Hash mismatch: {name}")
actual = {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file() and p != manifest}
errors.extend(f"Unlisted file: {name}" for name in sorted(actual - seen))
if errors:
    print("FAILED: " + str(len(errors)) + " issue(s)")
    print("\n".join(errors))
    sys.exit(1)
print(f"PASS: {len(seen)} files match the manifest.")
