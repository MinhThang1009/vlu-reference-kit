# Changelog tài nguyên

## 2026-10-22

- Phục hồi truy cập 32 hồ sơ từng lỗi DNS; đối chiếu lại toàn bộ 133 URL tài nguyên, ngữ cảnh 29 ảnh campus, sáu ảnh Lab/MSC và hai logo MSC. Giữ lịch sử lỗi và giới hạn quyền; ghi đầu mối văn bản cần đăng nhập, không thêm artwork.

- Bổ sung sáu hồ sơ ảnh Lab/MSC từ bài VLU, ghi rõ khách THPT và phạm vi Cơ sở 2 theo nguồn. Giữ byte ngoài Git; lưu riêng giới hạn web cache và lỗi DNS mới.

- Đối soát hướng dẫn: sửa trạng thái ảnh bìa, số liệu độ phủ, tên tệp/con trỏ audit và điều kiện mở tài nguyên metadata-only. Ghi lại nguồn mới, lỗi truy cập và phạm vi receipt lịch sử; không thêm artwork.

- Lượt đối soát tiếp theo: thêm ba hồ sơ ảnh Điều dưỡng, sửa mô tả sai chi tiết vai áo và ghi rõ hai ảnh trang ngành là snapshot lịch sử. Ghi riêng lỗi DNS, payload rỗng và kết quả hash mới; giữ artwork ngoài Git.

- Bổ sung 25 hồ sơ nguồn có hash: 17 ảnh bối cảnh/cơ sở vật chất, một ảnh bìa Facebook theo thời điểm và bảy tham chiếu portfolio họa sĩ. Không kèm byte artwork mới trong Git.
- Kiểm tra lại 101 bản ghi remote cũ từ 99 URL; giữ nguyên byte font/vendor/OFL và các asset đã kèm.
- Đối chiếu ảnh bìa qua JSON-LD của website VLU và dữ liệu public cover_photo; giữ riêng ngày quan sát, ngày công bố chưa biết và quyền chưa xác minh.
- Sửa URL dẫn tới trang không tồn tại cho nguồn màu; giữ 14 khoảng trống chính thức.

## 2026-10-17 (đầu vào c487e113ee9a)

- Kiểm kê 226 tệp; đối chiếu 99 URL nguyên bản khớp byte.
- Sửa nhãn năm preview QS Asia; bỏ nguồn IAST chưa xác nhận được; thêm 2 ảnh thực hành Điều dưỡng có nguồn.
- Chuẩn hóa tên/vị trí và mọi tham chiếu đang dùng; thêm path-map, checklist, nguồn mới và QA bản cuối.
- Sửa verifier Windows báo Unlisted file sai và liên kết RECHECK_ROUND2 thiếu.
- Hai biến thể nội bộ/cộng đồng; không gán quyền phân phối rộng rãi cho tài nguyên công khai.
- Các mục chính thức chưa có bằng chứng tiếp tục mở; không xác nhận “đầy đủ 100%”.

### Bổ sung cho bản repository cộng đồng, 17/10/2026

- Kèm LICENSE MIT và NOTICE.md cho phần tự biên soạn; không thay giấy phép bên thứ ba.
- Đồng bộ README, PUBLICATION và manifest. Không thay byte font, swatch hoặc artwork; không thực hiện thêm nghiên cứu nhận diện VLU trong audit repository này.

### Kiểm tra công cụ offline, 18/10/2026

- Ghi rõ Python tối thiểu 3.12 cho verifier trong ZIP; báo cách xử lý trước khi dùng API chưa có trên runtime cũ. Catalogue vẫn không cần Python.

- Verifier trong ZIP từ chối symlink/junction trước khi resolve, kiểm kê không theo thư mục liên kết và báo lỗi đọc manifest/cây thư mục. Không thay byte tài nguyên hoặc kết luận nguồn VLU.

### Đồng bộ catalogue offline, 20/10/2026

- Thêm mục tìm kiếm và liên kết tới `vlu-verified-colors.json` đã có trong gói và sổ nguồn; ghi rõ phạm vi HEX/RGB, chưa xác minh CMYK/Pantone.
- Đối soát các tài nguyên được kèm theo với catalogue và kiểm tra tài nguyên bị giữ lại không có liên kết tải local; cập nhật manifest sau thay đổi.
- Không thay byte tài nguyên, quyền phân phối hoặc kết luận nguồn VLU; không thực hiện nghiên cứu nhận diện mới trong lần sửa catalogue này.

### Lịch sử từ đầu vào

Các mục bên dưới mô tả round cũ, không thay thế bằng chứng hiện tại.

### Bổ sung logo website MSC — 17/10/2026

- Thêm 2 PNG gốc: biểu tượng VLU nền trong suốt và logo tiếng Anh từ website MSC; ghi rõ phạm vi, kích thước và khác biệt màu.
- Kiểm tra tệp tải trực tiếp thay vì phân loại qua ảnh xem trước; không gắn nhãn logo trắng.
- Ghi nhận liên kết quy định sinh viên yêu cầu đăng nhập, chưa có căn cứ để cập nhật catalogue đồng phục.
- Kiểm tra bảo toàn toàn bộ tài sản của bản 220 tệp; tạo lại QA và manifest.

