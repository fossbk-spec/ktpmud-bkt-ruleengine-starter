# DECISIONS — Nhật ký quyết định thiết kế (ADR)

> Nhóm 11 · Track A: Rule Engine · Cập nhật 10/11/2026 theo nhận xét Checkpoint 1
> Mỗi ADR ghi: bối cảnh, các phương án, quyết định, lý do, hệ quả.

---

## ADR-001: Tổ chức code của Rule Engine

**Trạng thái:** Đã chọn (08/11/2026), điều chỉnh phần audit ở ADR-004

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
- `classify()` thực hiện: chuẩn hóa input theo policy (ADR-003) → xét Tầng 2 → nếu khớp thì xét Tầng 1 → trả `muc_do`, `rule_id`, `ly_do`.
- Audit là một bước riêng, không nằm trong `classify()` (ADR-004).

### Lý do
- Chỉ có 4 điều kiện, hàm riêng đủ rõ mà không cần cơ chế phức tạp.
- Mỗi hàm một nhiệm vụ nên viết một test cho một AC (xem `TEST_PLAN.md`).
- Cấu trúc bám sát hai tầng của bảng quyết định, dễ đối chiếu và dễ giải thích.
- Tách audit giúp đảm bảo yêu cầu A-06 (không log dữ liệu thô) ngay từ thiết kế.

### Hệ quả
- Muốn thêm rule phải thêm hàm và thêm vào điều phối (chấp nhận được vì V1 chỉ có 4 rule và đề cấm thêm rule ngoài bảng).
- Thứ tự gọi trong `classify()` là một phần của thiết kế và được test bằng AC-28 (xem ADR-002).

---

## ADR-002: Khi nhiều kịch bản phản vệ cùng khớp thì `rule_id` là gì

**Trạng thái:** **Đã chốt** theo issue `fossbk-spec/ktpmud-project#15` (Q-01): R01 > R02 > R03

### Bối cảnh
Bảng quyết định cho phép khớp 1 trong 3 kịch bản nhưng output chỉ có **một** `rule_id`. Bảng không nói khi nhiều kịch bản cùng khớp thì chọn cái nào.

Phân tích: R01 yêu cầu `co_di_nguyen_nghi_ngo = false`, còn R02 và R03 yêu cầu `= true`, nên **R01 không bao giờ cùng khớp với R02 hoặc R03**. Chỉ R02 và R03 có thể cùng khớp. Ví dụ: nghi dị nguyên, có cả hô hấp (không hít) và tuần hoàn, thì đếm được 2 hệ nên R02 khớp, đồng thời R03 cũng khớp.

### Các phương án

| Phương án | Mô tả | Ưu | Nhược |
|---|---|---|---|
| A | Trả rule khớp đầu tiên theo thứ tự trong bảng (R01 → R02 → R03) | Đơn giản, tất định, bám thứ tự bảng | Có thể không phải ý của thầy |
| B | Trả rule "đặc thù" hơn (R03) khi trùng R02 | Có thể sát nghĩa lâm sàng hơn | Là suy diễn ngoài bảng, đề cấm |
| C | Chờ TA trả lời rồi mới code | Chắc chắn đúng | Có thể chưa kịp |

### Quyết định
Chọn **phương án A**: kiểm tra theo thứ tự R01 → R02 → R03, lấy rule đầu tiên khớp. Nhóm đã hỏi và thầy xác nhận đúng như giả định này ở issue #15.

### Lý do
- Tất định: cùng input luôn cho cùng output, test được.
- Không thêm quy tắc lâm sàng nào ngoài bảng (đề cấm ở Mục 5.2).
- Giữ nguyên thứ tự trình bày của bảng, dễ giải thích.

### Hệ quả
- Có test cố định hành vi này: **AC-28** (R02 và R03 cùng thỏa, không tụt HA → `PHAN_VE`, `R02-PV`).
- Nếu sau này thứ tự đổi, chỉ cần sửa thứ tự điều phối trong `classify()`, nhờ thiết kế ở ADR-001.

---

## ADR-003: Chính sách xử lý input thiếu, null, sai kiểu, ngoài miền (Q-05)

**Trạng thái:** Đã chốt (10/11/2026), theo hướng dẫn mục 5 của issue `ktpmud-project#15`

