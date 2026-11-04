# YÊU CẦU HỆ THỐNG & TIÊU CHÍ NGHIỆM THU (REQUIREMENTS & ACCEPTANCE CRITERIA)
**Dự án:** Track A — Dr May Day: Rule Engine Sprint  
**Mã nhóm:** [Điền mã nhóm của bạn]  
**Giai đoạn:** M1 — Understand (Checkpoint 1)  

---

## 1. Tổng quan hệ thống (System Overview)
Hệ thống **Dr May Day Rule Engine** là một thành phần backend dạng tất định (deterministic) có trách nhiệm tiếp nhận dữ liệu đầu vào mô phỏng (synthetic data) về triệu chứng lâm sàng, dấu hiệu sinh tồn và tiền sử của người bệnh, sau đó đối chiếu với bảng quyết định (Decision Table) chuẩn hóa để phân loại mức độ khẩn cấp y tế (Tầng 1: Sốc phản vệ và Tầng 2: Phản vệ)[cite: 2].

---

## 2. Yêu cầu chức năng (Functional Requirements)

* **FR-01: Thực thi Contract Phân loại (Classification Contract)**
  * Hệ thống phải cài đặt hoàn chỉnh hàm `classify()` trong module `rule_engine/classifier.py`, thay thế hoàn toàn ngoại lệ `NotImplementedError` có sẵn trong starter code[cite: 2].
  * Dữ liệu đầu vào phải tuân thủ nghiêm ngặt cấu trúc Từ điển dữ liệu (`Data Dictionary`) định nghĩa tại `docs/decision-table.md`[cite: 2].

* **FR-02: Phân loại chuẩn xác theo Ma trận Quyết định (Decision Logic)**
  * **Tầng 1 (Sốc phản vệ - Anaphylactic Shock):** Nhận diện chính xác các trường hợp đe dọa tính mạng dựa trên các tiêu chí huyết áp, hô hấp và tuần hoàn quy định trong contract.
  * **Tầng 2 (Phản vệ - Anaphylaxis):** Phân loại các trường hợp phản ứng dị ứng toàn thân đa cơ quan đạt ngưỡng kích hoạt.
  * *Ràng buộc cốt lõi:* Tuyệt đối **không tự ý suy diễn, thêm bớt hoặc thay đổi quy tắc lâm sàng** ngoài tài liệu `docs/decision-table.md`[cite: 2].

* **FR-03: Cơ chế Giải thích (Explainability / Reason)**
  * Kết quả trả về phải đính kèm trường giải thích (`reason`) nêu rõ quy tắc/điều kiện nào trong bảng quyết định đã kích hoạt kết quả phân loại đó.
  * Tuyệt đối không đưa ra các chẩn đoán tự do hoặc lời khuyên điều trị vượt quá chức năng của một công cụ rule engine hỗ trợ sàng lọc[cite: 2].

* **FR-04: Hệ thống Ghi nhật ký Kiểm toán (Audit Trail)**
  * Mỗi lần chạy phân loại phải sinh ra bản ghi audit log với cấu trúc tối thiểu bắt buộc:
    ```json
    [Timestamp, User_UUID, Action_Type, Status]
    ```
  * *Ràng buộc bảo mật:* **Không được phép** ghi nhận các thông tin định danh cá nhân (PII), triệu chứng thô (raw clinical input) hay điểm số sức khỏe vào audit log[cite: 2].

---

## 3. Yêu cầu phi chức năng (Non-Functional Requirements)

* **NFR-01: Hiệu năng và Độ trễ (Performance & Latency)**
  * Sau khi khởi động và chạy warm-up, hệ thống phải thực hiện tối thiểu 1.000 lần phân loại liên tục.
  * Chỉ số độ trễ phân vị $p95$ phải đạt dưới $100\text{ ms}$ trên môi trường đo kiểm được nhóm khai báo[cite: 2].

