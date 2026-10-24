> Bản sao dùng trong repository cộng đồng. Xem [phạm vi nhập](PUBLICATION.md). Các đường dẫn trong ví dụ tính từ thư mục `kit/`.

# VLU Reference Kit

Bản audit nguồn 2026-10-24, biến thể **cộng đồng, không kèm artwork chưa rõ quyền**. Đây là bộ tham chiếu đa chủ đề do người dùng tổng hợp, chưa phải bộ nhận diện đầy đủ do VLU phát hành hoặc phê duyệt.

## Bắt đầu

Giải nén toàn bộ, mở [index.html](index.html) để tra cứu offline. Đọc [START_HERE.md](START_HERE.md), [quyền sử dụng](RIGHTS.md), [khoảng trống](audit/official-gaps.md) và chọn tư liệu theo [danh mục nguồn](data/asset-sources.json). Tên tệp gốc và đường dẫn cũ được lưu ở [bảng đối chiếu](audit/path-map.csv).

Gói này giữ metadata và liên kết nguồn cho 177 tài nguyên bị loại vì chưa rõ quyền phân phối. Chúng không có thumbnail hoặc artwork trong gói cộng đồng. Font kèm OFL, swatch và mẫu chữ không nhúng artwork vẫn được giữ.

## Quy ước tổ chức

- `assets/originals/`: tệp được nguồn cung cấp, gồm cả rendition; không tự xem là master.
- `assets/derived/`: preview, bản xuất, bảng màu, mẫu chữ; `assets/custom/`: mẫu tự biên soạn.
- `assets/fonts/`: font và tài liệu vendor; giữ nguyên basename TTF, OFL.txt, METADATA.pb và upstream_info.md.
- `data/`: dữ liệu dùng lại; `guides/`, `prompts/`: hướng dẫn và yêu cầu mẫu.
- `audit/`: checklist, thay đổi và mapping; `evidence/`: kiểm tra mới; `evidence/history/`: bằng chứng cũ nguyên byte.

Tên tự đặt dùng English lowercase-kebab-case. Ngoại lệ root: README.md, START_HERE.md, CHANGELOG.md, RIGHTS.md, PUBLICATION.md, LICENSE, NOTICE.md, MANIFEST_SHA256.txt; ngoại lệ vendor như trên. Không thêm ngày chụp hay phiên bản thiết kế chưa xác minh vào tên. Dùng đường dẫn tương đối cho liên kết nội bộ, POSIX `/` trong dữ liệu; tránh tên chỉ khác chữ hoa/thường, tên Windows dành riêng và ký tự cấm. Đây là quy ước kit, không phải quy định VLU.

Đã sửa hai tên preview QS Asia: artwork in 2025, không phải 2026. Không chỉnh artwork để ép khớp mốc CMS. Không đổi tên mục đã đạt quy ước ở các round sau.

## Audit nguồn mới

Lượt đầu 23/10 đối soát lại nguồn; các lượt mới bổ sung hồ sơ ảnh mobile-cover, check-in Tết và mặt tiền từ Commons, giữ giới hạn ngày/vị trí/quyền. Chưa có master hoặc quyền mới để kèm artwork. Đầu mối Scribd mang tiêu đề liên quan VLU chưa được chấp nhận làm brandbook; nguồn PDF gốc và phê duyệt chưa xác minh. Lượt đối soát metadata mới bổ sung kích thước raster cho 24 hồ sơ và 50 mục chỉ mục ảnh, không đổi byte hoặc quyền. Chi tiết từng lượt nằm trong báo cáo.

Lượt 24/10 bổ sung hồ sơ ảnh khai mạc Hội thao từ VLU, có hash, credit và giới hạn ngày/quyền; đây không phải mẫu đồng phục thể chất hoặc template được duyệt. Xem [báo cáo 24/10/2026](audit/asset-audit-2026-10-24.md). Ledger có 223 bản ghi, gồm 46 mục kèm file và 177 mục chỉ có metadata. Catalogue có 155 thẻ; 68 bản dẫn xuất bị loại vẫn có hồ sơ trong ledger để tránh lặp thẻ preview. Có thêm 17 ảnh bối cảnh/cơ sở vật chất, một ảnh bìa Facebook quan sát theo ngày, bảy tham chiếu portfolio họa sĩ, ba ảnh Điều dưỡng từ snapshot legacy của trang ngành, sáu ảnh bối cảnh Lab/MSC, hai bảng biểu trưng kỷ niệm 30 năm, hai ảnh bối cảnh Khoa Kỹ thuật Ô tô và một ảnh chi tiết Phòng thờ Quốc Tổ từ nguồn VLU. Có thêm một ảnh mobile-cover từ bài Mirae Map; vị trí theo bài, chưa xác minh độc lập. Có thêm hồ sơ ảnh check-in Tết theo bài VLU; áo dài trong ảnh là bối cảnh sự kiện, chưa xác nhận đồng phục. Có thêm hồ sơ ảnh mặt tiền từ Commons; giữ khai báo giấy phép và giới hạn quyền/ngày/EXIF, không gọi là tài sản chính thức. Byte 43 tài nguyên bổ sung được giữ riêng ngoài Git vì chưa có căn cứ quyền phân phối.

## Kiểm chứng và duy trì

### Bằng chứng nhập lịch sử (17/10/2026)

Đầu vào: VLU_Reference_Kit_2026-10-16.zip; SHA-256 `c487e113ee9a9b27c0e1c8148d5615b17c74de18775115ffc8b27f8ba31d94e7`; 226 tệp. Lượt nguồn 17/10/2026 kiểm tra 40 URL trang/CSS, đối chiếu byte 99 tệp nguyên bản (97 URL riêng biệt) và hai ảnh mới. Google trả trang xác minh/shell; nghiên cứu tiếp qua công cụ tìm kiếm web và nguồn trực tiếp, không tuyên bố đã duyệt đầy đủ kết quả Google.

Xem [báo cáo](audit/audit-report.md), [checklist](audit/checklist.csv), [QA](evidence/qa-report.json) và [kiểm tra đóng gói](evidence/package-verification.json). Dùng `python tools/verify-manifest.py` từ bản đã giải nén để kiểm tra hash; cần Python 3.12 trở lên, không cần cài thư viện. Công cụ được kiểm thử trên Python 3.12 và 3.15; catalogue HTML mở được mà không cần Python. Hash đúng không chứng minh tính chính thức hoặc quyền sử dụng.

Dùng lại dữ liệu ổn định theo nguồn/ngày đã ghi. Tra mới khi cần đồng phục mới nhất, cover đang dùng, quy định khoa, lịch, địa chỉ, lãnh đạo, tuyển sinh hoặc xếp hạng. Không mặc định hội sách, tên/mã sinh viên, số người, phong cách hay thời điểm cho ảnh mới.
