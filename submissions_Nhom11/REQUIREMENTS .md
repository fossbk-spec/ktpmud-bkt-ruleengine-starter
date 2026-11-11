# REQUIREMENTS — Track A: Dr May Day Rule Engine Sprint

> Nhóm 11 · Phiên bản: v0.2 (sửa theo nhận xét Checkpoint 1; hạn sửa 23:59 15/11/2026)
> Nguồn đặc tả duy nhất: `docs/decision-table.md` (starter tag `bkt-2026-v1`).
> Câu trả lời chính thức của thầy cho Q-01…Q-04: issue `fossbk-spec/ktpmud-project#15`.

## 1. Mục tiêu và phạm vi

Xây một Rule Engine bằng Python có hàm `classify()` nhận dữ liệu synthetic theo Data Dictionary, phân loại theo bảng quyết định WAO/EAACI V1 (Tầng 1: Sốc phản vệ, Tầng 2: Phản vệ), trả kết quả kèm lý do giải thích được, và ghi audit trail tối thiểu.

**Trong phạm vi**
- Phân loại 3 mức: `SOC_PHAN_VE`, `PHAN_VE`, `THEO_DOI`.
- Giải thích rule đã kích hoạt (`rule_id`, `ly_do`).
- Audit 4 trường: `Timestamp, User_UUID, Action_Type, Status`.
- Unit test, CI, benchmark latency, tài liệu bàn giao.

**Ngoài phạm vi** (theo đề, Mục 7.4)
- Giao diện bệnh viện hoàn chỉnh.
- Chẩn đoán hoặc khuyến nghị điều trị.
- Thay đổi ngưỡng hoặc thêm rule ngoài `decision-table.md`.
- Machine learning / deep learning.
- Dữ liệu bệnh nhân thật; tích hợp Dr May Day production.

## 2. Dữ liệu vào (theo Data Dictionary)

| Trường | Kiểu | Ghi chú |
|---|---|---|
| `tuoi` | float (năm) | Cho phép số lẻ (0.5 = 6 tháng) |
| `huyet_ap_tam_thu` | int \| null | mmHg; null nếu không đo được |
| `huyet_ap_tam_thu_nen` | int \| null | mmHg; chỉ dùng khi `tuoi >= 18` cho tiêu chí giảm 30% |
| `co_di_nguyen_nghi_ngo` | bool | Nghi ngờ dị nguyên |
| `di_nguyen_qua_duong_hit` | bool | Dị nguyên đường hít (ảnh hưởng R03) |
| `co_ton_thuong_da_niem_mac` | bool | Da/niêm mạc |
| `co_trieu_chung_ho_hap` | bool | Hô hấp |
| `co_trieu_chung_tuan_hoan` | bool | Tuần hoàn |
| `co_trieu_chung_tieu_hoa_nang` | bool | Tiêu hóa nặng |

**Zero PII:** không chấp nhận hoặc lưu thêm trường định danh (tên, CCCD, SĐT, địa chỉ…).

## 3. Dữ liệu ra

```json
{ "muc_do": "SOC_PHAN_VE | PHAN_VE | THEO_DOI",
  "rule_id": "R-SOC | R01-PV | R02-PV | R03-PV | null",
  "ly_do": "chuỗi ngắn, không chứa dữ liệu lâm sàng thô" }
```

## 4. Yêu cầu chức năng

| ID | Yêu cầu | Nguồn trong decision-table |
|---|---|---|
| FR-01 | Khớp **R01**: không nghi dị nguyên **và** có tổn thương da/niêm mạc **và** (hô hấp **hoặc** tuần hoàn) | Tầng 2, R01 |
| FR-02 | Khớp **R02**: có nghi dị nguyên **và** ít nhất 2 trong 4 hệ (da/niêm mạc, hô hấp, tuần hoàn, tiêu hóa nặng) | Tầng 2, R02 |
| FR-03 | Khớp **R03**: có nghi dị nguyên **và** ((không hít **và** hô hấp) **hoặc** tuần hoàn) | Tầng 2, R03 |
| FR-04 | Phản vệ khi khớp **ít nhất 1** trong R01/R02/R03. Khi nhiều rule cùng khớp, lấy rule đầu tiên theo thứ tự **R01 > R02 > R03** (đã chốt, Q-01) | Tầng 2; issue #15 |
| FR-05 | Tính ngưỡng tụt HATT theo tuổi: <1 tuổi: <70; 1 đến <11: <70+2×tuổi; 11 đến <18: <90; ≥18: <90 **hoặc** giảm >30% so với huyết áp nền | Tầng 1 |
| FR-06 | **Sốc phản vệ** (`R-SOC`) khi khớp Tầng 2 **và** tụt huyết áp theo FR-05 | Tầng 1 |
| FR-07 | Không khớp Tầng 1 lẫn Tầng 2 → `THEO_DOI`, `rule_id = null`. Thiếu `tuoi` → `THEO_DOI` (Q-02, đã chốt) | Mục kết quả `THEO_DOI` |
| FR-08 | Trả `ly_do` chỉ ra rule đã kích hoạt, không đưa lời khuyên điều trị, không chứa giá trị lâm sàng thô | Output, A-05 |
| FR-09 | Mỗi lần phân loại ghi audit đúng 4 trường theo thiết kế ở mục 6.3; không ghi triệu chứng, điểm số, dữ liệu nhận dạng | A-06 |
| FR-10 | Xử lý input thiếu khóa, `null`, sai kiểu, ngoài miền theo **policy ở mục 6.2**; không crash, không báo lỗi, không hạ mức khi các trường đã biết đủ thỏa một rule | A-04; issue #15 mục 5 |

