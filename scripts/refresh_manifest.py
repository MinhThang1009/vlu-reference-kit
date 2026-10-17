"""Tạo lại manifest sau thay đổi có chủ đích trong kit/."""

from pathlib import Path
import hashlib
import sys

from validate_kit import inventory


def refresh(root: Path) -> None:
    files = inventory(root)
    lines = [hashlib.sha256(path.read_bytes()).hexdigest() + "  " + name
             for name, path in sorted(files.items()) if name != "MANIFEST_SHA256.txt"]
    (root / "MANIFEST_SHA256.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    target = Path(__file__).resolve().parents[1] / "kit"
    refresh(target)
    print("Đã cập nhật manifest; chạy validate_kit.py để kiểm tra trước khi đóng gói.")
