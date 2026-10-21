# Dependency công cụ

Catalogue chạy offline không cần cài package. Công cụ kit dùng Python standard
library; các package dưới đây chỉ phục vụ kiểm tra tài liệu.

Công cụ repo cần Python 3.12 trở lên, kể cả wrapper Markdown lint vì dùng
kiểm tra junction của `pathlib`. `tooling-python-minimum` ghi mức tối thiểu này;
`documentation-python: 3.x` vẫn chọn Python ổn định mới nhất trên CI. Mức tối
thiểu của package upstream riêng lẻ không thay yêu cầu của công cụ repo.

## Cài và cập nhật

```console
python -m pip install --require-hashes -r requirements-docs.lock
npm ci --ignore-scripts
python scripts/patch_braces.py
node --test tests/test_braces_guard.cjs tests/test_markdown_parser.cjs
python scripts/validate_tooling.py
```

`requirements-docs.txt` ghi dependency Python trực tiếp. Lockfile ghi cả
`mdurl` bắc cầu và hash các bản phân phối chưa bị yanked trên PyPI. Khi cập nhật,
resolve trong môi trường sạch, đối chiếu metadata PyPI của đúng phiên bản rồi
cập nhật lock và kiểm tra cài với `--require-hashes`. Hash không khóa compiler
hoặc dependency build khi pip phải biên dịch sdist.

