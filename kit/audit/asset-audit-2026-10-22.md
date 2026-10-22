# Audit nguồn tài nguyên VLU, 22/10/2026

## Phạm vi và kết quả

Đầu vào là repository tại commit `ed9ec0cb5ae59bb4a572eda166317638ee9dff61` (v0.1.23), không phải một lần nhập lại ZIP nội bộ. Phạm vi ban đầu: 53 yêu cầu, 180 bản ghi tài nguyên và 116 file kit. Bằng chứng bắt đầu thu thập ngày 21/10, được kiểm tra lại theo ngày 22/10/2026 (Asia/Saigon); timestamp truy cập trong JSON dùng UTC.

Các lượt bổ sung tổng cộng **34 hồ sơ nguồn**: 17 ảnh bối cảnh/cơ sở vật chất, một ảnh bìa Facebook theo thời điểm, bảy tham chiếu portfolio mascot, ba ảnh Điều dưỡng và sáu ảnh Lab/MSC. Ledger hiện có 214 bản ghi: 46 mục kèm file, 168 mục chỉ có metadata. Không thêm byte artwork mới vào Git hoặc ZIP công khai vì chưa có căn cứ quyền phân phối phù hợp.

Catalogue hiện có 146 thẻ; các lượt trước lần lượt có 112, 137 và 140 thẻ. 68 bản preview/bản chuyển đổi/bảng ghép đã loại vẫn có hồ sơ trong ledger, không được tạo thêm thẻ trùng lặp. Trong 168 mục không kèm file, 97 tài nguyên nguồn đã có byte đối chiếu riêng qua các lượt; 71 bản dẫn xuất lịch sử chỉ có metadata, không được tái tạo. Lượt tiếp theo tải lại được 86 trong 88 nguồn đã có, hai logo MSC lỗi DNS; thêm ba nguồn ảnh mới.

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

## Lượt đối soát hướng dẫn trên commit 84397f9

Đầu vào: nhánh `docs/vlu-nursing-reference-audit`, commit `84397f9723e1336343b7cccef4da36d41d532978`, ngày 22/10/2026; 208 hồ sơ, 53 yêu cầu, 131 file kit. Phạm vi không đổi: tài nguyên tham chiếu chung và hồ sơ/hướng dẫn phục vụ tái sử dụng. Trường `followup_round3` trong các bằng chứng ghi kết quả theo từng tài nguyên/yêu cầu, không dùng CI để suy tính đầy đủ.

Lượt này không thêm hồ sơ tài nguyên hoặc byte artwork mới. Phát hiện và sửa năm nhóm sai lệch mức thấp trong hướng dẫn: trạng thái ảnh bìa Facebook và tên chỉ mục cũ; số liệu độ phủ ảnh; tên tệp mẫu chữ/logo/hồ sơ trang phục; khả năng mở các template/logo vốn chỉ có metadata; điểm vào audit và cách diễn giải receipt/render lịch sử. Đồng bộ hướng dẫn về 61 hồ sơ ảnh, 29 ảnh từ các snapshot campus và 16 hồ sơ banner/cover. Các con số là độ phủ tuyển chọn, không phải danh mục chính thức đầy đủ.

