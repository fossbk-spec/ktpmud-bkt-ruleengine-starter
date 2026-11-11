# TEST PLAN — Track A: Rule Engine

> Nhóm 11 · Phiên bản: v0.2 (sửa theo nhận xét Checkpoint 1) · Ngày: 10/11/2026
> Đối chiếu: `REQUIREMENTS.md` (mục 7: AC-01…AC-45) và `docs/decision-table.md`.
> Tên hàm test dưới đây là **dự kiến**, sẽ chỉnh khi viết code thật.

## 1. Mục tiêu

Chứng minh `classify()` đúng theo bảng quyết định trên mọi ca, đặc biệt ở **ranh giới** (dấu `<` và `>` chặt, chuyển nhóm tuổi), và chứng minh policy input lỗi, audit, giải thích, hiệu năng đạt yêu cầu của đề (A-01…A-11).

## 2. Phạm vi test

| Loại | Công cụ | Nội dung | Tiêu chí đề |
|---|---|---|---|
| Unit test nghiệp vụ | `pytest` | Từng kịch bản R01, R02, R03; thứ tự ưu tiên; ngưỡng sốc theo tuổi | A-01, A-03, A-07 |
| Test biên | `pytest` (parametrize) | Ngưỡng tuổi 1, 11, 18; các cặp ±1 phân biệt nhóm tuổi; giảm đúng 30% | A-07 |
| Test policy input lỗi | `pytest` (parametrize theo bảng policy) | Thiếu khóa, `null`, sai kiểu, ngoài miền, trường lạ | A-04, A-07 |
| Test giải thích | `pytest` | `ly_do` có rule, không chứa giá trị lâm sàng thô | A-05 |
| Test audit | `pytest` | Đúng 4 khóa, không chứa dữ liệu input, UUID hợp lệ | A-06 |
| Test chống hard-code | `pytest` | Dữ liệu ngoài public fixture vẫn đúng | A-02 |
| Benchmark | `time.perf_counter` | ≥1.000 lần sau warm-up, p50/p95 | A-10 |
| CI | GitHub Actions | Chạy `pytest -q` trên mỗi Pull Request | A-08, A-09 |

**Không test:** machine learning, giao diện, tích hợp hệ thống thật (ngoài phạm vi theo đề).

## 3. Môi trường

| Mục | Giá trị |
|---|---|
| Python | Python 3 (ghi rõ bản cụ thể trong `TEST_REPORT.md` khi chạy thử) |
| OS | Windows |
| Thư viện | `pytest` (theo `requirements.txt` của starter) |
| Lệnh chạy | `python -m venv .venv` → `.venv\Scripts\activate` → `pip install -r requirements.txt` → `pytest -q` |
| Dữ liệu | Toàn bộ synthetic, không dùng dữ liệu thật |

## 4. Ma trận test (truy vết AC → test)

### 4.1. Phản vệ (Tầng 2) và thứ tự ưu tiên

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
| **AC-28** | R02 và R03 cùng thỏa, không tụt HA | `test_priority_r02_before_r03` | `PHAN_VE`, `R02-PV` |

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

**Ca chuyển nhóm tuổi (bổ sung theo nhận xét)**, test: `test_shock_age_group_transition` (parametrize). Mỗi cặp kiểm hai công thức ở hai phía của một ranh giới nhóm tuổi.

| AC | Tuổi | HATT (nền) | Ngưỡng áp dụng | Mong đợi |
|---|---|---|---|---|
| AC-29 | 0.99 | 71 | <1 tuổi: <70 | `PHAN_VE` |
| AC-30 | 1 | 71 | 70+2×1 = 72 | `SOC_PHAN_VE` |
| AC-31 | 1 | 72 | 72 | `PHAN_VE` |
| AC-32 | 10.9 | 91 | 70+2×10,9 = 91,8 | `SOC_PHAN_VE` |
| AC-33 | 10.9 | 92 | 91,8 | `PHAN_VE` |
| AC-34 | 11 | 91 | 11–<18: <90 | `PHAN_VE` |
| AC-35 | 17.9 | 100 (nền 150) | 11–<18: không dùng tiêu chí nền | `PHAN_VE` |
| AC-36 | 18 | 100 (nền 150) | ≥18: giảm 33,3% > 30% | `SOC_PHAN_VE` |

