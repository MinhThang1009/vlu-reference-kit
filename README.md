<div align="center">

# VLU Reference Kit

Bộ tham chiếu cộng đồng có nguồn cho hình ảnh liên quan đến Trường Đại học Văn Lang.

[![CI](https://github.com/MinhThang1009/vlu-reference-kit/actions/workflows/ci.yml/badge.svg)](https://github.com/MinhThang1009/vlu-reference-kit/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

</div>

## 1. Tổng quan

Tổng hợp dữ liệu nhận diện, bảng màu, font, metadata và hướng dẫn để dùng lại khi tạo hình ảnh về VLU. Phù hợp nhiều chủ đề như học tập, khuôn viên, đồng phục, sự kiện và truyền thông; hội sách chỉ là một ví dụ.

**Đây là bộ tham chiếu cộng đồng, chưa phải brandbook đầy đủ hoặc bộ nhận diện chính thức được VLU phê duyệt.** Có 46 tài nguyên kèm theo và metadata cho 177 tài nguyên ảnh/artwork chưa rõ quyền phân phối. Gói công khai không chứa các byte bị loại.

## 2. Bắt đầu

Clone hoặc tải mã nguồn rồi giải nén, mở [kit/index.html](kit/index.html) bằng trình duyệt. Dùng tìm kiếm để chọn bối cảnh, đọc ghi chú nguồn và quyền trước khi sử dụng. Một số mục chỉ có liên kết nguồn vì artwork không được kèm theo.

Đọc [audit tài nguyên 24/10/2026](kit/audit/asset-audit-2026-10-24.md) để xem kết quả đối soát gần nhất, nguồn và giới hạn quyền phân phối.

Xem [hướng dẫn kit](kit/START_HERE.md), [thông tin nền](kit/data/brand-facts.json), [nguồn tài nguyên](kit/data/asset-sources.json) và [khoảng trống chính thức](kit/audit/official-gaps.md). Dùng [mẫu yêu cầu](kit/prompts/brief-template.json) cho ảnh mới; không mặc định nhân vật, số người, trang phục, phong cách hoặc thời gian.

## 3. Cấu trúc và cập nhật

`kit/` là bản cộng đồng: assets, metadata, hướng dẫn và snapshot bằng chứng nguồn. `scripts/` kiểm tra repo và đóng gói; `tests/` kiểm tra hồi quy công cụ. Xem [phạm vi nhập](kit/PUBLICATION.md) để phân biệt bằng chứng ZIP nguồn với CI hiện tại.

Giữ tên theo quy ước trong [README kit](kit/README.md). Chỉ đổi mục chưa phù hợp, cập nhật mapping và tham chiếu. Kiểm chứng dữ kiện biến động như đồng phục mới nhất, cover đang dùng và lịch sự kiện khi cần; không suy từ ảnh sang quy chuẩn toàn trường.

## 4. Kiểm tra và đóng gói

Mở catalogue không cần cài dependency. Công cụ kit dùng Python theo [.github/runtime-support.json](.github/runtime-support.json); kiểm tra tài liệu dùng policy riêng trong [.github/ci-toolchain.json](.github/ci-toolchain.json).

```console
python scripts/validate_kit.py
python -m unittest discover -s tests -v
python -m pip install --require-hashes -r requirements-docs.lock
python -m unittest discover -s tests/docs -v
npm ci --ignore-scripts
python scripts/patch_braces.py
node --test tests/test_braces_guard.cjs tests/test_markdown_parser.cjs
python scripts/validate_tooling.py
python scripts/validate_scaffold.py --repository-root .
python scripts/ci_toolchain.py run-markdownlint
python scripts/build_community_package.py
```

Gói ZIP và SHA-256 được tạo trong `dist/`, không được commit. ZIP gồm MIT và thông báo phạm vi, font giữ OFL. Chỉ thay ZIP sau khi kiểm tra snapshot và byte trong archive; ZIP và checksum được thay từng tệp, không phải giao dịch hai tệp. Nếu bị ngắt ở bước bàn giao, chạy lại build và kiểm chứng checksum trước khi dùng.

Repo dùng [quy trình release](docs/releasing.md): tạo draft tự động, build, attest, đính kèm ZIP/checksum và công khai tự động khi mọi kiểm tra đạt. Workflow thủ công vẫn là đường sửa chữa cho các draft cũ. CI kiểm tra Linux và Windows; canary định kỳ chỉ cảnh báo thay đổi upstream, không tự nâng phiên bản. Xem [dependency và giới hạn đã biết](docs/dependencies.md).

[Release Please](.github/workflows/release-please.yml) quản lý PR cập nhật phiên bản/changelog và tạo GitHub Release nháp sau khi PR phiên bản được merge. Các job kế tiếp checkout đúng SHA phát hành, kiểm tra kit, tạo `vlu-reference-kit-community.zip` và `SHA256SUMS.txt`, attest, đính kèm cả hai rồi công khai Release. Cấu hình `skip-github-release: false`, `draft: true` và `force-tag-creation: true` tạo draft/tag ngay để pipeline xác minh target trước khi công khai. Workflow dùng secret riêng, không tự merge PR; xem quy trình release trước khi tạo PR phiên bản.

## 5. Đóng góp và hỗ trợ

Dùng [Issues](https://github.com/MinhThang1009/vlu-reference-kit/issues) cho lỗi dữ liệu hoặc yêu cầu tài nguyên; kèm URL gốc, phạm vi áp dụng và bằng chứng quyền phân phối. Đọc [CONTRIBUTING](CONTRIBUTING.md), [SUPPORT](SUPPORT.md) và [GOVERNANCE](GOVERNANCE.md). Người duy trì là [MinhThang1009](https://github.com/MinhThang1009), xem [CODEOWNERS](.github/CODEOWNERS).

Báo cáo nhạy cảm theo [SECURITY](SECURITY.md). Tuân thủ [Code of Conduct](CODE_OF_CONDUCT.md); giữ bản tiếng Anh Contributor Covenant 3.0 vì chưa có bản tiếng Việt chính thức cùng phiên bản tại ngày kiểm tra.

## 6. Giấy phép và bằng chứng

Mã nguồn và tài liệu tự biên soạn dùng [MIT](LICENSE). Font giữ SIL OFL, Code of Conduct giữ CC BY-SA 4.0; xem [THIRD_PARTY_NOTICES](THIRD_PARTY_NOTICES.md) và [nguồn upstream](docs/upstream-provenance.json).

Snapshot audit nguồn có 53 hạng mục, còn 14 hạng mục chưa đủ căn cứ chính thức và một kiểm tra render catalogue chưa thực hiện được; không dùng kết quả kiểm tra kỹ thuật để đóng các khoảng trống đó. Việc tài nguyên xuất hiện công khai không tự chứng minh quyền phân phối lại.
