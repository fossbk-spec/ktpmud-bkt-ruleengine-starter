# TEST PLAN - Kiểm thử Rule Engine WAO/EAACI

## 1. Công cụ và Môi trường
*   **Framework:** `pytest`
*   **Vị trí lưu trữ:** Các bài kiểm thử nghiệp vụ được lưu tại thư mục `tests/`.
*   **Lệnh thực thi:** `pytest -q`

## 2. Kế hoạch Unit Test (Độ bao phủ nghiệp vụ)
Hệ thống sử dụng các bộ từ điển dữ liệu giả lập (mock `PatientInput`) để đánh giá 4 kịch bản kiểm thử cốt lõi:

*   **Kịch bản Invalid/Missing:**
    *   Truyền một dictionary rỗng hoặc giá trị `None`.
    *   Truyền biến `tuoi` với giá trị âm hoặc sai kiểu dữ liệu (string).
    *   *Kỳ vọng:* Hệ thống ghi nhận lỗi đầu vào và trả kết quả `"muc_do": "THEO_DOI"`.
*   **Kịch bản Normal:**
    *   Cung cấp dữ liệu lâm sàng giả định khớp chính xác với điều kiện R01-PV (không rõ dị nguyên, có tổn thương da và hô hấp).
    *   Cung cấp dữ liệu giả định khớp với R02-PV (tiếp xúc dị nguyên, có >= 2/4 cơ quan đích).
    *   *Kỳ vọng:* Trả kết quả `"muc_do": "PHAN_VE"` kèm `rule_id` tương ứng.
*   **Kịch bản Boundary:**
    *   Kiểm tra một ca bệnh nhân đúng 11 tuổi có huyết áp tâm thu 89 mmHg (sát mốc ngưỡng < 90).
    *   *Kỳ vọng:* Hệ thống nội suy thành tụt huyết áp và trả kết quả `"muc_do": "SOC_PHAN_VE"`.

## 3. Kế hoạch Benchmark (Đo lường hiệu năng)
*   **Công cụ:** Sử dụng thư viện `time` (`time.perf_counter`) của Python.
*   **Quy trình:**
    1.  Warm-up: Khởi chạy hàm `classify()` 10 lần với dữ liệu giả lập để làm nóng môi trường thực thi.
    2.  Đo kiểm: Chạy vòng lặp 1.000 lần liên tiếp với cùng bộ dữ liệu, ghi nhận thời gian thực thi (latency) của từng vòng tính bằng milliseconds (ms).
    3.  Tính toán: Sắp xếp kết quả và trích xuất chỉ số tại bách phân vị 50 (p50) và 95 (p95).
*   **Tiêu chuẩn chốt:** Chỉ số p95 bắt buộc phải < 100ms.