## 5. Yêu cầu phi chức năng

| ID | Yêu cầu | Tiêu chí đề |
|---|---|---|
| NFR-01 | Không hard-code theo ID của public fixture | A-02 |
| NFR-02 | `pytest -q` đạt từ clean checkout | A-08 |
| NFR-03 | CI chạy test trên mỗi Pull Request | A-09 |
| NFR-04 | Benchmark ≥ 1.000 lần chạy sau warm-up, báo cáo p50/p95; **p95 < 100 ms** trên máy đo đã khai báo | A-10 |
| NFR-05 | README ghi "educational/synthetic — not for clinical use" | A-11 |
| NFR-06 | Không commit secret, `.env`, dữ liệu thật | Mục 5.2 của đề |

## 6. Các điểm đặc tả chưa rõ và cách chốt

### 6.1. Trạng thái Q-01…Q-06

| ID | Tình huống | Quyết định | Trạng thái |
|---|---|---|---|
| Q-01 | Nhiều rule Tầng 2 cùng khớp | **R01 > R02 > R03**, lấy rule đầu tiên khớp (ADR-002) | **Đã chốt** — issue `ktpmud-project#15` |
| Q-02 | Thiếu `tuoi` nhưng Tầng 2 vẫn khớp | `THEO_DOI` | **Đã chốt** — issue `ktpmud-project#15` |
| Q-03 | `huyet_ap_tam_thu` null khi đã khớp Tầng 2 | `PHAN_VE` (không đánh giá được tụt HA) | **Đã chốt** — issue `ktpmud-project#15` |
| Q-04 | Tuổi ≥ 18 mà `huyet_ap_tam_thu_nen` null | Chỉ dùng tiêu chí HATT < 90 | **Đã chốt** — issue `ktpmud-project#15` |
| Q-05 | Input thiếu khóa / null / sai kiểu / ngoài miền | Policy theo từng trường ở mục 6.2 (ADR-003) | **Nhóm chốt**, theo hướng dẫn mục 5 của issue #15 |
| Q-06 | `User_UUID` lấy từ đâu, audit ghi vào đâu | Thiết kế ở mục 6.3 (ADR-004) | **Nhóm chốt** |

### 6.2. Policy xử lý input không dùng được (Q-05)

**Nguyên tắc**
1. Không báo lỗi, không crash.
2. Một trường **không dùng được** (thiếu khóa, `null`, sai kiểu, hoặc ngoài miền) được coi là **"không xác định"** cho riêng trường đó.
3. "Không xác định" **không bao giờ** được tính là `true`, và không thỏa điều kiện nào cần giá trị cụ thể của trường đó.
4. **Không hạ mức:** một rule vẫn khớp nếu các trường **đã biết** đã đủ thỏa trọn điều kiện của rule, dù trường khác không xác định. Chỉ khi không rule nào thỏa mới ra `THEO_DOI`.
5. Khóa lạ (ví dụ trường định danh) bị bỏ qua, không lưu, không ghi audit. Nếu cả input không phải dict thì coi như mọi trường đều thiếu.

**Định nghĩa "ngoài miền" và "sai kiểu"**
- `tuoi`: hợp lệ khi là số hữu hạn ≥ 0 và không phải `bool`.
- `huyet_ap_tam_thu`, `huyet_ap_tam_thu_nen`: hợp lệ khi là số nguyên > 0 (không phải `bool`) hoặc `null`.
- Các trường bool: hợp lệ khi đúng là `True` hoặc `False` (chuỗi `"true"`, số `0/1` là sai kiểu).

