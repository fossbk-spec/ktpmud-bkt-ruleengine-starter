# GHI NHẬN QUYẾT ĐỊNH KIẾN TRÚC (ARCHITECTURE DECISION RECORDS - ADR)
**Dự án:** Track A — Dr May Day: Rule Engine Sprint  
**Mã nhóm:** [Nhóm 07]  
**Giai đoạn:** M1 — Understand (Checkpoint 1)  

---

## ADR-01: Lựa chọn mô hình biểu diễn bảng quyết định (Decision Table Pattern)

### 1. Ngữ cảnh (Context)
Track yêu cầu xây dựng một Rule Engine tất định dựa trên tài liệu đặc tả `docs/decision-table.md` bao gồm hai tầng phân loại khẩn cấp (Sốc phản vệ và Phản vệ)[cite: 2]. Hệ thống cần đảm bảo tính rõ ràng, dễ bảo trì, dễ viết unit test cho các trường hợp biên (boundary cases) và tuân thủ tuyệt đối quy tắc không tự ý thay đổi logic lâm sàng[cite: 2].

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
* Hàm `classify()` sẽ đóng vai trò là bộ máy duyệt qua các luật này theo đúng thứ tự ưu tiên của tầng 1 và tầng 2.

### 4. Hệ quả (Consequences)
* **Tích cực:** Mã nguồn mạch lạc, dễ dàng giải thích cho giảng viên/TA trong buổi vấn đáp (Viva) lý do tại sao code khớp với đặc tả[cite: 2]. Dễ dàng mở rộng test case cho các điều kiện biên.
* **Tiêu chuẩn:** Yêu cầu các thành viên phải tuân thủ nghiêm ngặt việc ánh xạ đúng tên trường từ Data Dictionary vào trong cấu trúc dữ liệu luật[cite: 2].

---

## ADR-02: Cơ chế cách ly Audit Log và bảo mật dữ liệu

### 1. Ngữ cảnh (Context)
Hệ thống xử lý các thông tin có tính chất y tế giả lập. Để tuân thủ các nguyên tắc về quyền riêng tư và an toàn thông tin cơ bản trong đề bài, tuyệt đối không được phép lưu trữ các dữ liệu nhạy cảm hoặc triệu chứng thô vào tệp log hệ thống[cite: 2].

### 2. Quyết định được chọn (Decision)
* Xây dựng một hàm bọc (Wrapper / Formatter) riêng biệt cho tầng Audit Trail.
* Trước khi ghi log, bộ lọc sẽ tự động cắt tỉa dữ liệu, chỉ giữ lại đúng 4 trường bắt buộc: `[Timestamp, User_UUID, Action_Type, Status]` và loại bỏ toàn bộ payload chứa thông tin triệu chứng hay định danh[cite: 2].

### 3. Hệ quả (Consequences)
* Đảm bảo đạt tuyệt đối tiêu chí an toàn dữ liệu của đề bài (A-06), tránh việc rò rỉ thông tin ngay cả trong môi trường giả lập[cite: 2].