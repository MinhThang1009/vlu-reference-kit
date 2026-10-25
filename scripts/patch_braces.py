"""Áp dụng giới hạn AST đã review cho parser braces 3.0.3 được khóa."""

from pathlib import Path
import hashlib
import os
import sys
import tempfile

from validate_kit import read_json, resolve_inside

UPSTREAM_SHA256 = "e572166565f15fa6ad9865ae49d678218e32aabfd1b3720f6d0d43d39800d310"
MAX_DEPTH = 100
GUARD = f"      if (stack.length > {MAX_DEPTH}) {{\n        throw new SyntaxError('VLU_BRACES_MAX_DEPTH: maximum AST nesting is {MAX_DEPTH}');\n      }}\n"


def guarded_source(source: bytes) -> bytes:
    text = source.decode("utf-8")
    for kind in ("CHAR_LEFT_PARENTHESES", "CHAR_LEFT_CURLY_BRACE"):
        marker = f"    if (value === {kind}) {{\n"
        if text.count(marker) != 1:
            raise ValueError("Không tìm thấy đúng parser branch đã review.")
        text = text.replace(marker, marker + GUARD, 1)
    return text.encode("utf-8")


def patch_dependencies(root: Path) -> int:
    packages = read_json(root / "package-lock.json")["packages"]
    targets = [name for name in packages if name.endswith("node_modules/braces")]
    if not targets:
        raise ValueError("Không còn braces trong lock; review để bỏ mitigation thay vì tự bỏ qua.")
    pending = []
    for name in targets:
        if packages[name].get("version") != "3.0.3":
            raise ValueError("Phiên bản braces đã đổi; cần review mitigation trước khi chạy lint.")
        package_path = resolve_inside(root, name + "/package.json")
        if read_json(package_path).get("version") != "3.0.3":
            raise ValueError("Phiên bản braces cài đặt không khớp lock.")
        target = resolve_inside(root, name + "/lib/parse.js")
        source = target.read_bytes()
        digest = hashlib.sha256(source).hexdigest()
        if digest == UPSTREAM_SHA256:
            pending.append((target, guarded_source(source)))
            continue
        # Chấp nhận đúng bản vá của repo, không dựa vào marker có thể xuất hiện
        # trong một bản nguồn khác chưa review.
        unpatched = source.replace(GUARD.encode("utf-8"), b"")
        if (source.count(GUARD.encode("utf-8")) != 2
                or hashlib.sha256(unpatched).hexdigest() != UPSTREAM_SHA256
                or guarded_source(unpatched) != source):
            raise ValueError("Hash parser braces không khớp upstream hoặc bản vá đã review.")
    for target, content in pending:
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(dir=target.parent, prefix=".braces-guard-", delete=False) as handle:
                temporary = Path(handle.name)
                handle.write(content)
            os.replace(temporary, target)
        finally:
            if temporary is not None and temporary.exists():
                temporary.unlink()
    return len(targets)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    try:
        count = patch_dependencies(Path(__file__).resolve().parents[1])
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"Không áp dụng được giới hạn braces: {exc}")
        raise SystemExit(1)
    print(f"PASS: {count} parser braces đã có giới hạn AST {MAX_DEPTH}.")