- **Nguồn và byte:** yêu cầu lại 127 URL tài nguyên, tải được 125, tương ứng 127 bản ghi khớp hash. 46 file kèm gói giữ nguyên byte; tổng 135/208 hồ sơ có byte đối chiếu ở lượt này. 73 mục còn lại gồm hai logo MSC lỗi DNS sau hai lần thử và 71 bản dẫn xuất metadata lịch sử. Không kết luận nguồn không tồn tại từ lỗi truy cập.
- **Trang nguồn:** mở trực tiếp 40 URL trang/CSS: 33 HTTP 200, năm lỗi DNS, một HTTP 500 và một Behance 429. Một trang agency thành công sau timeout ở lần thử trước; giữ riêng lỗi thử trước. Trang campus tiếng Việt trả payload rỗng; trang tiếng Anh có nội dung và đúng URL của 14/29 hồ sơ campus. Không suy 15 ảnh còn lại bị xóa hoặc dùng một response rỗng làm bằng chứng hiện trạng trường.
- **Ảnh bìa:** HTML công khai Facebook tiếp tục trả photo ID `1122903070252889` trong đúng trường cover của profile trường. Byte rendition khớp hash, nhưng quan sát chỉ áp dụng tại thời điểm truy cập; chưa xác nhận ngày công bố/chụp hay quyền phân phối. Hướng dẫn cũ nói chưa xác minh cover đã được sửa theo bằng chứng này.
- **Các nhóm còn lại:** mở nguồn nhận diện năm 2022, thể lệ màu năm 2024 bằng hai ngôn ngữ, font/CSS, portfolio, ảnh trang phục/lễ phục và hoạt động. Có thêm 16 truy vấn với output đầy đủ lưu ngoài repo; đầu mối chưa mở hoặc không đúng thẩm quyền không dùng để đóng yêu cầu. Chưa có căn cứ mới cho brandbook/master logo/biến thể/quy chuẩn sử dụng, hệ màu in ấn, typography toàn trường, master mascot/template, catalogue đồng phục hoặc quyền phân phối rộng rãi.
- **Bản cộng đồng:** không kèm logo, ảnh hoặc ba SVG template nhúng logo chưa rõ quyền. Hướng dẫn mở/chỉnh sửa được viết có điều kiện đã có file và quyền phù hợp. Tên tệp mẫu chữ trỏ tới file thực có; đường dẫn logo/template là hồ sơ metadata, không phải lỗi đóng gói.

Checklist giữ 28 verified, 10 fixed, 15 unverified: 14 khoảng trống nhận diện và một kiểm tra browser. Không thực hiện render browser mới; receipt Chromium/desktop/mobile cũ được ghi rõ là lịch sử. Bước tiếp theo cho khoảng trống chính thức vẫn là lấy bản gốc/quy định có phiên bản và căn cứ quyền từ đúng chủ thể; không tự liên hệ trong lượt này. Với Cơ sở 1/Cơ sở 2 hoặc góc chụp chưa có, cần nguồn ảnh đúng địa điểm; bộ ảnh hiện tại chưa đủ mọi cơ sở.

Kiểm tra kỹ thuật lượt này: 89 test standard library, 17 test tài liệu và 15 test Node đạt; validator kit/tooling/scaffold và Markdown lint đạt. Giải mã frame đầu 86 ảnh nguồn raster và ba mẫu chữ kèm gói; parse ba SVG với DTD/entity bị từ chối; load/cmap 30 TTF với mẫu NFC/NFD được ghi rõ, không kiểm tra mọi glyph hoặc tổ hợp trục variable. Xem lại trực tiếp ảnh bảng mascot 2022 và polo/quà K30, không phát hiện sai khác với mô tả hiện có. HTML catalogue giữ nguyên byte; kiểm tra ZIP cuối dùng manifest, CRC và đối chiếu từng byte sau giải nén. Render browser chưa thực hiện.

## Bổ sung bối cảnh Lab và MSC trên commit 6c19dd7

Đầu vào: nhánh `docs/vlu-nursing-reference-audit`, commit `6c19dd7671bd5a250a2c3db75a626b56c799055d`, ngày audit 22/10/2026; 208 hồ sơ, 53 yêu cầu và 131 file kit. Đã kiểm kê lại toàn bộ ledger, trạng thái file/quyền và các khoảng trống; kết quả từng mục nằm trong `followup_round4` của bằng chứng.

Bổ sung sáu hồ sơ nguồn từ hai bài VLU hiển thị ngày 03/06/2026: phòng Lab Giải phẫu; học sinh THPT trải nghiệm Điều dưỡng và Kỹ thuật Y học; mô hình trên giường, kho mô hình và phòng quan sát MSC. Bài về MSC xác định trung tâm ở Cơ sở 2; không tự gán ba ảnh Lab còn lại cho cơ sở đó. Giữ riêng chú thích nguồn và quan sát ảnh: biển phòng Sinh Học Phân Tử không tự là tên ngành; cảnh tham quan phòng quan sát không chứng minh đang chấm thi. Trang phục của khách THPT không phải mẫu đồng phục VLU.

