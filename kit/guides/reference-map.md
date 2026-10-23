> Mọi đường dẫn trong đoạn mã tính từ gốc kit. Hồ sơ nguồn và trạng thái tệp ở `data/asset-sources.json`. Gói cộng đồng chỉ lưu metadata cho ảnh/logo/template chưa rõ quyền phân phối; các tệp đó không kèm trong ZIP này. Không coi đường dẫn tham chiếu là tệp đã được cung cấp.

# Chọn tư liệu theo bối cảnh

Tất cả đường dẫn dưới đây tính từ thư mục gốc kit. Có 71 hồ sơ ảnh được phân nhóm trong `data/reference-index.json`; ảnh chưa rõ quyền chỉ có metadata, không kèm file trong bản cộng đồng. Chọn ảnh theo chi tiết cần tham khảo; không cần đưa toàn bộ bộ kit vào mỗi lần tạo ảnh.

| Nhu cầu | Tệp nên xem | Giới hạn |
| --- | --- | --- |
| Nhận diện và chữ | assets/originals/logos/; assets/derived/palette/; assets/fonts/; data/brand-facts.json | Phân biệt tệp gốc, bản xuất và quan sát website; chưa có toàn bộ brandbook |
| Ngoại cảnh, khuôn viên | assets/originals/photos/campus/vlu-main-campus.jpg; assets/originals/photos/campus/vlu-garden.png | Trang cơ sở chính cung cấp; chưa xác nhận ngày chụp |
| Thư viện, tự học | assets/originals/photos/campus/vlu-library.jpg; assets/originals/photos/campus/vlu-study-hall.jpg; assets/originals/photos/learning/vlu-library-2025.jpg | Trang phục trong ảnh là quan sát, không phải quy định đồng phục |
| Họa thất, thiết kế | assets/originals/photos/arts/vlu-drawing-studio.jpg; assets/originals/photos/arts/vlu-product-workshop.jpg | Tham khảo bàn, dụng cụ và không gian; không gán tự động cho mọi ngành |
| Thời trang | assets/originals/photos/arts/vlu-fashion-workshop.jpeg | Xưởng được trang cơ sở chính giới thiệu; không suy diễn danh mục ngành hiện hành |
| Công nghệ | assets/originals/photos/technology/vlu-ar-vr-room.jpg; assets/originals/photos/technology/vlu-computer-lab.jpg | Giữ đúng loại không gian; không tự thêm thương hiệu thiết bị hay thông số |
| Thể thao | assets/originals/photos/sports/vlu-tennis.png; assets/originals/photos/sports/vlu-swimming-pool.jpg | Không tự biến cảnh tập luyện thành sự kiện thi đấu chính thức |
| Hội trường, sự kiện | assets/originals/photos/events/vlu-auditorium.png | Hội trường Trịnh Công Sơn theo trang nguồn; nội dung trên sân khấu thuộc ảnh gốc |
| Tốt nghiệp | assets/originals/photos/graduation/; assets/originals/uniforms/ceremony/ | Có toàn cảnh và ảnh tân khoa 2025–2026; không sao chép năm/ngày/slogan chương trình vào ảnh mới |
| Cộng đồng, tình nguyện | assets/originals/photos/community/vlu-community-mural-2025.png | Tư liệu 2025; không mặc định dùng tên chiến dịch, khẩu hiệu, con số cũ |
| Đọc sách, hội sách | assets/originals/photos/book-fair/vlu-book-fair-2024.jpg; assets/originals/photos/book-fair/vlu-book-fair-2025.jpg | Một chủ đề tùy chọn, không phải chủ đề mặc định |
| Trang phục | guides/uniforms.md; data/uniform-reference-index.json | Có ảnh gốc 2024–2026 theo bối cảnh; chưa có toàn bộ mẫu thiết kế mới nhất |
| Banner/ảnh đầu trang | guides/banners.md; data/banner-index.json; assets/originals/banners/website/ | 14 banner website, một cover K32 và một ảnh bìa Facebook quan sát 21/10, đối chiếu 23/10/2026; không bảo đảm ảnh bìa giữ nguyên sau đó |
| Nhận diện lịch sử, mascot | assets/originals/photos/historical-identity/vlu-mascots-2022.jpg; assets/originals/photos/identity/vlu-launch-event-2022.jpg; data/mascots-2022.json | Tư liệu công bố 2022; chưa có artwork rời, không xác nhận cơ cấu hiện hành |

