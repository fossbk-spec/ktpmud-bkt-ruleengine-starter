# REQUIREMENTS — Dr May Day: Rule Engine Sprint (Track A)

- Nguồn đặc tả duy nhất: `docs/decision-table.md` (tag `bkt-2026-v1`)

## 1. Mục đích

Xây một module Rule Engine độc lập, nhận bộ dữ liệu synthetic theo Data Dictionary, phân loại theo bảng quyết định WAO/EAACI V1 thành `SOC_PHAN_VE`, `PHAN_VE` hoặc `THEO_DOI`, trả kết quả giải thích được và ghi audit trail tối thiểu.

## 2. Phạm vi

### 2.1. Trong phạm vi
- Hàm `classify()` trong `rule_engine/classifier.py`.
- Kiểm tra hợp lệ dữ liệu đầu vào (thiếu, sai kiểu, ngoài miền).
- Đánh giá Tầng 1 (R-SOC) và Tầng 2 (R01-PV, R02-PV, R03-PV) và thứ tự ưu tiên.
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
- `tuoi` — float (năm). Cho phép số lẻ, ví dụ 0.5 là 6 tháng tuổi.
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

## 5. Chính sách xử lý đầu vào (policy A-04)

Đề yêu cầu xử lý input thiếu, sai kiểu, ngoài miền "theo policy đã công bố". Policy của nhóm:

- Thiếu bất kỳ trường bắt buộc → `THEO_DOI`, `rule_id = null`.
- Trường bool nhận giá trị không phải `bool` (ví dụ `1`, `"true"`, `null`) → `THEO_DOI`, không ép kiểu.
- `tuoi` không phải số (kể cả `bool`, chuỗi), NaN, ±inf → `THEO_DOI`.
- `tuoi` ngoài miền `0 ≤ tuoi ≤ 120` (gồm tuổi âm) → `THEO_DOI`.
- HATT hoặc HATT nền không phải `int` hoặc `null` (kể cả `bool`, float, chuỗi) → `THEO_DOI`.
- HATT hoặc HATT nền là số nguyên ngoài miền `1 ≤ giá trị ≤ 300` → `THEO_DOI`.
- Có trường lạ ngoài 9 trường (nguy cơ PII) → `THEO_DOI`, không lặp lại tên hay giá trị trường lạ trong output hoặc audit.
- Hai trường HA vắng key → coi như `null`.
- `tuoi` là `int` → chấp nhận như số hợp lệ.

Nguyên tắc chung: không ném exception ra ngoài, không tự ép kiểu, không coi dữ liệu thiếu là `false`. `ly_do` của input không hợp lệ phải khác `ly_do` của trường hợp "không khớp quy tắc nào" để người dùng phân biệt được.

## 6. Yêu cầu chức năng

- **FR-01** — Nhận dữ liệu theo đúng 9 trường của Data Dictionary. (AC01)
- **FR-02** — Kiểm tra kiểu và miền giá trị theo mục 5; không ép kiểu. (AC02, AC05)
- **FR-03** — Thiếu dữ liệu cần thiết để đánh giá → `THEO_DOI`; xử lý đúng trường nullable. (AC03, AC04)
- **FR-04** — R01-PV: `co_di_nguyen_nghi_ngo = false` VÀ `co_ton_thuong_da_niem_mac = true` VÀ (`co_trieu_chung_ho_hap = true` HOẶC `co_trieu_chung_tuan_hoan = true`). (AC06)
- **FR-05** — R02-PV: `co_di_nguyen_nghi_ngo = true` VÀ số hệ cơ quan dương tính (da/niêm mạc, hô hấp, tuần hoàn, tiêu hóa nặng) ≥ 2. (AC07)
- **FR-06** — R03-PV: `co_di_nguyen_nghi_ngo = true` VÀ ((`di_nguyen_qua_duong_hit = false` VÀ `co_trieu_chung_ho_hap = true`) HOẶC `co_trieu_chung_tuan_hoan = true`). (AC08)
- **FR-07** — R-SOC: đạt ít nhất một kịch bản Tầng 2 VÀ HATT dưới ngưỡng theo tuổi (mục 7). (AC09)
- **FR-08** — Ưu tiên R-SOC > R03-PV > R02-PV. R01-PV loại trừ với R02/R03 vì khác `co_di_nguyen_nghi_ngo`. (AC10, AC11)
- **FR-09** — Không khớp Tầng 1 lẫn Tầng 2 → `THEO_DOI`, `rule_id = null`. (AC12, AC14)
- **FR-10** — Output có đủ `muc_do`, `rule_id`, `ly_do`; `ly_do` ngắn, truy vết được rule, không chứa dữ liệu lâm sàng thô, không có lời khuyên điều trị. (AC12–AC15, AC26)
- **FR-11** — Ghi audit đúng 4 trường cho mỗi lần phân loại, không ghi dữ liệu lâm sàng thô. (AC18, AC19)
- **FR-12** — Không tiếp nhận hoặc xuất thông tin định danh. (AC16)
- **FR-13** — Cùng input hợp lệ luôn cho cùng output. (AC17)

