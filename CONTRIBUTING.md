# Đóng góp cho VLU Reference Kit

Cảm ơn bạn đã quan tâm đóng góp! Tài liệu này mô tả quy trình làm việc.

## Quy trình (GitHub Flow)

1. Tạo branch từ **main**: `git checkout -b feat/<short-description>`.
2. Commit theo [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/): `feat(scope): description`.
3. Push branch và mở Pull Request vào **main**.
4. Mở PR để người duy trì review; chỉ cập nhật bản đã được kiểm tra.

## Language policy

Use English for commit messages, Pull Request titles and bodies, Release names,
and generated release notes. Keep Conventional Commit prefixes such as `feat:`,
`fix:`, and `chore:`. Project guides and VLU-facing content may remain in
Vietnamese when that is the intended audience; do not mix languages within one
commit, PR, or Release message.

Trước khi tạo hoặc cập nhật pull request, chạy
`python scripts/pr_template_preflight.py --title "<title>"`. Với thay đổi
security, deployment hoặc dependency update cần review chuyên biệt mà title
không có mapping bắt buộc, thêm `--template security`, `--template deployment`
hoặc `--template dependency-update`.

## Kỳ vọng về mã nguồn

- Tuân theo các quy ước hiện có của codebase.
- Chạy linter và test trước khi mở PR.
- Mỗi PR chỉ nên tập trung vào một mục tiêu, vì PR nhỏ dễ review hơn.

## Kiểm tra trước khi gửi

```console
python -m pip install --require-hashes -r requirements-docs.lock
python -m unittest discover -s tests/docs -v
npm ci --ignore-scripts
python scripts/patch_braces.py
node --test tests/test_braces_guard.cjs
python scripts/refresh_manifest.py
python scripts/validate_kit.py
python -m unittest discover -s tests -v
python scripts/validate_tooling.py
python scripts/validate_scaffold.py --repository-root .
python scripts/ci_toolchain.py run-markdownlint
python scripts/build_community_package.py
```

Chỉ tạo lại manifest sau thay đổi có chủ đích trong `kit/`. Tài nguyên mới cần URL nguồn, phạm vi áp dụng, hash và bằng chứng quyền phân phối. Bản cộng đồng không chứa artwork chưa rõ quyền.

Suite `tests/` kiểm tra công cụ standard library; suite `tests/docs/` chạy riêng
sau khi cài `requirements-docs.lock` vì cần parser Markdown/YAML. CI tài liệu
chạy suite này và từ chối kết quả nếu không duyệt đủ thư mục tài liệu.

Các tệp `upstream_info.md` của font được giữ nguyên byte và loại khỏi Markdown lint vì là tài liệu vendor; mọi tài liệu tự biên soạn vẫn được kiểm tra. Đọc `kit/PUBLICATION.md` trước khi diễn giải bằng chứng audit nguồn.

Khi đổi dependency, cập nhật cả manifest, policy và lockfile theo
[hướng dẫn dependency](docs/dependencies.md). Phát hành theo
[hướng dẫn release](docs/releasing.md), dùng commit đã qua CI.

## Báo cáo vấn đề

Dùng [Issues](https://github.com/MinhThang1009/vlu-reference-kit/issues) để báo lỗi dữ liệu, yêu cầu tài nguyên hoặc đặt câu hỏi. Gửi kèm nguồn và phạm vi áp dụng.

Tham gia dự án đồng nghĩa tuân thủ [quy tắc ứng xử](CODE_OF_CONDUCT.md).
