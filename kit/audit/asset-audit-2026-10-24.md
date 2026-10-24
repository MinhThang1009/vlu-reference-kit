# Fresh audit tài nguyên VLU, 24/10/2026

## Phạm vi và kết quả

Đầu vào branch `docs/vlu-tet-context-audit`, SHA `d216c30d0257a6fccf06233a1ab976dd1b5b0a4f`; main `a5aa604eae7f2687280569ce231f6500e3a2d26c`, PR #51 đang mở. Đóng băng 222 hồ sơ, 53 yêu cầu tự xây dựng và 133 tệp kit trước discovery; không nhập lại ZIP nội bộ. Đây là snapshot PR, chưa phải main đã merge.

Bổ sung một hồ sơ [ảnh khai mạc Hội thao Sinh viên Văn Lang](https://www.vlu.edu.vn/news/khai-mac-hoi-thao-sinh-vien-van-lang-2026-hon-2-500-van-dong-vien-san-sang-tranh-tai-1), metadata-only, để phân biệt ảnh hoạt động hội thao với hai ảnh cơ sở thể thao đã có. Không tạo artwork, không thêm byte ảnh vào Git/ZIP. Có **223 hồ sơ: 46 kèm file, 177 metadata-only/chờ đủ quyền; 74 hồ sơ ảnh và 155 thẻ catalogue**. Giữ nguyên 222 hồ sơ cũ, byte font/vendor/OFL và mọi đường dẫn cũ; thêm một dòng path-map. Không đóng khoảng trống nhận diện chính thức.

## Nguồn, chất lượng và quyền

JPEG gốc 6680 × 4453, 17.441.110 byte, SHA-256 `8f78b658d5d51dc9a3cd4d60ea563241228f2176587607211bf92f4c6091ac95`; giải mã và xem trực tiếp ở độ phân giải công cụ 1920 × 1280. Credit bài Lê Danh; quyền sở hữu và cấp phép từng ảnh chưa xác minh độc lập. Không cắt/nén/đổi artwork, không gán MIT. Chỉ có hồ sơ nguồn và link trong cộng đồng; byte giữ riêng chờ đủ quyền phân phối.

Ảnh lễ khai mạc Hội thao Sinh viên Văn Lang: nhóm người cầm cờ lưu niệm trước phông sân khấu. Chỉ tham chiếu bối cảnh sự kiện, không phải mẫu đồng phục thể chất, thiết kế banner trống hoặc quy chuẩn màu toàn trường. Ngày hiển thị 21/03/2026, sự kiện bài nêu 22/03/2026, published_date CMS 2026-03-21T17:00:00Z, publishedAt 25/03/2026 và EXIF DateTime giữ riêng; ngày chụp chưa xác nhận. Bài nêu các lượt kéo co tại Quảng trường Đông Sơn; địa điểm riêng của ảnh nhóm chưa được xác minh độc lập, không suy cơ sở/phòng từ ảnh.

## Nghiên cứu và đối soát

16 truy vấn mới, 68 URL kết quả duy nhất có mã, độ sâu review và disposition. 93 URL trang/CSS/giấy phép/PDF được yêu cầu trực tiếp, 76 tải đủ; 17 lỗi được ghi riêng. Snippet, trang cache, cuộc thi cũ hoặc blog đồng phục không xác nhận catalogue mới nhất. Bài áo dài Công đoàn và Hoa Khôi chỉ chứng minh ngữ cảnh tương ứng, không phải đồng phục bắt buộc của sinh viên. Không nhập mô tả supplier thành quy chuẩn VLU.

141 URL nguồn cũ tải lại, khớp 143 hồ sơ remote; 46 file local khớp hash. Thêm một URL ảnh mới, tổng 142 URL/144 hồ sơ remote khớp. Có byte đối chiếu cho 152/223 hồ sơ; 71 dẫn xuất lịch sử vẫn chỉ metadata, không tái tạo. 105 hồ sơ raster cũ và 73 chỉ mục ảnh cũ khớp kích thước/hash; ảnh mới bổ sung tương ứng. Hai trang MSC lần này tải đủ, các URL logo có trong HTML mới; không dùng kết quả này để tuyên bố đã xem PDF trong viewer. Lỗi truy cập ở lượt trước giữ phạm vi lịch sử, không coi là nội dung đã bị xóa.

Các nguồn VLU về nhận diện 2022, ba HEX 2024, giá trị cốt lõi, website/CSS, đồng phục theo hoạt động; portfolio tác giả, khai báo Commons và cover Facebook được đối chiếu theo phạm vi nguồn. Không suy CMYK/Pantone, master hoặc quyền phân phối từ ảnh/nguồn công khai.

## Kiểm tra bản bàn giao

89 test standard library, 17 test tài liệu, 15 test Node; validator kit/tooling/scaffold và Markdown lint 45 tệp đạt. Catalogue 155 thẻ đạt 25 ca tìm kiếm với DOM tổng hợp. Đối soát giữ nguyên toàn bộ 222 hồ sơ cũ, 73 ảnh chỉ mục cũ, 154 thẻ cũ, 268 dòng path-map cũ, byte 46 tài nguyên kèm và ID/domain/status của 53 yêu cầu. Kết quả được ghi trong evidence/asset-audit-2026-10-24.json. ZIP được build, giải nén và đối soát sau khi chốt receipt; digest giữ ngoài kit để tránh tự tham chiếu. Browser/SVG render, tương tác tour và mọi glyph/axis font chưa được xác minh đầy đủ. CI hoặc hash đúng không chứng minh hết bug, quyền phân phối hoặc đủ bộ nhận diện.

## Khoảng trống còn lại

Giữ 14 mục: BR-05; LG-03/04/05/06; CL-02/03; TY-04; ID-02; UN-08/09/10; CV-04; PK-09. Cần brandbook đầy đủ/hiện hành do VLU xác nhận; master logo/biến thể và quy tắc sử dụng; màu in ấn/bổ trợ; typography theo ấn phẩm; mascot/họa tiết/vector/3D/motion; catalogue/rập/thông số đồng phục theo khóa/khoa; template editable và quyền phân phối tương ứng. Đối chiếu tài liệu gốc, phiên bản và phạm vi trước khi đóng từng mục. PK-05 vẫn mở vì chưa kiểm render browser.

Xem từng yêu cầu và hồ sơ nguồn trong [bằng chứng](../evidence/asset-audit-2026-10-24.json), [checklist](checklist.json), [khoảng trống](official-gaps.md) và [ledger](../data/asset-sources.json). Checklist là danh mục tự xây dựng, không phải danh mục đầy đủ do VLU công bố. Không kết luận “đầy đủ 100%”.
