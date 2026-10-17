> Mọi đường dẫn trong đoạn mã tính từ gốc kit. Hồ sơ nguồn và trạng thái tệp ở `data/asset-sources.json`. Gói cộng đồng chỉ lưu metadata cho ảnh/logo/template chưa rõ quyền phân phối; các tệp đó không kèm trong ZIP này. Không coi đường dẫn tham chiếu là tệp đã được cung cấp.

# Nguồn và cách ghi nhận tài nguyên

data/asset-sources.json ghi nguồn tải, trang chứa tài nguyên, tác giả khi nguồn công bố, ngày lấy, hash và phân loại. data/reference-index.json cung cấp chú giải theo bối cảnh.

| Nhóm | Tình trạng |
| --- | --- |
| Logo, favicon, ảnh VLU | Tệp gốc từ nguồn công khai của VLU; nguồn đã xem không kèm giấy phép tái sử dụng rộng rãi. Quyền đối với thương hiệu, ảnh và người xuất hiện không được chuyển giao bởi bộ ZIP này. |
| Font | Giữ nguyên font và giấy phép SIL OFL đi kèm từng họ; xem OFL.txt để áp dụng điều khoản. |
| PNG/PDF xuất từ SVG, swatch | Bản chuyển đổi hoặc tệp tiện dụng có nguồn; vẫn phân biệt với master/tệp do trường phát hành. |
| Prompt, hướng dẫn, bố cục custom | Tài liệu tham khảo được biên soạn cho bộ kit; không phải quy chuẩn chính thức VLU. |

Khi cần ghi nguồn ảnh, lấy đúng tác giả/trang tương ứng trong danh mục, không gán toàn bộ ảnh cho một tác giả. Ảnh có người thật được dùng ở đây làm tư liệu bối cảnh; không tự mô tả họ là nhân vật của sự kiện mới. Với sản phẩm công bố chính thức hoặc khai thác thương mại, xác định quyền và quy trình duyệt theo phạm vi sử dụng thực tế.
