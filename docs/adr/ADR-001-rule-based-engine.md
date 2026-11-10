# ADR-001: Kiến trúc Rule Engine Tất định, Thứ tự Ưu tiên và Đánh đổi Không hạ mức

* **Trạng thái:** Accepted (Đã cập nhật theo phản hồi Checkpoint 1 & Issue #15)
* **Ngày cập nhật:** 11/11/2026
* **Nhóm thực hiện:** Nhóm 62 (Track A — Dr May Day: Rule Engine Sprint)

## 1. Bối cảnh (Context)

Module Rule Engine (`rule_engine/classifier.py`) cần phân loại nguy cơ phản vệ theo bảng quyết định WAO/EAACI V1 (`docs/decision-table.md`) thành 3 mức: `SOC_PHAN_VE`, `PHAN_VE`, `THEO_DOI`. Hệ thống phải thỏa mãn đồng thời các ràng buộc kỹ thuật và an toàn miền y tế:
- Hoạt động hoàn toàn tất định (deterministic), không dùng Machine Learning/LLM, độ trễ `p95 < 100 ms`.
- Đảm bảo nguyên tắc **Zero PII** (không tiếp nhận, không lưu trữ và không xuất thông tin định danh cá nhân hay dữ liệu lâm sàng thô trong `ly_do` và `Audit Trail`).
- Tuân thủ thứ tự ưu tiên quy tắc và nguyên tắc **"Không hạ mức" (No-Downgrade)** đối với các ca phản vệ rõ ràng theo kết luận tại Issue #15 (`fossbk-spec/ktpmud-project#15`).

## 2. Quyết định Thiết kế (Decision)

### 2.1. Kiến trúc Đánh giá Luật 2 Tầng Tất định & Tính toán Số nguyên
- Tách bạch rõ 3 bước xử lý tuần tự trong `classify()`:
  1. **Sanitization & Validation:** Lọc khóa hợp lệ và kiểm tra kiểu dữ liệu.
  2. **Rule Evaluation (Tầng 2 → Tầng 1):** Đánh giá 3 kịch bản phản vệ Tầng 2 trước; chỉ khi đạt ít nhất một kịch bản Tầng 2 mới kiểm tra ngưỡng tụt huyết áp tâm thu theo tuổi ở Tầng 1 (`R-SOC`).
  3. **Audit Logging:** Ghi bản ghi kiểm toán 4 trường tĩnh `[Timestamp, User_UUID, Action_Type, Status]`.
- Với tiêu chí người lớn (`tuoi >= 18`) tụt HATT > 30% so với `huyet_ap_tam_thu_nen`, sử dụng phép nhân số nguyên **`10 * HATT < 7 * HATT_nen`** thay vì số thực `HATT < 0.7 * HATT_nen` để triệt tiêu hoàn toàn sai số dấu phẩy động (floating-point precision error) tại điểm biên đúng 70%.

### 2.2. Thứ tự Ưu tiên Quy tắc (Rule Priority — Issue #15)
- Thứ tự ưu tiên chuẩn được khóa cố định là: **`R-SOC > R01-PV > R02-PV > R03-PV`**.
- Ở Tầng 2:
  - `R01-PV` (`co_di_nguyen_nghi_ngo = false`) loại trừ tương hỗ với `R02-PV` và `R03-PV` (`co_di_nguyen_nghi_ngo = true`).
  - Khi bệnh nhân có `co_di_nguyen_nghi_ngo = true` và đồng thời thỏa cả `R02-PV` (≥ 2/4 hệ cơ quan dương tính) lẫn `R03-PV` (hô hấp không qua đường hít hoặc tuần hoàn), hệ thống ưu tiên trả về **`R02-PV`**.

### 2.3. Đánh đổi Thiết kế 1: Xử lý Trường lạ ngoài 9 trường (An toàn PII ↔ Rủi ro Hạ mức)
- **Các phương án cân nhắc:**
  - *Phương án 1A (Reject on Unknown Fields):* Từ chối toàn bộ dict đầu vào và trả về `THEO_DOI / null` ngay khi phát hiện bất kỳ khóa nào ngoài 9 trường chuẩn. Phương án này chặn PII đơn giản nhưng gây rủi ro **hạ mức lâm sàng**: nếu hệ thống gọi đính kèm trường metadata hoặc định danh thừa trên một bệnh nhân đang phản vệ/sốc phản vệ cấp cứu, bệnh nhân sẽ bị trả về `THEO_DOI`.
  - *Phương án 1B (Whitelist Sanitization — Lọc bỏ trường lạ):* Ngay tại biên hàm `classify()`, chỉ giữ lại các khóa nằm trong tập 9 trường chuẩn (`KNOWN_FIELDS`), loại bỏ hoàn toàn các khóa lạ khỏi bộ nhớ xử lý, không bao giờ đọc hoặc đưa tên/giá trị trường lạ vào chuỗi `ly_do` hay `Audit Trail`.
- **Lựa chọn của nhóm:** Chọn **Phương án 1B (Whitelist Sanitization)**.
- **Lý do:** Đạt được cả hai mục tiêu: vừa ngăn chặn tuyệt đối rò rỉ PII ra output/audit (Zero PII), vừa giữ nguyên kết quả cảnh báo `PHAN_VE` / `SOC_PHAN_VE` khi dữ liệu lâm sàng hợp lệ đã đủ kết luận.

### 2.4. Đánh đổi Thiết kế 2: Xử lý Cờ Bool thiếu/null và HATT ngoài miền `1..300`
- **Với cờ `bool` thiếu khóa hoặc nhận `null` (Issue #15 mục 5):**
  - Đánh giá các kịch bản `R01-PV`, `R02-PV`, `R03-PV` dựa trên các cờ đang có giá trị `True`/`False` rõ ràng. Nếu các trường hiện có đã đủ làm thỏa trọn vẹn một quy tắc (ví dụ thiếu `co_trieu_chung_ho_hap` nhưng đã có `co_di_nguyen_nghi_ngo = true` và `co_trieu_chung_tuan_hoan = true`), hệ thống **không hạ mức** mà trả về đúng quy tắc đó (`R03-PV`, hoặc `R-SOC` nếu kèm tụt HATT).
  - Chỉ khi không có quy tắc nào thỏa mãn (kết quả phụ thuộc vào trường bị thiếu), hệ thống mới trả về `THEO_DOI / null` với trạng thái `INVALID_INPUT`.
  - Các trường `bool` truyền sai kiểu dữ liệu (như `"true"`, `1`, `0`) vẫn bị từ chối là `INVALID_INPUT` để đảm bảo tính chặt chẽ của kiểu dữ liệu (type safety).
- **Với `huyet_ap_tam_thu` / `huyet_ap_tam_thu_nen` ngoài miền `1..300` hoặc sai kiểu:**
  - Nếu ca bệnh đã thỏa một kịch bản Phản vệ ở Tầng 2, một giá trị HATT ngoài miền (ví dụ `0`, `-10`, `350`) được xử lý tương tự như trường hợp "không đo được huyết áp" (`null`): không dùng giá trị lỗi đó để kích hoạt nhầm `R-SOC`, nhưng **vẫn giữ nguyên mức `PHAN_VE`** của Tầng 2 thay vì hạ xuống `THEO_DOI`.
  - Nếu ca bệnh không thỏa kịch bản Tầng 2 nào và có HATT ngoài miền/sai kiểu, hệ thống trả về `THEO_DOI / null` (`INVALID_INPUT`).

## 3. Hệ quả (Consequences)

- **Tích cực:**
  - Không bỏ sót hoặc hạ mức các ca phản vệ/sốc phản vệ đã có đủ triệu chứng lâm sàng rõ ràng.
  - Chuỗi `ly_do` sử dụng từ điển thông điệp tĩnh theo mã quy tắc nên loại bỏ 100% nguy cơ rò rỉ dữ liệu lâm sàng thô hoặc thông tin cá nhân (PII).
  - Thời gian thực thi mỗi lần gọi `classify()` chỉ tốn vài micro-giây (`p95 < 0.05 ms`), vượt xa yêu cầu `< 100 ms`.
- **Giới hạn & Kiểm soát:**
  - Cần bộ kiểm thử tự động bao phủ cả nhánh "đủ điều kiện không hạ mức" và nhánh "thiếu dữ liệu phụ thuộc" (đã hiện thực hóa tại `TC03`, `TC05`, `TC08`, `TC11`, `TC14`, `TC33`, `TC34` trong `tests/test_classifier.py`).