> Mọi đường dẫn trong đoạn mã tính từ gốc kit. Hồ sơ nguồn và trạng thái tệp ở `data/asset-sources.json`. Gói cộng đồng chỉ lưu metadata cho ảnh/logo/template chưa rõ quyền phân phối; các tệp đó không kèm trong ZIP này. Không coi đường dẫn tham chiếu là tệp đã được cung cấp.

# Dùng bộ kit cho mọi chủ đề tạo ảnh VLU

Mục tiêu: giảm việc tìm lại tài sản đã kiểm chứng khi tạo ảnh sinh viên, học tập, hội sách, cắm trại, hoạt động câu lạc bộ, truyền thông sự kiện hoặc không gian trường. Không mặc định mọi chủ đề đều là hội sách.

| Tình huống | Tệp ưu tiên | Phạm vi cần nhớ |
| --- | --- | --- |
| Sinh viên mặc áo VLU | `assets/originals/photos/uniforms/vlu-polo-and-brand-items-2024.jpg` + `assets/originals/uniforms/vlu-student-polo-navy-observed-2026.jpg` | Mẫu polo xanh đậm quan sát được; không gán là catalogue mới nhất toàn trường |
| Y khoa/Điều dưỡng | `assets/originals/uniforms/specialized/vlu-medicine-white-coat-front-k31-2025.jpg`, `assets/originals/uniforms/specialized/vlu-nursing-white-uniform-k30-2025.jpg` | Hai bối cảnh khác nhau; chọn đúng ngành, không gộp thành một mẫu blouse |
| Tốt nghiệp | Hai ảnh trong `assets/originals/uniforms/ceremony/`; `assets/originals/photos/ceremony/vlu-graduation-stage-2026.jpg` | Ảnh tân khoa 2026, chưa đủ mọi văn bằng; vòng hoa/dải vinh danh theo người trong ảnh không tự là bắt buộc |
| Học quốc phòng | `assets/originals/uniforms/specialized/vlu-national-defence-green-tshirt-context-2026.jpg` | Áo cổ tròn xanh trong workshop K31/2026; ảnh có biển BETU, không dùng làm campus chính VLU |
| Nhà hàng–Khách sạn | `assets/originals/uniforms/specialized/vlu-hospitality-suits-source-2026.png`, `assets/originals/photos/uniforms/vlu-culinary-practice-2026.png` | Chọn vest/cà vạt hoặc trang phục bếp theo vai trò; năm nguồn không xác nhận mẫu mới nhất |
| Cắm trại/ngoại khóa | Hai ảnh polo trên nếu cần; `assets/derived/palette/vlu-verified-colors.json`; ảnh sân vườn cho tinh thần trẻ trung | Lều và địa điểm ngoài trường là bối cảnh sáng tạo; không tuyên bố đó là cơ sở VLU hoặc sự kiện có thật |
| Học nhóm/thư viện | `assets/originals/photos/learning/vlu-library-2025.jpg`, `assets/originals/photos/campus/vlu-library.jpg` | Giữ đặc điểm không gian khi cần tái hiện; tránh bê thông tin sự kiện từ ảnh gốc |
| Giảng đường | `assets/originals/photos/student-life/vlu-lecture-hall-activity-2026.jpg` | Màn hình trong ảnh có nội dung chương trình cũ |
| Khuôn viên | `assets/originals/photos/campus/vlu-main-campus-enrollment-source-2026.jpg`, `assets/originals/photos/campus/vlu-main-campus.jpg` | Không đồng nhất năm bài viết với năm chụp ảnh |
| Hội sách | Ảnh hội sách 2024–2025 | Dùng cho hoạt động và cách bố trí; không chép ưu đãi/ngày cũ |
| Tuyển sinh/truyền thông | `data/banner-index.json` | Có banner desktop và mobile; kiểm tra nội dung có năm/khóa/xếp hạng |
| Mascot | `assets/originals/photos/historical-identity/vlu-mascots-2022.jpg`, `data/mascots-2022.json` | Tham chiếu công bố 2022; không giả lập artwork rời chính thức |
| Dàn chữ và logo | `assets/originals/logos/`, `assets/derived/exports/`, `assets/fonts/` | Chèn artwork gốc khi hoàn thiện; kiểm tra dấu tiếng Việt |

Chỉ cần đính kèm 2–4 ảnh phù hợp cho mỗi yêu cầu: một ảnh trang phục, một ảnh không gian, một logo và thêm ảnh phong cách nếu cần. Số lượng này là gợi ý thao tác của bộ kit, không phải yêu cầu VLU. Nếu công cụ không đọc được ZIP, giải nén và đính kèm đúng các tệp đó cùng nội dung prompts/vlu-branding.txt.

Màu nền/mảng đồ họa có thể dùng #D72134, #1F2251, #FFFFFF theo nguồn chính thức. Không ép ảnh chụp, màu vải hoặc tệp logo lịch sử khớp tuyệt đối ba mã này. Không dùng hình chim khác, logo VLSC/VGS hay nhận diện Tập đoàn thay cho logo VLU khi đề bài chỉ yêu cầu Trường Đại học Văn Lang.

Các chi tiết phải kiểm tra sau tạo ảnh: đúng logo và tên trường; dấu tiếng Việt; vị trí logo trên áo; hình thể/tay/ngón tay; số người; thông tin khóa/ngày/nội dung mới. Phần chữ và logo nên được chèn từ tệp gốc ở bước hoàn thiện. Không coi ảnh minh họa AI là ảnh trường công bố.

