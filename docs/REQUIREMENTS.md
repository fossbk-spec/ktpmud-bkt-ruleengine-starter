# REQUIREMENTS - Track A (Dr May Day: Rule Engine Sprint)

## 1. Mục tiêu
Xây dựng một Rule Engine lõi (không bao gồm giao diện người dùng) bằng Python/pytest để phân loại mức độ phản vệ dựa trên tiêu chuẩn WAO/EAACI 2020. 
Kết quả trả về phải thuộc một trong 3 mức chẩn đoán: `SOC_PHAN_VE`, `PHAN_VE`, hoặc `THEO_DOI`.

## 2. Phạm vi dữ liệu (Scope of Data)
*   **Synthetic Data 100%:** Toàn bộ dữ liệu truyền vào hệ thống, bao gồm cả dữ liệu dùng để chạy Unit Test và Benchmark, đều là dữ liệu giả lập/hư cấu.
*   **Zero PII:** Tuân thủ tuyệt đối việc không sử dụng tên thật, CCCD, số điện thoại, địa chỉ, hoặc bất kỳ dữ liệu định danh bệnh nhân nào.
*   **Bảo mật Audit:** Hệ thống Audit Trail chỉ ghi nhận thông tin hệ thống dạng `[Timestamp, User_UUID, Action_Type, Status]`. Tuyệt đối không log dữ liệu lâm sàng thô hoặc điểm số sức khỏe.

## 3. Các tiêu chí nghiệm thu (Acceptance Criteria)
*   **A-01:** Hàm `classify()` thực thi đúng hợp đồng dữ liệu.
*   **A-02:** Không hard-code logic theo ID của các bài test có sẵn.
*   **A-03:** Bao phủ đầy đủ các kịch bản R-SOC, R01-PV, R02-PV, R03-PV và THEO_DOI theo `decision-table.md`.
*   **A-04:** Bắt lỗi và xử lý an toàn các trường hợp dữ liệu bị thiếu, sai kiểu, hoặc ngoài miền (trả về trạng thái THEO_DOI, không gây crash).
*   **A-05:** Cung cấp lý do (reason) giải thích quy tắc nào đã kích hoạt, không đưa ra lời khuyên điều trị.
*   **A-06:** Audit Trail xuất đúng 4 trường theo quy định.
*   **A-07 & A-08:** Có bộ Unit Test bao phủ 4 kịch bản (normal, boundary, invalid, missing) và lệnh `pytest -q` đạt 100%.
*   **A-09:** Tích hợp CI chạy test tự động khi mở Pull Request.
*   **A-10:** Thời gian thực thi p95 của 1.000 ca bệnh dưới 100ms.
*   **A-11:** Tuyên bố rõ "educational/synthetic — not for clinical use" trong README.

## 4. Ngoài phạm vi (Out of Scope)
*   Không xây dựng giao diện ứng dụng (Frontend/UI).
*   Không đưa ra bất kỳ chẩn đoán, cảnh báo hay khuyến nghị điều trị y khoa nào.
*   Không áp dụng Machine Learning / Deep Learning, chỉ dùng thuật toán Rule-based nội suy.
*   Không tự ý thay đổi ngưỡng huyết áp, triệu chứng ngoài bảng `decision-table.md`.
*   Không tương tác với cơ sở dữ liệu thật của bệnh viện.