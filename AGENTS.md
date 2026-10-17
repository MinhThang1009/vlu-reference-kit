# Hướng dẫn cho agent

## Phạm vi

Repo này chỉ chứa bản cộng đồng của VLU Reference Kit. Không thêm ZIP nội bộ, ảnh/logo/artwork chưa rõ quyền phân phối hoặc dữ liệu của máy cá nhân.

## Quy ước

- Tài liệu hướng tới người dùng dùng tiếng Việt; giữ nguyên tiếng Anh cho mã định danh, công cụ upstream và văn bản pháp lý canonical chưa có bản dịch tương ứng.
- Giữ byte font/vendor và OFL. Lưu nguồn, phạm vi, ngày kiểm tra, giấy phép và trạng thái included_in_package cho tài nguyên.
- Không tự dựng quy chuẩn VLU hoặc khẳng định đã đủ 100% bộ nhận diện. Kết quả audit nguồn không thay kết quả kiểm tra repository hiện tại.
- Sau thay đổi trong kit/, tính lại manifest rồi chạy `python scripts/validate_kit.py`, `python -m unittest discover -s tests -v`, `python scripts/validate_scaffold.py --repository-root .` và `python scripts/ci_toolchain.py run-markdownlint`.
- Không commit, push, tạo release hoặc sửa cài đặt GitHub nếu người dùng chưa cho phép. Giữ thay đổi ngoài phạm vi và không ghi đè công việc của người khác.

## Pull request

Dùng template phù hợp; có thể chuẩn bị bằng `python scripts/pr_template_preflight.py --title "<title>"`. Viết body UTF-8 và chỉ tick mục đã thực hiện. Người duy trì review trước khi merge; không có cam kết thời gian xử lý.
