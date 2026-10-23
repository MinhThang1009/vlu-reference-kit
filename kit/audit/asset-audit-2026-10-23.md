# Audit nguồn tài nguyên VLU, 23/10/2026

## Kết quả mới nhất: bối cảnh Tết (followup_round16)

Đầu vào `main` tại `a5aa604eae7f2687280569ce231f6500e3a2d26c`, sau merge PR #48/#50. Kiểm kê trước sửa: 220 hồ sơ, 133 tệp kit và 53 yêu cầu tự xây dựng. Bổ sung một ảnh check-in Tết từ [bài VLU](https://www.vlu.edu.vn/news/sinh-vien-quoc-te-tim-hieu-va-trai-nghiem-van-hoa-ngay-tet-tai-van-lang-cung-the-ultimate-tet-quest), JPEG 3969 × 2646, credit Hữu Tài theo bài. Đã tải, giải mã và xem trực tiếp; giữ nguyên byte ngoài Git vì chưa xác minh quyền phân phối. Không xác nhận danh tính/quốc tịch từng người, cơ sở cụ thể, đồng phục hoặc template được duyệt. Ngày hiển thị 28/01/2026, sự kiện bài nêu 29/01/2026, CMS và EXIF giữ riêng; `capture_date=null`.

Hiện có **221 hồ sơ: 46 kèm file, 175 metadata-only; 72 hồ sơ ảnh và 153 thẻ catalogue**. Giữ nguyên 220 hồ sơ cũ và byte font/vendor/OFL; chỉ thêm một dòng path-map, không đổi tên/di chuyển. Sửa số 170 tài nguyên bị loại và ngày audit cũ ở phần giới thiệu README cho khớp hiện trạng. Các lượt bên dưới là lịch sử, có phạm vi riêng.

Tìm mới 20 truy vấn, 44 URL kết quả có mức review/disposition; 67 request trang/CSS/PDF, 55 tải đủ. Tải lại 139 URL nguồn cũ khớp 141 hồ sơ remote, 46 file local; một nguồn mới bổ sung bằng chứng byte cho tổng 150/221 hồ sơ. 71 dẫn xuất lịch sử không tái tạo. Trong tám đối tượng ảnh gốc của bài Tết, xem một và chọn metadata; bảy đối tượng khác chưa tải/xem, không gán là trùng. Giữ 14 khoảng trống nhận diện và PK-05; lỗi truy cập, snippet, metadata và CI không chứng minh đầy đủ.

QA lượt này: 89 test standard library, 17 test tài liệu, 15 test Node, các validator và Markdown lint 44 tệp đạt. Catalogue 153 thẻ đạt 21 ca tìm kiếm với DOM tổng hợp. Đối soát giữ nguyên 220 hồ sơ cũ, byte 46 tài nguyên kèm, 266 dòng path-map và receipt lịch sử. ZIP được build sau receipt, giải nén và so CRC/đường dẫn/từng byte/132 mục manifest của 133 tệp; hash để ngoài kit. Browser/SVG render và tour tương tác chưa kiểm tra. Không tái diễn giải độc lập mọi ảnh cũ bằng visual review.

## Lượt bổ sung ảnh sự kiện (followup_round14)

Đầu vào `main` tại `2b9872a1d65c4ca2dbfc4f41443dcb430602e6ad`, sau khi PR #47 merge; cây tệp khớp checkout cũ `3b5af7b`. Lượt mới dùng branch `docs/vlu-campus-context-audit`, giữ toàn bộ công việc đã công bố. Hiện có **220 hồ sơ: 46 kèm file, 174 metadata-only; 71 hồ sơ ảnh và 152 thẻ catalogue**. Các số liệu ở phần lượt đầu bên dưới giữ phạm vi cũ.

