# Phát hành bản cộng đồng

Phạm vi phát hành là `kit/`, gồm MIT cho phần tự biên soạn, thông báo phạm vi,
font/OFL, catalogue và hồ sơ nguồn. Artwork chưa rõ quyền không được thêm vào
ZIP. Tag phiên bản kit không phải phiên bản nhận diện do VLU ban hành.

## Điều kiện

Người duy trì review/merge PR trước, đợi `ci-success` và `docs-contract` đạt trên
đúng commit `main`. Chọn phiên bản SemVer mới dạng `vMAJOR.MINOR.PATCH` theo
thay đổi của cấu trúc metadata, đường dẫn và cách dùng kit; chưa có API ổn định
thì dùng dòng `v0.y.z`. Không sửa nội dung bản đã phát hành.

CI và bộ kiểm tra phát hành cùng xác thực `.github/release-policy.json`:
`default_branch` phải là chuỗi không rỗng, `required_checks` là danh sách tên
không rỗng/không trùng và `actions_app_id` là số nguyên dương. Policy rỗng
không được dùng để bỏ qua đối chiếu CI; dữ liệu sai bị từ chối trước khi gọi
GitHub API.

Release Please dùng strategy `simple` cho kit, tách khỏi `package.json` chỉ phục
vụ lint. Đọc phiên bản dự kiến từ `version.txt` và mục `.` trong
`.release-please-manifest.json`. Manifest rỗng chỉ dùng lúc bootstrap; khi đó
`initial-version` là đề xuất ban đầu. PR phiên bản cập nhật manifest,
`version.txt` và CHANGELOG cùng nhau. Merge PR đó chưa đồng nghĩa tag hoặc
GitHub Release đã tồn tại; đối chiếu riêng hai tài nguyên trên GitHub.

