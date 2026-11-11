# PROGRESS — <Nhóm 11> — Track <A>

- Starter: <ktpmud-bkt-ruleengine-starter> · tag bkt-2026-v1 (hoặc v1.1)
- Fork: <https://github.com/phg-nam/ktpmud-bkt-ruleengine-starter>

## PC-1 — 11/11/2026

### 1.1. Tiến độ theo acceptance criteria
<!-- Track A: A-01…A-11 · Track B: B-01…B-10 (đề thi Mục 7.3 / 8.3). Đủ mọi mã. -->
| Mã | Trạng thái (Chưa / Đang / Xong) | Bằng chứng (commit / CI / file) | Ghi chú |
|---|---|---|---|
| A-01 | Chưa | `REQUIREMENTS.md` (FR-01…FR-07), `DECISIONS.md` (ADR-001, ADR-002); chưa có commit code | Đã chốt thiết kế và thứ tự ưu tiên R01 > R02 > R03. Chưa viết `r01`, `r02`, `r03`, `is_hypotensive`, `classify()` |
| A-02 | Chưa | `REQUIREMENTS.md` (NFR-01, AC-27) | Sẽ viết test dùng dữ liệu ngoài fixture công khai. Chưa có code |
| A-03 | Chưa | `REQUIREMENTS.md` (AC-01…AC-18, AC-28…AC-36), `TEST_PLAN.md` mục 4.1–4.2 | Ma trận ca test đã có, gồm ca biên mọi nhóm tuổi và ca ưu tiên. Chưa chạy |
| A-04 | Chưa | `REQUIREMENTS.md` mục 6.2 (policy theo trường), AC-19…AC-22, AC-37…AC-44, `DECISIONS.md` (ADR-003) | Policy đã chốt, chưa cài đặt. Cần đối chiếu lần cuối với issue `ktpmud-project#15` mục 5 |
| A-05 | Chưa | `REQUIREMENTS.md` (FR-08, AC-23) | Chưa có code sinh `ly_do` |
| A-06 | Chưa | `REQUIREMENTS.md` mục 6.3 (AC-24, AC-25, AC-45), `DECISIONS.md` (ADR-004) | Thiết kế xong (hàm bọc `classify_with_audit`, `audit_sink`). Chưa viết code |
| A-07 | Chưa | `TEST_PLAN.md` mục 4 (ma trận AC → test, đủ normal / boundary / invalid / missing) | Kế hoạch xong. Chưa có file test |
| A-08 | Chưa | Chưa có kết quả `pytest -q` để ghi nhận | Chỉ đạt sau khi có test; sẽ chạy từ clean checkout |
| A-09 | Chưa | Chưa có | Dự kiến thêm workflow GitHub Actions chạy `pytest -q` trên Pull Request |
| A-10 | Chưa | `TEST_PLAN.md` mục 5 (phương pháp benchmark) | Chưa có code benchmark. Sẽ đo ≥1.000 lần, báo p50/p95 |
| A-11 | Chưa | `REQUIREMENTS.md` (NFR-05) | Chưa thêm câu "educational/synthetic — not for clinical use" vào README |

### 1.2. Sửa đổi bắt buộc từ Checkpoint 1
| Mục | Trạng thái | Bằng chứng |
|---|---|---|
| Q-05 phải chốt, không hạ mức, viết bảng policy theo trường, thêm test |Đã xong | Mục 6.2, FR-10, AC-37…AC-44, ADR-003 |
| Thiếu ca chứng minh thứ tự ưu tiên |Đã xong | AC-28, ADR-002 |

### 1.3. Timeline dự kiến đến khi hoàn thành
| Việc | Vai trò phụ trách | Mốc (CP2 15/11 · M3 · Freeze 19/11 · M4 20/11) | Ngày dự kiến |
|---|---|---|---|
| Chạy `pytest -q` trên starter, đọc `classifier.py` và fixture; chốt chữ ký hàm; đối chiếu policy với issue #15 mục 5 | Thành viên 1 (logic rule) và Thành viên 2 (test) | PC-1 | 11/11 |
| Viết `r01`, `r02`, `r03`, `is_hypotensive` và bước chuẩn hóa input theo policy (A-01, A-03, A-04) | Thành viên 1 (logic rule) | CP2 15/11 | 12/11 |
| Viết `classify()` điều phối 2 tầng và `ly_do` (A-01, A-05) | Thành viên 1 (logic rule) | CP2 15/11 | 13/11 |
| Viết test nghiệp vụ và ca biên theo ma trận `TEST_PLAN.md` (A-03, A-07) | Thành viên 2 (test) | CP2 15/11 | 13/11 |
| Viết test input lỗi theo bảng policy và test thứ tự ưu tiên (A-04, A-07) | Thành viên 2 (test) | CP2 15/11 | 14/11 |
| Viết `classify_with_audit` và test audit (A-06) | Thành viên 3 (audit, CI, benchmark) | CP2 15/11 | 14/11 |
| Chạy `pytest -q` toàn bộ, demo nội bộ 5 phút (CP2) | Cả nhóm | CP2 15/11 | 15/11 |
| Thêm GitHub Actions chạy test trên Pull Request (A-09); thêm câu cảnh báo vào README (A-11) | Thành viên 3 (audit, CI, benchmark) | M3 | 16/11 |
| Viết và chạy benchmark ≥1.000 lần, ghi p50/p95; viết `TEST_REPORT.md` (A-10) | Thành viên 3 (audit, CI, benchmark) và Thành viên 2 (test) | M3 | 17/11 |
| Viết `SECURITY_PRIVACY_CHECKLIST.md`, `CONTRIBUTIONS.md`, `AI_USE.md`; soát để không có secret, dữ liệu thật hay họ tên | Cả nhóm | M3 | 18/11 |
| Rà soát cuối, soạn slide và demo script (≤7 phút), cập nhật mục "Kết quả cuối" | Cả nhóm | M3 | 18/11 |
| Freeze: gắn tag `bkt-2026-<mã nhóm>-rc1`, ghi SHA vào `PROGRESS.md` (hạn 23:59) | Thành viên 3 (audit, CI, benchmark) | Freeze 19/11 | 19/11 |
| Nộp Pull Request vào `ktpmud-project` theo erratum #25, đảm bảo CI xanh | Thành viên 1 (logic rule) | M4 20/11 | 20/11 |

### 1.4. Rủi ro / đang vướng
- 

### 1.5. Câu hỏi cho GV
- Q1: 

### 1.6. Phân công (alias hoặc vai trò, KHÔNG ghi họ tên/MSSV)
| Alias / vai trò | Đầu việc chính | Commit/PR tiêu biểu |
|---|---|---|



## Kết quả cuối — Freeze 19/11/2026
- Tag: bkt-2026-<mã nhóm>-rc1 · SHA: 
- Trạng thái cuối từng mã AC: (cập nhật bảng 2.2 hoặc ghi "như 2.2 trừ: …")
- Những việc trong timeline chưa hoàn thành và lý do: