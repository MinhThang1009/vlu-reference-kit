"""Đóng gói snapshot đã kiểm tra; chỉ thay ZIP cũ sau khi build thành công."""

from pathlib import Path
import hashlib
import os
import sys
import tempfile
import zipfile

from validate_kit import MAX_FILE_BYTES, MAX_TOTAL_BYTES, inventory, validate_kit

PREFIX = "vlu-reference-kit-community/"


def require_valid(root: Path) -> None:
    errors = validate_kit(root)
    if errors:
        raise ValueError("Không đóng gói kit chưa đạt kiểm tra: " + "; ".join(errors))


def build_package(kit_root: Path, destination: Path) -> str:
    if destination.suffix.lower() != ".zip":
        raise ValueError("Đầu ra phải là tệp .zip.")
    if destination.resolve().is_relative_to(kit_root.resolve()):
        raise ValueError("ZIP đầu ra phải nằm ngoài thư mục kit.")
    require_valid(kit_root)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".kit-build-", dir=destination.parent) as temporary:
        stage = Path(temporary)
        snapshot = stage / "snapshot"
        snapshot.mkdir()
        copied_bytes = 0
        for name, path in inventory(kit_root).items():
            target = snapshot / name
            target.parent.mkdir(parents=True, exist_ok=True)
            with path.open("rb") as source:
                content = source.read(MAX_FILE_BYTES + 1)
            if len(content) > MAX_FILE_BYTES:
                raise ValueError(f"Tệp thay đổi vượt giới hạn: {name}")
            copied_bytes += len(content)
            if copied_bytes > MAX_TOTAL_BYTES:
                raise ValueError("Snapshot vượt giới hạn tổng dung lượng.")
            target.write_bytes(content)
        require_valid(snapshot)
        pending = stage / destination.name
        files = inventory(snapshot)
        with zipfile.ZipFile(pending, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
            for name, path in sorted(files.items()):
                entry = zipfile.ZipInfo(PREFIX + name, date_time=(1980, 1, 1, 0, 0, 0))
                entry.compress_type = zipfile.ZIP_DEFLATED
                # Dùng metadata Unix thống nhất để checksum không phụ thuộc OS tạo ZIP.
                entry.create_system = 3
                entry.external_attr = 0o100644 << 16
                archive.writestr(entry, path.read_bytes())
        with zipfile.ZipFile(pending) as archive:
            if archive.testzip() is not None or set(archive.namelist()) != {PREFIX + name for name in files}:
                raise ValueError("ZIP không khớp snapshot đã kiểm tra.")
            for name, path in files.items():
                if archive.read(PREFIX + name) != path.read_bytes():
                    raise ValueError(f"Byte trong ZIP không khớp: {name}")
        digest = hashlib.sha256(pending.read_bytes()).hexdigest()
        checksum = stage / "SHA256SUMS.txt"
        checksum.write_text(digest + "  " + destination.name + "\n", encoding="utf-8", newline="\n")
        # Hai tệp không thể replace nguyên tử cùng lúc. Gỡ checksum cũ trước khi
        # đổi ZIP để một lần ngắt giữa chừng không để lại checksum của ZIP cũ.
        published_checksum = destination.parent / checksum.name
        published_checksum.unlink(missing_ok=True)
        os.replace(pending, destination)
        os.replace(checksum, published_checksum)
        return digest


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    destination = root / "dist/vlu-reference-kit-community.zip"
    digest = build_package(root / "kit", destination)
    print(f"Đã tạo {destination.name}; SHA-256 {digest}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
