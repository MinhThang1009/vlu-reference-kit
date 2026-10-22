# Audit nguồn tài nguyên VLU, 22/10/2026

## Phạm vi và kết quả

Đầu vào là repository tại commit `ed9ec0cb5ae59bb4a572eda166317638ee9dff61` (v0.1.23), không phải một lần nhập lại ZIP nội bộ. Phạm vi ban đầu: 53 yêu cầu, 180 bản ghi tài nguyên và 116 file kit. Bằng chứng bắt đầu thu thập ngày 21/10, được kiểm tra lại theo ngày 22/10/2026 (Asia/Saigon); timestamp truy cập trong JSON dùng UTC.

Bổ sung **25 hồ sơ nguồn**: 17 ảnh bối cảnh/cơ sở vật chất, một ảnh bìa Facebook theo thời điểm và bảy tham chiếu portfolio mascot của họa sĩ. Lượt tiếp theo trên commit `a16e3b089f2b14ed592dea3b5696dc70beb367fc` bổ sung ba hồ sơ ảnh Điều dưỡng. Ledger hiện có 208 bản ghi: 46 mục kèm file, 162 mục chỉ có metadata. Không thêm byte artwork mới vào Git hoặc ZIP công khai vì chưa có căn cứ quyền phân phối phù hợp.

Catalogue tăng từ 112 lên 140 thẻ qua hai lượt (137 thẻ sau lượt đầu). 68 bản preview/bản chuyển đổi/bảng ghép đã loại vẫn có hồ sơ trong ledger, không được tạo thêm thẻ trùng lặp. Trong 162 mục không kèm file, 91 tài nguyên nguồn đã có byte đối chiếu riêng qua hai lượt; 71 bản dẫn xuất lịch sử chỉ có metadata, không được tái tạo. Lượt tiếp theo tải lại được 86 trong 88 nguồn đã có, hai logo MSC lỗi DNS; thêm ba nguồn ảnh mới.

Checklist vẫn có 53 yêu cầu, gồm 28 `verified`, 10 `fixed` và **15 `unverified`** (14 khoảng trống nhận diện và một kiểm tra render catalogue). Đây là checklist tự xây dựng, không phải danh mục đầy đủ do VLU xác nhận. Trạng thái `verified` phải được đọc cùng phạm vi, ngày và `fresh_review`, không đồng nghĩa file được phân phối trong gói hoặc tài nguyên là master hiện hành.

## Các bổ sung có thể tra cứu

