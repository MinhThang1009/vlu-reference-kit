> Mọi đường dẫn trong đoạn mã tính từ gốc kit. Hồ sơ nguồn và trạng thái tệp ở `data/asset-sources.json`. Gói cộng đồng chỉ lưu metadata cho ảnh/logo/template chưa rõ quyền phân phối; các tệp đó không kèm trong ZIP này. Không coi đường dẫn tham chiếu là tệp đã được cung cấp.

# Font tham khảo theo website VLU

`assets/fonts/website-static/` có 26 TTF đúng các đường dẫn CSS của website: IBM Plex Sans 100–700 × normal/italic (14 tệp); Plus Jakarta Sans 200–700 × normal/italic (12 tệp). Hai thư mục họ font còn có 4 bản variable từ Google Fonts (normal/italic mỗi họ), metadata, thông tin upstream và giấy phép. Không xem quan sát website là xác nhận font nhận diện bắt buộc cho mọi ấn phẩm hoặc font chữ trong logo.

Cài bộ static hoặc bộ variable, tránh trùng tên. Giữ OFL.txt khi phân phối lại; bản sao giấy phép cũng có trong mỗi thư mục static. Các tệp font gốc không bị chỉnh sửa.

Mẫu trung tính: **Đại học Văn Lang · Tri thức và sáng tạo · 0123456789**. Đây là câu thử font, không phải slogan bổ sung của trường. Không có tên/mã sinh viên hoặc chủ đề mặc định.

assets/derived/specimens/vietnamese-specimen.png xem hai họ font chính. assets/derived/specimens/all-fonts-specimen-1.png và assets/derived/specimens/all-fonts-specimen-2.png hiển thị đủ 30 TTF, dạng NFC và NFD. evidence/history/vietnamese-validation-scope.json liệt kê tập ký tự; evidence/history/font-checks.json ghi kết quả cho từng TTF. Đã kiểm tra toàn bộ nguyên âm có dấu và Đ/đ chữ hoa/thường trong tập thử. Vẫn xem lại trong ứng dụng dàn chữ thực tế vì lựa chọn font và xử lý dấu có thể khác.


Receipt nguồn ngày 17/10/2026 ghi việc dựng hai bảng toàn bộ 30 font bằng Chromium shaping; đây là bằng chứng lịch sử, không phải lần render browser mới. Lượt đối chiếu 22/10 xác nhận lại byte font và mẫu chữ không đổi. Các font variable dùng instance mặc định; không phải kiểm tra mọi tổ hợp trục. Stylesheet có 39 @font-face tổng cộng; 26 static TTF trong kit thuộc hai họ tham chiếu, không phải toàn bộ font website.
