# BẢN GHI QUYẾT ĐỊNH KIẾN TRÚC (ARCHITECTURAL DECISION RECORDS - ADR)
> **Dự án:** Track A — Dr May Day: Rule Engine Sprint  
> **Mã đề:** KTPMUD-BKT-2026-PILOT  
> **Mã nhóm:** Nhóm 18 + 19  
> **Thành viên:** 202414288, 202414324, 202414276, 202414384  
> **Mốc hoàn thành:** Checkpoint 1 (M1 — Understand)  

---

## ADR-01: Kiến trúc phân tầng đánh giá quy tắc (Layered Rule Evaluation Architecture)

### 1. Bối cảnh (Context)
Hệ thống cần phân loại nguy cơ lâm sàng dựa trên hướng dẫn WAO/EAACI được đặc tả tại tài liệu chính thức `docs/decision-table.md`. Theo đặc tả:
- Sốc phản vệ (Tầng 1 - `R-SOC`) là trường hợp tối khẩn cấp, nhưng có **điều kiện tiên quyết**: bệnh nhân phải đạt tiêu chí Phản vệ ở Tầng 2 (bất kỳ 1 trong 3 kịch bản R01, R02, R03) **VÀ** có tụt huyết áp tâm thu theo độ tuổi.
- Nếu không thỏa mãn Tầng 2, bệnh nhân không thể bị xếp vào Sốc phản vệ.
- Nếu không khớp cả Tầng 1 và Tầng 2, kết quả là `THEO_DOI` (`rule_id = null`).

Cần lựa chọn mô hình điều khiển logic để thực hiện việc phân loại chính xác, tránh lặp mã và đạt độ trễ cực thấp ($p95 < 100\text{ ms}$).

### 2. Các phương án cân nhắc (Options Considered)
- **Phương án A (Flat If-Else):** Viết gộp toàn bộ điều kiện Tầng 1 và Tầng 2 vào các khối `if-elif` phẳng.
  * *Nhược điểm:* Dẫn đến việc lặp lại logic kiểm tra R01, R02, R03 nhiều lần; khó bảo trì và dễ sai sót logic.
- **Phương án B (Layered Evaluation Pipeline - Phương án được chọn):** Tách quá trình đánh giá thành các tầng tuần tự:
  1. *Validation Layer:* Kiểm tra kiểu dữ liệu và các trường bắt buộc (ví dụ: `tuoi`).
  2. *Anaphylaxis Layer (Tầng 2):* Đánh giá xem có thỏa mãn các kịch bản R01, R02, R03 hay không.
  3. *Shock Evaluation Layer (Tầng 1):* Nếu Tầng 2 thỏa mãn, kiểm tra tiếp tiêu chí tụt huyết áp. Nếu không tụt huyết áp, giữ nguyên kết quả Tầng 2.

### 3. Quyết định (Decision)
Nhóm quyết định áp dụng **Phương án B (Layered Evaluation Pipeline)**.
- Xây dựng các hàm thuần túy (pure functions):
  - `_kiem_tra_phan_ve(patient: PatientInput) -> Optional[Tuple[str, str]]`
  - `_kiem_tra_tut_huyet_ap(tuoi, hatt, hatt_nen) -> bool`
- Hàm chính `classify()` sẽ đóng vai trò điều phối các tầng và trả về kết quả theo chuẩn contract.

### 4. Hệ quả & Đánh đổi (Consequences & Rationale)
- **Ưu điểm:**
  - Logic thể hiện đúng 100% bản chất y khoa của đặc tả WAO/EAACI.
  - Mã nguồn sạch, dễ đọc, từng hàm nhỏ có thể viết unit test độc lập.
  - Độ phức tạp thuật toán là $O(1)$, thực thi trong khoảng $< 0.1\text{ ms}$, đảm bảo vượt xa yêu cầu benchmark $p95 < 100\text{ ms}$.
- **Đánh đổi:** Cần tổ chức mã nguồn thành các hàm module nhỏ, nhưng giúp đạt tính bảo trì (maintainability) tối đa.
