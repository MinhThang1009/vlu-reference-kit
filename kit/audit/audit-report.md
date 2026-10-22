# Fresh audit VLU, 2026-10-17

Đầu vào có **226 tệp**, SHA-256 `c487e113ee9a9b27c0e1c8148d5615b17c74de18775115ffc8b27f8ba31d94e7`. Bản đầu vào giữ nguyên. Audit giới hạn ở toàn bộ tệp được cung cấp và các nguồn công khai đã liệt kê; không truy cập kho nội bộ VLU, không có danh mục chính thức xác nhận đầy đủ.

## Kết quả nội dung

Giữ nguyên 99 nguyên bản có URL sau khi tải đối chiếu: 99/99 khớp SHA-256. Đối soát 37 thư mục suy ra từ ZIP ở folder-map.json. Ba HEX, tên, slogan năm 2022 và giá trị cốt lõi được kiểm tra lại từ nguồn VLU. Bộ ảnh trang phục là quan sát theo bối cảnh, chưa phải catalogue được duyệt. Có 41 ảnh bối cảnh sau khi thêm hai ảnh thực hành Điều dưỡng, ngày chụp chưa xác nhận; 14 banner trang chủ và một cover K32 có thời hạn. Website font không tự là typography bắt buộc của mọi ấn phẩm.

## Sửa và bổ sung

- Sửa tên hai preview ghi QS Asia 2026 thành 2025-artwork, giữ nguyên byte. Ảnh nguồn in 2025 dù CMS có mốc 2026; không dùng mốc này để xác nhận thứ hạng hiện tại.
- Gỡ khẳng định trang IAST xác nhận bổ sung bộ ba giá trị cốt lõi, vì dữ liệu tải mới không có bộ ba; about-us vẫn là bằng chứng trực tiếp.
- Thêm hai ảnh rendition từ trang Điều dưỡng. Đính chính 22/10/2026: ảnh lễ K30 cũng có chi tiết xanh ở vai; mô tả hồng tím trước đó sai. Phân biệt bối cảnh lễ/thực hành, không suy có hai mẫu thiết kế khác nhau.
- Chuẩn hóa tên/vị trí, đồng bộ tham chiếu, bảng đường dẫn cũ–mới, catalogue offline và công cụ kiểm tra manifest đa nền tảng. Giữ ngoại lệ basename font/vendor.
- Tách gói nội bộ và cộng đồng; gói cộng đồng bỏ 134 tài nguyên artwork/dẫn xuất chưa rõ quyền phân phối nhưng giữ metadata. Bằng chứng lịch sử giữ nguyên byte và đánh dấu không áp dụng như kết quả round này.

- Sửa lỗi verifier đầu vào báo Unlisted file sai trên Windows vì dấu phân cách đường dẫn; bổ sung kiểm tra hồi quy. Sửa tham chiếu RECHECK_ROUND2 không có trong ZIP.

## Độ phủ và bằng chứng

Checklist có 53 yêu cầu độc lập, mỗi mục thuộc một domain và có trạng thái; xem checklist.json/csv. Tám candidate: sáu xác nhận và sửa, hai loại sau kiểm tra (nghi viền đỏ polo và HTTP 200 của tên miền đỗ). Không còn candidate lỗi/dữ liệu chưa phân xử; đầu mối tìm kiếm chưa kiểm chứng được ghi riêng trong research-log.json; các khoảng trống tài liệu chính thức vẫn công khai ở official-gaps.md.

Đã kiểm tra 40 URL trang/CSS và 99 tệp nguyên bản (97 URL riêng biệt); nguồn bổ sung Điều dưỡng có hai URL rendition riêng. Google trực tiếp không trả kết quả đọc được; các truy vấn web chỉ phục vụ tìm đầu mối và không chứng minh tìm kiếm toàn bộ Internet. Hai lần tải trang mission-vision timeout; nguồn about-us đủ cho phần diễn giải nền. Các lỗi 403/shell/Page not found được giữ trong source-verification.json.

## Kiểm tra và giới hạn

Các receipt ../evidence/qa-report.json và ../evidence/package-verification.json ghi nhận source community archive trước khi nhập repository, nên các denominator 45/113/112 trong đó là số liệu historical. Kiểm tra hiện tại dùng scripts/validate_kit.py và CI; kit hiện tại có 116 tệp và manifest có 115 mục. Phạm vi receipt gồm giải mã ảnh, render SVG/PDF, cmap NFC/NFD và mẫu font, JSON/UTF-8, đường dẫn, loại tài nguyên gói cộng đồng, manifest và tái giải nén ZIP. Xem phạm vi kiểm tra trực quan riêng; không suy kiểm tra kỹ thuật thành xác nhận nhận diện chính thức.

Kết luận: bộ tham chiếu được chuẩn hóa và có bằng chứng cập nhật; **chưa đủ căn cứ xác nhận 100% bộ nhận diện chính thức hoặc catalogue đồng phục mới nhất**. Cần tài liệu gốc được VLU xác nhận cho các mục còn mở. Không gửi yêu cầu, công bố hoặc sử dụng tài khoản bên ngoài.
