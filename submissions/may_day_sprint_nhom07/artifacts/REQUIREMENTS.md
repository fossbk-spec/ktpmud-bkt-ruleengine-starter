# YÊU CẦU HỆ THỐNG & TIÊU CHÍ NGHIỆM THU (REQUIREMENTS & ACCEPTANCE CRITERIA)
**Dự án:** Track A — Dr May Day: Rule Engine Sprint  
**Mã nhóm:** Nhóm 07  
**Giai đoạn:** M1 — Understand & M2 — Refinement  

---

## 1. Tổng quan hệ thống (System Overview)
Hệ thống **Dr May Day Rule Engine** là một thành phần backend dạng tất định (deterministic) có trách nhiệm tiếp nhận dữ liệu đầu vào mô phỏng (synthetic data) về triệu chứng lâm sàng, dấu hiệu sinh tồn và tiền sử của người bệnh, sau đó đối chiếu với bảng quyết định (Decision Table) chuẩn hóa để phân loại mức độ khẩn cấp y tế (Tầng 1: Sốc phản vệ và Tầng 2: Phản vệ).

---

## 2. Yêu cầu chức năng (Functional Requirements)

* **FR-01: Thực thi Contract Phân loại (Classification Contract)**
  * Hệ thống phải cài đặt hoàn chỉnh hàm `classify()` trong module `rule_engine/classifier.py`, thay thế hoàn toàn ngoại lệ `NotImplementedError` có sẵn trong starter code.
  * Dữ liệu đầu vào phải tuân thủ nghiêm ngặt cấu trúc Từ điển dữ liệu (`Data Dictionary`) định nghĩa tại `docs/decision-table.md`.