* **NFR-02: Tính Khởi chạy & Tự động hóa (Reproducibility & CI)**
  * Dự án phải thiết lập môi trường và chạy thành công từ một thư mục sạch (clean checkout) thông qua lệnh tối thiểu:
    ```bash
    python -m venv .venv
    pip install -r requirements.txt
    pytest -q
    ```
  * Mọi thay đổi mã nguồn qua Pull Request phải được kiểm thử tự động thông qua GitHub Actions CI[cite: 2].

* **NFR-03: Tuyên bố Miễn trừ Trách nhiệm (Educational Disclaimer)**
  * Tài liệu `README.md` bắt buộc phải hiển thị rõ thông báo: *"Educational/Synthetic — Not for clinical use"*[cite: 2].

---

## 4. Chính sách xử lý ngoại lệ (Edge Cases Policy)
* **Missing Input (Thiếu dữ liệu):** Trả về mã lỗi/trạng thái validation hợp lệ thay vì làm sập (crash) chương trình.
* **Invalid Type (Sai kiểu dữ liệu):** Từ chối các tham số không đúng định dạng kiểu dữ liệu trong Data Dictionary.
* **Out-of-range (Giá trị ngoài miền):** Bắt ngoại lệ đối với các chỉ số sinh tồn vượt ngưỡng vật lý hợp lý.

---

## 5. Bảng ma trận Tiêu chí Nghiệm thu (Acceptance Criteria Matrix)

| ID | Tiêu chí nghiệm thu (Acceptance Criteria) | Phương pháp kiểm chứng | Trạng thái |
| :--- | :--- | :--- | :--- |
| **A-01** | `classify()` thực thi đúng contract; không còn `NotImplementedError`[cite: 2]. | Unit Test kiểm tra sự tồn tại và kiểu trả về của hàm. | Đã hoàn thành M1 |
| **A-02** | Không hard-code kết quả theo ID của public fixture[cite: 2]. | Code Review & Test với dữ liệu sinh ra mới. | Đã hoàn thành M1 |
| **A-03** | Bao phủ đủ các mức phân loại theo `docs/decision-table.md` (Tầng 1 & 2)[cite: 2]. | Chạy bộ test case đầy đủ cho các nhánh logic. | Đã hoàn thành M1 |
| **A-04** | Xử lý input thiếu, sai kiểu, ngoài miền theo policy đã công bố[cite: 2]. | Viết Negative Test cases tương ứng. | Đã lên kế hoạch |
| **A-05** | Trả `reason` truy vết được rule kích hoạt, không kèm lời khuyên điều trị[cite: 2]. | Kiểm tra schema kết quả trả về của hàm. | Đã lên kế hoạch |
| **A-06** | Ghi audit đúng 4 trường, không log raw clinical input hay PII[cite: 2]. | Kiểm tra nội dung audit log sinh ra qua test. | Đã lên kế hoạch |
| **A-07** | Có unit tests cho normal, boundary, invalid và missing cases[cite: 2]. | Chạy lệnh `pytest -q` kiểm tra độ bao phủ. | Đã lên kế hoạch |
| **A-08** | Lệnh `pytest -q` đạt từ clean checkout[cite: 2]. | Thực thi trên môi trường ảo sạch. | Đã lên kế hoạch |
| **A-09** | CI chạy test trên mỗi Pull Request[cite: 2]. | Kiểm tra tab Actions trên GitHub repository. | Đã lên kế hoạch |
| **A-10** | Benchmark tối thiểu 1.000 lần chạy sau warm-up; $p95 < 100\text{ ms}$[cite: 2]. | Chạy script benchmark và ghi vào `TEST_REPORT.md`. | Đã lên kế hoạch |
| **A-11** | `README.md` ghi rõ thông báo *"educational/synthetic — not for clinical use"*[cite: 2]. | Kiểm tra trực quan file `README.md`. | Đã lên kế hoạch |