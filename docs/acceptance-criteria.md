# Acceptance Criteria — Track A: Rule Engine

Nguồn: `docs/decision-table.md` (đặc tả duy nhất), `REQUIREMENTS.md` (chính sách đầu vào, audit, giả định) và Mục 7.3 của đề thi.
Mã quy tắc dùng đầy đủ: `R01-PV`, `R02-PV`, `R03-PV`, `R-SOC`.

Mỗi tiêu chí có ghi cách kiểm chứng ở cuối dòng; ánh xạ chi tiết sang test case nằm ở `test-plan.md`.

## 1. Input Validation

- **AC01:** Module tiếp nhận dữ liệu theo đúng 9 trường trong Data Dictionary. *(Kiểm chứng: unit test)*
- **AC02:** Kiểm tra kiểu và miền giá trị đầu vào theo chính sách ở `REQUIREMENTS.md` mục 5. Dữ liệu không hợp lệ (sai kiểu, ngoài miền, tuổi âm, NaN/inf, trường lạ) trả `THEO_DOI` với `rule_id = null` và không ném exception. *(unit test)*
- **AC03:** Thiếu trường bắt buộc cần cho việc đánh giá (kể cả `tuoi`) trả `THEO_DOI` với `rule_id = null`. *(unit test)*
- **AC04:** Hai trường được phép null (`huyet_ap_tam_thu`, `huyet_ap_tam_thu_nen`) được xử lý đúng theo Data Dictionary: vắng key hoặc `null` đều hợp lệ; HATT nền chỉ dùng khi `tuoi >= 18`; người lớn không có HATT nền thì chỉ áp dụng tiêu chí HATT < 90. *(unit test)*
- **AC05:** Không tự động chuyển đổi dữ liệu sai kiểu (kể cả `bool` ở trường số, `int` ở trường bool) và không coi dữ liệu thiếu là `false`. *(unit test)*

## 2. Rule Evaluation

- **AC06:** Xác định đúng `R01-PV` khi `co_di_nguyen_nghi_ngo = false` VÀ `co_ton_thuong_da_niem_mac = true` VÀ (`co_trieu_chung_ho_hap = true` HOẶC `co_trieu_chung_tuan_hoan = true`); không kích hoạt khi thiếu một trong các vế. *(unit test)*
- **AC07:** Xác định đúng `R02-PV` khi `co_di_nguyen_nghi_ngo = true` VÀ có ít nhất 2/4 hệ cơ quan dương tính (da/niêm mạc, hô hấp, tuần hoàn, tiêu hóa nặng); đúng 1/4 thì không thỏa. *(unit test)*
- **AC08:** Xác định đúng `R03-PV` khi `co_di_nguyen_nghi_ngo = true` VÀ ((`di_nguyen_qua_duong_hit = false` VÀ `co_trieu_chung_ho_hap = true`) HOẶC `co_trieu_chung_tuan_hoan = true`). Tác nhân hít vào chỉ kèm triệu chứng hô hấp thì không thỏa. *(unit test)*
- **AC09:** Xác định đúng `R-SOC` khi đồng thời đạt ít nhất một kịch bản Tầng 2 VÀ HATT dưới ngưỡng theo tuổi (0–<1: <70; 1–<11: <70+2×tuổi; 11–<18: <90; ≥18: <90 hoặc giảm >30% so với HATT nền). So sánh dùng `<` thực sự; giảm 30% tính bằng số nguyên. *(unit test, boundary test)*

## 3. Rule Priority

- **AC10:** Nếu thỏa điều kiện sốc phản vệ, kết quả phải là `SOC_PHAN_VE` với `rule_id = R-SOC`, bất kể kịch bản Tầng 2 nào đã khớp. *(priority test)*
- **AC11:** Nếu `R02-PV` và `R03-PV` cùng thỏa nhưng không đủ điều kiện sốc, ưu tiên `R03-PV`. (`R01-PV` loại trừ với R02/R03 vì khác `co_di_nguyen_nghi_ngo`.) *(priority test)*

## 4. Output

- **AC12:** `muc_do` thuộc đúng một trong ba giá trị: `SOC_PHAN_VE`, `PHAN_VE`, `THEO_DOI`. Không khớp Tầng 1 lẫn Tầng 2 thì trả `THEO_DOI`. *(unit test)*
- **AC13:** Kết quả luôn có đủ ba trường `muc_do`, `rule_id`, `ly_do`. *(unit test)*
- **AC14:** `rule_id` tương ứng đúng quy tắc được kích hoạt (`R-SOC`, `R01-PV`, `R02-PV`, `R03-PV`); không có quy tắc phù hợp (kể cả input không hợp lệ) thì `null`. *(unit test)*
- **AC15:** `ly_do` giải thích ngắn gọn, truy vết được quy tắc đã kích hoạt hoặc nhóm lý do không hợp lệ; không chứa dữ liệu lâm sàng thô (giá trị tuổi, HATT, trạng thái cờ triệu chứng); lý do của "input không hợp lệ" khác với "không đủ tiêu chí". *(unit test, kiểm tra chuỗi)*

## 5. Privacy and Consistency

- **AC16:** Module không tiếp nhận hoặc xuất thông tin định danh cá nhân; trường lạ bị từ chối và không được lặp lại trong output hay audit; dữ liệu test và demo là synthetic. *(unit test, review)*
- **AC17:** Cùng một bộ dữ liệu đầu vào hợp lệ luôn cho cùng kết quả (tất định). *(test lặp nhiều lần)*

## 6. Audit

- **AC18:** Mỗi lần phân loại ghi đúng bốn trường `[Timestamp, User_UUID, Action_Type, Status]`; `User_UUID` là của người vận hành, không phải bệnh nhân. *(unit test)*
- **AC19:** Audit không chứa triệu chứng, điểm số sức khỏe, giá trị đầu vào hay dữ liệu nhận dạng. *(unit test, review)*

## 7. Quality and Delivery

- **AC20:** Có unit test cho các trường hợp normal, boundary, invalid và missing, bao phủ đủ ba mức phân loại. *(pytest)*
- **AC21:** `pytest -q` đạt từ clean checkout (tạo venv, `pip install -r requirements.txt`). *(chạy trên máy sạch)*
- **AC22:** CI chạy test tự động trên Pull Request. *(workflow CI xanh)*
- **AC23:** Benchmark tối thiểu 1.000 lần chạy sau warm-up; báo cáo p50 và p95; p95 < 100 ms trên máy đo được khai báo trong `TEST_REPORT.md`. *(script benchmark)*
- **AC24:** README ghi rõ "educational/synthetic — not for clinical use". *(review)*
- **AC25:** `classify()` thực thi đúng contract: không còn `NotImplementedError`, không hard-code theo ID của public fixture. *(review, test)*
- **AC26:** `ly_do` không đưa lời khuyên điều trị. *(review, kiểm tra chuỗi)*

## 8. Ánh xạ sang tiêu chí của đề thi (Mục 7.3)

- **A-01** → AC25
- **A-02** → AC25
- **A-03** → AC06, AC07, AC08, AC09, AC10, AC11, AC12
- **A-04** → AC02, AC03, AC04, AC05
- **A-05** → AC14, AC15, AC26
- **A-06** → AC18, AC19
- **A-07** → AC20
- **A-08** → AC21
- **A-09** → AC22
- **A-10** → AC23
- **A-11** → AC24

Các AC còn lại (AC01, AC13, AC16, AC17) bổ sung thêm so với đề, xuất phát từ Data Dictionary, Output contract và yêu cầu Zero PII.
