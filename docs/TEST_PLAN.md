# TEST PLAN — Track A: Rule Engine

> Nhóm: `[mã nhóm / alias]` · Phiên bản: v0.1 (Checkpoint 1) · Ngày: 08/11/2026
> Đối chiếu: `REQUIREMENTS.md` (mục 7: AC-01…AC-27) và `docs/decision-table.md`.
> Tên hàm test dưới đây là **dự kiến**, sẽ chỉnh khi viết code thật.

## 1. Mục tiêu

Chứng minh `classify()` đúng theo bảng quyết định trên mọi ca, đặc biệt ở **ranh giới** (dấu `<` và `>` chặt), và chứng minh audit, giải thích, hiệu năng đạt yêu cầu của đề (A-01…A-11).

## 2. Phạm vi test

| Loại | Công cụ | Nội dung | Tiêu chí đề |
|---|---|---|---|
| Unit test nghiệp vụ | `pytest` | Từng kịch bản R01, R02, R03; ngưỡng sốc theo tuổi | A-01, A-03, A-07 |
| Test biên | `pytest` (parametrize) | Ngưỡng tuổi 1, 11, 18; HATT sát ngưỡng; giảm đúng 30% | A-07 |
| Test input lỗi | `pytest` | Thiếu trường, sai kiểu, ngoài miền, trường lạ | A-04, A-07 |
| Test giải thích | `pytest` | `ly_do` có rule, không chứa giá trị lâm sàng thô | A-05 |
| Test audit | `pytest` | Đúng 4 trường, không chứa dữ liệu input | A-06 |
| Test chống hard-code | `pytest` | Dữ liệu ngoài public fixture vẫn đúng | A-02 |
| Benchmark | `time.perf_counter` | ≥1.000 lần sau warm-up, p50/p95 | A-10 |
| CI | GitHub Actions | Chạy `pytest -q` trên mỗi Pull Request | A-08, A-09 |

**Không test:** machine learning, giao diện, tích hợp hệ thống thật (ngoài phạm vi theo đề).

## 3. Môi trường

| Mục | Giá trị |
|---|---|
| Python | `[điền: bản đang dùng, ví dụ 3.11]` |
| OS | `[Windows 10/11 ...]` |
| Thư viện | `pytest` (theo `requirements.txt` của starter) |
| Lệnh chạy | `python -m venv .venv` → `.venv\Scripts\activate` → `pip install -r requirements.txt` → `pytest -q` |
| Dữ liệu | Toàn bộ synthetic, không dùng dữ liệu thật |

## 4. Ma trận test (truy vết AC → test)

### 4.1. Phản vệ (Tầng 2)

| AC | Ca | Test dự kiến | Kết quả mong đợi |
|---|---|---|---|
| AC-01 | R01 đủ điều kiện | `test_r01_match` | `PHAN_VE`, `R01-PV` |
| AC-02 | R01 chỉ có tiêu hóa | `test_r01_digestive_only_not_match` | `THEO_DOI` |
| AC-03 | R01 thiếu da/niêm mạc | `test_r01_no_skin_not_match` | `THEO_DOI` |
| AC-04 | R02 đúng 2 hệ | `test_r02_two_systems` | `PHAN_VE`, `R02-PV` |
| AC-05 | R02 chỉ 1 hệ | `test_r02_one_system_not_match` | `THEO_DOI` |
| AC-06 | R03 hô hấp, không hít | `test_r03_respiratory_no_inhaled` | `PHAN_VE`, `R03-PV` |
| AC-07 | R03 hô hấp, có hít | `test_r03_respiratory_inhaled_not_match` | `THEO_DOI` |
| AC-08 | R03 tuần hoàn | `test_r03_circulatory` | `PHAN_VE`, `R03-PV` |

### 4.2. Sốc phản vệ (Tầng 1), ca biên

Điều kiện nền: input đã khớp Tầng 2. Viết dạng **một test có `parametrize`** để mỗi dòng là một ca.

