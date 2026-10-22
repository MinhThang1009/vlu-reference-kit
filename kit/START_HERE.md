# Bắt đầu dùng bộ tham chiếu

1. Đọc README.md và RIGHTS.md; mở index.html từ thư mục đã giải nén.
2. Lấy nền VLU ở data/brand-facts.json và prompts/vlu-branding.txt.
3. Chọn ảnh đúng ngữ cảnh theo data/reference-index.json, trang phục theo data/uniform-reference-index.json và banner theo data/banner-index.json. Kiểm tra included_in_package trong data/asset-sources.json trước khi tìm tệp.
4. Điền prompts/brief-template.json; không coi các ví dụ là quy chuẩn trường.
5. Khi hoàn thiện ảnh, ghép artwork gốc có quyền sử dụng và dàn chữ đúng dấu tiếng Việt. Không yêu cầu AI tái tạo chính xác logo bằng trí nhớ.

Thông tin ổn định được dùng lại theo ngày nguồn. Thông tin biến động hoặc yêu cầu “mới nhất/hiện hành” phải đối chiếu mới. Những gì chưa có bằng chứng vẫn ở audit/official-gaps.md; không tự điền để đạt “100%”.

## Nguồn bổ sung ngày 22/10/2026

Đọc [báo cáo](audit/asset-audit-2026-10-22.md), [ảnh bìa theo thời điểm](data/facebook-cover-observation.json) và [portfolio mascot](data/mascot-source-observations.json). Đây là metadata của nguồn, không phải file ảnh được phép phân phối trong gói. Kiểm tra `included_in_package` và quyền của từng mục trước khi tìm file hoặc tái sử dụng.