Không có ảnh cụ thể cho mọi cơ sở, ngành học, phòng thí nghiệm y tế hay mọi loại sự kiện. Với bối cảnh chưa có, có thể tạo cảnh minh họa khái quát và mô tả đúng là minh họa; nếu phải tái hiện chính xác địa điểm/thiết bị thì cần bổ sung nguồn gốc phù hợp. Các đơn vị khác cùng hệ sinh thái không tự động dùng chung nhận diện của Trường Đại học Văn Lang.

Nguồn và hash của từng ảnh: data/asset-sources.json. Danh mục chú giải: data/reference-index.json. Mọi ảnh được giữ nguyên tệp tải từ nguồn, chưa cắt, nén lại hay xóa thông tin nguồn.

Ảnh trang phục Y/Điều dưỡng, quốc phòng và Nhà hàng–Khách sạn nằm trong assets/originals/uniforms/specialized; chỉ dùng theo bối cảnh của từng ảnh. Có hai bảng tổng hợp trong previews để xem nhanh, không phải bản vẽ thiết kế được trường ban hành.

Lab/Y khoa và nội thất MSC: tra `health_learning_references` và `campus_2_msc_references` trong `data/reference-map.json`. Phân biệt mô hình với bệnh nhân thật, khách THPT với sinh viên VLU; bài đăng năm 2026 không xác nhận năm chụp.

## Biểu trưng kỷ niệm 30 năm

Hai bảng GIF từ [bài công bố VLU](https://www.vlu.edu.vn/news/truong-dai-hoc-van-lang-cong-bo-bieu-trung-chinh-thuc-ky-niem-30-nam-thanh-lap-truong) có biến thể biểu trưng và cách ghép với logo, dùng làm tham chiếu cho bối cảnh kỷ niệm 1995–2025. Tra `anniversary_identity` trong `data/brand-facts.json`; mỗi GIF chỉ có một frame, không phải motion hoặc master chỉnh sửa được. Thông điệp của kỳ kỷ niệm không thay slogan chung; không mặc định dùng biểu trưng cho mọi ảnh. Gói cộng đồng chỉ có metadata, không kèm ảnh.

## Thực hành kỹ thuật ô tô

Tra `engineering_learning_references` trong `data/reference-map.json` để tham khảo hai góc kiểm tra xe. Bài nguồn xác định khu thực hành ô tô VLU, chưa xác minh cơ sở cụ thể hoặc ngày chụp. Trang phục là quan sát theo hoạt động, không phải catalogue đồng phục. PNG nguồn 1009 × 673, chưa xác nhận master in khổ lớn; gói cộng đồng chỉ có metadata.

## Di sản và Phòng thờ Quốc Tổ

Tra `heritage_references` trong `data/reference-map.json` khi đề bài liên quan di sản hoặc Phòng thờ Quốc Tổ. Ảnh nguồn là góc chi tiết, không tự là toàn cảnh hiện hành hoặc tài sản nhận diện. Không suy cơ sở, ngày chụp, vật liệu hoặc mã màu chuẩn từ ảnh. Basename ghi ngày quan sát; metadata năm 2020 và CMS có mốc riêng chưa phải ngày chụp đã xác nhận. Gói cộng đồng chỉ có hồ sơ nguồn, byte JPEG giữ riêng chờ xác minh quyền phân phối.

## Tour 360° trực tuyến

Tra `online_virtual_tour` trong `data/reference-map.json` và [phạm vi kiểm tra tour](campus.md). Hai trang VLU cùng dẫn tới một tour bên ngoài; đây là liên kết cần internet, chưa xác minh tương tác, ngày chụp từng cảnh hoặc quyền panorama, không phải tài nguyên offline được kèm gói.

## Bối cảnh ảnh của bài Mirae Map

Tra `campus_1_article_context_references` trong `data/reference-map.json`; đọc giới hạn ngày/vị trí ở ledger. Chỉ có metadata, không phải ảnh hiện trạng hoặc mẫu nhận diện được duyệt.
