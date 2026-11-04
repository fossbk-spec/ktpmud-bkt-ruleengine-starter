# KẾ HOẠCH KIỂM THỬ (TEST PLAN) — TRACK A: RULE ENGINE
**Dự án:** Track A — Dr May Day: Rule Engine Sprint  
**Mã nhóm:** [Nhóm 07]  
**Giai đoạn:** M1 — Understand (Checkpoint 1)  

---

## 1. Mục tiêu kiểm thử (Testing Objectives)
* **Đảm bảo tính chính xác tất định (Deterministic Accuracy):** Kiểm chứng toàn bộ logic phân loại dựa trên bảng quyết định (`docs/decision-table.md`) từ Tầng 1 (Sốc phản vệ) đến Tầng 2 (Phản vệ).
* **Độ bao phủ toàn diện (Coverage):** Xây dựng bộ test phủ kín các kịch bản chuẩn (Normal), ranh giới (Boundary), dữ liệu lỗi/không hợp lệ (Invalid) và thiếu dữ liệu (Missing)[cite: 2].
* **Tuân thủ an toàn & Kiểm toán (Audit & Safety Compliance):** Xác thực định dạng audit log (`[Timestamp, User_UUID, Action_Type, Status]`) và cam kết tuyệt đối không để lộ thông tin nhạy cảm hoặc triệu chứng thô[cite: 2].

---

## 2. Chiến lược thiết kế Test Cases

### 2.1. Normal Cases (Ca đúng chuẩn)
* **Mục tiêu:** Kiểm tra các trường hợp dữ liệu đầu vào thỏa mãn hoàn toàn các điều kiện quy định rõ ràng trong ma trận quyết định của `docs/decision-table.md`[cite: 2].
* **Kịch bản mẫu:**
  * *TC-NORM-01:* Bệnh nhân có dấu hiệu tụt huyết áp nghiêm trọng kèm theo suy hô hấp cấp độ nặng $\rightarrow$ Kỳ vọng phân loại đúng **Tầng 1 (Sốc phản vệ)** kèm theo trường `reason` chỉ rõ quy tắc kích hoạt.
  * *TC-NORM-02:* Bệnh nhân phản ứng dị ứng toàn thân đa cơ quan đạt ngưỡng kích hoạt nhưng chưa đến mức sốc $\rightarrow$ Kỳ vọng phân loại đúng **Tầng 2 (Phản vệ)**.

### 2.2. Boundary Cases (Ca ranh giới giá trị)
* **Mục tiêu:** Kiểm tra các giá trị nằm sát ngưỡng phân định (ví dụ: ranh giới huyết áp tâm thu theo độ tuổi, giới hạn số lần nôn/đau bụng) để đảm bảo hệ thống không bị sai lệch ở biên[cite: 2].
* **Kịch bản mẫu:**
  * *TC-BOUND-01:* Huyết áp tâm thu nằm ngay tại giá trị mốc ranh giới quy định trong bảng quyết định (ví dụ: mốc áp dụng giảm 30% đối với trẻ em hoặc người lớn).
  * *TC-BOUND-02:* Tần suất triệu chứng (như nôn $\ge 2$ lần) kiểm tra với đúng 2 lần và 1 lần để xem hàm phân loại xử lý ranh giới thế nào[cite: 2].

### 2.3. Invalid / Missing Cases (Ca dữ liệu lỗi hoặc thiếu)
* **Mục tiêu:** Đảm bảo hệ thống có cơ chế bắt lỗi an toàn (Robustness) thay vì bị crash khi gặp đầu vào bất thường[cite: 2].
* **Kịch bản mẫu:**
  * *TC-MISSING-01:* Thiếu các trường dữ liệu bắt buộc trong Data Dictionary (ví dụ: thiếu thông tin huyết áp hoặc thiếu trường triệu chứng sinh tồn) $\rightarrow$ Kỳ vọng hệ thống trả về mã lỗi validation/ngoại lệ hợp lệ.
  * *TC-INVALID-02:* Dữ liệu truyền vào sai kiểu (ví dụ: truyền chuỗi text vào trường tuổi hoặc giá trị âm cho huyết áp) $\rightarrow$ Kỳ vọng hệ thống từ chối xử lý hoặc báo lỗi dữ liệu.

---

## 3. Kiểm thử Phi chức năng & Bảo mật (Non-Functional & Security Tests)

* **TC-AUDIT-01 (Audit Trail Compliance):** 
  * *Nội dung:* Kiểm tra output của hệ thống sau mỗi lần chạy phân loại.
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