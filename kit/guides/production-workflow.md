> Mọi đường dẫn trong đoạn mã tính từ gốc kit. Hồ sơ nguồn và trạng thái tệp ở `data/asset-sources.json`. Gói cộng đồng chỉ lưu metadata cho ảnh/logo/template chưa rõ quyền phân phối; các tệp đó không kèm trong ZIP này. Không coi đường dẫn tham chiếu là tệp đã được cung cấp.

# Quy trình tạo và hoàn thiện ảnh

Đây là hướng dẫn thực hành do bộ kit biên soạn, không phải quy chuẩn do VLU ban hành.

1. **Chốt yêu cầu hiện tại.** Xác định chủ đề, người xem, mục đích, đầu ra; không tự thêm thông tin sinh viên hoặc ràng buộc từ một bài tập cũ. Dùng prompts/brief-template.json nếu cần.
2. **Chọn tài nguyên.** Lấy thông tin nền từ data/brand-facts.json; chọn một vài ảnh đúng bối cảnh và logo phù hợp. Nêu chi tiết nào của ảnh cần giữ, chi tiết nào chỉ là tham khảo.
3. **Viết prompt.** Mô tả không gian, thời điểm, chủ thể/hành động, vật thể, ánh sáng, góc máy/bố cục, phong cách và tỷ lệ. Có thể tạo cảnh không có người. Các lựa chọn phải phục vụ yêu cầu mới.
4. **Tạo và điều chỉnh cảnh.** Kiểm tra tương tác, tư thế, tay/ngón tay, mặt, tỷ lệ, vật thể, phối cảnh, ánh sáng và số chủ thể. Sửa phần sai trước khi dàn chữ; ghi rõ phần giữ và phần đổi khi chỉnh ảnh.
5. **Biên tập chính xác.** Ghép logo gốc trong Canva, Photoshop, Illustrator, Inkscape hoặc công cụ phù hợp; giữ tỷ lệ. Dàn tên trường, tiêu đề, slogan và nội dung từ văn bản chính xác; không dựa vào chữ AI vẽ để thay artwork. Cài một bộ font static hoặc variable, tránh trùng font.
6. **Kiểm tra dữ kiện.** Đối chiếu mọi ngày, địa điểm sự kiện, tên đơn vị, số liệu, tài trợ và thông tin liên hệ với yêu cầu hiện tại. Không mặc định ảnh tham khảo là bằng chứng cho các dữ kiện mới.
7. **Xuất và xem lại.** Xem ở tỷ lệ 100% và kích thước người xem thực sự sử dụng; chữ rõ, không thiếu dấu, logo không bị kéo dãn/cắt, khoảng trống không bị tràn, không còn khung hoặc chữ giữ chỗ. Chọn PNG/JPEG/PDF, kích thước và hệ màu theo kênh đầu ra; chưa có CMYK/Pantone chính thức trong kit.
8. **Lưu bản sửa được.** Nếu cần tái sử dụng, lưu bản nguồn có lớp chữ/logo, ảnh xuất và prompt cuối; đặt tên theo yêu cầu dự án mới. Không có tên file hay mã sinh viên cố định trong bộ kit chung.

Ledger giữ metadata ba SVG tự biên soạn cho tỷ lệ 1:1, 4:5 và 9:16 trong assets/custom/templates/. Các SVG nhúng logo chưa rõ quyền không kèm trong gói cộng đồng; chỉ chỉnh sửa khi đã có file và quyền phù hợp, hoặc tự soạn bố cục mới rồi ghi rõ nguồn gốc. Khoảng đệm và kích thước trong các SVG là lựa chọn của mẫu, chưa phải khoảng bảo vệ/kích thước tối thiểu chính thức VLU.