**Bảng policy** (áp dụng cho cả 4 tình huống: thiếu khóa / `null` / sai kiểu / ngoài miền)

| Trường | Khi không dùng được thì | Hệ quả |
|---|---|---|
| `tuoi` | → `THEO_DOI` ngay (Q-02), `rule_id = null` | Không đánh giá tiếp |
| `huyet_ap_tam_thu` | Không xác định | Không đánh giá được tụt HA; nếu khớp Tầng 2 → `PHAN_VE` (Q-03) |
| `huyet_ap_tam_thu_nen` | Không xác định | Tuổi ≥ 18 chỉ dùng tiêu chí HATT < 90 (Q-04) |
| `co_di_nguyen_nghi_ngo` | Không xác định | R01 (cần `false`) và R02/R03 (cần `true`) đều không thỏa → `THEO_DOI` |
| `di_nguyen_qua_duong_hit` | Không xác định | Nhánh "không hít và hô hấp" của R03 không thỏa; nhánh tuần hoàn của R03 và R02 **không bị ảnh hưởng** |
| `co_ton_thuong_da_niem_mac` | Không xác định, không tính là `true` | Không tính vào R01/R02; các rule khác vẫn xét bình thường |
| `co_trieu_chung_ho_hap` | Không xác định, không tính là `true` | Như trên |
| `co_trieu_chung_tuan_hoan` | Không xác định, không tính là `true` | Như trên |
| `co_trieu_chung_tieu_hoa_nang` | Không xác định, không tính là `true` | Không tính vào đếm của R02 |

### 6.3. Thiết kế audit (Q-06)

- `classify(data)` giữ nguyên chữ ký của starter, **không nhận** `User_UUID`, chỉ trả `muc_do`, `rule_id`, `ly_do`.
- Hàm bọc **`classify_with_audit(data, user_uuid, audit_sink)`** gọi `classify()` rồi ghi audit.
- **`User_UUID`** do **bên gọi** cung cấp qua tham số riêng, nằm ngoài dữ liệu lâm sàng; phải là chuỗi UUID hợp lệ (không hợp lệ → `ValueError`, vì đây là lỗi của bên gọi, không phải dữ liệu lâm sàng).
- **Nơi ghi:** `audit_sink` do bên gọi truyền vào (mặc định: danh sách trong bộ nhớ). Test đọc trực tiếp từ sink này.
- **Bản ghi** gồm đúng 4 khóa: `Timestamp` (ISO 8601, UTC), `User_UUID`, `Action_Type` (`"CLASSIFY"`), `Status` (`"OK"` hoặc `"ERROR"`).
- Không ghi `muc_do`, `rule_id`, `ly_do` hay bất kỳ giá trị nào của input.

## 7. Acceptance criteria

Mỗi tiêu chí dạng Given–When–Then, kiểm bằng unit test tương ứng. Cột "Loại" theo yêu cầu A-07 của đề. Các tiêu chí **AC-28 trở đi là bổ sung theo nhận xét của thầy**.

### 7.1. Phân loại Tầng 2 (Phản vệ)

| ID | Loại | Given | Then |
|---|---|---|---|
| AC-01 | normal | Không nghi dị nguyên, da/niêm mạc ✓, hô hấp ✓, HATT bình thường | `PHAN_VE`, `R01-PV` |
| AC-02 | boundary | Không nghi dị nguyên, da/niêm mạc ✓, **chỉ** tiêu hóa ✓ | `THEO_DOI` (R01 cần hô hấp hoặc tuần hoàn) |
| AC-03 | boundary | Không nghi dị nguyên, da/niêm mạc ✗, hô hấp ✓ | `THEO_DOI` |
| AC-04 | normal | Nghi dị nguyên, da/niêm mạc ✓ + tiêu hóa ✓ (đúng 2 hệ) | `PHAN_VE`, `R02-PV` |
| AC-05 | boundary | Nghi dị nguyên, chỉ da/niêm mạc ✓ (1 hệ) | `THEO_DOI` |
| AC-06 | normal | Nghi dị nguyên, chỉ hô hấp ✓, không hít | `PHAN_VE`, `R03-PV` |
| AC-07 | boundary | Nghi dị nguyên, chỉ hô hấp ✓, **có** hít | `THEO_DOI` |
| AC-08 | normal | Nghi dị nguyên, chỉ tuần hoàn ✓ | `PHAN_VE`, `R03-PV` |
| **AC-28** | priority | Nghi dị nguyên, hô hấp ✓ (không hít) **và** tuần hoàn ✓ (đồng thời thỏa R02 và R03), HATT không tụt | `PHAN_VE`, **`R02-PV`** (R02 đứng trước R03) |