### Bối cảnh
Đặc tả không nói rõ khi input thiếu hoặc không hợp lệ thì làm gì. Thầy yêu cầu: với trường bool thiếu khóa hoặc `null` thì **không được lỗi** và **không được hạ mức** khi các trường đã có đã đủ thỏa trọn một rule.

### Các phương án

| Phương án | Mô tả | Ưu | Nhược |
|---|---|---|---|
| A | Mọi input lỗi hoặc thiếu đều trả `THEO_DOI` | Đơn giản, an toàn về mặt "không kết luận" | **Hạ mức sai**: một ca đã đủ dữ kiện cho `PHAN_VE`/`SOC_PHAN_VE` bị trả `THEO_DOI` chỉ vì một trường phụ thiếu. Thầy đã nói không chấp nhận |
| B | Ném ngoại lệ khi input không hợp lệ | Rõ ràng cho người gọi | Chương trình crash, vi phạm A-04 |
| C | Mỗi trường không dùng được coi là "không xác định"; rule vẫn khớp nếu các trường đã biết đủ thỏa trọn; "không xác định" không bao giờ tính là `true` | Không hạ mức sai, không crash, tất định, test được bằng bảng | Phải viết policy theo từng trường và nhiều ca test |

### Quyết định
Chọn **phương án C**. Policy đầy đủ theo từng trường nằm ở `REQUIREMENTS.md` mục 6.2. Riêng `tuoi` không dùng được thì `THEO_DOI` (Q-02 đã chốt).

### Lý do
- Làm đúng yêu cầu của thầy: không lỗi, không hạ mức.
- "Không xác định" không tính là `true` nên không bao giờ làm một ca khớp rule nhờ dữ liệu không tồn tại (tránh báo phản vệ giả).
- Một nguyên tắc chung cho mọi trường, dễ giải thích khi vấn đáp.

### Hệ quả
- Phải có hàm kiểm tra giá trị chặt (chỉ `True`/`False` mới là bool hợp lệ; `"true"`, `1` là sai kiểu).
- Test theo bảng: AC-37…AC-44.
- Nếu thầy chỉnh policy, chỉ cần sửa bảng ở mục 6.2 và các AC tương ứng.

---

## ADR-004: Cung cấp `User_UUID` và nơi ghi audit (Q-06)

**Trạng thái:** Đã chốt (10/11/2026)

### Bối cảnh
Output của `classify()` chỉ gồm `muc_do`, `rule_id`, `ly_do`, và input bị cấm có trường định danh. Nhưng audit cần `User_UUID`. Cần quyết định UUID đến từ đâu và bản ghi audit được ghi vào đâu để viết được AC-24/AC-25.

### Các phương án

| Phương án | Mô tả | Ưu | Nhược |
|---|---|---|---|
| A | Thêm tham số `user_uuid` vào `classify()` | Gọi một hàm là xong | Đổi chữ ký của starter, có thể lệch với test của thầy; trộn audit vào hàm nghiệp vụ |
| B | Đặt `User_UUID` trong dict input | Không đổi chữ ký | Vi phạm hợp đồng dữ liệu (chỉ 9 trường), trộn định danh vào dữ liệu lâm sàng |
| C | Hàm bọc `classify_with_audit(data, user_uuid, audit_sink)` gọi `classify()` rồi ghi audit | `classify()` giữ nguyên; audit tách khỏi nghiệp vụ; test được qua `audit_sink` | Phải gọi hàm bọc khi cần audit |

### Quyết định
Chọn **phương án C**:
- `User_UUID` do **bên gọi** cung cấp, nằm ngoài dữ liệu lâm sàng.
- Audit ghi vào `audit_sink` do bên gọi truyền vào (mặc định: danh sách trong bộ nhớ).
- Bản ghi gồm đúng 4 khóa `Timestamp`, `User_UUID`, `Action_Type` (`"CLASSIFY"`), `Status` (`"OK"`/`"ERROR"`), và không chứa bất kỳ giá trị lâm sàng nào.

### Lý do
- Giữ nguyên chữ ký `classify()` của starter, giảm rủi ro lệch test của thầy.
- Phù hợp ADR-001: audit là bước riêng.
- `audit_sink` truyền vào giúp test đọc được bản ghi mà không cần file hay hệ thống ngoài.

### Hệ quả
- Test AC-24, AC-25, AC-45 đọc trực tiếp từ `audit_sink`.
- Cần kiểm tra chữ ký hàm trong `rule_engine/classifier.py` của starter trước khi viết code, để hàm bọc khớp.
