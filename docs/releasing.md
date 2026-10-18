# Phát hành bản cộng đồng

Phạm vi phát hành là `kit/`, gồm MIT cho phần tự biên soạn, thông báo phạm vi,
font/OFL, catalogue và hồ sơ nguồn. Artwork chưa rõ quyền không được thêm vào
ZIP. Tag phiên bản kit không phải phiên bản nhận diện do VLU ban hành.

## Điều kiện

Người duy trì review/merge PR trước, đợi `ci-success` và `docs-contract` đạt trên
đúng commit `main`. Chọn phiên bản SemVer mới dạng `vMAJOR.MINOR.PATCH` theo
thay đổi của cấu trúc metadata, đường dẫn và cách dùng kit; chưa có API ổn định
thì dùng dòng `v0.y.z`. Không sửa nội dung bản đã phát hành.

Release Please dùng strategy `simple` cho kit, tách khỏi `package.json` chỉ phục
vụ lint. `version.txt` hiện là đề xuất ban đầu `0.1.0`; manifest rỗng thể hiện
chưa có phiên bản đã phát hành. Đây chưa phải tag/release và chưa phải phiên bản
do người dùng xác nhận. Người duy trì có thể sửa đề xuất trước PR phát hành đầu.
Sau đó Release Please cập nhật manifest, `version.txt` và CHANGELOG trong PR;
CI từ chối metadata phiên bản không đồng bộ. Phiên bản trong tag phải khớp
`version.txt` của commit đã qua CI.

Chế độ đã chuẩn bị là **quản lý PR**, `skip-github-release: true` ở cả action
và config. Merge PR phiên bản không tự tạo tag/release. Không cài dispatcher
`push.tags` cạnh luồng này. Dùng secret `RELEASE_PLEASE_TOKEN`, chỉ cấp cho repo
này với Contents, Pull requests và Issues: read/write để PR do bot tạo có thể
kích hoạt CI. Không dùng token local của người duy trì làm secret hoặc gửi giá
trị token vào chat/log. Xem [credential upstream](https://github.com/googleapis/release-please-action#github-credentials).

Tại lượt audit 18/10/2026, secret chưa hiện trong API ở lần preflight gần nhất;
workflow Release Please ở [bản chờ cài](release-please.yml.example), chưa tuyên bố đã chạy hoặc kích
hoạt. Cần preflight xác nhận đúng tên secret trước khi đưa workflow vào
`.github/workflows/release-please.yml`; chỉ kiểm tra tên không chứng minh scope
hoặc token còn hiệu lực. Giới hạn này sẽ được cập nhật sau khi kiểm tra lại.

Workflow [release.yml](../.github/workflows/release.yml) chỉ chạy thủ công từ
`main`. Input `tag` phải tồn tại và trỏ đúng `commit_sha` đầy đủ. Commit đó phải
trùng SHA của lần dispatch trên `main` để provenance cùng nguồn, thuộc lịch sử
`main` và có hai check thành công từ GitHub Actions. Nếu `main` tiến lên giữa
lúc tạo tag và dispatch, dừng và review lại phiên bản/commit, không di chuyển
tag đã công bố để ép khớp.

## Thực hiện khi có yêu cầu phát hành

1. Xác nhận phiên bản mới, commit đã qua CI, thay đổi và quyền phân phối.
2. Tạo annotated tag tại commit đó, push đúng tag. Không tự tạo tag trong build.
3. Trong Actions, chạy **Phát hành cộng đồng** từ `main`, nhập tag và full SHA.
4. Build kiểm tra kit, test và ZIP bằng token chỉ đọc. Artifact chuyển trong cùng
   workflow run, bước download kiểm tra digest; job attest và publish không
   checkout/chạy mã dự án với token có quyền ghi.
5. Workflow tạo hoặc sửa draft, đính kèm ZIP/checksum, kiểm tra tag lại rồi
   publish. Rerun có thể sửa draft; bản đã công bố bị từ chối thay asset.
   Rerun failed jobs khi artifact của build còn hiệu lực (giữ 1 ngày); sau đó
   review và chạy một workflow mới. Không dùng `--clobber` lên bản đã công bố.

## Kiểm chứng bản tải về

Kiểm tra SHA-256 của ZIP so với `SHA256SUMS.txt`, giải nén và chạy
`python tools/verify-manifest.py` từ gói. Kiểm tra attestation bằng GitHub CLI
(thay đường dẫn ZIP, dùng repository và workflow chính xác):

```console
gh attestation verify dist/vlu-reference-kit-community.zip --repo MinhThang1009/vlu-reference-kit --signer-workflow MinhThang1009/vlu-reference-kit/.github/workflows/release.yml
```

Đối chiếu thêm digest, commit nguồn trong provenance và tag/commit thực tế.
Attestation chứng minh nguồn build, không chứng minh quyền artwork hoặc kit đầy
đủ. Tại 17/10/2026 mới kiểm tra cấu hình, preflight, test và artifact build;
chưa tạo tag, publish release hoặc chạy thử luồng attest trên GitHub. Chưa bật
immutable releases thì không tuyên bố GitHub đã khóa tag/asset. Tham khảo
[attestation](https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations)
và [immutable releases](https://docs.github.com/en/code-security/concepts/supply-chain-security/immutable-releases).
