# REQUIREMENTS — Dr May Day: Rule Engine Sprint (Track A)
- Nguồn đặc tả duy nhất: `docs/decision-table.md` (tag `bkt-2026-v1`) và Issue #15 (`fossbk-spec/ktpmud-project#15`).

## 1. Mục đích

Xây một module Rule Engine độc lập, nhận bộ dữ liệu synthetic theo Data Dictionary, phân loại theo bảng quyết định WAO/EAACI V1 thành `SOC_PHAN_VE`, `PHAN_VE` hoặc `THEO_DOI`, trả kết quả giải thích được và ghi audit trail tối thiểu.

## 2. Phạm vi

### 2.1. Trong phạm vi
- Hàm `classify()` trong `rule_engine/classifier.py`.
- Kiểm tra hợp lệ dữ liệu đầu vào theo nguyên tắc "không hạ mức" (Issue #15).
- Đánh giá Tầng 1 (`R-SOC`) và Tầng 2 (`R01-PV`, `R02-PV`, `R03-PV`) theo thứ tự ưu tiên chuẩn `R-SOC > R01-PV > R02-PV > R03-PV`.
- Output `{muc_do, rule_id, ly_do}`.
- Audit trail `[Timestamp, User_UUID, Action_Type, Status]`.
- Unit test, CI, benchmark latency, tài liệu bàn giao.

### 2.2. Ngoài phạm vi
- Giao diện, quản lý hồ sơ, lưu trữ dữ liệu bệnh nhân.
- Chẩn đoán hoặc khuyến nghị điều trị.
- Thay đổi ngưỡng hoặc thêm quy tắc ngoài `decision-table.md`.
- Machine learning / deep learning.
- Dữ liệu thật; tích hợp với Dr May Day production.

## 3. Thuật ngữ

- **HATT:** huyết áp tâm thu (`huyet_ap_tam_thu`), đơn vị mmHg.
- **HATT nền:** `huyet_ap_tam_thu_nen`, chỉ dùng cho người từ 18 tuổi trở lên.
- **Tầng 1 / Tầng 2:** điều kiện sốc phản vệ / điều kiện phản vệ trong bảng quyết định.
- **THEO_DOI:** trạng thái "chưa đủ dữ kiện kết luận", **không** phải kết luận an toàn.
- **Dữ liệu lâm sàng thô:** giá trị cụ thể của tuổi, HATT và các cờ triệu chứng.

## 4. Data Dictionary (9 trường)

Bắt buộc (7 trường):
- `tuoi` — float (năm). Cho phép số lẻ, ví dụ 0.5 là 6 tháng tuổi (chấp nhận cả `int`).
- `co_di_nguyen_nghi_ngo` — bool.
- `di_nguyen_qua_duong_hit` — bool. Ảnh hưởng R03.
- `co_ton_thuong_da_niem_mac` — bool.
- `co_trieu_chung_ho_hap` — bool.
- `co_trieu_chung_tuan_hoan` — bool.
- `co_trieu_chung_tieu_hoa_nang` — bool.

Được phép null hoặc vắng key (2 trường):
- `huyet_ap_tam_thu` — int hoặc null. Đơn vị mmHg, null nếu không đo được.
- `huyet_ap_tam_thu_nen` — int hoặc null. Chỉ dùng khi `tuoi >= 18` và muốn áp dụng tiêu chí giảm 30%.

**Zero PII:** không nhận và không xuất tên, CCCD, SĐT, địa chỉ hay bất kỳ trường định danh nào.

## 5. Chính sách xử lý đầu vào (Policy A-04 — Cập nhật theo Issue #15)

- **Thiếu hoặc sai `tuoi`:** `tuoi` vắng mặt, `null`, không phải số (kể cả `bool`, chuỗi), `NaN`, `±inf`, hoặc ngoài miền `0 ≤ tuoi ≤ 120` → `THEO_DOI`, `rule_id = null`, `Status = INVALID_INPUT`.
- **Trường bool sai kiểu:** Nhận giá trị khác `bool` và khác `null` (ví dụ `1`, `0`, `"true"`) → `THEO_DOI`, `rule_id = null`, không ép kiểu.
- **Trường bool thiếu khóa hoặc `null` (Nguyên tắc không hạ mức — Issue #15 mục 5):**
  - Nếu các trường hợp lệ hiện có **đã thỏa trọn một quy tắc** (ví dụ thiếu `co_trieu_chung_ho_hap` nhưng đã có `co_di_nguyen_nghi_ngo = true` và `co_trieu_chung_tuan_hoan = true`) → **không hạ mức**, trả về đúng mức phân loại đạt được (`PHAN_VE` hoặc `SOC_PHAN_VE`).
  - Chỉ khi không có quy tắc nào thỏa mãn (kết quả phụ thuộc vào khóa bị thiếu) → trả về `THEO_DOI`, `rule_id = null`, `Status = INVALID_INPUT`.
- **HATT hoặc HATT nền ngoài miền `1..300` hoặc sai kiểu (Nguyên tắc không hạ mức):**
  - Nếu đã thỏa một kịch bản Tầng 2: coi chỉ số huyết áp lỗi đó như không đo được (`null`) để **vẫn giữ mức `PHAN_VE`**, không hạ xuống `THEO_DOI` (xem đánh đổi tại `ADR-001`).
  - Nếu không thỏa kịch bản Tầng 2 nào: trả về `THEO_DOI`, `rule_id = null`, `Status = INVALID_INPUT`.
- **Trường lạ ngoài 9 trường (Bảo vệ PII & Không hạ mức):**
  - Hệ thống lọc bỏ (ignore) mọi trường lạ ngay khi tiếp nhận, tuyệt đối không đưa tên hay giá trị trường lạ vào `ly_do` hoặc `Audit Trail`, và tiếp tục đánh giá 9 trường chuẩn để không làm hạ mức ca phản vệ (xem đánh đổi tại `ADR-001`).

Nguyên tắc chung: không ném exception ra ngoài, không tự ép kiểu. `ly_do` của input thiếu/không hợp lệ khác với `ly_do` của trường hợp "không khớp quy tắc nào".

## 6. Yêu cầu chức năng

- **FR-01** — Nhận dữ liệu theo đúng 9 trường của Data Dictionary; lọc bỏ trường lạ an toàn. (AC01, AC16)
- **FR-02** — Kiểm tra kiểu và miền giá trị theo mục 5; không ép kiểu. (AC02, AC05)
- **FR-03** — Áp dụng nguyên tắc không hạ mức với khóa bool bị thiếu/null và trường HA nullable/ngoài miền. (AC03, AC04)
- **FR-04** — R01-PV: `co_di_nguyen_nghi_ngo = false` VÀ `co_ton_thuong_da_niem_mac = true` VÀ (`co_trieu_chung_ho_hap = true` HOẶC `co_trieu_chung_tuan_hoan = true`). (AC06)
- **FR-05** — R02-PV: `co_di_nguyen_nghi_ngo = true` VÀ số hệ cơ quan dương tính (da/niêm mạc, hô hấp, tuần hoàn, tiêu hóa nặng) ≥ 2. (AC07)
- **FR-06** — R03-PV: `co_di_nguyen_nghi_ngo = true` VÀ ((`di_nguyen_qua_duong_hit = false` VÀ `co_trieu_chung_ho_hap = true`) HOẶC `co_trieu_chung_tuan_hoan = true`). (AC08)
- **FR-07** — R-SOC: đạt ít nhất một kịch bản Tầng 2 VÀ HATT hợp lệ dưới ngưỡng theo tuổi (mục 7). (AC09)
- **FR-08** — Thứ tự ưu tiên chuẩn theo Issue #15: **`R-SOC > R01-PV > R02-PV > R03-PV`**. Khi cả `R02-PV` và `R03-PV` cùng thỏa thì ưu tiên `R02-PV`. `R01-PV` loại trừ với `R02/R03` vì khác `co_di_nguyen_nghi_ngo`. (AC10, AC11)
- **FR-09** — Không khớp Tầng 1 lẫn Tầng 2 → `THEO_DOI`, `rule_id = null`. (AC12, AC14)
- **FR-10** — Output có đủ `muc_do`, `rule_id`, `ly_do`; `ly_do` ngắn, truy vết được rule, không chứa dữ liệu lâm sàng thô, không có lời khuyên điều trị. (AC12–AC15, AC26)
- **FR-11** — Ghi audit đúng 4 trường cho mỗi lần phân loại, không ghi dữ liệu lâm sàng thô. (AC18, AC19)
- **FR-12** — Không tiếp nhận hoặc xuất thông tin định danh. (AC16)
- **FR-13** — Cùng input hợp lệ luôn cho cùng output. (AC17)

## 7. Ngưỡng sốc phản vệ theo tuổi (Tầng 1)

Chỉ áp dụng khi đã đạt Tầng 2 và có HATT hợp lệ (`1 ≤ HATT ≤ 300`):
- `0 ≤ tuoi < 1`: HATT < 70.
- `1 ≤ tuoi < 11`: HATT < 70 + 2 × tuoi.
- `11 ≤ tuoi < 18`: HATT < 90.
- `tuoi ≥ 18`: HATT < 90 **hoặc** giảm > 30% so với HATT nền hợp lệ, tức `10 × HATT < 7 × HATT_nền`.

Quy ước triển khai:
- So sánh là **nhỏ hơn thực sự** (`<`); bằng ngưỡng thì không thỏa.
- Tiêu chí giảm 30% tính bằng số nguyên (`10 * HATT < 7 * HATT_nen`) để tránh sai số số thực; đúng bằng 70% HATT nền thì không thỏa.
- Người lớn không có HATT nền thì chỉ dùng tiêu chí `< 90`, không coi là thiếu dữ liệu.
- HATT = null (hoặc ngoài miền) thì không đánh giá được Tầng 1, giữ kết quả `PHAN_VE` của Tầng 2.

## 8. Output

```json
{ "muc_do": "SOC_PHAN_VE" | "PHAN_VE" | "THEO_DOI",
  "rule_id": "R-SOC" | "R01-PV" | "R02-PV" | "R03-PV" | null,
  "ly_do": "chuỗi giải thích ngắn"
}