Tải, giải mã và xem cả sáu ảnh; không có hash trùng với ledger đầu vào hoặc trùng nhau. Tệp giữ nguyên byte nguồn, ngày chụp chưa xác nhận. Tác giả bài không mặc định là nhiếp ảnh gia; con số/phát biểu quảng bá trong bài không được xác minh độc lập như dữ kiện hiện hành. Quyền phân phối chưa xác minh nên chỉ thêm metadata vào Git; các ảnh nằm ngoài repo và ZIP công khai.

Lượt này thực hiện 16 truy vấn, giữ output đầy đủ ngoài repo. Có 40 URL trang được yêu cầu trực tiếp (39 URL trong batch và một route bài MSC không có tiền tố vi); 34 lỗi DNS trong batch, một Behance 429 và bốn HTTP 200. Route MSC bổ sung cũng lỗi DNS. Hai bài mới đọc được nội dung cùng liên kết ảnh qua web tool, nhưng công cụ ghi tuổi crawl lần lượt bốn tuần và hai tháng; không coi đó là bằng chứng trang vẫn triển khai trực tiếp đúng tại giờ audit. Không dùng snippet làm bằng chứng cuối cùng. Gallery Dược, các PDF cẩm nang và đầu mối không mở được không dùng để đóng mục thiếu.

Trong 127 URL tài nguyên cũ, 95 tải được, tương ứng 97 bản ghi khớp hash. 32 URL lỗi DNS gồm 30 từ website chính và hai từ MSC. 46 file kèm gói vẫn khớp byte đầu vào; 26 font kèm gói có nguồn remote không truy cập lại được vẫn là file offline dùng được, không bị đánh dấu thiếu. Có 131/208 hồ sơ đầu vào có byte đối chiếu mới; 77 mục còn lại là sáu nguồn ảnh/logo chưa tải lại được và 71 bản dẫn xuất chỉ có metadata. Cộng sáu file nguồn mới, 137/214 hồ sơ có byte đối chiếu trong round này. Không dùng kết quả tải thành công cũ để gán đạt cho các request mới bị lỗi.

Hiện có 214 bản ghi, gồm 46 kèm file và 168 metadata-only; 67 hồ sơ ảnh và 146 thẻ catalogue. Path-map giữ 226 dòng đầu vào và 34 dòng bổ sung, không đổi tên/di chuyển file cũ. Vẫn 131 file kit và 130 mục manifest. Không thêm nhóm thư mục thực hoặc artwork chưa rõ quyền vào gói cộng đồng. Các nguồn còn lại về nhận diện, màu, typography, mascot, trang phục và banner được đối chiếu theo khả năng truy cập; không có căn cứ mới để đóng 14 khoảng trống nhận diện. Kiểm tra browser vẫn chưa thực hiện. Bước tiếp theo là xác minh lại nguồn lỗi truy cập và lấy master/quy định có phiên bản, phạm vi và quyền từ đúng chủ thể; không tự liên hệ trong lượt này.

QA của lượt bổ sung: 89 test standard library, 17 test tài liệu và 15 test Node đạt; validator kit/tooling/scaffold và Markdown lint đạt. 85 ảnh nguồn cũ cùng sáu ảnh mới đã giải mã frame đầu; sáu ảnh mới được xem trực tiếp. Load/cmap 30 font kèm gói với mẫu NFC/NFD giới hạn; ba SVG website không tải lại được nên không ghi nhận parse mới. Catalogue có 146 thẻ và 10 trường hợp chạy mã tìm kiếm thực với DOM tổng hợp; không thay kiểm tra browser. Bản ZIP cuối được build sau cập nhật receipt, giải nén và so từng đường dẫn/byte/checksum.

Đã thử lại khả năng dùng browser trong round này: `cua.getState` trả danh sách browser rỗng và lỗi Local browser use is disabled in Work settings. Không có render browser mới hoặc cách chạy headless để thay thế; PK-05 tiếp tục chưa xác minh.
