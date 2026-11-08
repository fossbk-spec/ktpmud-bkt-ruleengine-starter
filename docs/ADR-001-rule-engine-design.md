# ADR 001: Lựa chọn cấu trúc thuật toán cho Rule Engine

*   **Trạng thái:** Đề xuất
*   **Ngày:** 08/11/2026
*   **Tác giả:** Nhóm 49

## Ngữ cảnh
Track A yêu cầu xây dựng một Rule Engine xử lý các dữ liệu y khoa đầu vào (theo chuẩn WAO/EAACI 2020) để phân loại thành các mức Sốc phản vệ, Phản vệ, hoặc Theo dõi. Hệ thống phải đảm bảo hiệu năng tính toán cực cao (p95 < 100ms) trên 1.000 ca bệnh mô phỏng và có khả năng lưu Audit log an toàn không chứa PII.

## Các phương án đã xem xét
1.  Sử dụng các thư viện Rule Engine chuyên dụng bên thứ ba (như `business-rules` hoặc `rule-engine`).
2.  Viết thuật toán rẽ nhánh mã cứng trực tiếp (Hard-coded Decision Tree) bằng cấu trúc `if/elif/else` thuần túy của Python.

## Quyết định
Nhóm 49 quyết định sử dụng **Phương án 2: Viết thuật toán rẽ nhánh mã cứng trực tiếp (Code Python)**. Dữ liệu sẽ được ánh xạ qua cấu trúc `TypedDict` và xử lý thông qua cây logic tuần tự.

## Lý do 
1.  **Hiệu năng tuyệt đối:** Bài toán Tầng 1 và Tầng 2 trong `decision-table.md` tương đối hữu hạn và tuyến tính. Việc chạy mã Python thuần không qua bất kỳ thư viện trung gian nào giúp tối ưu tốc độ thực thi, đảm bảo dư sức đáp ứng chuẩn p95 < 100ms.
2.  **Dễ dàng kiểm soát luồng Audit:** Việc đặt các điểm chốt lưu vết (`_ghi_audit()`) vào từng nhánh `if/else` giúp nhóm kiểm soát chính xác vị trí phát sinh log, đồng thời ngăn chặn tuyệt đối nguy cơ các thư viện bên thứ ba tự động log ra dữ liệu lâm sàng thô vi phạm chuẩn Zero PII.
3.  **Khả năng bảo trì:** Vì cấu trúc bảng quyết định được giới hạn cố định trong V1 của kỳ thi, việc dùng `if/elif` trực tiếp giúp mã nguồn có độ tương đồng 1-1 với tài liệu đặc tả, thuận lợi cho TA trong quá trình chấm điểm.