| AC | Tuổi | HATT (nền) | Mong đợi |
|---|---|---|---|
| AC-09 | 0.5 | 69 | `SOC_PHAN_VE` |
| AC-10 | 0.5 | 70 | `PHAN_VE` |
| AC-11 | 5 | 79 | `SOC_PHAN_VE` |
| AC-12 | 5 | 80 | `PHAN_VE` |
| AC-13 | 11 | 89 | `SOC_PHAN_VE` |
| AC-14 | 11 | 90 | `PHAN_VE` |
| AC-15 | 18 | 89 (nền null) | `SOC_PHAN_VE` |
| AC-16 | 18 | 90 (nền null) | `PHAN_VE` |
| AC-17 | 40 | 104 (nền 150) | `SOC_PHAN_VE` |
| AC-18 | 40 | 105 (nền 150) | `PHAN_VE` |

Test: `test_shock_threshold_by_age` (parametrize).
Bổ sung ca ngưỡng chuyển nhóm tuổi (chọn khi viết code): tuổi 1 (ngưỡng 72), tuổi 10.9, tuổi 17.9.

### 4.3. Input thiếu / sai / ngoài miền

| AC | Ca | Test dự kiến | Mong đợi |
|---|---|---|---|
| AC-19 | Thiếu `tuoi` | `test_missing_age` | Theo Q-02 |
| AC-20 | HATT null, đã khớp Tầng 2 | `test_missing_bp_after_match` | Theo Q-03 |
| AC-21 | Tuổi âm, sai kiểu, bool sai | `test_invalid_input` | Theo Q-05, không crash |
| AC-22 | Có trường định danh | `test_extra_pii_field_not_stored` | Không lưu, không ghi audit |

### 4.4. Giải thích, audit, hiệu năng

| AC | Ca | Test dự kiến |
|---|---|---|
| AC-23 | `ly_do` có rule, không chứa giá trị lâm sàng | `test_reason_no_raw_clinical_data` |
| AC-24 | Mỗi lần gọi sinh 1 bản ghi audit, đúng 4 trường | `test_audit_has_four_fields` |
| AC-25 | Audit không chứa giá trị input | `test_audit_no_clinical_data` |
| AC-26 | p95 < 100 ms | `benchmark.py` (chạy riêng, ghi vào `TEST_REPORT.md`) |
| AC-27 | Dữ liệu ngoài public fixture | `test_not_hardcoded_to_fixture` |

## 5. Phương pháp benchmark (A-10)

1. Chạy `classify()` một số lần để **warm-up** (không tính).
2. Đo **≥ 1.000 lần** bằng `time.perf_counter()`, mỗi lần một input hợp lệ.
3. Tính **p50, p95** của thời gian mỗi lần chạy (mili-giây).
4. Ghi cấu hình máy đo (CPU, RAM, OS, Python) vào `TEST_REPORT.md`.
5. Đạt khi **p95 < 100 ms**.

## 6. Tiêu chí vào / ra

| | Điều kiện |
|---|---|
| Vào (bắt đầu viết test) | `REQUIREMENTS.md` được TA duyệt scope; Q-01…Q-06 có trả lời hoặc đã ghi giả định trong `DECISIONS.md` |
| Ra (coi là xong) | `pytest -q` đạt từ clean checkout; đủ 4 loại ca (normal, boundary, invalid, missing); CI xanh; benchmark đạt |

## 7. Phân công

| Phần | Người phụ trách (MSSV) |
|---|---|
| Test phản vệ (4.1) | `[MSSV]` |
| Test sốc, ca biên (4.2) | `[MSSV]` |
| Test input lỗi + audit (4.3, 4.4) | `[MSSV]` |
| CI + benchmark | `[MSSV]` |

## 8. Rủi ro và giới hạn

| Rủi ro | Cách giảm |
|---|---|
| Test ẩn của thầy kiểm tra ca mà nhóm chưa nghĩ tới | Bao phủ cả hai phía của mỗi điều kiện và mọi ngưỡng; không tự thêm quy tắc ngoài bảng |
| Điểm mơ hồ Q-01…Q-06 | Đã hỏi TA; ghi quyết định vào `DECISIONS.md` |
| Thời gian benchmark phụ thuộc máy | Khai báo cấu hình máy đo |
