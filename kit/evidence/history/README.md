# Bằng chứng lịch sử

Các JSON trong thư mục này giữ nguyên byte của đầu vào. Chúng mô tả round cũ và dùng tên/đường dẫn cũ, không phải liên kết vận hành của bản hiện tại. Tra `audit/path-map.csv` từ gốc kit để đối chiếu đường dẫn. Các hash bên trong là số liệu tại thời điểm cũ.

Các receipt `evidence/qa-report.json` và `evidence/package-verification.json` vẫn giữ số liệu source archive historical; không dùng chúng làm denominator hiện tại. Kết quả hiện tại phải chạy `python scripts/validate_kit.py`, bộ test và CI; đối chiếu thêm `evidence/source-verification.json` và `audit/checklist.json`. Không dùng một cờ PASS lịch sử để kết luận bản hiện tại đã qua kiểm tra.