Dữ liệu có thời hạn cần tra lại khi đề bài đòi hỏi tính hiện hành: đồng phục mới nhất, cover đang dùng, logo phiên bản mới, quy định khoa, xếp hạng, lịch sự kiện, địa chỉ và số liệu tuyển sinh. Các ảnh/tệp đã lưu vẫn dùng được làm tham khảo theo ngày nguồn.

Các nhóm nghệ thuật, công nghệ, thể thao và cộng đồng được giữ trong guides/reference-map.md. Chúng có cùng phạm vi tham chiếu, không phải mặc định chủ đề.

## Nguồn đã mở rộng ngày 22/10/2026

- Tra [ảnh cơ sở và hoạt động](../data/reference-index.json) cho HUB, media studio, canteen, lớp học, phòng y tế, thực hành Răng Hàm Mặt và Du lịch. Ngày chụp chưa được xác nhận.
- [Ảnh bìa Facebook](../data/facebook-cover-observation.json) chỉ được xác nhận theo lần quan sát; không lấy xếp hạng trong artwork làm kết luận hiện hành độc lập.
- [Portfolio mascot](../data/mascot-source-observations.json) gồm hình minh họa và ảnh ứng dụng của tác giả; không thay master vector/3D hoặc cơ cấu khối ngành hiện tại.

Các file mới chỉ có hồ sơ trong bản cộng đồng. Dùng `source_page` để đối chiếu và xác định quyền; không coi đường dẫn trong ledger là file đã kèm khi `included_in_package` là false. Ảnh biểu diễn có trang phục xanh không được dùng làm quy chuẩn GDQP.

Xem `data/uniform-reference-index.json` để chọn ảnh theo snapshot. Hai payload trang ngành Điều dưỡng được ghi nhận ngày 22/10/2026: legacy lúc 04:49 UTC chứa ba ảnh thực hành; new lúc 09:24 UTC và các lần 10:08–10:13 UTC chứa lại hai URL ban đầu. Tên field/vị trí ảnh là quan sát theo snapshot, không xác nhận việc ngừng dùng vĩnh viễn hoặc đổi thiết kế đồng phục. Ảnh lễ K30 có chi tiết xanh ở vai, không phải viền hồng tím. Màu quan sát không thay mã màu vải và ảnh không xác nhận ngày đổi thiết kế.

## Lab và trung tâm mô phỏng y khoa

Sáu hồ sơ nguồn mới nằm trong `health_learning_references` của `data/reference-map.json`: Giải phẫu, hai hoạt động học sinh THPT trải nghiệm và ba ảnh MSC. Không dùng áo của khách THPT làm đồng phục VLU. Chú thích bài về chức năng quan sát không chứng minh ảnh chụp lúc chấm thi; không gán danh tính/vai trò từng người. Ba ảnh Lab không tự xác định được cơ sở; ba ảnh MSC dùng phạm vi Cơ sở 2 theo bài nguồn. Gói cộng đồng chỉ có hồ sơ, chưa kèm byte ảnh.

## Biểu trưng kỷ niệm 30 năm

Hai bảng GIF từ [bài công bố VLU](https://www.vlu.edu.vn/news/truong-dai-hoc-van-lang-cong-bo-bieu-trung-chinh-thuc-ky-niem-30-nam-thanh-lap-truong) có biến thể biểu trưng và cách ghép với logo, dùng làm tham chiếu cho bối cảnh kỷ niệm 1995–2025. Tra `anniversary_identity` trong `data/brand-facts.json`; mỗi GIF chỉ có một frame, không phải motion hoặc master chỉnh sửa được. Thông điệp của kỳ kỷ niệm không thay slogan chung; không mặc định dùng biểu trưng cho mọi ảnh. Gói cộng đồng chỉ có metadata, không kèm ảnh.

## Kỹ thuật và phục vụ cộng đồng

Hai hồ sơ trong `assets/originals/photos/engineering/` từ [bài VLU](https://www.vlu.edu.vn/news/khoa-ky-thuat-o-to-van-lang-to-chuc-chuong-trinh-mien-phi-bao-duong-o-to-xe-may-cho-cong-dong) bổ sung góc khoang hành khách và khoang động cơ ô tô. Chọn nguồn qua `data/reference-index.json` và `data/reference-map.json`. Không suy quy trình an toàn, vai trò từng người, cơ sở cụ thể hoặc thông số đồng phục từ ảnh. Ngày bài đăng 15/06/2026 và ngày sự kiện bài nêu 13/06/2026 không tự là ngày chụp. Giữ nguyên ảnh nguồn ngoài Git; chưa xác minh quyền phân phối.

## Tư liệu di sản

Tra `heritage_references` trong `data/reference-map.json` khi đề bài liên quan di sản hoặc Phòng thờ Quốc Tổ. Ảnh nguồn là góc chi tiết, không tự là toàn cảnh hiện hành hoặc tài sản nhận diện. Không suy cơ sở, ngày chụp, vật liệu hoặc mã màu chuẩn từ ảnh. Basename ghi ngày quan sát; metadata năm 2020 và CMS có mốc riêng chưa phải ngày chụp đã xác nhận. Gói cộng đồng chỉ có hồ sơ nguồn, byte JPEG giữ riêng chờ xác minh quyền phân phối.

## Tour 360° trực tuyến

Tra `online_virtual_tour` trong `data/reference-map.json` và [phạm vi kiểm tra tour](campus.md). Hai trang VLU cùng dẫn tới một tour bên ngoài; đây là liên kết cần internet, chưa xác minh tương tác, ngày chụp từng cảnh hoặc quyền panorama, không phải tài nguyên offline được kèm gói.