* **FR-02: Phân loại chuẩn xác theo Ma trận Quyết định (Decision Logic)**
  * **Tầng 1 (Sốc phản vệ - Anaphylactic Shock):** Được xác định khi đạt một trong ba kịch bản Tầng 2 (`R01`, `R02`, `R03`) VÀ bị tụt Huyết áp tâm thu (HATT) theo đúng ngưỡng phân chia theo 4 nhóm tuổi (trong đó đối với người từ $\ge$ 18 tuổi, tiêu chí này bao gồm cả tiêu chí giảm $> 30\%$ so với HATT nền của bệnh nhân).
  * **Cụ thể các kịch bản Tầng 1 / Tầng 2 & Thứ tự ưu tiên:** 
    * Các kịch bản rule hợp lệ: `R01`, `R02`, `R03`.
    * Thứ tự ưu tiên khi có nhiều rule cùng thỏa mãn: **`R01 > R02 > R03`** (theo thông tin issue #15).
    * Giá trị `muc_do` trả về hợp lệ: `SOC_PHAN_VE`, `PHAN_VE`, `THEO_DOI`, `BINH_THUONG` (tùy theo kết quả khớp bảng quyết định và ngưỡng huyết áp).
  * **Tầng 2 (Phản vệ - Anaphylaxis):** Phân loại các trường hợp phản ứng dị ứng toàn thân đa cơ quan đạt ngưỡng kích hoạt theo đặc tả chuẩn.
  * *Ràng buộc cốt lõi:* Tuyệt đối **không tự ý suy diễn, thêm bớt hoặc thay đổi quy tắc lâm sàng** ngoài tài liệu `docs/decision-table.md`.

* **FR-03: Cơ chế Giải thích (Explainability / Reason)**
  * Kết quả trả về phải đính kèm trường giải thích (`ly_do`) nêu rõ quy tắc/điều kiện nào trong bảng quyết định đã kích hoạt kết quả phân loại đó (lưu ý: trường này sử dụng tên `ly_do` khớp với Data Dictionary).
  * Tuyệt đối không đưa ra các chẩn đoán tự do hoặc lời khuyên điều trị vượt quá chức năng của một công cụ rule engine hỗ trợ sàng lọc.

* **FR-04: Hệ thống Ghi nhật ký Kiểm toán (Audit Trail)**
  * Mỗi lần chạy phân loại phải sinh ra bản ghi audit log với cấu trúc tối thiểu bắt buộc:
    ```json
    [Timestamp, User_UUID, Action_Type, Status]
    ```
  * *Ràng buộc bảo mật:* **Không được phép** ghi nhận các thông tin định danh cá nhân (PII), triệu chứng thô (raw clinical input) hay điểm số sức khỏe vào audit log.

---

## 3. Yêu cầu phi chức năng (Non-Functional Requirements)

* **NFR-01: Hiệu năng và Độ trễ (Performance & Latency)**
  * Sau khi khởi động và chạy warm-up, hệ thống phải thực hiện tối thiểu 1.000 lần phân loại liên tục.
  * Chỉ số độ trễ phân vị $p95$ phải đạt dưới $100\text{ ms}$ trên môi trường đo kiểm được nhóm khai báo.

* **NFR-02: Tính Khởi chạy & Tự động hóa (Reproducibility & CI)**
  * Dự án phải thiết lập môi trường và chạy thành công từ một thư mục sạch (clean checkout) thông qua lệnh tối thiểu:
    ```bash
    python -m venv .venv
    pip install -r requirements.txt
    pytest -q
    ```
  * Mọi thay đổi mã nguồn qua Pull Request phải được kiểm thử tự động thông qua GitHub Actions CI.

* **NFR-03: Tuyên bố Miễn trừ Trách nhiệm (Educational Disclaimer)**
  * Tài liệu `README.md` bắt buộc phải hiển thị rõ thông báo: *"Educational/Synthetic — Not for clinical use"*.

---

## 4. Chính sách xử lý ngoại lệ (Edge Cases Policy)
Dưới đây là bảng policy xử lý chi tiết theo từng trường dữ liệu đầu vào (cập nhật theo yêu cầu issue #15):

| Trường dữ liệu | Thiếu khóa (Missing key) | Giá trị Null | Sai kiểu (Invalid type) | Ngoài miền (Out-of-range) | Kết quả xử lý | Lý do / Ghi chú |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **tuoi** | Mặc định hoặc xử lý an toàn | Báo lỗi / Từ chối | Từ chối | Ngoài khoảng sinh lý | `THEO_DOI` / Lỗi validation | Thiếu tuổi quy về theo dõi hoặc không đủ cơ sở kết luận |
| **huyết áp (HATT)** | Không bắt buộc nếu đã đủ kịch bản Tầng 2 | Bỏ qua kiểm tra Tầng 1 | Từ chối | Ngoài khoảng sinh lý | Xử lý theo rule Tầng 2 | Thiếu huyết áp nhưng đã thỏa kịch bản Tầng 2 $\rightarrow$ trả về `PHAN_VE` |
| **Các khóa boolean** | Không được gây sập (crash) | Xem như False/Mặc định | Từ chối | Không áp dụng | Giữ nguyên logic | Không được lỗi, không tự hạ mức khi dữ liệu hiện có đã đủ kết luận |

---

## 5. Bảng ma trận Tiêu chí Nghiệm thu (Acceptance Criteria Matrix)

| ID | Tiêu chí nghiệm thu (Acceptance Criteria) | Phương pháp kiểm chứng | Trạng thái |
| :--- | :--- | :--- | :--- |
| **A-01** | `classify()` thực thi đúng contract; không còn `NotImplementedError`. | Unit Test kiểm tra sự tồn tại và kiểu trả về của hàm. | **Đã lên kế hoạch** |
| **A-02** | Không hard-code kết quả theo ID của public fixture. | Code Review & Test với dữ liệu sinh ra mới. | **Đã lên kế hoạch** |
| **A-03** | Bao phủ đủ các mức phân loại theo `docs/decision-table.md` (Tầng 1 & 2). | Chạy bộ test case đầy đủ cho các nhánh logic. | **Đã lên kế hoạch** |
| **A-04** | Xử lý input thiếu, sai kiểu, ngoài miền theo policy bảng trên. | Viết Negative Test cases tương ứng. | Đã lên kế hoạch |
| **A-05** | Trả trường `ly_do` (ánh xạ từ yêu cầu reason) truy vết được rule kích hoạt, không kèm lời khuyên điều trị. | Kiểm tra schema kết quả trả về của hàm. | Đã lên kế hoạch |
| **A-06** | Ghi audit đúng 4 trường, không log raw clinical input hay PII. | Kiểm tra nội dung audit log sinh ra qua test. | Đã lên kế hoạch |
| **A-07** | Có unit tests cho normal, boundary, invalid và missing cases. | Chạy lệnh `pytest -q` kiểm tra độ bao phủ. | Đã lên kế hoạch |
| **A-08** | Lệnh `pytest -q` đạt từ clean checkout. | Thực thi trên môi trường ảo sạch. | Đã lên kế hoạch |
| **A-09** | CI chạy test trên mỗi Pull Request. | Kiểm tra tab Actions trên GitHub repository. | Đã lên kế hoạch |
| **A-10** | Benchmark tối thiểu 1.000 lần chạy sau warm-up; $p95 < 100\text{ ms}$. | Chạy script benchmark và ghi vào `TEST_REPORT.md`. | Đã lên kế hoạch |
| **A-11** | `README.md` ghi rõ thông báo *"educational/synthetic — not for clinical use"*. | Kiểm tra trực quan file `README.md`. | Đã lên kế hoạch |