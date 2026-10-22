> Mọi đường dẫn trong đoạn mã tính từ gốc kit. Hồ sơ nguồn và trạng thái tệp ở `data/asset-sources.json`. Gói cộng đồng chỉ lưu metadata cho ảnh/logo/template chưa rõ quyền phân phối; các tệp đó không kèm trong ZIP này. Không coi đường dẫn tham chiếu là tệp đã được cung cấp.

# Khuôn viên và cơ sở vật chất

Chỉ mục có **29 hồ sơ ảnh** từ các lần chụp dữ liệu trang cơ sở chính: 12 tham chiếu ban đầu và 17 bổ sung ngày 22/10/2026. Ngoài ngoại cảnh, thư viện, xưởng, hội trường và thể thao còn có HUB, media studio, lớp học, canteen, y tế, thực hành Răng Hàm Mặt/Du lịch và hoạt động sân khấu. Đây là metadata trong gói cộng đồng, không phải 29 file ảnh được kèm. Tra `data/reference-index.json` và `data/asset-sources.json` để biết từng nguồn, kích thước và rendition.

Nguồn: https://www.vlu.edu.vn/about-us/campuses-facilities/co-so-chinh

Các hồ sơ giữ riêng ngày quan sát nguồn và ngày chụp chưa xác nhận. Lượt phục hồi nguồn ngày 22/10 tải được nội dung trang campus tiếng Việt, xác nhận đúng 29 URL đã ghi và hash ảnh không đổi. Response rỗng ở lượt trước được giữ như lịch sử trong bằng chứng, không phải hiện trạng kiểm tra mới nhất. Chưa xác nhận hiện trạng mọi chi tiết vào ngày sử dụng. Không gán ảnh cơ sở chính thành Cơ sở 1/Cơ sở 2, không dùng ảnh phối cảnh như ảnh công trình đã hoàn thành. Khi cần tái hiện đúng góc nhìn, cơ sở hoặc phòng chưa có trong danh mục, cần bổ sung ảnh đúng nguồn.

Kit còn có banner website, ảnh thư viện, sự kiện, tốt nghiệp và cộng đồng phục vụ nhiều bối cảnh khác. Đây là tuyển chọn để tạo ảnh, không phải toàn bộ thư viện ảnh mọi cơ sở của VLU. Danh mục không chứa bản vẽ kiến trúc hoặc ảnh 360 độ đầy đủ.

Trang tiếng Anh `https://www.vlu.edu.vn/en/about-us/campuses-facilities/main-campus` được dùng để đối chiếu bổ sung; số liệu 14/29 URL trong lượt trước là snapshot theo response đó. Lượt mới đã đối chiếu đủ 29 URL trên trang tiếng Việt, không suy việc khác URL theo ngôn ngữ là ảnh bị xóa hoặc cơ sở thay đổi. Chưa có bộ ảnh cụ thể đầy đủ cho Cơ sở 1/Cơ sở 2.

## Bối cảnh MSC có nguồn gắn với Cơ sở 2

Ba hồ sơ ảnh từ bài VLU ngày 03/06/2026 bổ sung mô hình trên giường, kho mô hình và phòng quan sát MSC. Bài nguồn xác định MSC ở Cơ sở 2; ngày chụp và hiện trạng chưa xác nhận. Đây là nội thất/bối cảnh mô phỏng, chưa phải bộ ảnh ngoại thất đầy đủ của Cơ sở 2 hoặc Cơ sở 1. Tra `campus_2_msc_references` trong `data/reference-map.json`.
