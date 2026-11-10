# TÀI LIỆU ĐẶC TẢ YÊU CẦU & KẾ HOẠCH KIỂM THỬ (REQUIREMENTS & TEST PLAN)

- **Dự án:** Track A — Dr May Day: Rule Engine Sprint
- **Mã đề:** KTPMUD-BKT-2026-PILOT
- **Mã nhóm:** Nhóm 18 + 19
- **Thành viên:** 202414288, 202414324, 202414276, 202414384
- **Căn cứ kỹ thuật (SSoT):** `docs/decision-table.md` và quy định làm rõ tại [Issue #15 ktpmud-project](https://github.com/fossbk-spec/ktpmud-project/issues/15)

---

## 1. PHẠM VI HỆ THỐNG (SCOPE)

### 1.1. Trong phạm vi (In-Scope)
- Hiện thực hàm `classify(patient: PatientInput) -> ClassificationResult` trong `rule_engine/classifier.py` theo đúng contract dữ liệu của `docs/decision-table.md`.
- Đánh giá phân loại tất định (deterministic) 2 tầng:
  - **Tầng 1 (Sốc phản vệ):** Gán nhãn `SOC_PHAN_VE`, mã rule `R-SOC`.
  - **Tầng 2 (Phản vệ):** Gán nhãn `PHAN_VE`, mã rule theo thứ tự ưu tiên `R01-PV`, `R02-PV`, `R03-PV`.
  - **Trạng thái theo dõi:** Gán nhãn `THEO_DOI`, `rule_id = None`.
- Áp dụng chính sách xử lý dữ liệu thiếu / không hợp lệ theo bảng quy chuẩn tại Mục 3.
- Ghi nhận nhật ký kiểm toán (Audit Trail) tối thiểu 4 trường: `[Timestamp, User_UUID, Action_Type, Status]` không chứa dữ liệu lâm sàng thô.
- Kiểm thử tự động với `pytest`, kiểm soát chất lượng qua GitHub Actions CI.
- Đo kiểm benchmark độ trễ thực thi: p95 < 100 ms với tối thiểu 1.000 lượt chạy sau warm-up.

### 1.2. Ngoài phạm vi (Out-of-Scope)
- Giao diện người dùng (UI), ứng dụng web/mobile.
- Kết nối cơ sở dữ liệu thật, dịch vụ bên ngoài hoặc môi trường production Dr May Day.
- Khuyến nghị điều trị, phác đồ cấp cứu, hoặc kê đơn trong trường `ly_do`.
- Huấn luyện hoặc suy luận mô hình học máy (ML/DL/LLM).
- Sử dụng dữ liệu định danh thực tế (áp dụng nguyên tắc Zero PII).

---

## 2. QUY TẮC PHÂN LOẠI & THỨ TỰ ƯU TIÊN RULE

Hệ thống tuân thủ thứ tự đánh giá được quy định tại `docs/decision-table.md` và thống nhất chung tại Issue #15:

1. **Điều kiện Sốc phản vệ (Tầng 1 - `R-SOC`):**
   - Phải thỏa mãn **ít nhất một rule Phản vệ ở Tầng 2** (`R01-PV`, `R02-PV`, hoặc `R03-PV`).
   - **VÀ** có bằng chứng tụt huyết áp tâm thu (HATT) theo độ tuổi:
     - $0 \le \text{tuoi} < 1$: $\text{HATT} < 70\text{ mmHg}$.
     - $1 \le \text{tuoi} < 11$: $\text{HATT} < 70 + 2 \times \text{tuoi}\text{ mmHg}$.
     - $11 \le \text{tuoi} < 18$: $\text{HATT} < 90\text{ mmHg}$.
     - $\text{tuoi} \ge 18$: $\text{HATT} < 90\text{ mmHg}$ **hoặc** $\text{HATT} < 0.7 \times \text{HATT nền}$ (mức giảm $> 30\%$, không tính bằng).
   - Khi đạt cả hai điều kiện trên: Kết quả là `SOC_PHAN_VE`, mã `R-SOC` (bỏ qua mã rule Tầng 2).

2. **Thứ tự ưu tiên Tầng 2 khi không đạt Sốc:**
   - Khi dữ liệu thỏa mãn đồng thời nhiều rule Tầng 2, hệ thống trả về kết quả `PHAN_VE` với duy nhất một `rule_id` theo thứ tự ưu tiên:
     $$\text{R01-PV} > \text{R02-PV} > \text{R03-PV}$$
   - Cụ thể: Nếu thỏa cả R02 và R03 thì trả về `rule_id = "R02-PV"`. Trường `ly_do` có thể ghi chú thêm việc thỏa mãn rule phụ.

3. **Trường hợp gán nhãn `THEO_DOI`:**
   - Không khớp bất kỳ rule nào ở Tầng 1 và Tầng 2.
   - Hoặc dữ liệu đầu vào thiếu trường `tuoi` (không đủ căn cứ xác định ngưỡng HATT cho Tầng 1).

---

## 3. CHÍNH SÁCH XỬ LÝ DỮ LIỆU THIẾU & KHÔNG HỢP LỆ (A-04 POLICY)

Bảng chính sách xử lý dữ liệu theo chuẩn thống nhất tại [Issue #15](https://github.com/fossbk-spec/ktpmud-project/issues/15):

| Trường dữ liệu | Giá trị đầu vào | Chính sách xử lý của Engine | Kết quả phân loại (`muc_do`, `rule_id`) |
| :--- | :--- | :--- | :--- |
| `tuoi` | `null` hoặc thiếu khóa | Không đủ căn cứ xác định ngưỡng huyết áp Tầng 1. | Trả về `THEO_DOI`, `rule_id = None`. `ly_do` ghi rõ thiếu tuổi. |
| `tuoi` | Sai kiểu dữ liệu hoặc $\text{tuoi} < 0$ | Dữ liệu không hợp lệ. | Trả về `THEO_DOI`, `rule_id = None`. |
| `huyet_ap_tam_thu` | `null` hoặc thiếu khóa | Coi như không có bằng chứng tụt huyết áp để chứng minh Tầng 1. | Nếu thỏa Tầng 2: Trả `PHAN_VE` + rule_id tương ứng (không hạ mức xuống `THEO_DOI`). `ly_do` nêu rõ chưa đánh giá được sốc do thiếu HATT. Nếu không thỏa Tầng 2: Trả `THEO_DOI`. |
| `huyet_ap_tam_thu` | Giá trị $\le 0$ | Giá trị đo sinh lý không hợp lệ, coi như thiếu đo. | Xử lý tương tự trường hợp `null`. |
| `huyet_ap_tam_thu_nen` | `null` hoặc thiếu khóa (với $\text{tuoi} \ge 18$) | Nhánh giảm $> 30\%$ không đủ dữ liệu tính toán, coi như không thỏa nhánh này. | Nếu $\text{HATT} < 90$: Vẫn đạt `R-SOC`. Nếu $\text{HATT} \ge 90$: Không đạt Tầng 1, trả `PHAN_VE` nếu thỏa Tầng 2. `ly_do` nêu không đánh giá được mức giảm do thiếu HATT nền. |
| Các khóa boolean (`co_...`, `di_nguyen_qua_duong_hit`) | `null` hoặc thiếu khóa | Chương trình không phát sinh ngoại lệ runtime. Nếu các trường còn lại đã đủ điều kiện thỏa mãn rule, giữ nguyên kết quả rule đó. Nếu kết quả phụ thuộc vào trường thiếu: mặc định coi là `False`. | Đánh giá theo các trường hiện có; không hạ mức phân loại nếu tập trường hiện hữu đã đủ kết luận. |

---

## 4. TIÊU CHÍ NGHIỆM THU CHI TIẾT (ACCEPTANCE CRITERIA)

### 4.1. Tiêu chí cho từng Rule nghiệp vụ (Rule-Level Acceptance Criteria)

| Mã AC | Input kiểm thử cụ thể | Kết quả kỳ vọng (`muc_do`, `rule_id`) | Diễn giải logic |
| :--- | :--- | :--- | :--- |
| **AC-R01** | `co_di_nguyen_nghi_ngo: False`, `co_ton_thuong_da_niem_mac: True`, `co_trieu_chung_ho_hap: True`, `tuoi: 20`, `huyet_ap_tam_thu: 110` | `muc_do: "PHAN_VE"`<br>`rule_id: "R01-PV"` | Khớp kịch bản R01 (Không rõ dị nguyên + da + hô hấp), huyết áp 110 >= 90 không tụt. |
| **AC-R02** | `co_di_nguyen_nghi_ngo: True`, `co_ton_thuong_da_niem_mac: True`, `co_trieu_chung_tieu_hoa_nang: True`, `tuoi: 25`, `huyet_ap_tam_thu: 120` | `muc_do: "PHAN_VE"`<br>`rule_id: "R02-PV"` | Khớp kịch bản R02 (Có dị nguyên + 2/4 hệ cơ quan gồm da và tiêu hóa), không tụt HA. |
| **AC-R03** | `co_di_nguyen_nghi_ngo: True`, `di_nguyen_qua_duong_hit: False`, `co_trieu_chung_ho_hap: True`, `tuoi: 30`, `huyet_ap_tam_thu: 115` | `muc_do: "PHAN_VE"`<br>`rule_id: "R03-PV"` | Khớp kịch bản R03 (Dị nguyên đã biết không qua đường hít + hô hấp), không tụt HA. |
| **AC-SOC-01** | Thỏa R01, `tuoi: 0.5`, `huyet_ap_tam_thu: 69` | `muc_do: "SOC_PHAN_VE"`<br>`rule_id: "R-SOC"` | Trẻ < 1 tuổi có HATT 69 < 70 mmHg. |
| **AC-SOC-02** | Thỏa R02, `tuoi: 5.0`, `huyet_ap_tam_thu: 79` | `muc_do: "SOC_PHAN_VE"`<br>`rule_id: "R-SOC"` | Trẻ 5 tuổi có ngưỡng tụt $70 + 2 \times 5 = 80$; HATT 79 < 80 mmHg. |
| **AC-SOC-03** | Thỏa R03, `tuoi: 15.0`, `huyet_ap_tam_thu: 89` | `muc_do: "SOC_PHAN_VE"`<br>`rule_id: "R-SOC"` | Tuổi 11–17 có HATT 89 < 90 mmHg. |
| **AC-SOC-04** | Thỏa R02, `tuoi: 30.0`, `huyet_ap_tam_thu: 89` | `muc_do: "SOC_PHAN_VE"`<br>`rule_id: "R-SOC"` | Người >= 18 tuổi có HATT 89 < 90 mmHg. |
| **AC-SOC-05** | Thỏa R02, `tuoi: 40.0`, `huyet_ap_tam_thu: 95`, `huyet_ap_tam_thu_nen: 140` | `muc_do: "SOC_PHAN_VE"`<br>`rule_id: "R-SOC"` | Ngưỡng giảm 30% là $140 \times 0.7 = 98$; HATT 95 < 98 mmHg (giảm > 30%). |
| **AC-PRIORITY**| Thỏa cả R02 (da + hô hấp) và R03 (không đường hít + hô hấp), `tuoi: 20`, `HATT: 120` | `muc_do: "PHAN_VE"`<br>`rule_id: "R02-PV"` | Ưu tiên R02-PV trước R03-PV theo Issue #15. |
| **AC-MISS-HA** | Thỏa R01, `tuoi: 20`, `huyet_ap_tam_thu: null` | `muc_do: "PHAN_VE"`<br>`rule_id: "R01-PV"` | Thiếu HATT nhưng đã thỏa Tầng 2, không hạ mức xuống THEO_DOI. |
| **AC-MISS-AGE**| Thỏa R01, không có trường `tuoi` | `muc_do: "THEO_DOI"`<br>`rule_id: null` | Thiếu tuổi không thể đánh giá Tầng 1, trả THEO_DOI theo đặc tả. |
| **AC-NONE** | `co_di_nguyen_nghi_ngo: True`, chỉ có `co_ton_thuong_da_niem_mac: True` (1/4 cơ quan) | `muc_do: "THEO_DOI"`<br>`rule_id: null` | Có triệu chứng nhưng không đủ điều kiện kích hoạt bất kỳ rule nào. |

### 4.2. Tiêu chí nghiệm thu Hợp đồng & Phi chức năng (Interface & Non-Functional AC)

| Mã AC | Hạng mục kiểm tra | Điều kiện nghiệm thu (Acceptance Criteria) |
| :--- | :--- | :--- |
| **AC-IF-01** | **Output Contract** | Hàm `classify(patient)` luôn trả về dictionary/object chứa đầy đủ 3 trường bắt buộc: `muc_do` (string), `rule_id` (string hoặc null), `ly_do` (string mô tả căn cứ logic). |
| **AC-IF-02** | **Robustness** | Không ném ngoại lệ chưa bắt (uncaught exception) khi thiếu khóa hoặc giá trị `None`; tự động fallback an toàn theo chính sách A-04. |
| **AC-NFR-01** | **Tính tất định (Determinism)** | Với cùng một bộ dữ liệu đầu vào, kết quả trả về luôn giống nhau 100% qua mọi lần chạy (không phụ thuộc trạng thái ngẫu nhiên hay môi trường). |
| **AC-NFR-02** | **Độ trễ thực thi (Latency)** | Đánh giá rule bằng Pure Python trong bộ nhớ; độ trễ xử lý đơn lẻ $\le 1\text{ ms}$, p95 benchmark $< 100\text{ ms}$ cho 1.000 ca kiểm thử. |

---

## 5. KẾ HOẠCH KIỂM THỬ ĐẶC TẢ (DETAILED TEST SUITE PLAN)

Test suite được phân loại cụ thể với các cặp giá trị biên $\pm 1$ nhằm đảm bảo kiểm tra độc lập từng ranh giới logic:

### 5.1. Nhóm ca Boundary Tuổi và Huyết áp tâm thu ($\pm 1$)

| ID Test Case | Mục đích kiểm thử | Dữ liệu đầu vào (`tuoi`, `HATT`, `HATT nền`, Triệu chứng) | Ngưỡng tính toán | Kết quả mong đợi (`muc_do`, `rule_id`) |
| :--- | :--- | :--- | :--- | :--- |
| `test_bnd_age_0_9_shock` | Ranh giới dưới 1 tuổi (có sốc) | `tuoi: 0.9`, `HATT: 69`, Thỏa R01 | Ngưỡng: HATT < 70 | `SOC_PHAN_VE`, `R-SOC` |
| `test_bnd_age_0_9_no_shock` | Ranh giới dưới 1 tuổi (chạm biên không sốc) | `tuoi: 0.9`, `HATT: 70`, Thỏa R01 | Ngưỡng: HATT < 70 | `PHAN_VE`, `R01-PV` |
| `test_bnd_age_1_0_shock` | Ranh giới mốc 1 tuổi (có sốc) | `tuoi: 1.0`, `HATT: 71`, Thỏa R01 | Ngưỡng: $70 + 2 \times 1 = 72$ | `SOC_PHAN_VE`, `R-SOC` |
| `test_bnd_age_1_0_no_shock` | Ranh giới mốc 1 tuổi (chạm biên không sốc) | `tuoi: 1.0`, `HATT: 72`, Thỏa R01 | Ngưỡng: 72 | `PHAN_VE`, `R01-PV` |
| `test_bnd_age_10_9_shock` | Ranh giới cận trên 11 tuổi (có sốc) | `tuoi: 10.9`, `HATT: 91`, Thỏa R01 | Ngưỡng: $70 + 2 \times 10.9 = 91.8$ | `SOC_PHAN_VE`, `R-SOC` |
| `test_bnd_age_10_9_no_shock`| Ranh giới cận trên 11 tuổi (chạm biên) | `tuoi: 10.9`, `HATT: 92`, Thỏa R01 | Ngưỡng: 91.8 | `PHAN_VE`, `R01-PV` |
| `test_bnd_age_11_0_shock` | Ranh giới mốc 11 tuổi (có sốc) | `tuoi: 11.0`, `HATT: 89`, Thỏa R01 | Ngưỡng: HATT < 90 | `SOC_PHAN_VE`, `R-SOC` |
| `test_bnd_age_11_0_no_shock`| Ranh giới mốc 11 tuổi (chạm biên không sốc) | `tuoi: 11.0`, `HATT: 90`, Thỏa R01 | Ngưỡng: HATT < 90 | `PHAN_VE`, `R01-PV` |
| `test_bnd_age_17_9_shock` | Ranh giới cận 18 tuổi (có sốc) | `tuoi: 17.9`, `HATT: 89`, Thỏa R01 | Ngưỡng: HATT < 90 | `SOC_PHAN_VE`, `R-SOC` |
| `test_bnd_age_17_9_no_shock`| Ranh giới cận 18 tuổi (chạm biên không sốc) | `tuoi: 17.9`, `HATT: 90`, Thỏa R01 | Ngưỡng: HATT < 90 | `PHAN_VE`, `R01-PV` |
| `test_bnd_age_18_0_drop_30_exact` | Người lớn giảm đúng 30% (không đạt sốc) | `tuoi: 25.0`, `HATT: 98`, `HATT_nen: 140`, Thỏa R01 | Ngưỡng giảm $> 30\%$ ($140 \times 0.7 = 98$) | `PHAN_VE`, `R01-PV` |
| `test_bnd_age_18_0_drop_30_over` | Người lớn giảm > 30% (đạt sốc) | `tuoi: 25.0`, `HATT: 97`, `HATT_nen: 140`, Thỏa R01 | Ngưỡng: $97 < 98$ | `SOC_PHAN_VE`, `R-SOC` |

### 5.2. Nhóm ca Kiểm tra Loại trừ & Thứ tự Ưu tiên (Rule Interactions)

| ID Test Case | Mục đích kiểm thử | Dữ liệu đầu vào | Kết quả mong đợi |
| :--- | :--- | :--- | :--- |
| `test_r03_inhalation_excluded` | R03 bị loại trừ do dị nguyên qua đường hít | `co_di_nguyen_nghi_ngo: True`, `di_nguyen_qua_duong_hit: True`, `co_trieu_chung_ho_hap: True` (các triệu chứng khác `False`) | `THEO_DOI`, `rule_id: null` |
| `test_r03_inhalation_valid_non_hit` | R03 hợp lệ khi không qua đường hít | `co_di_nguyen_nghi_ngo: True`, `di_nguyen_qua_duong_hit: False`, `co_trieu_chung_ho_hap: True` | `PHAN_VE`, `rule_id: "R03-PV"` |
| `test_multi_rule_r02_r03_priority` | Nhiều rule thỏa (R02 + R03): ưu tiên R02 | `co_di_nguyen_nghi_ngo: True`, `di_nguyen_qua_duong_hit: False`, `da: True`, `ho_hap: True` (thỏa cả 2/4 cơ quan và R03) | `PHAN_VE`, `rule_id: "R02-PV"` |
| `test_symptom_insufficient` | Có triệu chứng đơn lẻ nhưng không đủ rule | `co_di_nguyen_nghi_ngo: True`, `co_ton_thuong_da_niem_mac: True` (chỉ 1/4 hệ cơ quan) | `THEO_DOI`, `rule_id: null` |

### 5.3. Nhóm ca Xử lý Dữ liệu Thiếu & Biên Giá trị (Missing & Edge Inputs)

| ID Test Case | Mục đích kiểm thử | Dữ liệu đầu vào | Kết quả mong đợi |
| :--- | :--- | :--- | :--- |
| `test_missing_age` | Khuyết trường tuổi | Thỏa R01, không truyền khóa `tuoi` | `THEO_DOI`, `rule_id: null` |
| `test_missing_hatt_with_tier2` | Khuyết HATT nhưng đủ tiêu chí Tầng 2 | Thỏa R02, `huyet_ap_tam_thu: null` | `PHAN_VE`, `rule_id: "R02-PV"` |
| `test_missing_baseline_hatt_adult` | Người lớn thiếu HATT nền, HATT >= 90 | `tuoi: 30`, `HATT: 100`, `HATT_nen: null`, Thỏa R01 | `PHAN_VE`, `rule_id: "R01-PV"` |
| `test_missing_bool_key_safe` | Khuyết khóa boolean không gây crash | Chỉ truyền `tuoi: 20`, `co_di_nguyen_nghi_ngo: False`, `co_ton_thuong_da_niem_mac: True`, `co_trieu_chung_ho_hap: True` (khuyết các khóa tuần hoàn, tiêu hóa...) | `PHAN_VE`, `rule_id: "R01-PV"` |
| `test_invalid_negative_age` | Tuổi mang giá trị âm | `tuoi: -2.0`, Thỏa R01 | `THEO_DOI`, `rule_id: null` |
