# Cập nhật Actions và core

## Cơ chế tự động

Dependabot kiểm tra hằng ngày hai phạm vi: `github-actions` cập nhật tham chiếu
Action bằng full SHA, và npm tại `.github/actions/release-please` cập nhật core
trong manifest/lockfile của wrapper. Mỗi cập nhật mở PR, phải qua CI và review;
không tự merge hoặc chạy `npx ...@latest` trong job release. Lịch kiểm tra không
đồng nghĩa PR xuất hiện ngay: GitHub có cooldown và hàng đợi xử lý.

Workflow `freshness.yml` kiểm tra hằng ngày lúc 06:17 UTC, cho phép dispatch và
dùng issue nhắc việc hiện có. Báo cáo JSON/Markdown đầy đủ được giữ bảy ngày trong
artifact `freshness-<sha>-<run_id>`. Cấu hình lịch chỉ bắt đầu được GitHub xử lý
sau khi vào default branch; CI của PR chưa chứng minh scheduler đã chạy bản mới.

## Kiểm tra mọi Action đang dùng

`scripts/action_dependencies.py` đọc manifest/lockfile tại đúng SHA, xác minh Git
blob, lưu SHA-256/URL và kiểm tra cả wrapper local. Lượt 24/10/2026 đã đọc ba tệp
metadata của mỗi mục: checkout, setup-python, setup-node, upload-artifact,
download-artifact, attest và wrapper Release Please.

Checker đối chiếu dependency trực tiếp giữa package.json và root npm lock,
kiểm kê mọi entry trong lock, rồi truy vấn registry latest cho dependency trực
tiếp, gồm dependency phát triển. Nó không đánh giá mọi range semver, không so
từng dependency bắc cầu với latest, không chạy lifecycle script hoặc rebuild
bundle. Chênh phiên bản là tín hiệu cần review, không phải kết luận lỗ hổng hay
khẳng định bản mới tương thích. Lock khai báo không chứng minh độc lập mọi byte
trong dist của upstream.

Composite/Docker, Action lồng nhau/có subpath hoặc lock format chưa hỗ trợ được ghi
indeterminate. Nhiều lockfile đồng thời, metadata dependency khác chưa hỗ trợ hoặc
packageManager không phải npm cũng cần review, không tự chọn npm lock rồi báo đủ.
Hiện sáu Action từ xa đều là Node 24, có package.json/package-lock.json.
Giới hạn: 32 Action, 256 tên package registry, 4 MiB mỗi tệp metadata và 10.000
entry mỗi lock; truy vấn có timeout. Lỗi truy cập/parser/registry không bị coi là current.

Nếu Action chính thức đã mới nhất nhưng core còn cũ, cần upstream phát hành
hoặc wrapper/fork được review riêng. Repo không tự sửa dependency của các Action
bên thứ ba. Chỉ Release Please hiện có runtime do repo trực tiếp quản lý.

## Wrapper Release Please

docs-contract cũng kiểm tra metadata của toàn bộ Action tại các pin mà PR đề xuất,
giữ JSON trong artifact action-dependencies. Thiếu file/registry hoặc format chưa
hỗ trợ làm check thất bại; chỉ lệch latest không tự chặn vì chưa chứng minh bất
tương thích hoặc lỗ hổng. Khi bước kiểm tra thất bại, báo cáo JSON đã tạo vẫn được
upload để chẩn đoán; job giữ trạng thái thất bại. Như vậy cập nhật SHA có bằng chứng
metadata trước merge.

Phiên bản core thực lấy từ manifest/lockfile của wrapper; lần kiểm tra 24/10/2026
dùng 17.11.2 với lock/integrity riêng, Node 24 trên workflow và Node >=22 khi kiểm
tra local. Core giữ Apache-2.0 của upstream;
wrapper tự biên soạn thuộc MIT. Không dùng core 17.6.0 bundle trong Action v5.0.0.

Workflow cài bằng npm ci --ignore-scripts từ thư mục runtime, chỉ truyền PAT ở
bước chạy wrapper trên main. Adapter giữ policy root/simple/version.txt,
draft và force-tag, cùng output release_created/tag_name/sha cho các job tạo,
attest, gắn asset và publish hiện có. API bị giới hạn origin/timeout; mutation
chỉ được phép ở main push hoặc dispatch.

```console
cd .github/actions/release-please
npm ci --ignore-scripts --no-fund
npm test
```

docs-contract chạy test adapter, API của core thực cài và dry-run bằng token chỉ
đọc qua chính local Action. Dry-run với repo thật
ngày 24/10/2026 đã đọc cấu hình/lập kế hoạch thành công, không tạo PR/Release.
Vòng đời tạo draft, gắn asset và publish bằng wrapper sau merge vẫn cần run thực
tế để xác nhận; không dùng dry-run hoặc test giả lập thay bằng chứng đó.

Khi nâng core, review cả lock diff, engines, license, advisory và API. `$schema`
chỉ là tài liệu cấu hình; freshness nhắc cập nhật schema riêng khi cần, không
coi đổi schema là nâng runtime. Rollback qua PR có chủ đích, giữ nguyên lịch sử
tag/release đã công khai và không chuyển sang tải latest không khóa.
