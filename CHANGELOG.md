# Changelog

## 0.1.0 (2026-10-18)


### Sửa lỗi

* **ci:** ràng buộc snapshot kiểm tra release ([42720a7](https://github.com/MinhThang1009/vlu-reference-kit/commit/42720a7af4ea37250ca49161e2762f1c918d508a))
* **release:** kiểm tra lần chạy CI mới nhất ([b70bbae](https://github.com/MinhThang1009/vlu-reference-kit/commit/b70bbaea6ef80fbcb048ea54d6dd027ad3e208d6))
* sửa tính toàn vẹn và luồng phát hành kit ([fab0c8f](https://github.com/MinhThang1009/vlu-reference-kit/commit/fab0c8f47a8634b36cd3e0e31cd075baf46e4947))
* sửa tính toàn vẹn và luồng phát hành kit ([5c59de0](https://github.com/MinhThang1009/vlu-reference-kit/commit/5c59de0f5929914148347f3b3591179bed7a4a5d))

## Changelog

## Chưa phát hành

* Audit vòng tiếp theo: từ chối phiên bản sai SemVer/ngoài ASCII, tên không tương thích Windows và lỗi đọc cây thư mục; đồng bộ hướng dẫn với vòng PR Release Please đã chạy.

* Fresh audit repo: chặn JSON không chuẩn và metadata sai kiểu; báo lỗi encoding có kiểm soát.
* Build từ snapshot đã xác minh, kiểm tra byte/CRC trước khi thay ZIP; kèm MIT và thông báo phạm vi.
* Khóa dependency Python/npm, vá hai advisory bắc cầu và ghi rõ advisory braces chưa có bản vá.
* Thêm release thủ công, ràng buộc tag/dispatch/CI cùng commit, tách build, attest và publish.
* Sửa allowlist đồng bộ setup-node, ghi rõ khác biệt nguồn helper với tag scaffold đã xuất bản.
* Cài workflow/config/manifest Release Please sau khi xác minh secret tồn tại; tách khỏi package công cụ, kiểm tra metadata phiên bản đồng bộ và giữ bước publish riêng sau CI.

* Nhập bản cộng đồng có metadata, font/OFL, bảng màu và mẫu chữ; loại artwork chưa rõ quyền phân phối.
* Thêm community-health files, issue/PR templates, ownership, kiểm tra kit và đóng gói.
* Thêm CI có action ghim SHA, policy runtime, kiểm tra tài liệu và canary upstream.
* MIT áp dụng cho mã/tài liệu tự biên soạn; quyền bên thứ ba giữ riêng.
