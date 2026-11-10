# GHI NHẬN QUYẾT ĐỊNH KIẾN TRÚC (ARCHITECTURE DECISION RECORDS - ADR)
**Dự án:** Track A — Dr May Day: Rule Engine Sprint  
**Mã nhóm:** Nhóm 07  
**Giai đoạn:** M1 — Understand & M2 — Refinement  

---

## ADR-01: Lựa chọn mô hình biểu diễn bảng quyết định (Decision Table Pattern)

### 1. Ngữ cảnh (Context)
Track yêu cầu xây dựng một Rule Engine tất định dựa trên tài liệu đặc tả `docs/decision-table.md` bao gồm hai tầng phân loại khẩn cấp (Sốc phản vệ và Phản vệ). Hệ thống cần đảm bảo tính rõ ràng, dễ bảo trì, dễ viết unit test cho các trường hợp biên (boundary cases) và tuân thủ tuyệt đối quy tắc không tự ý thay đổi logic lâm sàng.

### 2. Các phương án cân nhắc (Options Considered)
* **Phương án A: Sử dụng chuỗi câu lệnh điều kiện `if-else` lồng nhau thủ công.**
  * *Ưu điểm:* Dễ cài đặt nhanh ban đầu ở quy mô nhỏ.
  * *Nhược điểm:* Khó bảo trì, dễ sót nhánh logic khi bảng quyết định mở rộng, mã nguồn dài và khó kiểm tra độ bao phủ (coverage).
* **Phương án B: Mô hình hóa Bảng quyết định thành cấu trúc dữ liệu ánh xạ (Decision Table Mapping / Rule Pattern Object).**
  * *Ưu điểm:* Tách biệt hoàn toàn phần định nghĩa luật (data/rules) khỏi phần mã thực thi logic (engine core). Giúp việc đối chiếu trực tiếp với `docs/decision-table.md` trở nên trực quan, dễ dàng viết test cho từng dòng điều kiện.
  * *Nhược điểm:* Tốn một ít thời gian thiết kế cấu trúc dữ liệu ban đầu.

### 3. Quyết định được chọn (Decision)
Nhóm thống nhất lựa chọn **Phương án B (Decision Table Mapping Pattern)**. 
* Tách biệt rõ ràng các quy tắc trong `docs/decision-table.md` thành một lớp hoặc cấu trúc bảng dữ liệu luật có cấu trúc.
* **Cơ chế duyệt và thứ tự ưu tiên:** Hàm `classify()` sẽ đóng vai trò là bộ máy duyệt qua các luật theo thứ tự ưu tiên nghiêm ngặt: **`R01 > R02 > R03`** (đảm bảo tuân thủ theo `issue #15`).
* **Cơ chế kết hợp Tầng 1 và Tầng 2:** Engine tiến hành đối chiếu kiểm tra kịch bản Tầng 2 trước (`R01`, `R02`, `R03`), sau đó mới kiểm tra đến các ngưỡng sụt giảm Huyết áp tâm thu (HATT) theo 4 nhóm tuổi (với người $\ge 18$ tuổi bao gồm tiêu chí giảm $>30\%$ so với HATT nền) để kích hoạt Tầng 1 (Sốc phản vệ).
* **Gắn kết quả:** Mỗi luật khi kích hoạt sẽ gắn mã định danh (`rule_id`) tương ứng và trích xuất chuỗi giải thích vào trường `ly_do` (khớp với Data Dictionary).

### 4. Hệ quả (Consequences)
* **Tích cực:** Mã nguồn mạch lạc, dễ dàng giải thích cho giảng viên/TA trong buổi vấn đáp (Viva) lý do tại sao code khớp với đặc tả. Dễ dàng mở rộng test case cho các điều kiện biên.
* **Tiêu chuẩn:** Yêu cầu các thành viên phải tuân thủ nghiêm ngặt việc ánh xạ đúng tên trường từ Data Dictionary vào trong cấu trúc dữ liệu luật.

---

## ADR-02: Cơ chế cách ly Audit Log và bảo mật dữ liệu

### 1. Ngữ cảnh (Context)
Hệ thống xử lý các thông tin có tính chất y tế giả lập. Để tuân thủ các nguyên tắc về quyền riêng tư và an toàn thông tin cơ bản trong đề bài, hệ thống không được phép lưu trữ các dữ liệu nhạy cảm hoặc triệu chứng thô vào tệp log hệ thống.

### 2. Quyết định được chọn (Decision)
* **Cơ chế kỹ thuật cụ thể:** Xây dựng một hàm bọc (Wrapper / Formatter) độc lập cho tầng Audit Trail.
* **Nguồn dữ liệu & Nơi lưu trữ:** Tham số `User_UUID` được truyền vào từ caller dưới dạng mã hóa giả định (pseudonymous ID) hoặc mã phiên. Bản ghi log được xuất ra dưới dạng cấu trúc JSON thông qua bộ ghi nhật ký chuẩn nội bộ, qua đó bộ lọc sẽ tự động cắt tỉa dữ liệu, chỉ giữ lại đúng 4 trường bắt buộc: `[Timestamp, User_UUID, Action_Type, Status]` và loại bỏ toàn bộ payload chứa thông tin triệu chứng hay định danh.
* **Minh chứng kiểm thử:** Xây dựng một unit test riêng biệt (`TC-AUDIT-01`) thực hiện chạy giả lập các request phân loại và kiểm tra tự động đầu ra của hàm log, qua đó xác thực cơ chế hoạt động đúng đắn mà không cần dùng đến các khẳng định cảm tính.

### 3. Hệ quả (Consequences)
* Đảm bảo đạt tiêu chuẩn an toàn dữ liệu khắt khe của đề bài (A-06), ngăn ngừa rò rỉ thông tin trong môi trường vận hành giả lập.