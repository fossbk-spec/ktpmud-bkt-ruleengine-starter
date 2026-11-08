# REQUIREMENTS — Track A: Dr May Day Rule Engine Sprint

> Nhóm 11 · Phiên bản: v0.1 (Checkpoint 1)
> Nguồn đặc tả duy nhất: `docs/decision-table.md` (starter tag `bkt-2026-v1`).

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
| FR-04 | Phản vệ khi khớp **ít nhất 1** trong R01/R02/R03 | Tầng 2 |
| FR-05 | Tính ngưỡng tụt HATT theo tuổi: <1 tuổi: <70; 1 đến <11: <70+2×tuổi; 11 đến <18: <90; ≥18: <90 **hoặc** giảm >30% so với huyết áp nền | Tầng 1 |
| FR-06 | **Sốc phản vệ** (`R-SOC`) khi khớp Tầng 2 **và** tụt huyết áp theo FR-05 | Tầng 1 |
| FR-07 | Không khớp Tầng 1 lẫn Tầng 2 → `THEO_DOI`, `rule_id = null`. Trường hợp thiếu `tuoi` xử lý theo Q-02 (mục 6) | Mục kết quả `THEO_DOI` |
| FR-08 | Trả `ly_do` chỉ ra rule đã kích hoạt, không đưa lời khuyên điều trị, không chứa giá trị lâm sàng thô | Output, A-05 |
| FR-09 | Mỗi lần phân loại ghi audit `[Timestamp, User_UUID, Action_Type, Status]`; không ghi triệu chứng, điểm số, dữ liệu nhận dạng | A-06 |
| FR-10 | Xử lý input thiếu, sai kiểu, ngoài miền theo policy đã công bố (mục 6) | A-04 |

## 5. Yêu cầu phi chức năng

| ID | Yêu cầu | Tiêu chí đề |
|---|---|---|
| NFR-01 | Không hard-code theo ID của public fixture | A-02 |
| NFR-02 | `pytest -q` đạt từ clean checkout | A-08 |
| NFR-03 | CI chạy test trên mỗi Pull Request | A-09 |
| NFR-04 | Benchmark ≥ 1.000 lần chạy sau warm-up, báo cáo p50/p95; **p95 < 100 ms** trên máy đo đã khai báo | A-10 |
| NFR-05 | README ghi "educational/synthetic — not for clinical use" | A-11 |
| NFR-06 | Không commit secret, `.env`, dữ liệu thật | Mục 5.2 của đề |

## 6. Giả định và câu hỏi mở (chờ TA xác nhận)

Đặc tả không nói rõ các điểm sau. Nhóm **không tự suy diễn rule lâm sàng**, chỉ đưa ra giả định kỹ thuật tạm thời, có đánh dấu, và sẽ sửa nếu TA trả lời khác.

| ID | Tình huống | Giả định tạm thời | Trạng thái |
|---|---|---|---|
| Q-01 | Nhiều rule Tầng 2 cùng khớp (vd R02 và R03) thì `rule_id` là gì | Tạm thời: kiểm tra theo thứ tự R01 → R02 → R03, lấy rule đầu tiên khớp (xem ADR-002 trong `DECISIONS.md`) | Chờ TA |
| Q-02 | Thiếu `tuoi` nhưng Tầng 2 vẫn khớp | Theo đúng câu chữ của bảng: `THEO_DOI` | Chờ TA |
| Q-03 | `huyet_ap_tam_thu` là null khi đã khớp Tầng 2 | Không đánh giá được tụt huyết áp, trả `PHAN_VE` | Chờ TA |
| Q-04 | Tuổi ≥ 18 mà `huyet_ap_tam_thu_nen` là null | Chỉ dùng tiêu chí HATT < 90 | Chờ TA |
| Q-05 | Input sai kiểu, tuổi âm, thiếu trường bool, có trường lạ | Chưa chốt: (a) trả `THEO_DOI` như trường hợp thiếu dữ liệu, hoặc (b) từ chối kèm thông báo lỗi. Nhóm sẽ quyết định và ghi lý do vào `DECISIONS.md` | Chờ TA |
| Q-06 | `User_UUID` của audit lấy từ đâu (không nằm trong 9 trường input) | Truyền riêng như tham số của `classify()`, ngoài dữ liệu lâm sàng | Chờ TA |

## 7. Acceptance criteria

Mỗi tiêu chí dạng Given–When–Then, kiểm bằng unit test tương ứng. Cột "Loại" theo yêu cầu A-07 của đề.

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

### 7.2. Phân loại Tầng 1 (Sốc phản vệ), ca biên theo ngưỡng tuổi

Điều kiện nền: input đã khớp Tầng 2.

| ID | Loại | Tuổi | HATT (nền) | Then |
|---|---|---|---|---|
| AC-09 | boundary | 0.5 | 69 | `SOC_PHAN_VE`, `R-SOC` |
| AC-10 | boundary | 0.5 | 70 | `PHAN_VE` (không tụt, dấu `<` chặt) |
| AC-11 | boundary | 5 | 79 | `SOC_PHAN_VE` (ngưỡng 70+2×5 = 80) |
| AC-12 | boundary | 5 | 80 | `PHAN_VE` |
| AC-13 | boundary | 11 | 89 | `SOC_PHAN_VE` |
| AC-14 | boundary | 11 | 90 | `PHAN_VE` |
| AC-15 | boundary | 18 | 89 (nền null) | `SOC_PHAN_VE` |
| AC-16 | boundary | 18 | 90 (nền null) | `PHAN_VE` |
| AC-17 | boundary | 40 | 104 (nền 150) | `SOC_PHAN_VE` (giảm 30,7% > 30%) |
| AC-18 | boundary | 40 | 105 (nền 150) | `PHAN_VE` (giảm đúng 30%, không "> 30%") |

### 7.3. Input thiếu, sai, ngoài miền

| ID | Loại | Given | Then |
|---|---|---|---|
| AC-19 | missing | Thiếu `tuoi` | Theo Q-02 (tạm: `THEO_DOI`), không báo lỗi hệ thống |
| AC-20 | missing | Khớp Tầng 2, `huyet_ap_tam_thu` null | Theo Q-03 (tạm: `PHAN_VE`) |
| AC-21 | invalid | `tuoi` âm hoặc sai kiểu; trường bool nhận giá trị không phải bool | Theo Q-05 (xử lý nhất quán, không crash) |
| AC-22 | invalid | Input chứa trường định danh (vd tên) | Không được lưu hoặc ghi vào audit/log (Zero PII) |

### 7.4. Giải thích, audit, hiệu năng

| ID | Đối chiếu | Tiêu chí |
|---|---|---|
| AC-23 | A-05 | `ly_do` nêu rule đã kích hoạt, không chứa giá trị tuổi/huyết áp/triệu chứng, không có lời khuyên điều trị |
| AC-24 | A-06 | Mỗi lần gọi `classify()` sinh đúng 1 bản ghi audit gồm đúng 4 trường |
| AC-25 | A-06 | Bản ghi audit không chứa bất kỳ giá trị nào từ input lâm sàng |
| AC-26 | A-10 | 1.000 lần chạy sau warm-up, p95 < 100 ms, kèm khai báo cấu hình máy đo |
| AC-27 | A-02 | Test có ca dùng dữ liệu không nằm trong public fixture, kết quả vẫn đúng |