### 7.2. Phân loại Tầng 1 (Sốc phản vệ), ca biên theo ngưỡng tuổi

Điều kiện nền: input đã khớp Tầng 2.

| ID | Loại | Tuổi | HATT (nền) | Then |
|---|---|---|---|---|
| AC-09 | boundary | 0.5 | 69 | `SOC_PHAN_VE`, `R-SOC` |
| AC-10 | boundary | 0.5 | 70 | `PHAN_VE` (không tụt, dấu `<` chặt) |
| AC-11 | boundary | 5 | 79 | `SOC_PHAN_VE` (ngưỡng 70+2×5 = 80) |
| AC-12 | boundary | 5 | 80 | `PHAN_VE` |
| AC-13 | boundary | 11 | 89 | `SOC_PHAN_VE` (ca này **không** phân biệt hai nhóm tuổi; xem AC-31…AC-34) |
| AC-14 | boundary | 11 | 90 | `PHAN_VE` |
| AC-15 | boundary | 18 | 89 (nền null) | `SOC_PHAN_VE` |
| AC-16 | boundary | 18 | 90 (nền null) | `PHAN_VE` |
| AC-17 | boundary | 40 | 104 (nền 150) | `SOC_PHAN_VE` (giảm 30,7% > 30%) |
| AC-18 | boundary | 40 | 105 (nền 150) | `PHAN_VE` (giảm đúng 30%, không "> 30%") |

**Ca chuyển nhóm tuổi (bổ sung theo nhận xét):** mỗi cặp dưới đây phân biệt công thức của hai nhóm tuổi kề nhau.

| ID | Loại | Tuổi | HATT (nền) | Ngưỡng áp dụng | Then |
|---|---|---|---|---|---|
| AC-29 | boundary | 0.99 | 71 | <1 tuổi: <70 | `PHAN_VE` (71 không tụt) |
| AC-30 | boundary | 1 | 71 | 1–<11: 70+2×1 = 72 | `SOC_PHAN_VE` |
| AC-31 | boundary | 1 | 72 | 72 | `PHAN_VE` (72 < 72 sai) |
| AC-32 | boundary | 10.9 | 91 | 1–<11: 70+2×10,9 = 91,8 | `SOC_PHAN_VE` |
| AC-33 | boundary | 10.9 | 92 | 91,8 | `PHAN_VE` |
| AC-34 | boundary | 11 | 91 | 11–<18: <90 (công thức nhóm trước sẽ cho 92, tức là sốc) | `PHAN_VE` |
| AC-35 | boundary | 17.9 | 100 (nền 150) | 11–<18: chỉ xét <90, **không** dùng tiêu chí nền | `PHAN_VE` |
| AC-36 | boundary | 18 | 100 (nền 150) | ≥18: giảm 33,3% > 30% | `SOC_PHAN_VE` |

### 7.3. Input thiếu, sai, ngoài miền (theo policy mục 6.2)

| ID | Loại | Given | Then |
|---|---|---|---|
| AC-19 | missing | Thiếu `tuoi` (hoặc `null`) | `THEO_DOI`, không lỗi (Q-02) |
| AC-20 | missing | Khớp Tầng 2, `huyet_ap_tam_thu` thiếu hoặc null | `PHAN_VE` (Q-03) |
| AC-21 | invalid | `tuoi` âm hoặc sai kiểu (chuỗi, `bool`, NaN) | `THEO_DOI`, không crash |
| AC-22 | invalid | Input chứa trường định danh (vd tên) | Bỏ qua, không lưu, không ghi vào audit/log (Zero PII) |
| **AC-37** | missing | Nghi dị nguyên, da/niêm mạc ✓, hô hấp ✓, **thiếu khóa** `co_trieu_chung_tieu_hoa_nang` | `PHAN_VE`, `R02-PV` (không hạ mức) |
| **AC-38** | missing | Nghi dị nguyên, tuần hoàn ✓, `di_nguyen_qua_duong_hit` là `null` | `PHAN_VE`, `R03-PV` (nhánh tuần hoàn không cần trường hít) |
| **AC-39** | missing | Nghi dị nguyên, hô hấp ✓, `di_nguyen_qua_duong_hit` là `null` (chỉ 1 hệ, không rule nào thỏa đủ) | `THEO_DOI` |
| **AC-40** | missing | `co_di_nguyen_nghi_ngo` thiếu hoặc `null`, các triệu chứng khác đầy đủ | `THEO_DOI` (R01/R02/R03 đều cần biết trường này) |
| **AC-41** | invalid | Trường bool nhận chuỗi `"true"` hoặc số `1` (sai kiểu) | Coi như không xác định, không crash, không tính là `true` |
| **AC-42** | invalid | `huyet_ap_tam_thu` âm, bằng 0 hoặc sai kiểu; đã khớp Tầng 2 | Coi như không xác định → `PHAN_VE` |
| **AC-43** | missing | Tuổi ≥ 18, `huyet_ap_tam_thu_nen` thiếu, HATT = 100, đã khớp Tầng 2 | `PHAN_VE` (chỉ dùng tiêu chí < 90, Q-04) |
| **AC-44** | invalid | Input không phải dict (`None`, danh sách) | `THEO_DOI`, không crash |