| Nhóm | Bổ sung | Bằng chứng và giới hạn |
| --- | --- | --- |
| Cơ sở và hoạt động | 17 hồ sơ: HUB, media studio, canteen, lớp học, cửa hàng, y tế, thực hành Răng Hàm Mặt/Du lịch, hội trường, sân khấu và hoạt động học tập | Ảnh được [trang cơ sở chính VLU](https://www.vlu.edu.vn/about-us/campuses-facilities/co-so-chinh) liên kết. Phân biệt ảnh kiến trúc với ảnh hoạt động; không suy năm chụp từ ngày CMS. Các bản lớn do CMS cung cấp được ghi rõ khi dùng rendition. |
| Ảnh bìa Facebook | Photo ID `1122903070252889`, rendition 960 × 462 | Website VLU khai báo trang Facebook trong JSON-LD `sameAs`; HTML công khai của trang trả `cover_photo.photo`. Đã tải và xem ảnh, kiểm tra lại cùng photo ID ngày 22/10. Đây là quan sát theo thời điểm, không phải file master hoặc bảo đảm ảnh bìa không đổi sau này. |
| Mascot và ứng dụng | 7 hồ sơ từ portfolio hadée atelier, gồm hai hình minh họa và năm ảnh ứng dụng | [Trang tác giả](https://hadeeatelier.com/portfolio/vlu-the-uniland/) ghi dự án do B&A đặt hàng và quyền thuộc agency/client. Portfolio chỉ chứng minh cách trình bày dự án, không xác nhận bộ master VLU hiện hành. Không tự gắn giấy phép MIT hoặc suy có file vector/3D từ ảnh render. |

Tra chi tiết từng file, URL trang/tệp nguồn, kích thước, SHA-256, credit và quyền tại [asset ledger](../data/asset-sources.json), [ảnh bìa theo thời điểm](../data/facebook-cover-observation.json), [chỉ mục ảnh](../data/reference-index.json) và [quan sát nguồn mascot](../data/mascot-source-observations.json).

Ngày của ảnh bìa trong basename là ngày quan sát đầu tiên 21/10; `last_verified_on` ghi lần kiểm tra tiếp theo. Ngày công bố và ngày chụp chưa xác nhận được giữ là `null`. URL CDN Facebook có thể hết hạn; dùng trang nguồn/photo ID để kiểm tra lại. Xếp hạng và huy hiệu in trong artwork chưa được kiểm chứng độc lập như dữ kiện hiện hành.

## Đối chiếu các nhóm còn lại

- **Brandbook, logo và hệ ứng dụng:** đã mở lại bài VLU công bố nhận diện năm 2022 và các nguồn liên quan. Không tìm được danh mục master đầy đủ, hiện hành, có xác nhận của trường trong phạm vi nghiên cứu này. Không lấy bài tập thiết kế hoặc website tải logo làm bằng chứng quy chuẩn chính thức.
- **Màu:** ba HEX tiếp tục được đối chiếu với [thể lệ thi logo 30 năm năm 2024](https://www.vlu.edu.vn/news/truong-dai-hoc-van-lang-to-chuc-cuoc-thi-thiet-ke-logo-30-nam-thanh-lap). Sửa các citation dùng URL thiếu chữ `thi`, vốn trả HTTP 200 nhưng nội dung là Page not found. Không suy ra Pantone, CMYK, tỷ lệ phối màu hoặc thông số màu vải chính thức.
- **Typography:** tải lại nguồn font và CSS; bảo toàn byte font/vendor/OFL. 30 TTF được load và kiểm tra cmap với mẫu tiếng Việt NFC/NFD đã ghi rõ. Điều này không xác nhận font logotype, typography bắt buộc cho mọi ấn phẩm hoặc độ đúng của mọi glyph.
- **Đồng phục:** mở lại nguồn và đối chiếu ảnh polo, bối cảnh sơ mi chụp ảnh thẻ, blouse/lễ phục, thực hành chuyên ngành và GDQP. Chưa có catalogue thiết kế mới nhất, rập trước/sau, màu vải/chất liệu/size và quy định đầy đủ theo khóa/khoa. Ảnh biểu diễn trang phục xanh trong gallery campus không phải bằng chứng quy chuẩn GDQP; ảnh workshop có biển BETU không được dùng làm kiến trúc campus VLU.
- **Banner:** 14 URL banner homepage trong cấu hình vẫn khớp hồ sơ đã có; phân biệt banner chiến dịch với template trống và master có thể chỉnh sửa. Không sửa artwork để ép năm xếp hạng khớp thời điểm audit.
- **Mascot/họa tiết:** giữ bảng tên bảy mascot theo ảnh công bố 2022 như dữ liệu lịch sử. Trang họa sĩ mô tả bảy nhân vật; portfolio B&A có heading năm mascot. Giữ cả hai phạm vi và sự khác biệt, không sửa cơ cấu đào tạo hiện hành theo một heading portfolio.

## Bằng chứng truy cập và kiểm tra

Đã ghi tám truy vấn tìm kiếm mới ngày 22/10, cùng 28 truy vấn ban đầu ngày 21/10. Output đầy đủ của các truy vấn ban đầu không được lưu trọn vẹn; không suy ra đã đối soát hết mọi kết quả. Nhật ký công khai giữ truy vấn và disposition của các đầu mối; output tìm kiếm đầy đủ và trang tải về nằm ngoài Git. Không tuyên bố đã duyệt hết Google hoặc mọi kết quả tìm kiếm.

Trong lần kiểm tra lại ngày 22/10, 36 URL trang/CSS được yêu cầu: 35 trả HTTP 200, một trả 429. HTTP 200 không tự là xác minh nội dung: có một trang Page not found và các trang MSC chỉ đủ xác nhận navigation/liên kết, chưa đủ xác nhận nội dung PDF. Web text tool Facebook có thể bị chặn trong khi tải HTML công khai trực tiếp trả được dữ liệu; hai phương thức này được ghi riêng.

Đã tải và hash **124 URL tài nguyên riêng biệt**. Toàn bộ 101 bản ghi remote cũ (99 URL) khớp SHA-256 đã lưu; 25 file mới được tải, kiểm tra kích thước và xem trực tiếp. Có 85 lần giải mã đầy đủ frame đầu của ảnh raster, ba SVG được parse với DTD/entity bị từ chối và 30 font được load/kiểm tra mẫu. Byte không đổi không đồng nghĩa nguồn đúng, mới nhất hoặc có giấy phép phân phối.

- [Đối soát từng yêu cầu và tài nguyên](../evidence/asset-audit-2026-10-22.json)
- [Kết quả tải trang và tài nguyên](../evidence/source-recheck-2026-10-22.json)
- [Truy vấn và đầu mối](../evidence/research-log-2026-10-22.json)
- [Kiểm tra font từ lượt thu thập đầu tiên](../evidence/font-recheck-2026-10-21.json)
- [Kiểm tra ảnh từ lượt thu thập đầu tiên](../evidence/image-recheck-2026-10-21.json)
- [QA bản bàn giao](../evidence/asset-package-qa-2026-10-22.json)

Các receipt nguồn cũ vẫn là bằng chứng lịch sử. Bản checklist trước cập nhật được giữ tại `evidence/history/`; path-map giữ 226 dòng đầu vào và bổ sung 25 dòng nguồn mới có `old_path`/`input_sha256` rỗng, vì chúng không nằm trong ZIP đầu vào. `package_path` rỗng cho các file chỉ được lưu riêng, không phải file bị bỏ sót khi đóng gói cộng đồng.

## Những khoảng trống vẫn mở

Xem [14 yêu cầu còn thiếu căn cứ](official-gaps.md): brandbook đầy đủ; master vector tiếng Việt; lockup và biến thể được duyệt; clear-space/kích thước/nền/co-branding; CMYK/Pantone và hệ màu bổ trợ; typography bắt buộc; master mascot/vector/3D/motion; catalogue và thông số thiết kế đồng phục; template/master cover chỉnh sửa; quyền phân phối rộng rãi cho artwork.

Bước xử lý là lấy tài liệu hoặc xác nhận từ đúng chủ thể có thẩm quyền, đối chiếu phiên bản/phạm vi và quyền trước khi thêm byte vào gói công khai. Không tìm thấy trong các nguồn đã kiểm tra không chứng minh tài liệu không tồn tại. Không tự liên hệ đơn vị, dùng tài khoản để vượt giới hạn truy cập hoặc tạo tài sản giả để đóng các mục này.

## Kiểm tra hiển thị còn giới hạn

Local browser use bị tắt trong Work settings nên không thực hiện được browser smoke test. Đã parse HTML, đối soát thẻ/ledger và chạy chính mã tìm kiếm với DOM tối thiểu tổng hợp trong sáu trường hợp, gồm tiếng Việt NFD. Đây không phải bằng chứng kiểm tra desktop/mobile, bàn phím hoặc zoom/reflow trên browser thật. PK-05 được mở lại và không kế thừa trạng thái render đã đạt của receipt cũ.

## Tái sử dụng

Chọn bối cảnh từ catalogue/ledger, kiểm tra `included_in_package` trước khi tìm file, và đọc quyền cùng ngày nguồn. Tư liệu lịch sử vẫn dùng được làm tham chiếu đúng phạm vi. Các khẳng định “mới nhất”, “đang dùng” hoặc số liệu trên banner phải được kiểm tra lại khi thực hiện sản phẩm về sau. Bộ kit không mặc định hội sách, nhân vật, số người hoặc phong cách ảnh.

## Lượt đối soát tiếp theo trên commit a16e3b0

Phạm vi cố định: nhánh `docs/vlu-asset-source-audit`, commit `a16e3b089f2b14ed592dea3b5696dc70beb367fc`, 205 hồ sơ và 53 yêu cầu; ngày audit 22/10/2026. Kiểm tra GitHub trước bàn giao xác nhận PR #45 đã merge vào main tại `713ce8cc6e41f9c3bfa8dda4c6a25b7bd9e231af`, cây tệp khớp commit đầu vào a16e3b0. Các sửa đổi tiếp theo được bàn giao qua nhánh/PR mới. Hồ sơ từng mục và kết quả tải nằm trong trường `followup` của các JSON bằng chứng ở trên.

- **Sửa mô tả trang phục:** xem lại ảnh gốc lễ Điều dưỡng K30 cho thấy chi tiết xanh ở vai, không phải viền hồng tím. Đồng bộ ledger, chỉ mục, catalogue, hướng dẫn và UN-03; không suy màu vải chính xác hoặc hai thiết kế khác nhau từ bối cảnh lễ/thực hành.
- **Bổ sung ba hồ sơ ảnh từ trang ngành Điều dưỡng:** ảnh banner thực hành với mô hình, ảnh mục chuẩn đầu ra và ảnh mục dạy/học. Tải nguyên bản, giải mã và xem cả năm candidate; không thêm hai ảnh có bố cục trùng/gần với ảnh đã chọn hoặc tham chiếu cũ. Đây là đánh giá nội dung hình ảnh, không khẳng định các byte giống nhau. Giữ ngày chụp chưa xác nhận, ngày CMS không phải ngày đổi thiết kế.
- **Sửa tính hiện hành:** hai URL ảnh từ snapshot trang Điều dưỡng trước không xuất hiện trong payload tải mới. Giữ hash và nguồn lịch sử; không gọi là banner hiện hành. URL file vẫn tải được không chứng minh trang còn sử dụng file đó.
- **Truy cập nguồn:** yêu cầu 36 URL trang/CSS, sau đó thử lại 27 URL VLU lỗi DNS. Kết quả cuối gồm 30 HTTP 200, bốn lỗi DNS, một HTTP 500 và một Behance 429. Ba route campus trả payload rỗng dù HTTP 200, trong đó hai route chỉ là probe chưa được xác nhận; web text view đọc được nội dung campus nhưng không thay bằng chứng tải trực tiếp. Không kết luận tài liệu không tồn tại từ các lỗi này.
- **Đối soát byte:** 122/124 URL nguồn có sẵn tải thành công, tương ứng 124 bản ghi remote khớp hash; hai logo MSC chưa kiểm tra lại được. 46 file kèm gói vẫn nguyên byte. Tổng 132/205 hồ sơ đầu vào có byte được đối soát ở lượt này; 73 mục còn lại gồm hai logo không truy cập được và 71 bản dẫn xuất metadata lịch sử. Ba file mới được lưu riêng ngoài Git; không thêm artwork vào ZIP công khai.
- **Tìm kiếm:** thực hiện thêm 20 truy vấn, giữ đầy đủ output ngoài repo cho 13 truy vấn; bảy truy vấn không có output lưu trọn vẹn. Kết quả nhà cung cấp, bài tập và tài liệu về thương hiệu khác chỉ là đầu mối, không chứng minh quy chuẩn VLU. Chưa có bằng chứng đóng thêm 14 khoảng trống nhận diện. PK-05 vẫn chưa xác minh render browser.

Path-map giữ 226 dòng đầu vào và 28 dòng nguồn bổ sung. Không đổi tên/di chuyển file hiện có; các dòng nguồn mới không có đường dẫn ZIP đầu vào hoặc đường dẫn file trong gói cộng đồng. Bộ kit vẫn 131 file, manifest 130 mục; chỉ thay metadata và tài liệu.