Bộ đối soát của repo chỉ nhận `name==version`, comment, khoảng trắng quanh
`==`, dòng nối bằng `\` và tùy chọn `--hash=sha256:<64 ký tự hex thường>`.
Mỗi package trong lock phải có hash; tên được chuẩn hóa không phân biệt hoa/thường,
gộp `-`, `_`, `.` để bắt khai báo trùng. Range, wildcard, extras, marker,
URL/path, include `-r`/`-c` và tùy chọn khác bị báo lỗi để review phạm vi trước
khi dùng. Đây là subset có chủ đích, không phải parser đầy đủ của pip hoặc bộ
xác thực mọi phiên bản PEP 440. Pip vẫn kiểm tra cú pháp và hash khi cài thật.
Freshness dùng chung parser này: không bỏ qua include, khai báo trùng hoặc
dòng nối chưa kết thúc; lockfile thiếu hash cũng được ghi là `indeterminate`.
Hash được kiểm tra định dạng ở bước đọc; việc xác minh byte package vẫn do pip
thực hiện khi cài bằng `--require-hashes`.

Phiên bản Markdown lint trong `.github/ci-toolchain.json` phải đồng bộ
`package.json` và `package-lock.json`. Chạy `npm install --package-lock-only
--ignore-scripts` sau thay đổi có chủ đích, review toàn bộ lock diff rồi
`npm ci --ignore-scripts`, `npm audit` và lint. Dependabot theo dõi pip, npm
và Actions; PR cập nhật Python cần đồng bộ lock có hash trước khi merge.

Kiểm kê workflow để đối chiếu SHA pin đọc từng thư mục bằng một lượt quét cho
cả `.yml` và `.yaml`. Lỗi đọc được báo rõ; freshness ghi trạng thái
`indeterminate`, không coi danh sách đọc được một phần là `current`. Khi gặp
lỗi này, kiểm tra đường dẫn/quyền đọc và chạy lại trước khi cập nhật pin.
CLI `sync_action_pins.py` mặc định chỉ quét `.github/workflows` của repo này;
dùng `--workflow-directory` khi cần chọn thư mục khác hoặc lặp tùy chọn để
chọn nhiều thư mục. Công cụ cần token đọc API trong `GITHUB_TOKEN`; mặc định
chỉ liệt kê thay đổi dự kiến, chỉ ghi khi có `--write` sau khi đã review.

## Advisory tại 17/10/2026

Override `smol-toml` 1.9.1 sửa
[GHSA-r4xh-jqrq-34v2](https://github.com/advisories/GHSA-r4xh-jqrq-34v2).
Override `katex` 0.18.2 sửa
[GHSA-238p-pmpm-9mq7](https://github.com/advisories/GHSA-238p-pmpm-9mq7).
Đây là các dependency bắc cầu đã có, chưa thêm thư viện ứng dụng.

[GHSA-vfj7-8cjw-p6xm](https://github.com/advisories/GHSA-vfj7-8cjw-p6xm)
trong `braces` chưa có bản vá được công bố. npm audit báo 5 package bị ảnh hưởng
trên cùng chuỗi `braces → micromatch → fast-glob/globby → markdownlint-cli2`,
không phải 5 lỗ hổng gốc độc lập. Đây là advisory High của package. Trong repo,
đầu vào nguy hiểm là glob có lồng ngoặc sâu; không có dịch vụ nhận glob công khai.
PR chạy trên runner GitHub, token chỉ đọc, không secrets, có timeout. Người chạy
lint local chỉ nên dùng config đã review; không có kết luận dependency sạch.
Giữ override có lý do, cập nhật khi upstream vá và review lại ảnh hưởng thực tế.

### Cập nhật parser Markdown, 21/10/2026

`markdownlint-cli2` 0.23.3 ghim `markdown-it` 15.0.1. Override parser hiện có
lên 15.0.3 để xử lý ba advisory DoS:
[smartquotes](https://github.com/advisories/GHSA-r7fv-28h4-cvq7),
[inline HTML](https://github.com/advisories/GHSA-vfgh-jcmw-g37q) và
[reference nhiều dòng](https://github.com/advisories/GHSA-gfr2-rv44-r23c).
Hai advisory đầu phụ thuộc tùy chọn; reference nhiều dòng ảnh hưởng cả mặc định.
CLI tạo parser với `html: true`, còn `typographer` không được bật mặc định.
Đây là dependency công cụ đọc Markdown, không phải dịch vụ production công khai.

Đã đối chiếu [changelog upstream 15.0.3](https://github.com/markdown-it/markdown-it/blob/15.0.3/CHANGELOG.md)
và integrity npm, cập nhật lockfile rồi cài bằng `npm ci --ignore-scripts`.
`tests/test_markdown_parser.cjs` dùng parser được resolve từ chính CLI, chạy
đầu vào tổng hợp trong tiến trình con giới hạn năm giây và kiểm tra render
tiếng Việt thông thường. Test bao quát reference, inline HTML và smartquotes;
không chứng minh mọi loại Markdown đều có giới hạn độ phức tạp.
Advisory `braces` và mitigation riêng vẫn được giữ rõ, không bị coi là đã sửa
bởi cập nhật parser này.

### Bản vá cục bộ ngày 18/10/2026

`scripts/patch_braces.py` kiểm tra đúng version 3.0.3 và SHA-256 của `lib/parse.js`
đã đối chiếu archive npm canonical, rồi giới hạn AST ở 100 cấp cho cả ngoặc nhọn
và ngoặc tròn. Đầu vào sâu hơn bị từ chối bằng `SyntaxError` trước khi các walker
đệ quy chạy. Không phụ thuộc `maxDepth` do caller đưa vào. Chuỗi escape/quote
và glob bình thường vẫn được kiểm thử.

Chạy patch sau mỗi `npm ci --ignore-scripts`. Wrapper `ci_toolchain.py
run-markdownlint` cũng xác minh/áp dụng patch trước khi chạy lint. CI thử các
API nhận chuỗi thực của braces và đường gọi qua micromatch. Nếu version hoặc
source hash đổi, workflow dừng để review, không tự bỏ qua guard. Không có
install hook hoặc dependency mới; không commit `node_modules`.

Wrapper chạy binary cục bộ khớp policy bằng Node, không dùng `npx` tải/cached
một cây dependency khác. Chạy CLI ngoài wrapper, thay `node_modules` sau khi
patch hoặc tự dựng AST nằm ngoài đường chạy được kiểm chứng này.

Phạm vi là parser nhận chuỗi trong toolchain này. Không bảo vệ AST do caller
tự dựng truyền thẳng vào walker, mọi dạng regex DoS hoặc lỗi dependency khác.
Không dùng guard làm sandbox cho code/config không tin cậy. `npm audit` vẫn
báo advisory vì package thực vẫn là 3.0.3; không đổi giả phiên bản hoặc ẩn cảnh
báo. Khi upstream có bản sửa chính thức, review và thay mitigation có chủ đích.

Metadata PyPI ngày kiểm tra chưa báo advisory cho ba package Python đã khóa.
Đây là bằng chứng của nguồn đó tại thời điểm kiểm tra, không chứng minh mọi
package không có lỗ hổng.
