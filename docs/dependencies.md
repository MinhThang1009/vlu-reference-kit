# Dependency công cụ

Catalogue chạy offline không cần cài package. Công cụ kit dùng Python standard
library; dependency tài liệu và runtime phát hành được quản lý riêng.

Công cụ repo cần Python 3.12 trở lên, kể cả wrapper Markdown lint vì dùng
kiểm tra junction của `pathlib`. `tooling-python-minimum` ghi mức tối thiểu này;
`documentation-python: 3.x` vẫn chọn Python ổn định mới nhất trên CI. Mức tối
thiểu của package upstream riêng lẻ không thay yêu cầu của công cụ repo.

## Cài và cập nhật

Xem [cập nhật Actions và core](action-updates.md) về kiểm tra manifest/lockfile
upstream, lịch Dependabot và wrapper Release Please do repo quản lý.

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
Chỉ dòng vật lý không phải comment và kết thúc ngay bằng `\` được nối;
comment nguyên dòng có `\` cuối không được nuốt dòng kế tiếp. Khoảng trắng
sau `\` không tạo continuation. Comment inline vẫn được loại sau khi nối,
theo [thứ tự xử lý của pip](https://pip.pypa.io/en/stable/reference/requirements-file-format/#comments).
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
UTF-8 BOM đầu workflow không được che khuất các Action trong flow mapping.
Khi cập nhật pin, giữ BOM, kiểu xuống dòng và nội dung scalar còn lại.

## Advisory tại 17/10/2026

Override `smol-toml` 1.9.1 sửa
[GHSA-r4xh-jqrq-34v2](https://github.com/advisories/GHSA-r4xh-jqrq-34v2).
Override `katex` 0.18.2 sửa
[GHSA-238p-pmpm-9mq7](https://github.com/advisories/GHSA-238p-pmpm-9mq7).
Đây là các dependency bắc cầu đã có, chưa thêm thư viện ứng dụng.

Tại ngày 17/10/2026,
[GHSA-vfj7-8cjw-p6xm](https://github.com/advisories/GHSA-vfj7-8cjw-p6xm)
trong `braces` được phân loại High, chưa có bản vá được công bố. Khi đó npm audit
ghi nhận 5 package trên cùng chuỗi
`braces → micromatch → fast-glob/globby → markdownlint-cli2`, cùng một advisory gốc.
Đây là bằng chứng lịch sử; trạng thái mới được ghi bên dưới.

### Cập nhật trạng thái braces, 25/10/2026

GitHub đã [rút advisory ngày 23/10/2026](https://github.com/advisories/GHSA-vfj7-8cjw-p6xm)
vì đánh giá vấn đề không thể khai thác thực tế. Không có bản vá upstream mới được
công bố trong hồ sơ đó. Hai lượt `npm audit --json --ignore-scripts` ngày 25/10
qua registry npm canonical báo 0 advisory: cây công cụ root có 89 entry và runtime
Release Please có 162 entry. Đây là kết quả của nguồn và thời điểm kiểm tra,
không bảo đảm mọi dependency hết lỗi.

Giữ guard AST 100 cấp như giới hạn hành vi parser đã được kiểm thử, cùng version,
hash và phạm vi bên dưới. Việc rút advisory không tự thay đổi byte parser; lời
nhắc của công cụ chỉ xác nhận guard, không khẳng định scanner còn báo advisory.
PR chạy trên runner GitHub với token chỉ đọc, không secrets và có timeout;
lint local vẫn cần config đã review. Snapshot 17/10 và 18/10 trong provenance
được giữ nguyên, kèm hồ sơ cập nhật trạng thái ngày 25/10.

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
Giới hạn AST riêng của `braces` vẫn được giữ; trạng thái advisory được đối chiếu
riêng trong mục cập nhật ngày 25/10 ở trên.

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
Không dùng guard làm sandbox cho code/config không tin cậy. Package vẫn là 3.0.3;
kết quả `npm audit` phụ thuộc dữ liệu advisory tại thời điểm chạy. Không đổi giả
phiên bản hoặc ẩn cảnh báo. Khi upstream có bản sửa chính thức, review và thay
mitigation có chủ đích.

Metadata PyPI ngày kiểm tra chưa báo advisory cho ba package Python đã khóa.
Đây là bằng chứng của nguồn đó tại thời điểm kiểm tra, không chứng minh mọi
package không có lỗ hổng.

### Cập nhật freshness ngày 23/10/2026

Issue #49 ghi nhận pin Actions và CLI đã có phiên bản upstream mới.
Đối chiếu [setup-python v7.1.0](https://github.com/actions/setup-python/releases/tag/v7.1.0)
và tag canonical trước khi thay bảy vị trí bằng SHA
`6d4fd22b20465ccc0f7354476588e8df7c9ca0e0`. Action vẫn dùng Node 24;
đã review manifest, nguồn setup/install/find/cache, lockfile và các entrypoint
bundled tại đúng commit. Hash/giới hạn review được ghi trong
`upstream-provenance.json`; chưa tái build độc lập toàn bộ bundle upstream.
Không bật mirror hoặc mirror-token mới. Quyền job, checkout và điều kiện
pip cache chỉ trên push vào main được giữ nguyên.

[markdownlint-cli2 0.24.0](https://github.com/DavidAnson/markdownlint-cli2/releases/tag/v0.24.0)
yêu cầu Node >=22, dùng markdownlint 0.42.0, markdown-it 15.0.3 và js-yaml
5.4.3. Đã đồng bộ policy, manifest, lock và provenance từ registry canonical;
cài bằng `npm ci --ignore-scripts`, chạy guard parser, test và lint. Các
override đã review vẫn được giữ. Giới hạn AST ở trên không tự thay đổi theo
cập nhật freshness hoặc CI xanh; trạng thái advisory cần đối chiếu nguồn riêng.

### Lockfile của Action upstream, 25/10/2026

Kết quả 0 ở trên chỉ áp dụng cây npm root và runtime Release Please do repo quản
lý. Lượt kiểm tra riêng 12 truy vấn registry trên lockfile tại đúng SHA của sáu
Action từ xa ghi nhận các số sau; không cài package hoặc chạy bundle upstream.
Nguồn, hash và URL advisory nằm trong mục `upstream_action_lock_audit_2026_10_25`
của [hồ sơ provenance](upstream-provenance.json).

| Action | Tất cả package | Bỏ dev |
| --- | ---: | ---: |
| actions/attest | 21 | 8 |
| actions/checkout | 7 | 1 |
| actions/download-artifact | 17 | 6 |
| actions/setup-node | 3 | 2 |
| actions/setup-python | 2 | 1 |
| actions/upload-artifact | 15 | 5 |

Đây là số bản ghi package/Action do npm trả về, có cả metavulnerability lan
truyền qua dependency; không phải số CVE duy nhất hoặc số lỗi đã chứng minh khai
thác được trong repo. Tổng nhóm bỏ dev là 23 bản ghi; 47 advisory gốc được đọc
lại qua GitHub API, chưa có mục nào bị rút tại thời điểm kiểm tra.

Ví dụ, lock của download-artifact ghi fast-xml-parser 5.3.4, nằm trong phạm vi
[GHSA-m7jm-9gc2-mpf2](https://github.com/advisories/GHSA-m7jm-9gc2-mpf2).
Advisory cần ngữ cảnh xử lý XML không tin cậy và dùng kết quả ở sink nhạy cảm.
Đã đối chiếu byte tám entrypoint bundle với Git blob và SHA-256, kiểm kê 74 tệp
source và đọc một số đường gọi. Việc này chưa chứng minh phiên bản thư viện,
mọi đường gọi hoặc khả năng khai thác trong bundle. Mức Critical của registry
không tự trở thành mức rủi ro Critical cho repo.

Các điều kiện ở một số đường gọi đã được ghi nhận: parser CSV của attest dùng
`columns: false`; setup-node nhận version trực tiếp trước nhánh đọc file; các
bước download hiện chọn artifact theo tên, không dùng nhánh pattern. Đây là
quan sát có phạm vi, chưa loại trừ các đường HTTP/XML hoặc SDK lồng nhau.

[Issue #61](https://github.com/MinhThang1009/vlu-reference-kit/issues/61) vẫn theo
dõi chênh lệch upstream. Override npm tại root không thay byte của Action đã
ghim. Khắc phục cần bản phát hành upstream hoặc fork/wrapper được review riêng,
gồm lockfile, bundle, đường gọi và kiểm thử workflow; chưa tuyên bố đã xử lý các
advisory này chỉ vì CI đạt hoặc pin Action đã là bản chính thức mới nhất.
Quyết định ngày 25/10 là giữ pin chính thức và theo dõi upstream; chưa triển
khai fork/wrapper cho sáu Action này hoặc bỏ qua cảnh báo.
