# TÀI LIỆU ĐẶC TẢ YÊU CẦU & KẾ HOẠCH KIỂM THỬ (REQUIREMENTS & TEST PLAN)
> **Dự án:** Track A — Dr May Day: Rule Engine Sprint  
> **Mã đề:** KTPMUD-BKT-2026-PILOT  
> **Mã nhóm:** Nhóm 18 + 19  
> **Thành viên:** 202414288, 202414324, 202414276, 202414384  
> **Mốc hoàn thành:** Checkpoint 1 (M1 — Understand)  
> **Tài liệu căn cứ (SSoT):** `docs/decision-table.md`  

---

## 1. PHẠM VI DỰ ÁN (SCOPE)

### 1.1. Trong phạm vi (In-Scope)
- Xây dựng module Rule Engine (`rule_engine/classifier.py`) nhận dữ liệu đầu vào JSON synthetic theo cấu trúc `Data Dictionary`.
- Đánh giá phân loại 2 tầng theo tiêu chí WAO/EAACI:
  - **Tầng 1:** Sốc phản vệ (`SOC_PHAN_VE` - Rule `R-SOC`).
  - **Tầng 2:** Phản vệ (`PHAN_VE` - Gồm 3 kịch bản `R01-PV`, `R02-PV`, `R03-PV`).
  - Trạng thái chưa đủ dữ kiện kết luận (`THEO_DOI` - `rule_id = null`).
- Trả về kết quả JSON chuẩn chứa trường `ly_do` nêu rõ căn cứ luật kích hoạt mà không đưa ra lời khuyên y khoa.
- Xử lý an toàn dữ liệu thiếu (missing), dữ liệu sai kiểu/ngoài miền (invalid).
- Ghi vết kiểm toán (Audit Trail) tối thiểu 4 trường: `[Timestamp, User_UUID, Action_Type, Status]`.
- Kiểm thử tự động bằng `pytest` đạt từ clean checkout.
- Đo kiểm benchmark độ trễ: $p95 < 100\text{ ms}$ cho tối thiểu 1.000 lần chạy.

### 1.2. Ngoài phạm vi (Out-of-Scope)
- Giao diện người dùng (UI / Web frontend / Mobile app).
- Kết nối cơ sở dữ liệu thật hoặc hệ thống production của Dr May Day.
- Đưa ra khuyến nghị điều trị, phác đồ cấp cứu, hoặc kê đơn thuốc trong trường `ly_do`.
- Áp dụng mô hình Machine Learning / Deep Learning / LLM sinh kết quả runtime.
- Thu thập hoặc sử dụng dữ liệu bệnh nhân thật (Cam kết Zero PII/PHI).

---

## 2. TIÊU CHÍ NGHIỆM THU (ACCEPTANCE CRITERIA)

| Mã tiêu chí | Nội dung tiêu chí | Giải pháp đáp ứng của nhóm |
| :--- | :--- | :--- |
| **A-01** | `classify()` thực thi đúng contract, không còn `NotImplementedError` | Cài đặt hàm nhận `PatientInput` và trả về `ClassificationResult`. |
| **A-02** | Không hard-code theo ID của fixture công khai | Logic đánh giá hoàn toàn dựa trên giá trị các trường sinh lý trong dict đầu vào. |
| **A-03** | Bao phủ đủ các mức phân loại theo `docs/decision-table.md` | Hỗ trợ đầy đủ: `SOC_PHAN_VE`, `PHAN_VE` (R01, R02, R03), và `THEO_DOI`. |
| **A-04** | Xử lý input thiếu, sai kiểu, ngoài miền theo policy công bố | Kiểm tra validation đầu vào; trường hợp thiếu tuổi hoặc sai kiểu sẽ trả về `THEO_DOI` an toàn, không gây crash hệ thống. |
| **A-05** | Trả `ly_do` truy vết được rule, không đưa lời khuyên điều trị | Chỉ giải thích điều kiện thỏa mãn rule (ví dụ: *"Khớp R01 do có tổn thương da và hô hấp không rõ dị nguyên"*). Tuyệt đối không chứa từ ngữ chỉ định thuốc hay điều trị. |
| **A-06** | Ghi audit đúng 4 trường, không log raw clinical input | Log đúng định dạng: `[Timestamp, User_UUID, Action_Type, Status]`. Không ghi nhận triệu chứng, huyết áp hay PII. |
| **A-07** | Có unit tests cho normal, boundary, invalid và missing cases | Xây dựng bộ test suite đa dạng trong thư mục `tests/`. |
| **A-08** | `python -m pytest tests/ -q` đạt từ clean checkout | Đảm bảo mã nguồn chạy pass 100% không phụ thuộc môi trường ngoài. |
| **A-09** | CI chạy test trên Pull Request | Thiết lập GitHub Actions tự động kiểm tra trên PR. |
| **A-10** | Benchmark tối thiểu 1.000 lần chạy; $p95 < 100\text{ ms}$ | Viết script đo lường với `time.perf_counter()`, tính toán p50 và p95. |
| **A-11** | README ghi rõ cảnh báo an toàn | Đưa cảnh báo: *"educational/synthetic — not for clinical use"* lên đầu README. |

---

## 3. KẾ HOẠCH KIỂM THỬ (TEST PLAN)

| Nhóm Test | Mục tiêu kiểm thử | Dữ liệu đầu vào dự kiến | Kết quả mong đợi |
| :--- | :--- | :--- | :--- |
| **Normal - R01** | Test kịch bản phản vệ không rõ dị nguyên | `co_di_nguyen_nghi_ngo=False`, `co_ton_thuong_da_niem_mac=True`, `co_trieu_chung_ho_hap=True` | `muc_do="PHAN_VE"`, `rule_id="R01-PV"` |
| **Normal - R02** | Test phản vệ có dị nguyên nghi ngờ, ≥2 cơ quan | `co_di_nguyen_nghi_ngo=True`, `da=True`, `tieu_hoa_nang=True` | `muc_do="PHAN_VE"`, `rule_id="R02-PV"` |
| **Normal - R03** | Test phản vệ dị nguyên đã biết không qua đường hít | `co_di_nguyen_nghi_ngo=True`, `di_nguyen_qua_duong_hit=False`, `ho_hap=True` | `muc_do="PHAN_VE"`, `rule_id="R03-PV"` |
| **Normal - R-SOC**| Test sốc phản vệ ở trẻ < 1 tuổi | Khớp Tầng 2, `tuoi=0.5`, `huyet_ap_tam_thu=65` (<70) | `muc_do="SOC_PHAN_VE"`, `rule_id="R-SOC"` |
| **Boundary - HATT**| Kiểm tra huyết áp chạm đúng ngưỡng so sánh | `tuoi=15`, `huyet_ap_tam_thu=90` (ngưỡng <90) | `muc_do="PHAN_VE"` (Không bị sốc) |
| **Boundary - Tuổi**| Chạm mốc đổi công thức tính huyết áp | `tuoi=1.0`, `tuoi=11.0`, `tuoi=18.0` | Tính đúng ngưỡng áp dụng |
| **Invalid** | Dữ liệu sai miền giá trị | `tuoi=-5`, huyết áp âm | `muc_do="THEO_DOI"`, `rule_id=None` |
| **Missing** | Dữ liệu bị khuyết trường bắt buộc | Không truyền trường `tuoi` | `muc_do="THEO_DOI"`, `rule_id=None` |
