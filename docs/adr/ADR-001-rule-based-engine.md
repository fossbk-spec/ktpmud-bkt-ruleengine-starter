# ADR-001: Lựa chọn Rule-Based Engine

- Liên quan: `REQUIREMENTS.md`, `acceptance-criteria.md`, `test-plan.md`

## 1. Context
- Module cần phân loại dữ liệu đầu vào thành `SOC_PHAN_VE`, `PHAN_VE` hoặc `THEO_DOI` theo bảng quyết định WAO/EAACI V1 trong `docs/decision-table.md`.
- Bảng quyết định là contract đã khóa của đề thi: ngưỡng và quy tắc rõ ràng, không được tự thay đổi hay thêm quy tắc lâm sàng ngoài bảng.
- Kết quả cần tất định (cùng input hợp lệ cho cùng output) và giải thích được qua mã quy tắc (`R-SOC`, `R01-PV`, `R02-PV`, `R03-PV`).
- Đề yêu cầu audit trail `[Timestamp, User_UUID, Action_Type, Status]`, zero PII, p95 < 100 ms, và loại trừ machine learning khỏi phạm vi (Mục 7.4 của đề).
- Phạm vi là một module đánh giá độc lập, không phải hệ thống bệnh viện.

## 2. Decision
Dùng **Rule-Based Engine** cài đặt trong `rule_engine/classifier.py`, với các nguyên tắc thiết kế sau:

1. **Bám contract:** cài đặt đúng điều kiện R01-PV, R02-PV, R03-PV và R-SOC theo `decision-table.md`; không bổ sung ngưỡng hay quy tắc khác.
2. **Thứ tự đánh giá cố định:** kiểm tra hợp lệ đầu vào, sau đó Tầng 2 (xác định các kịch bản khớp), rồi Tầng 1 (sốc nếu đạt Tầng 2 và HATT dưới ngưỡng theo tuổi). Ưu tiên kết quả: R-SOC > R03-PV > R02-PV; R01-PV loại trừ với R02/R03 vì khác `co_di_nguyen_nghi_ngo`. Không khớp gì thì `THEO_DOI` với `rule_id = null`.
3. **Kiểm tra đầu vào trước khi đánh giá:** dữ liệu thiếu, sai kiểu, ngoài miền hoặc có trường lạ trả `THEO_DOI`; không ép kiểu, không coi dữ liệu thiếu là `false`, không ném exception ra ngoài. Chi tiết ở `REQUIREMENTS.md` mục 5.
4. **Tính toán an toàn số học:** so sánh ngưỡng dùng `<` thực sự; tiêu chí giảm > 30% tính bằng số nguyên (`10 × HATT < 7 × HATT_nền`) để tránh sai số float.
5. **Tập trung quy tắc:** ngưỡng và điều kiện khai báo ở một chỗ, tách khỏi luồng xử lý, để review và test đối chiếu trực tiếp với decision table.
6. **Kết quả truy vết được:** trả `{muc_do, rule_id, ly_do}`; `ly_do` chỉ nêu quy tắc hoặc nhóm lý do, không chứa dữ liệu lâm sàng thô và không có lời khuyên điều trị.
7. **Audit tối thiểu:** mỗi lần phân loại ghi đúng 4 trường `[Timestamp, User_UUID, Action_Type, Status]`. `User_UUID` là của người vận hành do bên gọi cung cấp, không phải bệnh nhân. Audit không chứa input hay triệu chứng.
8. **Giữ module độc lập:** không đảm nhiệm giao diện, quản lý hồ sơ hoặc lưu trữ dữ liệu bệnh nhân. Bản ghi audit là nhật ký thao tác, không phải kho dữ liệu bệnh nhân.

## 3. Alternatives

- **AI / Machine Learning Classification** — không chọn vì ngoài phạm vi theo đề (Mục 7.4); cần dữ liệu huấn luyện mà dự án chỉ có dữ liệu synthetic; kết quả khó giải thích bằng mã quy tắc; khó đảm bảo tính tất định và khó đối chiếu với bảng quyết định đã khóa.
- **Hybrid AI + Rule-Based Engine** — không chọn vì thêm độ phức tạp và bề mặt kiểm thử mà contract không yêu cầu; phần AI có thể tạo kết quả trái bảng quyết định, vi phạm quy định "không sửa hay suy diễn quy tắc ngoài contract".
- **Bảng quyết định dạng dữ liệu (đọc từ file cấu hình)** — có thể cân nhắc về sau; ở V1 số quy tắc ít và cố định, nên hard-code có cấu trúc rõ ràng thì đơn giản và dễ test hơn. Điều kiện sốc theo tuổi cũng cần logic tính toán chứ không chỉ tra bảng.

## 4. Rationale
- Không cần dữ liệu huấn luyện.
- Quy tắc rõ ràng, ánh xạ 1-1 sang bảng quyết định, dễ review và dễ kiểm thử (có thể viết oracle độc lập trong test).
- Kết quả giải thích được thông qua mã quy tắc và `ly_do`.
- Tất định theo thiết kế, đáp ứng AC17.
- Độ phức tạp tính toán rất thấp, dễ đạt p95 < 100 ms.
- Phù hợp với phạm vi một module độc lập và thời gian 18 ngày.

## 5. Consequences

### Positive
- Dễ triển khai và kiểm thử; đủ để bao phủ boundary, priority, invalid, missing.
- Kết quả nhất quán với cùng đầu vào.
- Dễ truy vết quy tắc được kích hoạt, thuận lợi cho audit và vấn đáp.
- Không có phụ thuộc ngoài (chỉ `pytest`), dễ chạy từ clean checkout.

### Negative
- Độ đúng của hệ thống phụ thuộc hoàn toàn vào độ chính xác của bộ quy tắc; nhóm không đánh giá độ đúng y khoa, chỉ đảm bảo cài đặt trung thành với contract.
- Khi tiêu chí thay đổi (ví dụ bảng V2), cần cập nhật quy tắc, AC và kiểm thử lại.
- Không thích ứng với trường hợp ngoài bảng; những ca đó rơi vào `THEO_DOI`.
- `THEO_DOI` chỉ có nghĩa "chưa đủ dữ kiện kết luận", không phải kết luận an toàn; người dùng module không được hiểu nó như một đánh giá âm tính.

## 6. Risks and Mitigations

- **Cài đặt lệch bảng quyết định** → oracle độc lập trong test (TC54), ca biên có tính tay (TC37–TC45).
- **Sai số float ở ngưỡng tuổi và giảm 30%** → so sánh số nguyên cho tiêu chí 30%; test tuổi 10.99 và 11.0.
- **Giả định chưa rõ trong contract (HATT null, miền hợp lệ...)** → ghi ở `REQUIREMENTS.md` mục 11, hỏi TA qua GitHub Issues, test tương ứng đánh dấu ở `test-plan.md` mục 10.
- **Rò thông tin định danh hoặc dữ liệu thô qua `ly_do` hoặc audit** → AC15, AC16, AC19; test quét chuỗi (TC49, TC52, TC58).