CI từ chối metadata không đồng bộ hoặc sai [SemVer 2.0.0](https://semver.org/spec/v2.0.0.html).
Phiên bản dùng chữ số ASCII, không có tiền tố `v`; tag thêm đúng một tiền tố
`v` và phải khớp `version.txt` của commit đã qua CI. Giới hạn của kit là
127 ký tự cho phiên bản và 128 ký tự cho tag, không phải giới hạn do SemVer đặt.

Chế độ được cấu hình là **tạo Release nháp**: `skip-github-release: false` ở
cả action và config, `draft: true` và `force-tag-creation: true` trong config.
Sau khi PR phiên bản merge, Release Please tạo bản nháp có ghi chú phát hành và
tag ngay tại SHA phát hành. Job build tin cậy checkout đúng SHA đó, kiểm tra kit,
tạo ZIP/checksum, job attest tạo provenance rồi job có quyền ghi đính kèm cả hai
và công khai Release sau khi mọi kiểm tra đạt. Không cài dispatcher `push.tags` cạnh luồng
này. Dùng secret `RELEASE_PLEASE_TOKEN`, chỉ cấp cho repo
này với Contents, Pull requests và Issues: read/write để PR do bot tạo có thể
kích hoạt CI. Không dùng token local của người duy trì làm secret hoặc gửi giá
trị token vào chat/log. Xem [credential upstream](https://github.com/googleapis/release-please-action#github-credentials).

`force-tag-creation: true` tránh cơ chế lazy tag của GitHub khi dùng draft. Job
upload vẫn đọc và peel tag qua API, rồi từ chối nếu tag không trỏ đúng SHA do
Release Please trả về. Không di chuyển tag đã có. Xem [draft và tag trong schema
upstream](https://github.com/googleapis/release-please/blob/v17.11.2/schemas/config.json).

Run thành công không tự chứng minh asset của các draft cũ đã được xử lý. Đối
chiếu riêng PR, draft, tag, commit và assets; label `autorelease: tagged` cũng
không thay bằng chứng công khai khi dùng draft. Trạng thái chờ cũ có thể báo
`untagged, merged release PRs outstanding` khi còn PR phiên bản chưa được xử lý.

[Workflow Release Please](../.github/workflows/release-please.yml) chạy khi push
vào `main` hoặc chạy thủ công từ `main`. Sau khi output `release_created=true`,
các job `build-release-assets`, `attest-release-assets` và
`attach-release-assets` lần lượt tạo, attest, đính kèm và công khai Release.
Ngày 18/10/2026, [run đầu tiên](https://github.com/MinhThang1009/vlu-reference-kit/actions/runs/39092725672)
đã thành công; [PR phiên bản #3](https://github.com/MinhThang1009/vlu-reference-kit/pull/3)
được tạo, sửa lỗi định dạng changelog, qua CI và merge vào `main` khi cấu hình
còn ở chế độ PR-only. Đây là bằng
chứng vận hành theo thời điểm, không chứng minh token còn hiệu lực trong tương
lai hoặc đã phát hành ZIP. Các lần sau kiểm tra run/PR/CI mới, không dùng lại
kết luận của run đầu tiên.

Workflow [release.yml](../.github/workflows/release.yml) chỉ chạy thủ công từ
`main` để sửa chữa hoặc backfill draft cũ. Input `tag` phải tồn tại và trỏ đúng `commit_sha` đầy đủ. Commit đó phải
trùng SHA của lần dispatch trên `main` để provenance cùng nguồn, thuộc lịch sử
`main` và có hai check thành công từ GitHub Actions. Nếu `main` tiến lên giữa
lúc tạo tag và dispatch, dừng và review lại phiên bản/commit, không di chuyển
tag đã công bố để ép khớp.

## Thực hiện khi có yêu cầu phát hành

1. Xác nhận phiên bản mới, commit đã qua CI, thay đổi và quyền phân phối.
2. Kiểm tra draft do Release Please tạo và tag tương ứng. Pipeline tự tạo tag
   với `force-tag-creation`, không di chuyển tag đã có.
3. Đợi workflow Release Please hoàn tất `build-release-assets`,
   `attest-release-assets` và `attach-release-assets`; kiểm tra Release đã có
   ZIP, `SHA256SUMS.txt`, attestation và trạng thái công khai.
4. Chỉ chạy **Phát hành cộng đồng** từ `main` cho draft cũ hoặc khi pipeline
   tự động thất bại; nhập tag và full SHA.
5. Build kiểm tra kit, test và ZIP bằng token chỉ đọc. Artifact chuyển trong
   cùng workflow run, bước download kiểm tra digest; job attest và publish
   không checkout/chạy mã dự án với token có quyền ghi.
6. Workflow tự kiểm tra lại tag, attest asset rồi công khai draft. Rerun có thể
   sửa draft; bản đã công bố bị từ chối thay asset.
   Rerun failed jobs khi artifact của build còn hiệu lực (giữ 1 ngày); sau đó
   review và chạy một workflow mới. Không dùng `--clobber` lên bản đã công bố.
7. Xác minh Release đã công khai và tải kiểm tra ZIP/checksum. Release Please
   có thể tự đổi label từ `autorelease: pending` sang `autorelease: tagged`
   khi tạo draft; label không chứng minh artifact đã phát hành. Với PR cũ từ
   chế độ PR-only, chỉ sửa label còn thiếu sau khi đã kiểm chứng phát hành.
   Xem [vòng đời label upstream](https://github.com/googleapis/release-please/blob/v17.11.2/docs/customizing.md#release-lifecycle-labels).

Ngày 19/10/2026, tag `v0.1.0` đã được tạo tại commit
`d1037383a0072e8ecf8b370d26fce5714e073495`, chưa có GitHub Release công khai
tại thời điểm đổi cấu hình. Giữ nguyên tag đó. Nếu `main` đã tiến lên khiến
điều kiện dispatch không còn khớp, review phiên bản/commit mới thay vì chuyển
tag cũ hoặc bỏ kiểm tra provenance để ép phát hành.

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
chưa chạy thử luồng publish tự động trên GitHub. Chưa bật
immutable releases thì không tuyên bố GitHub đã khóa tag/asset. Tham khảo
[attestation](https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations)
và [immutable releases](https://docs.github.com/en/code-security/concepts/supply-chain-security/immutable-releases).
