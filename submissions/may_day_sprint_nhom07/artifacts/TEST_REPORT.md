# KẾ HOẠCH & BÁO CÁO KIỂM THỬ (TEST PLAN & REPORT) — TRACK A: RULE ENGINE
**Dự án:** Track A — Dr May Day: Rule Engine Sprint  
**Mã nhóm:** Nhóm 07  
**Giai đoạn:** M1 — Understand & M2 — Refinement  

---

## 1. Mục tiêu kiểm thử (Testing Objectives)
* **Đảm bảo tính chính xác tất định (Deterministic Accuracy):** Kiểm chứng toàn bộ logic phân loại dựa trên bảng quyết định (`docs/decision-table.md`) từ Tầng 1 (Sốc phản vệ) đến Tầng 2 (Phản vệ).
* **Độ bao phủ toàn diện (Coverage):** Xây dựng bộ test phủ kín các kịch bản chuẩn (Normal), ranh giới (Boundary), dữ liệu lỗi/không hợp lệ (Invalid) và thiếu dữ liệu (Missing) theo đúng chính sách tại `issue #15`[cite: 2].
* **Tuân thủ an toàn & Kiểm toán (Audit & Safety Compliance):** Xác thực định dạng audit log (`[Timestamp, User_UUID, Action_Type, Status]`) và cam kết tuyệt đối không để lộ thông tin nhạy cảm hoặc triệu chứng thô[cite: 2].

---

## 2. Chiến lược thiết kế Test Cases

### 2.1. Normal Cases (Ca đúng chuẩn)
* **Mục tiêu:** Kiểm tra các trường hợp dữ liệu đầu vào thỏa mãn hoàn toàn các điều kiện quy định trong ma trận quyết định.
* **Kịch bản mẫu:**
  * `TC-NORM-01 (Kịch bản R01):` Bệnh nhân đạt tiêu chuẩn kịch bản Tầng 2 `R01` kèm theo HATT tụt quá ngưỡng phân loại theo nhóm tuổi $\rightarrow$ Kỳ vọng `muc_do: SOC_PHAN_VE`, `rule_id: R01`, kèm trường `ly_do`.
  * `TC-NORM-02 (Kịch bản R02):` Bệnh nhân thỏa mãn kịch bản Tầng 2 `R02` (với đúng 2 hệ cơ quan bị ảnh hưởng) nhưng huyết áp không tụt quá ngưỡng Tầng 1 $\rightarrow$ Kỳ vọng `muc_do: PHAN_VE`, `rule_id: R02`.
  * `TC-NORM-03 (Kịch bản R03):` Bệnh nhân thỏa mãn kịch bản `R03` (có xét nhánh loại trừ dị nguyên qua đường hít) $\rightarrow$ Kỳ vọng trả về `PHAN_VE` hoặc `SOC_PHAN_VE` tùy theo mức giảm huyết áp.
  * `TC-NORM-04 (Trường hợp THEO_DOI):` Bệnh nhân có triệu chứng nhưng không đủ điều kiện kích hoạt các kịch bản phản vệ $\rightarrow$ Kỳ vọng `muc_do: THEO_DOI`.

### 2.2. Boundary Cases (Ca ranh giới giá trị)
* **Mục tiêu:** Kiểm tra các giá trị nằm sát ngưỡng phân định theo đúng đặc tả kỹ thuật:
  * `TC-BOUND-01 (Ranh giới tuổi & mức giảm 30% HATT):` 
    * Kiểm thử các cặp biên tuổi $\pm 1$ quanh các mốc: `0.99 / 1`, `10.99 / 11`, `17.99 / 18`.
    * **Lưu ý quan trọng:** Tiêu chí giảm $>30\%$ so với HATT nền **chỉ áp dụng cho người $\ge 18$ tuổi**, tuyệt đối không áp dụng cho trẻ em. Test case phải kiểm chứng mức giảm đúng $30\%$ (chưa đạt Tầng 1) và mức giảm $>30\%$ (đạt Tầng 1).
  * `TC-BOUND-02 (Ranh giới số hệ cơ quan của R02):` 
    * Kiểm thử với số hệ cơ quan bị ảnh hưởng bằng đúng 2 và 1 để đảm bảo logic phân định ranh giới của `R02` hoạt động chính xác.

### 2.3. Invalid / Missing Cases (Xử lý ngoại lệ theo Issue #15)
* **Mục tiêu:** Kiểm chứng các ca thiếu dữ liệu hoặc sai định dạng tuân thủ tuyệt đối policy đã định nghĩa:
  * `TC-MISSING-01:` Trường hợp thiếu `tuoi` $\rightarrow$ Xử lý trả về `THEO_DOI` (không làm crash hệ thống).
  * `TC-MISSING-02:` Trường hợp thiếu giá trị huyết áp nhưng đã thỏa mãn một kịch bản Tầng 2 $\rightarrow$ Kết quả trả về `PHAN_VE`.
  * `TC-MISSING-03:` Trường hợp thiếu khóa boolean $\rightarrow$ Không được báo lỗi (exception), và không được tự động hạ mức khi dữ liệu hiện có đã đủ kết luận.

### 2.4. Các ca test mở rộng khác
* Kiểm tra kịch bản có nhiều rule cùng thỏa mãn đồng thời $\rightarrow$ Hệ thống phải tuân thủ nghiêm ngặt thứ tự ưu tiên: **`R01 > R02 > R03`** (theo issue #15).
* Kiểm chứng phân vùng `SOC_PHAN_VE` phân bổ đúng theo cả 4 nhóm tuổi.

---

## 3. Kiểm thử Phi chức năng & Bảo mật (Non-Functional & Security Tests)

* **TC-AUDIT-01 (Audit Trail Compliance):** 
  * *Nội dung:* Kiểm tra output bản ghi log của hệ thống sau mỗi lần chạy phân loại.
  * *Kỳ vọng:* Bản ghi log chỉ chứa đúng 4 trường `[Timestamp, User_UUID, Action_Type, Status]` và **tuyệt đối không chứa** triệu chứng thô hay dữ liệu nhận dạng cá nhân (PII)[cite: 2].
* **TC-PERF-01 (Latency Benchmark):**
  * *Nội dung:* Chạy thử nghiệm tự động 1.000 lần liên tục sau giai đoạn warm-up.
  * *Kỳ vọng:* Chỉ số độ trễ phân vị $p95 < 100\text{ ms}$ trên máy đo được nhóm khai báo[cite: 2].

---

## 4. Công cụ và Môi trường thực thi
* **Framework:** `pytest` (phiên bản $\ge 8.0$)[cite: 3].
* **Lệnh thực thi tối thiểu tại thư mục gốc của dự án:**
  ```bash
  python -m venv .venv
  pip install -r requirements.txt
  pytest -q