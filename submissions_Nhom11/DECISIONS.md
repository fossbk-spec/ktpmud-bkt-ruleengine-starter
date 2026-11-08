# DECISIONS — Nhật ký quyết định thiết kế (ADR)

> Nhóm 11 · Track A: Rule Engine
> Mỗi ADR ghi: bối cảnh, các phương án, quyết định, lý do, hệ quả.

---

## ADR-001: Tổ chức code của Rule Engine

**Trạng thái:** Đã chọn (08/11/2026)

### Bối cảnh
`docs/decision-table.md` có đúng 3 kịch bản phản vệ (R01, R02, R03) và 1 điều kiện sốc (tụt huyết áp theo tuổi). Ta cần một cách tổ chức code để:
- test được từng rule riêng;
- truy vết được rule nào đã kích hoạt (`rule_id`);
- giải thích được cho người chấm khi vấn đáp;
- không trộn dữ liệu lâm sàng vào phần ghi audit.

### Các phương án

| Phương án | Mô tả | Ưu | Nhược |
|---|---|---|---|
| A | Một hàm `classify()` chứa toàn bộ `if/else` lồng nhau | Nhanh viết nhất | Khó test từng rule, khó truy vết rule, dễ sai điều kiện |
| B | Rule khai báo dạng dữ liệu (bảng điều kiện) và một bộ chạy chung | Dễ thêm rule | Quá phức tạp cho 4 rule; khó đọc và khó giải thích |
| C | Mỗi rule là một hàm thuần riêng (nhận input, trả đúng/sai); `classify()` chỉ điều phối theo 2 tầng; audit tách riêng | Test từng rule độc lập; rõ ràng; dễ giải thích | Thêm rule mới phải viết thêm hàm |

### Quyết định
Chọn **phương án C**:
- Hàm riêng cho từng rule: `r01`, `r02`, `r03`.
- Hàm riêng cho ngưỡng sốc: `is_hypotensive(tuoi, hatt, hatt_nen)`.
- `classify()` thực hiện: kiểm tra input → xét Tầng 2 → nếu khớp thì xét Tầng 1 → trả `muc_do`, `rule_id`, `ly_do`.
- Audit là một bước riêng, chỉ nhận `User_UUID`, loại hành động và trạng thái, **không nhận dữ liệu lâm sàng**.

### Lý do
- Chỉ có 4 điều kiện, hàm riêng đủ rõ mà không cần cơ chế phức tạp.
- Mỗi hàm một nhiệm vụ nên viết một test cho một AC (xem `TEST_PLAN.md`).
- Cấu trúc bám sát hai tầng của bảng quyết định, dễ đối chiếu và dễ giải thích.
- Tách audit giúp đảm bảo yêu cầu A-06 (không log dữ liệu thô) ngay từ thiết kế.

### Hệ quả
- Muốn thêm rule phải thêm hàm và thêm vào điều phối (chấp nhận được vì V1 chỉ có 4 rule và đề cấm thêm rule ngoài bảng).
- Thứ tự gọi trong `classify()` là một phần của thiết kế và được test (xem ADR-002).

---

## ADR-002: Khi nhiều kịch bản phản vệ cùng khớp thì `rule_id` là gì

**Trạng thái:** Tạm thời, chờ TA xác nhận (Q-01)

### Bối cảnh
Bảng quyết định cho phép khớp 1 trong 3 kịch bản nhưng output chỉ có **một** `rule_id`. Bảng không nói khi nhiều kịch bản cùng khớp thì chọn cái nào.

Phân tích: R01 yêu cầu `co_di_nguyen_nghi_ngo = false`, còn R02 và R03 yêu cầu `= true`, nên **R01 không bao giờ cùng khớp với R02 hoặc R03**. Chỉ R02 và R03 có thể cùng khớp. Ví dụ: nghi dị nguyên, có cả hô hấp (không hít) và tuần hoàn, thì đếm được 2 hệ nên R02 khớp, đồng thời R03 cũng khớp.

### Các phương án

| Phương án | Mô tả | Ưu | Nhược |
|---|---|---|---|
| A | Trả rule khớp đầu tiên theo thứ tự trong bảng (R01 → R02 → R03) | Đơn giản, tất định, bám thứ tự bảng | Có thể không phải ý của thầy |
| B | Trả rule "đặc thù" hơn (R03) khi trùng R02 | Có thể sát nghĩa lâm sàng hơn | Là suy diễn ngoài bảng, đề cấm |
| C | Chờ TA trả lời rồi mới code | Chắc chắn đúng | Có thể chưa kịp |

### Quyết định tạm thời
Chọn **phương án A** làm mặc định: kiểm tra theo thứ tự R01 → R02 → R03, lấy rule đầu tiên khớp. Đồng thời **hỏi TA** (Q-01). Nếu TA trả lời khác, sửa lại thứ tự và cập nhật ADR này.

### Lý do
- Tất định: cùng input luôn cho cùng output, test được.
- Không thêm quy tắc lâm sàng nào ngoài bảng (đề cấm ở Mục 5.2).
- Giữ nguyên thứ tự trình bày của bảng, dễ giải thích.

### Hệ quả
- Phải có test cố định hành vi này (ca R02 và R03 cùng khớp).
- Nếu TA chọn thứ tự khác, chỉ cần đổi thứ tự điều phối trong `classify()`, nhờ thiết kế ở ADR-001.
- Các điểm mơ hồ còn lại (Q-02…Q-06) xử lý theo giả định trong `REQUIREMENTS.md` mục 6 và sẽ có ADR riêng nếu cần.
