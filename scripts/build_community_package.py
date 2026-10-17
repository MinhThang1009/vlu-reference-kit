"""Đóng gói bản cộng đồng đã kiểm tra; không lấy dữ liệu từ bản nội bộ."""

from pathlib import Path
import hashlib
import sys
import zipfile

from validate_kit import inventory, validate_kit


def build_package(kit_root: Path, destination: Path) -> str:
    errors = validate_kit(kit_root)
    if errors:
        raise ValueError("Không đóng gói kit chưa đạt kiểm tra: " + "; ".join(errors))
    files = inventory(kit_root)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for name, path in sorted(files.items()):
            entry = zipfile.ZipInfo("vlu-reference-kit-community/" + name, date_time=(1980, 1, 1, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o100644 << 16
            archive.writestr(entry, path.read_bytes())
    return hashlib.sha256(destination.read_bytes()).hexdigest()


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    destination = root / "dist/vlu-reference-kit-community.zip"
    digest = build_package(root / "kit", destination)
    (destination.parent / "SHA256SUMS.txt").write_text(digest + "  " + destination.name + "\n", encoding="utf-8")
    print(f"Đã tạo {destination.name}; SHA-256 {digest}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