### Cập nhật ngày 17/10/2026 — hợp nhất bộ tham chiếu chung

- Kiểm tra đúng bản không có (1): đầu vào 130 tệp, 93 tài sản trong sổ nguồn.
- Giữ nguyên byte của toàn bộ tài sản đầu vào; bổ sung 18 tài sản gốc có nguồn VLU.
- Giữ các nhóm nghệ thuật, công nghệ, thể thao, cộng đồng và tốt nghiệp riêng của bản này; tránh sao chép lại 14 banner trùng byte.
- Mở rộng trang phục với ảnh hoạt động 2026 và ảnh chuyên ngành/nghi lễ; không gán thành catalogue mới nhất.
- Thêm cover K32, bảng trang phục, thumbnail, trang duyệt ảnh và chỉ mục dùng chung.
- Đối chiếu lại 12 ảnh gốc riêng với URL nguồn: tất cả khớp SHA-256; tạo lại QA và manifest cho bản cuối.

### Những phần đã cập nhật ngày 16/10/2026

- Giữ nguyên bảy tài sản hình ảnh/vector gốc của bản trước; kiểm tra lại ba tệp logo từ URL nguồn.
- Thêm favicon gốc của website, bốn ảnh khuôn viên/thư viện/sinh viên và một ảnh sự kiện 2022.
- Bổ sung 26 font static đúng các khai báo CSS của hai họ font trên website; bốn font variable và giấy phép OFL từ Google Fonts.
- Thêm bản xuất PNG/PDF từ SVG gốc; swatch CSS/GPL/ASE và ba bố cục SVG tự biên soạn có ghi rõ nguồn gốc.
- Thêm mẫu chữ tiếng Việt, trang xem nhanh offline, thông tin nhận diện có nguồn và hồ sơ kiểm tra toàn bộ tệp.
- Sửa diễn giải màu: PNG tiếng Việt lịch sử có đỏ #D21F36, SVG website dùng #D72134; không tô lại tệp gốc.
- Nêu rõ các phần chưa có tài liệu gốc: brandbook, logo tiếng Việt vector hiện hành, quy chuẩn đặt logo, màu in ấn và tài sản mascot rời.
- Không đưa một SVG trùng byte vào ZIP; không dùng ảnh sự kiện có logo cũ trên màn hình làm tham chiếu nhận diện hiện hành.

#### Lượt rà soát tiếp theo

- Bổ sung diễn giải có nguồn về tầm nhìn, sứ mệnh và định hướng chuẩn bị hình ảnh.
- Mở rộng kiểm tra đủ 30 font với bộ ký tự tiếng Việt NFC và NFD, ghi phạm vi kiểm tra và phiên bản từng font.
- Bổ sung hai bảng mẫu cho toàn bộ 30 font và đường dẫn đến chỉ mục ảnh, mascot trên trang xem nhanh.
- Thêm đối chiếu từng nhóm thành phần; các mục chưa có brandbook/artwork chính thức vẫn giữ trạng thái chưa xác minh.

#### Mở rộng thành bộ tham chiếu dùng chung

- Bổ sung 10 ảnh gốc VLU: họa thất, thời trang, thiết kế sản phẩm, AR/VR, phòng máy tính, tennis, hồ bơi, hội trường, tốt nghiệp 2025 và tình nguyện 2025; tổng 19 ảnh tham khảo.
- Thêm hướng dẫn dùng lại, hồ sơ chung, mẫu yêu cầu trống, ví dụ đa chủ đề, bản đồ tư liệu, quy trình tạo ảnh và cập nhật.
- Thay mẫu font chứa thông tin sinh viên bằng chữ trung tính; dựng lại cả ba PNG mẫu và kiểm tra 30 TTF với NFC/NFD.
- Bỏ mặc định bài hội sách, tên/mã sinh viên khỏi hướng dẫn và bố cục; hội sách còn là một bối cảnh tùy chọn.
- Giữ nguyên mọi tài nguyên gốc trước đó; chỉ thay các tệp dẫn xuất liên quan đến mẫu chữ và chân trang custom.
- Ghi riêng ngày hiển thị và trường ngày CMS khác nhau ở bài tốt nghiệp 2025; không dùng chúng làm ngày chụp ảnh.
- Giữ nguyên trạng thái các khoảng trống tài liệu chính thức; không gọi bộ tham khảo này là toàn bộ brandbook VLU.

#### Bổ sung theo yêu cầu đồng phục và banner

- Lưu 14 banner gốc từ cấu hình website VLU: 7 desktop và 7 mobile; ghi nguồn, kích thước, hash, trường dữ liệu và giới hạn theo kênh.
- Thêm ảnh polo/vật phẩm 2024, hai ảnh trang phục thực hành theo bài ngành nhà hàng 2026 và một ảnh từ bài lễ tốt nghiệp 2026; tổng 23 ảnh tham khảo.
- Thêm hồ sơ trang phục phân theo bối cảnh, không gắn nhãn đã có toàn bộ mẫu đồng phục mới nhất.
- Ghi rõ ảnh bìa Facebook hiện hành chưa xác minh được; không thay bằng thiết kế tự dựng.
- Bổ sung đối chiếu phạm vi yêu cầu với trạng thái bằng chứng; tiếp tục giữ các khoảng trống tài liệu gốc.
