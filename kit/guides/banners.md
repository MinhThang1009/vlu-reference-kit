> Mọi đường dẫn trong đoạn mã tính từ gốc kit. Hồ sơ nguồn và trạng thái tệp ở `data/asset-sources.json`. Gói cộng đồng chỉ lưu metadata cho ảnh/logo/template chưa rõ quyền phân phối; các tệp đó không kèm trong ZIP này. Không coi đường dẫn tham chiếu là tệp đã được cung cấp.

# Banner/ảnh đầu trang từ nguồn chính thức VLU

Ledger giữ hồ sơ **14 tệp nguồn** trong cấu hình banner trang chủ https://www.vlu.edu.vn/ khi kiểm tra ngày 17/10/2026: 7 ảnh desktop 8000 × 3333 px và 7 ảnh mobile 3333 × 5333 px. Đường dẫn tệp, trường dữ liệu, URL, hash và chủ đề hình ảnh nằm trong `data/banner-index.json` và `data/asset-sources.json`. Các file ảnh không kèm trong gói cộng đồng khi chưa rõ quyền phân phối.

Đây là artwork raster hoàn chỉnh được website chính thức cung cấp. Các ảnh không phải template trống hoặc file nguồn có lớp để sửa. Bộ này không khẳng định ảnh trong cấu hình xuất hiện đồng thời trên mọi thiết bị hoặc đã được dùng làm ảnh bìa Facebook.

## Dùng làm tham khảo

- Xem cách trường phối hình, chữ, khoảng trống và thông điệp; giữ nguyên bản gốc trong kho tư liệu. Khi cần bố cục mới, dùng mẫu custom hoặc tự dàn lại theo yêu cầu, ghi đúng nguồn gốc.
- Một số banner chứa năm, xếp hạng, chứng nhận và logo tổ chức thứ ba. Nội dung đó là phần của artwork tại thời điểm nguồn, không phải dữ kiện mặc định cho ảnh mới. Cần xác minh khi tái công bố các thông tin này.
- Study with US là thông điệp xuất hiện trên các banner, không thay thế slogan đã công bố WHERE IMPACT MATTERS. Màu trang phục, màu chiến dịch và logo QS/Microsoft không tự trở thành màu chuẩn hoặc thương hiệu riêng của VLU.
- Không dùng thời gian createdAt/updatedAt của CMS làm ngày chụp hay ngày phát hành chính thức. Có banner chứa năm khác dữ kiện trên các phần khác của website; không sửa file gốc để ép đồng nhất.

## Ảnh bìa mạng xã hội

Đã quan sát ảnh bìa trang Facebook trường ngày 21/10 và đối chiếu lại ngày 23/10/2026: photo ID `1122903070252889`, rendition 960 × 462 px. Website VLU khai báo trang trong JSON-LD `sameAs`; HTML công khai của Facebook trả cùng ID tại trường `cover_photo.photo`. Hồ sơ tại `data/facebook-cover-observation.json` ghi URL, hash và giới hạn truy cập. Kết quả shell/chặn của công cụ web ở lượt cũ không thay kết quả tải HTML công khai trực tiếp.

Đây là quan sát theo thời điểm, không phải master chỉnh sửa được hoặc bảo đảm ảnh bìa còn giữ nguyên sau này. URL CDN có thể hết hạn; kiểm tra lại trang/photo ID khi cần tuyên bố hiện hành. Chưa xác minh ngày công bố, ngày chụp hoặc quyền phân phối; gói cộng đồng chỉ có hồ sơ, không kèm ảnh.

## Cover chiến dịch có thời hạn

Có thêm assets/originals/banners/campaign/vlu-k32-welcome-2026.jpg từ bài hướng dẫn nhập học K32 năm 2026. Đây là ảnh đầu bài/chiến dịch có năm và khóa; không phải xác nhận cover Facebook hiện hành. Chỉ mục phân biệt 14 banner website, một cover chiến dịch và một rendition ảnh bìa Facebook theo thời điểm, tổng 16 hồ sơ; không nhân đôi những banner trùng byte.


QS Asia: hai artwork desktop 02/mobile 03 in năm 2025. Tên preview cũ có 2026 đã được sửa; giữ nguyên ảnh và không diễn giải mốc CMS thành năm in trên ảnh.