### 7.4. Giải thích, audit, hiệu năng

| ID | Đối chiếu | Tiêu chí |
|---|---|---|
| AC-23 | A-05 | `ly_do` nêu rule đã kích hoạt, không chứa giá trị tuổi/huyết áp/triệu chứng, không có lời khuyên điều trị |
| AC-24 | A-06 | Mỗi lần gọi `classify_with_audit()` sinh đúng 1 bản ghi trong `audit_sink`, có đúng 4 khóa `Timestamp, User_UUID, Action_Type, Status` |
| AC-25 | A-06 | Bản ghi audit không chứa `muc_do`, `rule_id`, `ly_do` hay bất kỳ giá trị nào từ input lâm sàng |
| **AC-45** | A-06 | `User_UUID` trong bản ghi đúng bằng UUID bên gọi truyền vào; UUID không hợp lệ → `ValueError` và không ghi bản ghi nào |
| AC-26 | A-10 | 1.000 lần chạy sau warm-up, p95 < 100 ms, kèm khai báo cấu hình máy đo |
| AC-27 | A-02 | Test có ca dùng dữ liệu không nằm trong public fixture, kết quả vẫn đúng |

## 8. Bảng truy vết

| Tiêu chí đề | Yêu cầu | Tiêu chí chấp nhận |
|---|---|---|
| A-01, A-03 | FR-01…FR-07 | AC-01…AC-18, AC-28…AC-36 |
| A-02 | NFR-01 | AC-27 |
| A-04 | FR-10 | AC-19…AC-22, AC-37…AC-44 |
| A-05 | FR-08 | AC-23 |
| A-06 | FR-09 | AC-24, AC-25, AC-45 |
| A-07 | (cả bộ test) | Đủ normal / boundary / invalid / missing |
| A-08, A-09 | NFR-02, NFR-03 | Kiểm bằng CI, ghi trong `TEST_REPORT.md` |
| A-10 | NFR-04 | AC-26 |
| A-11 | NFR-05 | Kiểm thủ công trong README |

## 9. Rủi ro

| Rủi ro | Cách giảm |
|---|---|
| Hiểu sai điều kiện R01/R02/R03 (test ẩn chấm 10đ) | Có ca test cho cả hai phía của mỗi điều kiện (AC-01…AC-08) và ca ưu tiên (AC-28) |
| Sai dấu so sánh ở ngưỡng, hoặc lẫn công thức giữa các nhóm tuổi | Ca biên AC-09…AC-18 và các cặp phân biệt nhóm tuổi AC-29…AC-36 |
| Policy input lỗi (mục 6.2) lệch với hướng dẫn của thầy | Đối chiếu với issue #15 mục 5; mỗi dòng policy có ca test |
| Trùng lịch với đồ án PBL | Chia việc theo tuần |

## 10. Lịch sử sửa theo nhận xét Checkpoint 1

| Nhận xét của thầy | Đã xử lý ở |
|---|---|
| Q-01…Q-04 đã có câu trả lời ở issue #15 | Mục 6.1 (đổi trạng thái, dẫn link), FR-04, FR-07 |
| Q-05 phải chốt, không hạ mức, viết bảng policy theo trường, thêm test | Mục 6.2, FR-10, AC-37…AC-44, ADR-003 |
| Thiếu ca chứng minh thứ tự ưu tiên | AC-28, ADR-002 |
| AC-13 không phân biệt nhóm tuổi | AC-29…AC-36 (kèm ghi chú ở AC-13) |
| Q-06 chốt ai cấp `User_UUID` và audit ghi vào đâu | Mục 6.3, AC-24, AC-25, AC-45, ADR-004 |