Thêm một JPEG mobile-cover từ [bài VLU](https://www.vlu.edu.vn/news/mirae-map-ve-lo-trinh-dinh-tuong-lai-dong-hanh-cung-sinh-vien-khoa-ngon-ngu-va-van-hoa-han-quoc-truoc-nga-re-chuyen-nganh), 6061 × 4041, tín dụng ảnh theo bài. Ảnh cho thấy góc rộng phòng/sự kiện. Nguồn gắn sự kiện với Cơ sở 1 nhưng vị trí từng ảnh chưa xác minh độc lập. Banner in **2025**; ngày hiển thị **02/02/2026**, nội dung sự kiện **03/02/2026**, CMS và EXIF có mốc riêng. Giữ `capture_date=null`, không tự phân xử các mốc hoặc sửa artwork. Đây không phải xác nhận hiện trạng, quy chuẩn hay ngày chụp. Đã tải, giải mã và xem trực tiếp; hash khác các nguồn đã ghi. Chưa rõ quyền phân phối nên chỉ metadata vào Git/ZIP.

Kiểm kê 7 ảnh nội dung và 3 đối tượng cover/mobile/thumbnail gốc. Xem thêm một ảnh cận cảnh rồi không chọn; tám ảnh khác chưa tải/xem, không gán là trùng. Tải lại 138 URL cũ khớp 140 hồ sơ; thêm hai candidate tải riêng, chỉ một vào ledger. Có byte đối chiếu cho 149/220 hồ sơ, 71 dẫn xuất lịch sử không tái tạo. 16 truy vấn và 54 URL kết quả có mức review/disposition; 54 request trang/CSS, 50 tải đủ. Không dùng nguồn discovery-only hoặc lỗi truy cập để đóng yêu cầu.

Sửa hai receipt có field `current_*` còn ghi 131 tệp/130 mục manifest thành 133/132 và trỏ QA hiện tại về bằng chứng 23/10. Giữ nguyên phần receipt historical 113 tệp. Path-map thêm một dòng metadata mới, không đổi đường dẫn cũ. Byte font/vendor/OFL và 219 hồ sơ cũ giữ nguyên. Vẫn 14 khoảng trống nhận diện và PK-05; browser/tour tương tác chưa kiểm tra. Chưa có căn cứ tuyên bố đầy đủ 100%.

QA lượt bổ sung: 89 test standard library, 17 test tài liệu và 15 test Node đạt; validator kit/tooling/scaffold và Markdown lint 44 tệp đạt. Catalogue 152 thẻ đạt 19 ca tìm kiếm với DOM tổng hợp, không thay browser. Review xác nhận 219 hồ sơ cũ, byte của 46 tài nguyên kèm và mọi receipt cũ giữ đúng phạm vi; 174 đường dẫn bị loại không có trong gói. Hai candidate mới đã giải mã/xem trực tiếp, chỉ một vào ledger. ZIP cuối build sau receipt, giải nén và đối soát CRC/đường dẫn/từng byte/132 mục manifest; hash để ngoài kit.

## Phạm vi và kết quả lượt đầu

Đầu vào: branch `docs/vlu-automotive-reference-audit`, commit `62708a876686551f37628890d663120bdd6861a7`; tại thời điểm lượt đầu, PR #47 còn mở. Kiểm kê trước khi sửa: 219 hồ sơ nguồn, 53 yêu cầu và 131 file kit. Đây là checklist tự xây dựng, không phải danh mục đầy đủ được VLU xác nhận. [Bằng chứng mới](../evidence/asset-audit-2026-10-23.json) ghi từng hồ sơ/yêu cầu, nguồn, trạng thái truy cập, mức review và giới hạn; [báo cáo 22/10](asset-audit-2026-10-22.md) giữ nguyên như lịch sử.

| Nhóm trạng thái | Kết quả |
| --- | --- |
| Có file trong gói, hash và khả năng đọc được kiểm tra | 46 tài nguyên, gồm font/vendor/OFL, swatch và mẫu chữ |
| Chỉ metadata, chưa có quyền phân phối phù hợp | 173 hồ sơ không có byte trong Git/ZIP |
| Nguồn gốc tải riêng có byte đối chiếu mới | 102 hồ sơ, không thành tài nguyên được phép chia sẻ |
| Dẫn xuất lịch sử không tái tạo | 71 hồ sơ metadata-only, không coi là file đã cung cấp |
| Phạm vi checklist chưa đủ bằng chứng | 14 khoảng trống nhận diện và PK-05 browser render |

Tải mới toàn bộ 138 URL tệp nguồn, đối chiếu đúng hash 140 hồ sơ remote; 46 tài nguyên kèm gói giữ nguyên byte. Tổng 148/219 hồ sơ có bằng chứng byte mới, không có hash thay đổi cần thay tệp. Ledger giữ 219 hồ sơ, chỉ mục ảnh 70 mục và catalogue 151 thẻ. Không thêm artwork, hồ sơ asset hoặc quy chuẩn suy diễn.

## Nghiên cứu và phân xử nguồn

Thực hiện 20 truy vấn web, ghi 71 URL kết quả duy nhất theo mức review. Có 53 request trang/CSS, 49 tải đủ; hai EventBox lỗi truy cập và hai project Behance trả 429. Không xem search snippet, HTTP 200, số lượng file hoặc CI xanh là bằng chứng đầy đủ. Không tuyên bố đã tìm toàn bộ internet.

- **Brandbook/logo/màu/typography:** các nguồn VLU năm 2022 và thể lệ thi logo năm 2024 vẫn hỗ trợ đúng phạm vi đã ghi; không xác nhận bộ master hiện hành, Pantone/CMYK, màu bổ trợ hoặc typography cho mọi ấn phẩm. Không nhập thông số từ tài liệu bên thứ ba chưa được xác thực.
- **Đầu mối “Guideline v3” trên Scribd:** [trang nguồn](https://www.scribd.com/document/836080861/guideline-v3) có mô tả AI-enhanced nhắc cả VLU và Mỹ Hảo. Bản text preview đã mở qua web tool có nội dung về Mỹ Hảo nhưng được công cụ ghi tuổi crawl bảy tháng; tải HTML trực tiếp mới chỉ đọc được mô tả, chưa lấy PDF gốc. Không dùng đầu mối này làm brandbook VLU hoặc xác nhận màu/font/khoảng bảo vệ; chưa xác minh tác giả, phiên bản, phê duyệt hay quyền. Đây là phân xử phạm vi bằng chứng, không kết luận tài liệu giả hoặc nguồn có ý đồ xấu.
- **Mascot/họa tiết/portfolio:** hadée và Line Collective chỉ hỗ trợ phạm vi dự án họ trình bày; chưa có master hoặc quyền chia sẻ mới. [Project Behance 215764877](https://www.behance.net/gallery/215764877/Van-Lang-University-Rebrand) được search gắn với B&A, nhưng mở web thất bại và tải trực tiếp 429. Chỉ giữ đầu mối, không xác nhận publisher/owners hoặc artwork từ kết quả search.
- **Đồng phục và lễ phục:** nguồn K32, hoạt động 2026 và các sự kiện chuyên ngành được kiểm tra lại trong phạm vi cũ. [Route giáo dục thể chất](https://www.vlu.edu.vn/dynamic/chuong-trinh-giao-duc-the-chat) trả HTTP 200 nhưng nội dung Page not found. [Bài Công đoàn](https://congdoan.vlu.edu.vn/truong-dai-hoc-van-lang-lan-toa-ve-dep-ao-dai-va-cham-lo-suc-khoe-nu-cong-doan-vien-nhan-ngay-quoc-te-phu-nu-83-263) nói về hoạt động áo dài của cán bộ/giảng viên/nhân viên, không xác nhận catalogue đồng phục sinh viên. Không suy mẫu mới nhất, rập, màu vải hoặc quy định bắt buộc từ ảnh.
- **Cover/banner/template:** cover public vẫn cùng photo ID `1122903070252889` trong đúng profile được website VLU liên kết; rendition nguồn khớp hash. Đây là quan sát ngày 23/10, không phải master, giấy phép hoặc bảo đảm cover sẽ không đổi. Banner/campaign giữ phạm vi snapshot; không có template editable được phê duyệt mới.
- **Khuôn viên/hoạt động:** giữ tuyển chọn có nguồn; không xác nhận đủ ảnh mọi cơ sở, ngày chụp hoặc hiện trạng từng góc. Tour do hai trang VLU liên kết vẫn mới được kiểm tra HTML, chưa kiểm kê/render cảnh. Ba ảnh Điều dưỡng legacy không có trong payload hiện tại nhưng URL byte còn tải được; giữ phạm vi lịch sử thay vì suy đã đổi thiết kế.

## Thay đổi và quyền phân phối

Bổ sung báo cáo/bằng chứng ngày 23/10, cảnh báo đầu mối chưa đủ căn cứ và cập nhật con trỏ audit/quan sát cover. Giữ nguyên toàn bộ 219 bản ghi ledger, byte font/vendor/OFL, checklist và path-map vì không thêm/đổi tên/di chuyển asset. Hai tệp mới là hồ sơ audit, không phải tài nguyên VLU mới. Gói có 133 file, 132 mục manifest sau cập nhật. Giấy phép MIT chỉ áp dụng phần tự biên soạn trong phạm vi LICENSE/NOTICE; không gán lại cho VLU hoặc bên thứ ba.

## Khoảng trống và bước tiếp theo

Checklist giữ 28 verified, 10 fixed và 15 unverified. Cần nguồn VLU xác nhận brandbook hiện hành; vector/lockup/biến thể và quy tắc đặt logo; bảng màu in ấn/bổ trợ; typography theo ấn phẩm; master mascot/họa tiết; catalogue/rập đồng phục theo khóa/khoa; master cover/template và quyền phân phối. Tra [từng khoảng trống](official-gaps.md) và checklist trong bằng chứng mới để biết phạm vi cụ thể. Nguồn không truy cập được cần thử lại hợp lệ hoặc tài liệu gốc được phép cung cấp; không suy tài liệu không tồn tại.

Browser đang bị tắt trong Work settings nên PK-05 và tour tương tác chưa kiểm tra. Giải mã/parse, đối soát hash và chạy mã catalogue không thay bằng chứng hiển thị. Khi cần hình mới nhất/đúng cơ sở hoặc quảng bá có xếp hạng/ngày/quy định, đối chiếu mới; tư liệu ổn định chỉ dùng lại theo ngày và phạm vi nguồn. Chưa đủ căn cứ tuyên bố bộ nhận diện đầy đủ 100%.

## Kiểm tra kỹ thuật và bàn giao

89 test standard library, 17 test tài liệu và 15 test Node đạt; validator kit/tooling/scaffold và Markdown lint 44 tệp đạt. Mã catalogue thực giữ nguyên, 151 thẻ đạt 17 ca tìm kiếm với DOM tổng hợp. Đã giải mã 99 raster nguồn và ba mẫu chữ kèm gói; hai GIF một frame được kiểm đủ frame; parse ba SVG có chặn DTD/entity; load/cmap 30 font với mẫu NFC/NFD giới hạn. Không xác nhận mọi glyph/axis, SVG render hoặc browser.

Review xác nhận nguyên byte 46 tài nguyên kèm gói, toàn bộ 219 bản ghi ledger và các receipt audit cũ; 173 đường dẫn không được phân phối vẫn vắng mặt. ZIP cuối build sau khi chốt report/evidence, giải nén thử và so CRC/đường dẫn/từng byte/132 mục manifest của 133 file. Hash ZIP và receipt kiểm tra được giữ ngoài kit, tránh tự tham chiếu. Các kết quả kỹ thuật này không thay bằng chứng tính chính thức, hiện hành hay quyền sử dụng.
