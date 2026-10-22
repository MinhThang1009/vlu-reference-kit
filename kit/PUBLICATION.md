# Phạm vi bản công khai

Nguồn là bản cộng đồng 17/10/2026, SHA-256 `92ba7b3174c19b351a76e880e8844e55e4141a285610aa01a289c8446c9e4b17`. Không lấy tài nguyên từ ZIP nội bộ.

- Receipt của source community archive ghi nhận 45 tài nguyên được phép kèm theo: font/OFL, metadata vendor, swatch và mẫu chữ không nhúng artwork.
- 134 tài nguyên ảnh/logo/artwork/dẫn xuất chưa rõ quyền phân phối chỉ có metadata và liên kết nguồn.
- Lược địa chỉ máy trong hồ sơ đầu vào; đánh dấu các báo cáo kỹ thuật nhập từ ZIP là bằng chứng của bản nguồn, không phải kết quả CI của repository.
- Tính lại MANIFEST_SHA256.txt sau các điều chỉnh công khai. Kiểm tra bản hiện tại bằng `python scripts/validate_kit.py` từ gốc repository.

Đây là bộ tham chiếu do cộng đồng tổng hợp, không phải brandbook đầy đủ hoặc tài sản được VLU phê duyệt cho mọi mục đích. MIT cho phần tự biên soạn được kèm trong [LICENSE](LICENSE), có [thông báo phạm vi](NOTICE.md). Font và tài nguyên bên thứ ba giữ giấy phép riêng; xem [RIGHTS.md](RIGHTS.md).

Sổ nguồn hiện tại có 218 bản ghi: 46 bản ghi được kèm theo và 172 bản ghi bị loại. Receipt historical vẫn giữ số liệu source archive 45/134; đây là điều chỉnh metadata, không bổ sung artwork trường.

Audit nguồn 22/10/2026 bổ sung 38 hồ sơ qua các lượt đối soát, không bổ sung artwork trường vào Git hoặc ZIP công khai. Portfolio họa sĩ có phạm vi dự án và yêu cầu xin phép riêng. Xem [báo cáo mới](audit/asset-audit-2026-10-22.md).
