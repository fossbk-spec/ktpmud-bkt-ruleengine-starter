# BẢN GHI QUYẾT ĐỊNH KIẾN TRÚC (ARCHITECTURAL DECISION RECORDS - ADR)

- **Dự án:** Track A — Dr May Day: Rule Engine Sprint
- **Mã đề:** KTPMUD-BKT-2026-PILOT
- **Mã nhóm:** Nhóm 18 + 19
- **Thành viên:** 202414288, 202414324, 202414276, 202414384
- **Căn cứ kỹ thuật (SSoT):** `docs/decision-table.md` và quy định làm rõ tại [Issue #15 ktpmud-project](https://github.com/fossbk-spec/ktpmud-project/issues/15)

---

## ADR-01: Lựa chọn mô hình thiết kế Rule Engine đánh giá phân tầng

### 1. Ngữ cảnh (Context)
Đặc tả kỹ thuật tại `docs/decision-table.md` yêu cầu xây dựng một thành phần Rule Engine tất định (deterministic), thực hiện phân loại tình trạng bệnh nhân dựa trên dữ liệu đầu vào JSON. Ràng buộc của đề bài:
1. **Phân tầng logic:** Sốc phản vệ (Tầng 1 - `R-SOC`) có điều kiện tiên quyết là phải thỏa mãn tối thiểu một kịch bản Phản vệ ở Tầng 2 (`R01-PV`, `R02-PV`, `R03-PV`) và kèm theo tiêu chuẩn tụt huyết áp theo tuổi.
2. **Thứ tự ưu tiên rule:** Khi dữ liệu cùng thỏa mãn nhiều rule Tầng 2 (ví dụ đồng thời thỏa R02 và R03), hệ thống phải giải quyết xung đột bằng cách gán duy nhất một mã `rule_id` theo thứ tự ưu tiên đã chốt tại [Issue #15](https://github.com/fossbk-spec/ktpmud-project/issues/15): `R01-PV > R02-PV > R03-PV`.
3. **Hiệu năng:** Độ trễ thực thi phải đạt chỉ số p95 < 100 ms khi benchmark 1.000 lần liên tục.

Cần lựa chọn mô hình kiến trúc để biểu diễn và thực thi các quy tắc này trong module `rule_engine/classifier.py`.

### 2. Các phương án cân nhắc (Options Considered)

#### Phương án 1: Mô hình Rule Engine hướng dữ liệu (Table-driven / Rule Data Structure)
- **Mô tả:** Biểu diễn mỗi rule nghiệp vụ thành một bản ghi dữ liệu có cấu trúc gồm các trường:
  ```python
  {
      "rule_id": "R01-PV",
      "priority": 1,
      "predicate": Callable[[PatientInput], bool],
      "ly_do": str
  }
  ```
  Một vòng lặp duyệt qua danh sách các rule đã sắp xếp theo thứ tự `priority` để tìm rule đầu tiên khớp điều kiện (`predicate(input) == True`).
- **Ưu điểm:**
  - Tách biệt rõ ràng giữa tập luật (data) và bộ máy thực thi (engine execution).
  - Dễ dàng mở rộng, thêm rule mới hoặc thay đổi thứ tự ưu tiên mà không cần can thiệp vào luồng điều khiển chung.
  - Phù hợp với các hệ thống rule phức tạp có số lượng rule lớn.
- **Nhược điểm:**
  - Phát sinh chi phí trừu tượng hóa (overhead) khi khởi tạo đối tượng hàm/predicate.
  - Xử lý quan hệ phụ thuộc phân tầng giữa Tầng 1 và Tầng 2 (Tầng 1 yêu cầu kết quả của Tầng 2) đòi hỏi cơ chế chaining hoặc hai lượt duyệt dữ liệu, làm tăng độ phức tạp của code với bài toán quy mô cố định (4 rule).

#### Phương án 2: Mô hình phân tầng luồng điều khiển hàm thuần (Layered Functional Pipeline)
- **Mô tả:** Tổ chức mã nguồn thành các hàm kiểm tra độc lập (pure functions) theo đúng cấu trúc 2 tầng của contract:
  - Hàm thẩm định dữ liệu đầu vào (`_validate_input`).
  - Hàm đánh giá phản vệ Tầng 2 (`_eval_tier2`), duyệt tuần tự theo thứ tự ưu tiên `R01 -> R02 -> R03`.
  - Hàm kiểm tra ngưỡng tụt huyết áp Tầng 1 (`_eval_hypotension`).
- **Ưu điểm:**
  - Khớp trực tiếp với cấu trúc contract trong `docs/decision-table.md`: Tầng 1 phụ thuộc trực tiếp vào kết quả Tầng 2.
  - Không có chi phí overhead; độ phức tạp thuật toán là $O(1)$, thời gian thực thi ở mức microsecond, tối ưu cho yêu cầu đo benchmark.
  - Dễ dàng kiểm thử đơn vị độc lập cho từng hàm phụ trợ.
- **Nhược điểm:**
  - Khả năng mở rộng động kém hơn phương án 1 nếu số lượng rule tăng lên hàng chục hoặc hàng trăm rule trong tương lai.

### 3. Quyết định (Decision)
Nhóm lựa chọn **kết hợp ưu điểm của Phương án 1 và Phương án 2: Mô hình Danh sách Rule có cấu trúc trong từng Tầng (Tiered Rule Registry)**:
- Tầng 2 được biểu diễn bằng một tuple các bản ghi rule cố định sắp xếp theo độ ưu tiên:
  ```python
  TIER2_RULES = (
      ("R01-PV", 1, _check_r01, "Phản vệ theo kịch bản R01 (không rõ dị nguyên, có tổn thương da và hô hấp/tuần hoàn)"),
      ("R02-PV", 2, _check_r02, "Phản vệ theo kịch bản R02 (có dị nguyên nghi ngờ, tổn thương từ 2 hệ cơ quan trở lên)"),
      ("R03-PV", 3, _check_r03, "Phản vệ theo kịch bản R03 (dị nguyên đã biết không qua đường hít kèm triệu chứng hô hấp hoặc tuần hoàn)"),
  )
  ```
- Hàm `classify()` thực hiện luồng điều khiển:
  1. Kiểm tra tính hợp lệ của dữ liệu đầu vào (nếu thiếu tuổi -> trả `THEO_DOI`).
  2. Duyệt qua `TIER2_RULES` theo thứ tự ưu tiên để xác định rule Tầng 2 đầu tiên thỏa mãn.
  3. Nếu không thỏa mãn bất kỳ rule Tầng 2 nào -> Trả về `THEO_DOI`.
  4. Nếu thỏa mãn Tầng 2, chuyển tiếp kết quả sang bước thẩm định tụt huyết áp Tầng 1:
     - Nếu có bằng chứng tụt huyết áp theo độ tuổi -> Gán kết quả `SOC_PHAN_VE`, mã `R-SOC`.
     - Nếu không có bằng chứng hoặc thiếu dữ liệu huyết áp -> Giữ nguyên kết quả Tầng 2 `PHAN_VE`.

### 4. Hệ quả & Đánh đổi (Consequences & Rationale)
- **Đạt được:**
  - Giải quyết dứt điểm vấn đề thứ tự ưu tiên khi nhiều rule cùng thỏa theo quy định tại Issue #15 (`R01 > R02 > R03`).
  - Thể hiện rõ ràng contract kỹ thuật của bài toán, mã nguồn trong sáng và kiểm thử được từng phần.
  - Tối ưu hóa hiệu năng thực thi với thời gian chạy trung bình $< 0.05\text{ ms}$, thỏa mãn tiêu chí A-10 (p95 < 100 ms).
- **Ràng buộc:**
  - Quy tắc đánh giá tuân thủ nghiêm ngặt bảng contract kỹ thuật của đề bài, không tự ý bổ sung logic ngoài phạm vi tài liệu.
