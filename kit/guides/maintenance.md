> Mọi đường dẫn trong đoạn mã tính từ gốc kit. Hồ sơ nguồn và trạng thái tệp ở `data/asset-sources.json`. Gói cộng đồng chỉ lưu metadata cho ảnh/logo/template chưa rõ quyền phân phối; các tệp đó không kèm trong ZIP này. Không coi đường dẫn tham chiếu là tệp đã được cung cấp.

# Duy trì bộ tham chiếu qua các lần sử dụng

Mốc chụp dữ liệu: 16/10/2026. Không cần tìm lại từ đầu logo, màu, font và ảnh đã có cho mỗi yêu cầu. Dùng tài nguyên tại chỗ và ngày/nguồn ghi trong hồ sơ.

| Loại dữ liệu | Cách dùng lại | Khi nào đối chiếu thêm |
| --- | --- | --- |
| Tệp logo gốc, font, bảng màu đã lưu | Dùng đúng tệp và giới hạn phiên bản | Có thông báo đổi nhận diện hoặc có artwork/brandbook mới được cung cấp |
| Slogan, giá trị, định hướng | Dùng thông tin có nguồn; phân biệt diễn giải và nguyên văn | Khi cần tuyên bố chính thức hiện hành hoặc trường công bố thay đổi |
| Ảnh không gian, trang phục, sự kiện | Dùng làm tư liệu tại thời điểm nguồn cung cấp | Khi cần mô tả chính xác hiện trạng, đồng phục bắt buộc hoặc sự kiện mới |
| Lịch, lãnh đạo, cơ cấu đơn vị, học phí, tuyển sinh, xếp hạng, số liệu | Không có giá trị mặc định trong kit | Xác minh cho từng yêu cầu có sử dụng dữ kiện đó |
| Template, prompt do bộ kit soạn | Chỉnh theo mục đích mới | Khi cần template chính thức hoặc thông số đầu ra khác |

## Khi bổ sung hoặc thay tài nguyên

1. Ưu tiên nguồn VLU và bản gốc; ghi source_url, source_page, retrieved_on, phiên bản/năm nguồn, tác giả nếu có. Không lưu toàn văn bài viết khi chỉ cần ảnh và chú giải.
2. Giữ bản gốc nguyên vẹn. Đặt bản xuất/cắt/chuyển đổi ở nhóm riêng; ghi derived_from và thao tác; không gắn nhãn artwork chính thức cho tệp tự dựng.
3. Nếu hai nguồn khác nhau, lưu riêng quan sát và ngày nguồn; chưa giải quyết được thì ghi rõ, không tự chọn một con số làm chuẩn. Ví dụ màu PNG tiếng Việt 2022 khác SVG website, và hai trường ngày của bài tốt nghiệp 2025 khác nhau.
4. Cập nhật data/asset-sources.json, data/reference-index.json, trang xem nhanh và CHANGELOG.md. Khi có brandbook gốc, đối chiếu từng mục trong audit/official-gaps.md trước khi đổi trạng thái.
5. Tính lại SHA-256 cho tài nguyên thay đổi và mọi tệp trong MANIFEST_SHA256.txt (trừ chính manifest); kiểm tra ZIP, ảnh, font, SVG/PDF, JSON, liên kết và hồ sơ nguồn. evidence/qa-report.json phải phản ánh lần kiểm tra thực tế.

## Kiểm tra tính toàn vẹn nhanh

Trong thư mục gốc đã giải nén, Linux/macOS có thể dùng `sha256sum -c MANIFEST_SHA256.txt` (macOS có thể cần công cụ tương đương). Trên Windows dùng công cụ SHA-256 hoặc Get-FileHash để đối chiếu từng tệp. Hash đúng xác nhận byte tệp khớp bản đóng gói, không tự xác nhận quyền sử dụng hay độ đầy đủ của thương hiệu.