## 7. Ngưỡng sốc phản vệ theo tuổi (Tầng 1)

Chỉ áp dụng khi đã đạt Tầng 2. Ngưỡng lấy nguyên văn từ `decision-table.md`:

- `0 ≤ tuoi < 1`: HATT < 70.
- `1 ≤ tuoi < 11`: HATT < 70 + 2 × tuoi.
- `11 ≤ tuoi < 18`: HATT < 90.
- `tuoi ≥ 18`: HATT < 90 **hoặc** giảm > 30% so với HATT nền, tức `10 × HATT < 7 × HATT_nền`.

Quy ước triển khai (không đổi ngưỡng, chỉ làm rõ cách tính):
- So sánh là **nhỏ hơn thực sự** (`<`); bằng ngưỡng thì không thỏa.
- Tiêu chí giảm 30% tính bằng số nguyên để tránh sai số float; đúng bằng 70% HATT nền thì không thỏa.
- Người lớn không có HATT nền thì chỉ dùng tiêu chí `< 90`, và không coi đây là thiếu dữ liệu.
- HATT = null thì không đánh giá được Tầng 1, chuyển sang kết quả Tầng 2 (nếu có).

## 8. Output

```json
{ "muc_do": "SOC_PHAN_VE" | "PHAN_VE" | "THEO_DOI",
  "rule_id": "R-SOC" | "R01-PV" | "R02-PV" | "R03-PV" | null,
  "ly_do": "chuỗi giải thích ngắn"
}
```

Quy ước `ly_do`:
- Chỉ nêu tên quy tắc hoặc nhóm tiêu chí đã kích hoạt, hoặc nhóm lý do không hợp lệ (thiếu, sai kiểu, ngoài miền, chưa đủ tiêu chí).
- Không in giá trị tuổi, HATT hay trạng thái các cờ triệu chứng.
- Không có lời khuyên điều trị.
- Với `THEO_DOI`, nêu rõ đây là "chưa đủ dữ kiện kết luận".

## 9. Audit trail

Mỗi lần gọi `classify()` ghi một bản ghi gồm đúng 4 trường:

- `Timestamp` — thời điểm phân loại (UTC, ISO 8601).
- `User_UUID` — UUID của **người vận hành hoặc hệ thống gọi**, không phải bệnh nhân. Do bên gọi cung cấp, không nằm trong 9 trường input.
- `Action_Type` — loại hành động, ví dụ `CLASSIFY`.
- `Status` — trạng thái xử lý, ví dụ `SUCCESS` hoặc `INVALID_INPUT`.

Audit tuyệt đối không chứa triệu chứng, điểm số sức khỏe, giá trị đầu vào hay dữ liệu nhận dạng.

## 10. Yêu cầu phi chức năng

- **NFR-01** — Hiệu năng: benchmark tối thiểu 1.000 lần chạy sau warm-up, báo cáo p50/p95, **p95 < 100 ms** trên máy đo được khai báo. (AC23)
- **NFR-02** — Không hard-code theo ID của public fixture; có unit test cho normal, boundary, invalid, missing. (AC20, AC25)
- **NFR-03** — `pytest -q` đạt từ clean checkout. (AC21)
- **NFR-04** — CI chạy test trên Pull Request. (AC22)
- **NFR-05** — README ghi rõ "educational/synthetic — not for clinical use". (AC24)
- **NFR-06** — Ngưỡng và quy tắc khai báo tập trung một chỗ, không rải magic number; không dùng ML.
- **NFR-07** — Dữ liệu dùng trong test và demo đều là synthetic. (AC16)

## 11. Giả định cần xác nhận với TA

`decision-table.md` không nêu rõ các điểm sau. Nhóm đã chọn cách xử lý tạm ở trên và sẽ hỏi trên GitHub Issues của `fossbk-spec/ktpmud-project`:

- **Q1** — Đạt Tầng 2 nhưng HATT = null thì trả `PHAN_VE` hay `THEO_DOI`? Tạm thời: `PHAN_VE` (không khớp Tầng 1 vì không đánh giá được; Tầng 2 vẫn khớp).
- **Q2** — Miền hợp lệ của `tuoi` và HATT là bao nhiêu? Tạm thời: `0 ≤ tuoi ≤ 120`; HATT từ 1 đến 300.
- **Q3** — `tuoi` dạng `int` có được chấp nhận không? Tạm thời: có.
- **Q4** — Trường nullable vắng key có tính là thiếu không? Tạm thời: không, coi như `null`.
- **Q5** — Input có trường lạ xử lý thế nào? Tạm thời: `THEO_DOI`.
- **Q6** — Chữ ký `classify()` nhận `User_UUID` từ đâu? Tạm thời: tham số riêng hoặc ngữ cảnh của bên gọi, khớp theo starter.

## 12. Truy vết

- FR/NFR → AC: xem phần trong ngoặc ở mục 6 và 10.
- AC → Test case: xem `test-plan.md`.
- Quyết định kiến trúc: xem `ADR-001-rule-based-engine.md`.
- Ánh xạ sang ID của đề (A-01 … A-11): xem `acceptance-criteria.md`.
