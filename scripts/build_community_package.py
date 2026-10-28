"""Đóng gói snapshot đã kiểm tra; chỉ thay ZIP cũ sau khi build thành công."""

from pathlib import Path
import hashlib
import os
import shutil
import stat
import sys
import tempfile
import zipfile

from validate_kit import MAX_FILE_BYTES, MAX_TOTAL_BYTES, inventory, validate_kit

PREFIX = "vlu-reference-kit-community/"


def require_valid(root: Path) -> None:
    errors = validate_kit(root)
    if errors:
        raise ValueError("Không đóng gói kit chưa đạt kiểm tra: " + "; ".join(errors))


def backup_existing_file(path: Path, backup: Path) -> bool:
    """Make a verified rollback copy before replacing a published output."""
    try:
        metadata = path.lstat()
    except FileNotFoundError:
        return False
    reparse = getattr(metadata, "st_file_attributes", 0) & getattr(
        stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400
    )
    if not stat.S_ISREG(metadata.st_mode) or stat.S_ISLNK(metadata.st_mode) or reparse:
        raise ValueError(f"Tệp đầu ra hiện có phải là tệp thường: {path.name}")
    original_digest = hashlib.sha256(path.read_bytes()).digest()
    shutil.copyfile(path, backup)
    if hashlib.sha256(backup.read_bytes()).digest() != original_digest:
        raise OSError(f"Không tạo được bản sao khôi phục hợp lệ: {path.name}")
    if hashlib.sha256(path.read_bytes()).digest() != original_digest:
        raise OSError(f"Tệp đầu ra thay đổi khi đang sao lưu: {path.name}")
    return True


def restore_output(path: Path, backup: Path, existed: bool) -> None:
    """Restore the previous output or remove a newly published partial file."""
    if existed:
        os.replace(backup, path)
    else:
        path.unlink(missing_ok=True)


def preserve_recovery_copy(
    source: Path, directory: Path, label: str, suffix: str
) -> Path:
    """Keep a verified backup outside the temporary build directory."""
    descriptor, name = tempfile.mkstemp(
        prefix=f".vlu-package-recovery-{label}-", suffix=suffix, dir=directory
    )
    os.close(descriptor)
    recovery = Path(name)
    try:
        expected = hashlib.sha256(source.read_bytes()).digest()
        shutil.copy2(source, recovery)
        if hashlib.sha256(recovery.read_bytes()).digest() != expected:
            raise OSError(f"Bản sao phục hồi không khớp: {source.name}")
    except OSError as cause:
        try:
            recovery.unlink(missing_ok=True)
        except OSError as cleanup_error:
            raise OSError(
                f"Recovery copy failed and partial file remains at {recovery}: {cleanup_error}"
            ) from cause
        raise
    return recovery


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
        published_checksum = destination.parent / checksum.name
        backup_zip = stage / "previous.zip"
        backup_checksum = stage / "previous.SHA256SUMS.txt"
        had_zip = backup_existing_file(destination, backup_zip)
        had_checksum = backup_existing_file(published_checksum, backup_checksum)
        checksum_removed = False
        zip_replaced = False
        try:
            # Two paths cannot be replaced as one filesystem operation. Remove
            # the stale checksum, then restore both prior files if publication fails.
            published_checksum.unlink(missing_ok=True)
            checksum_removed = True
            os.replace(pending, destination)
            zip_replaced = True
            os.replace(checksum, published_checksum)
        except OSError as publication_error:
            rollback_errors = []
            if checksum_removed:
                try:
                    published_checksum.unlink(missing_ok=True)
                except OSError as error:
                    rollback_errors.append(error)
            if zip_replaced:
                try:
                    restore_output(destination, backup_zip, had_zip)
                except OSError as error:
                    rollback_errors.append(error)
            if checksum_removed:
                try:
                    restore_output(published_checksum, backup_checksum, had_checksum)
                except OSError as error:
                    rollback_errors.append(error)
            if rollback_errors:
                details = "; ".join(str(error) for error in rollback_errors)
                recovery_paths = []
                recovery_errors = []
                for label, backup, suffix in (
                    ("zip", backup_zip, ".zip"),
                    ("checksum", backup_checksum, ".txt"),
                ):
                    try:
                        backup.lstat()
                    except FileNotFoundError:
                        continue
                    except OSError as error:
                        recovery_errors.append(str(error))
                        continue
                    try:
                        recovery = preserve_recovery_copy(
                            backup, destination.parent, label, suffix
                        )
                    except OSError as error:
                        recovery_errors.append(str(error))
                    else:
                        recovery_paths.append(recovery.name)
                message = (
                    "Không xuất bản được ZIP/checksum sau lỗi "
                    f"{publication_error}; rollback chưa hoàn tất: {details}"
                )
                if recovery_paths:
                    message += "; bản sao phục hồi được giữ tại: " + ", ".join(recovery_paths)
                if recovery_errors:
                    message += "; không lưu được một số bản sao phục hồi: " + "; ".join(
                        recovery_errors
                    )
                raise OSError(
                    message
                ) from publication_error
            raise
        return digest


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    destination = root / "dist/vlu-reference-kit-community.zip"
    digest = build_package(root / "kit", destination)
    print(f"Đã tạo {destination.name}; SHA-256 {digest}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