### 4.3. Input thiếu / sai / ngoài miền (theo policy `REQUIREMENTS.md` mục 6.2)

Viết **một test parametrize theo từng dòng của bảng policy**, mỗi trường thử đủ 4 tình huống: thiếu khóa, `null`, sai kiểu, ngoài miền.

| AC | Ca | Test dự kiến | Mong đợi |
|---|---|---|---|
| AC-19 | Thiếu `tuoi` hoặc `null` | `test_missing_age` | `THEO_DOI` |
| AC-20 | HATT thiếu/null, đã khớp Tầng 2 | `test_missing_bp_after_match` | `PHAN_VE` |
| AC-21 | `tuoi` âm hoặc sai kiểu | `test_invalid_age` | `THEO_DOI`, không crash |
| AC-22 | Có trường định danh | `test_extra_pii_field_not_stored` | Bỏ qua, không lưu, không ghi audit |
| **AC-37** | Thiếu khóa `co_trieu_chung_tieu_hoa_nang`, da ✓ + hô hấp ✓, nghi dị nguyên | `test_missing_bool_no_downgrade` | `PHAN_VE`, `R02-PV` |
| **AC-38** | `di_nguyen_qua_duong_hit` null, tuần hoàn ✓, nghi dị nguyên | `test_null_inhaled_circulatory_branch` | `PHAN_VE`, `R03-PV` |
| **AC-39** | `di_nguyen_qua_duong_hit` null, chỉ hô hấp ✓, nghi dị nguyên | `test_null_inhaled_respiratory_branch` | `THEO_DOI` |
| **AC-40** | `co_di_nguyen_nghi_ngo` thiếu/null | `test_missing_suspected_allergen` | `THEO_DOI` |
| **AC-41** | Bool nhận `"true"` hoặc `1` | `test_wrong_type_bool` | Không xác định, không crash, không tính là `true` |
| **AC-42** | HATT âm, 0 hoặc sai kiểu, đã khớp Tầng 2 | `test_invalid_bp_after_match` | `PHAN_VE` |
| **AC-43** | Tuổi ≥18, nền thiếu, HATT 100, đã khớp Tầng 2 | `test_missing_baseline_adult` | `PHAN_VE` |
| **AC-44** | Input là `None` hoặc danh sách | `test_non_dict_input` | `THEO_DOI`, không crash |

### 4.4. Giải thích, audit, hiệu năng

| AC | Ca | Test dự kiến |
|---|---|---|
| AC-23 | `ly_do` có rule, không chứa giá trị lâm sàng | `test_reason_no_raw_clinical_data` |
| AC-24 | Mỗi lần gọi hàm bọc sinh 1 bản ghi trong `audit_sink`, đúng 4 khóa | `test_audit_has_four_fields` |
| AC-25 | Audit không chứa `muc_do`, `rule_id`, `ly_do`, giá trị input | `test_audit_no_clinical_data` |
| **AC-45** | `User_UUID` đúng giá trị truyền vào; UUID sai → `ValueError`, không ghi bản ghi | `test_audit_user_uuid` |
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
| Vào (bắt đầu viết test) | Q-01…Q-04 đã chốt theo issue #15; policy Q-05 và thiết kế audit Q-06 đã có trong `REQUIREMENTS.md` mục 6 |
| Ra (coi là xong) | `pytest -q` đạt từ clean checkout; đủ 4 loại ca (normal, boundary, invalid, missing); CI xanh; benchmark đạt |

## 7. Rủi ro và giới hạn

| Rủi ro | Cách giảm |
|---|---|
| Test ẩn của thầy kiểm tra ca mà nhóm chưa nghĩ tới | Bao phủ cả hai phía của mỗi điều kiện và mọi ngưỡng, kể cả ranh giới giữa các nhóm tuổi; không tự thêm quy tắc ngoài bảng |
| Policy input lỗi lệch với hướng dẫn của thầy | Đối chiếu với issue #15 mục 5; mỗi dòng policy có ca test |
| Chữ ký `classify()` thật khác dự kiến | Kiểm tra `rule_engine/classifier.py` trước khi viết hàm bọc audit |
| Thời gian benchmark phụ thuộc máy | Khai báo cấu hình máy đo |
