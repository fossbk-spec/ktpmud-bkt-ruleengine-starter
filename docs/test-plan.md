# Test Plan — Track A: Rule Engine

Căn cứ: `docs/decision-table.md` (đặc tả duy nhất), `REQUIREMENTS.md`, `acceptance-criteria.md` (AC01–AC26).

## 1. Testing Objectives
- Kiểm tra tính hợp lệ của dữ liệu đầu vào (thiếu, sai kiểu, ngoài miền).
- Kiểm tra kết quả đánh giá của R01-PV, R02-PV, R03-PV và R-SOC, kể cả các ca âm tính.
- Kiểm tra thứ tự ưu tiên giữa các quy tắc.
- Kiểm tra ngưỡng huyết áp theo tuổi tại các điểm biên.
- Kiểm tra định dạng, nội dung `ly_do` và tính nhất quán của đầu ra.
- Kiểm tra audit trail, hiệu năng và quy trình tích hợp (clean checkout, CI).

## 2. Testing Scope

Trong phạm vi: Input Validation, Rule Evaluation, Rule Priority, Boundary Cases, Output Validation, Consistency, Audit, Performance, Integration.

Ngoài phạm vi: giao diện, lưu trữ dữ liệu bệnh nhân, độ đúng y khoa của bảng quyết định (bảng là contract đã khóa của đề thi).

## 3. Môi trường và dữ liệu test

- Python 3.x, `pytest>=8.0`, chạy trong virtualenv sạch. Môi trường chính xác (OS, CPU, RAM, phiên bản Python) ghi trong `TEST_REPORT.md`.
- Toàn bộ dữ liệu là synthetic, không dùng dữ liệu thật.
- File test đặt ở `tests/test_*.py`; dùng `pytest.mark.parametrize` cho các ca có nhiều giá trị.

**Ký hiệu viết tắt cho các trường:**
- NN = `co_di_nguyen_nghi_ngo`
- HIT = `di_nguyen_qua_duong_hit`
- DA = `co_ton_thuong_da_niem_mac`
- HH = `co_trieu_chung_ho_hap`
- TH = `co_trieu_chung_tuan_hoan`
- TD = `co_trieu_chung_tieu_hoa_nang`
- HATT = `huyet_ap_tam_thu`, NEN = `huyet_ap_tam_thu_nen`

**Input nền B0:** `tuoi = 30`, `HATT = 120`, `NEN = null`, mọi cờ bool = `false`. Các test case chỉ ghi phần **khác** B0.

**Nền P3:** B0 + `NN = true`, `TH = true`. Thỏa R03-PV, không thỏa R02-PV vì chỉ 1/4 hệ. Dùng cho các ca ngưỡng sốc, vì chỉ cần đổi HATT là kết quả đổi giữa `PHAN_VE` và `SOC_PHAN_VE`.

**Cách ghi kết quả:** `muc_do / rule_id`. "Không hợp lệ" nghĩa là `THEO_DOI / null` với `ly_do` thuộc nhóm input không hợp lệ.

## 4. Test Cases

Mỗi dòng: mã test, mô tả, kỳ vọng, AC liên quan.

### 4.1. Input Validation

- **TC01** — Đầu vào đầy đủ 9 trường, đúng kiểu. Kỳ vọng: tiếp tục đánh giá bình thường, không bị từ chối. (AC01)
- **TC02** — Thiếu `tuoi`. Kỳ vọng: không hợp lệ. (AC03)
- **TC03** — Thiếu một trường bool bắt buộc (ví dụ `HH`). Kỳ vọng: không hợp lệ; không coi là `false`. (AC03, AC05)
- **TC04** — Vắng key `HATT` và `NEN` (không để `null`) trên nền không phản vệ. Kỳ vọng: hợp lệ; `THEO_DOI / null` do chưa đủ tiêu chí. (AC04)
- **TC05** — Trường bool nhận `"true"`, `1`, hoặc `null`. Kỳ vọng: không hợp lệ; không ép kiểu. (AC02, AC05)
- **TC06** — `tuoi = "30"` (chuỗi). Kỳ vọng: không hợp lệ. (AC02, AC05)
- **TC07** — `tuoi = True`. Kỳ vọng: không hợp lệ (bool không được coi là số). (AC05)
- **TC08** — `HATT` là `True`, `85.5` hoặc `"85"`. Kỳ vọng: không hợp lệ. (AC02, AC05)
- **TC09** — `tuoi = -1`. Kỳ vọng: không hợp lệ. (AC02)
- **TC10** — `tuoi` là `NaN`, `inf`, `-inf`. Kỳ vọng: không hợp lệ. (AC02)
- **TC11** — Thêm trường lạ `ho_ten = "Nguyen Van Test"`. Kỳ vọng: không hợp lệ; tên và giá trị trường lạ không xuất hiện trong output. (AC02, AC16)
- **TC12** — `tuoi = 30` kiểu `int` trên nền P3. Kỳ vọng: `PHAN_VE / R03-PV`. (AC02)

### 4.2. Domain Boundary

- **TC13** — Nền P3 với `tuoi = 0` và `tuoi = 120`. Kỳ vọng: hợp lệ, `PHAN_VE / R03-PV`. Với `tuoi = -0.01` và `tuoi = 120.01`: không hợp lệ. (AC02)
- **TC14** — Biên của HATT và NEN trên nền P3:
  - `HATT = 1` (NEN = null): `SOC_PHAN_VE / R-SOC`.
  - `HATT = 300` (NEN = null): `PHAN_VE / R03-PV`.
  - `NEN = 1` (HATT = 120): `PHAN_VE / R03-PV`.
  - `NEN = 300` (HATT = 120): `SOC_PHAN_VE / R-SOC`, vì 120 nhỏ hơn 70% của 300.
  - `HATT` hoặc `NEN` bằng `0` và `301`: không hợp lệ.
  - (AC02)

### 4.3. Rule Evaluation

- **TC15** — R01: `NN=false`, `DA=true`, `HH=true`. Kỳ vọng: `PHAN_VE / R01-PV`. (AC06)
- **TC16** — R01: `NN=false`, `DA=true`, `TH=true`. Kỳ vọng: `PHAN_VE / R01-PV`. (AC06)
- **TC17** — R01 âm: `NN=false`, chỉ `DA=true`. Kỳ vọng: `THEO_DOI / null`. (AC06)
- **TC18** — R01 âm: `NN=false`, `DA=false`, `HH=true`, `TH=true`. Kỳ vọng: `THEO_DOI / null`. (AC06)
- **TC19** — R02: `NN=true`, `DA=true`, `TD=true` (HH, TH = false). Kỳ vọng: `PHAN_VE / R02-PV`. (AC07)
- **TC20** — R02: `NN=true`, `HIT=true`, `DA=true`, `HH=true` (R03 không thỏa do HIT). Kỳ vọng: `PHAN_VE / R02-PV`. (AC07)
- **TC21** — R02 âm: `NN=true`, chỉ `TD=true` (1/4). Kỳ vọng: `THEO_DOI / null`. (AC07)
- **TC22** — R03: `NN=true`, `HIT=false`, chỉ `HH=true`. Kỳ vọng: `PHAN_VE / R03-PV`. (AC08)
- **TC23** — R03: `NN=true`, chỉ `TH=true`. Kỳ vọng: `PHAN_VE / R03-PV`. (AC08)
- **TC24** — R03 âm: `NN=true`, `HIT=true`, chỉ `HH=true`. Kỳ vọng: `THEO_DOI / null`. (AC08)
- **TC25** — R03 âm: `NN=false`, chỉ `TH=true`. Kỳ vọng: `THEO_DOI / null`. (AC08)
- **TC26** — Không thỏa quy tắc nào (B0, mọi cờ false). Kỳ vọng: `THEO_DOI / null`; `ly_do` nói chưa đủ tiêu chí. (AC12)
- **TC27** — R-SOC từ R01: `NN=false`, `DA=true`, `HH=true`, `HATT=80`. Kỳ vọng: `SOC_PHAN_VE / R-SOC`. (AC09)
- **TC28** — R-SOC từ R02: `NN=true`, `DA=true`, `TD=true`, `HATT=80`. Kỳ vọng: `SOC_PHAN_VE / R-SOC`. (AC09)
- **TC29** — R-SOC từ R03: `NN=true`, `HIT=false`, `HH=true`, `HATT=80`. Kỳ vọng: `SOC_PHAN_VE / R-SOC`. (AC09)
- **TC30** — Chỉ tụt HA, không thỏa Tầng 2: B0 với `HATT=80`. Kỳ vọng: `THEO_DOI / null`, vì tụt HA đơn độc không phải sốc phản vệ. (AC09)
- **TC31** — Nền P3 với `HATT = null`. Kỳ vọng: `PHAN_VE / R03-PV`, vì không đánh giá được Tầng 1. *Theo giả định Q1.* (AC04)
- **TC32** — B0 với `HATT = null`. Kỳ vọng: `THEO_DOI / null`. (AC04)

### 4.4. Rule Priority

- **TC33** — R02 và R03 cùng thỏa, không sốc: `NN=true`, `HIT=false`, `DA=true`, `HH=true`, `HATT=120`. Kỳ vọng: `PHAN_VE / R03-PV`. (AC11)
- **TC34** — 4/4 hệ cơ quan dương tính, `NN=true`, `HIT=false`, `HATT=120`. Kỳ vọng: `PHAN_VE / R03-PV`. (AC11)
- **TC35** — Cùng input TC33 nhưng `HATT=80`. Kỳ vọng: `SOC_PHAN_VE / R-SOC`. (AC10)
- **TC36** — Duyệt mọi tổ hợp cờ: R01 và (R02 hoặc R03) không bao giờ cùng kích hoạt. Kỳ vọng: luôn đúng. (AC11)

### 4.5. Boundary Cases — Ngưỡng sốc theo tuổi

Dùng nền P3. Với mỗi mốc tuổi, thử HATT ngay dưới ngưỡng (sốc) và HATT đúng bằng ngưỡng (không sốc).

- **TC37** — `tuoi = 0` và `0.99` (ngưỡng < 70). HATT 69: `SOC_PHAN_VE / R-SOC`. HATT 70: `PHAN_VE / R03-PV`. (AC09)
- **TC38** — `tuoi = 1.0` (ngưỡng < 72) và `tuoi = 5` (ngưỡng < 80). HATT 71 và 79: `SOC_PHAN_VE`. HATT 72 và 80: `PHAN_VE`. (AC09)
- **TC39** — `tuoi = 10.99` (ngưỡng < 91.98). HATT 91: `SOC_PHAN_VE`. HATT 92: `PHAN_VE`. (AC09)
- **TC40** — `tuoi = 11.0` và `17.99` (ngưỡng < 90). HATT 89: `SOC_PHAN_VE`. HATT 90: `PHAN_VE`. (AC09)
- **TC41** — `tuoi = 18`, `NEN = null` (ngưỡng < 90). HATT 89: `SOC_PHAN_VE`. HATT 90: `PHAN_VE`. (AC09)
- **TC42** — `tuoi = 30`, `NEN = 200`, giảm đúng 30%. HATT 140 (đúng 70%): `PHAN_VE`. HATT 139: `SOC_PHAN_VE`. (AC09)
- **TC43** — `tuoi = 30`, `HATT = 95`, `NEN = 140` (≥ 90 nhưng 95 < 98). Kỳ vọng: `SOC_PHAN_VE / R-SOC` do tiêu chí giảm > 30%. (AC09)
- **TC44** — `tuoi = 30`, `HATT = 100`, `NEN = null`. Kỳ vọng: `PHAN_VE / R03-PV`; thiếu NEN không bị coi là thiếu dữ liệu. (AC04)
- **TC45** — `tuoi = 15`, `HATT = 95`, `NEN = 200`. Kỳ vọng: `PHAN_VE / R03-PV`; nhóm dưới 18 tuổi bỏ qua NEN. (AC09)

### 4.6. Output Validation

- **TC46** — Cấu trúc đầu ra ở mọi nhánh (SOC, PV, THEO_DOI, không hợp lệ). Kỳ vọng: có đủ `muc_do`, `rule_id`, `ly_do`; `muc_do` thuộc ba giá trị cho phép. (AC12, AC13)
- **TC47** — Mã quy tắc trong output (tham số hóa theo TC15, 19, 22, 27). Kỳ vọng: `R01-PV`, `R02-PV`, `R03-PV`, `R-SOC` khớp quy tắc được kích hoạt. (AC14)
- **TC48** — `rule_id` ở `THEO_DOI` do chưa đủ tiêu chí và do input không hợp lệ. Kỳ vọng: đều là `null`. (AC14)
- **TC49** — `ly_do` không chứa giá trị tuổi, HATT, NEN hay trạng thái cờ triệu chứng (quét chuỗi với input có giá trị đặc trưng, ví dụ `HATT=137`). Kỳ vọng: không xuất hiện. (AC15)
- **TC50** — `ly_do` không chứa từ khóa lời khuyên điều trị (ví dụ "tiêm", "adrenalin", "điều trị", "dùng thuốc"), không rỗng, dài tối đa 200 ký tự. Kỳ vọng: đạt. (AC15, AC26)
- **TC51** — So sánh `ly_do` của input không hợp lệ với `ly_do` của "chưa đủ tiêu chí". Kỳ vọng: hai chuỗi khác nhau. (AC15)
- **TC52** — Kiểm tra PII trên toàn bộ output của các test. Kỳ vọng: không có thông tin định danh. (AC16)

### 4.7. Consistency and Contract

- **TC53** — Gọi lặp 100 lần với cùng input hợp lệ. Kỳ vọng: output giống hệt; input không bị sửa (không mutate). (AC17)
- **TC54** — Duyệt toàn bộ tổ hợp 6 cờ bool × tập tuổi/HATT/NEN đại diện, so với hàm oracle độc lập trong test (viết thẳng từ `decision-table.md`, không gọi lại code của classifier). Kỳ vọng: mọi tổ hợp khớp. (AC20, AC25)
- **TC55** — `classify()` không ném `NotImplementedError`; test dùng giá trị không trùng ID của public fixture. Kỳ vọng: đạt. (AC25)

### 4.8. Audit

- **TC56** — Mỗi lần gọi `classify()` hợp lệ. Kỳ vọng: ghi đúng 1 bản ghi gồm 4 trường `Timestamp`, `User_UUID`, `Action_Type`, `Status`, không thừa trường. (AC18)
- **TC57** — Định dạng bản ghi. Kỳ vọng: `Timestamp` là ISO 8601 UTC; `User_UUID` là UUID hợp lệ và do bên gọi cung cấp. (AC18)
- **TC58** — Quét toàn bộ bản ghi audit với input có giá trị đặc trưng. Kỳ vọng: không chứa giá trị input, triệu chứng, điểm số sức khỏe hay tên/giá trị trường lạ. (AC19)
- **TC59** — Input không hợp lệ. Kỳ vọng: vẫn ghi audit với `Status` thể hiện input không hợp lệ. (AC18)

### 4.9. Performance

- **TC60** — Warm-up tối thiểu 100 lần, sau đó đo tối thiểu 1.000 lần `classify()` (gồm ghi audit) bằng `time.perf_counter`, trộn các nhánh SOC / PV / THEO_DOI / không hợp lệ. Kỳ vọng: báo cáo p50 và p95; **p95 < 100 ms**; ghi rõ máy đo (OS, CPU, RAM, Python). (AC23)

### 4.10. Integration

- **TC61** — Clone mới, tạo venv, `pip install -r requirements.txt`, `pytest -q`. Kỳ vọng: toàn bộ test đạt. (AC21)
- **TC62** — Mở Pull Request. Kỳ vọng: CI chạy `pytest` tự động và xanh. (AC22)
- **TC63** — Kiểm tra `README.md`. Kỳ vọng: có dòng "educational/synthetic — not for clinical use". (AC24)
- **TC64** — Quét repo tìm `.env`, token, key, dữ liệu thật. Kỳ vọng: không có. (AC16)

## 5. Testing Categories

- **Functional Testing:** TC15–TC36, TC46–TC47 (các mức phân loại, rule_id, `ly_do` tương ứng).
- **Input Validation:** TC01–TC14 (missing, invalid type, out-of-domain).
- **Boundary Testing:** TC13, TC14, TC37–TC45.
- **Priority Testing:** TC33–TC36.
- **Audit Testing:** TC56–TC59 (đủ 4 trường, không ghi dữ liệu lâm sàng thô).
- **Performance Testing:** TC60 (warm-up, ≥ 1.000 lần, p50/p95).
- **Integration Testing:** TC61–TC64 (pytest từ clean checkout, CI trên Pull Request).
- **Property / Exhaustive Testing:** TC36, TC53, TC54.

## 6. Testing Method
- Unit test cho từng nhóm quy tắc, mỗi rule có ca dương tính và ít nhất một ca âm tính.
- Boundary testing cho ngưỡng tuổi (0, 0.99, 1, 10.99, 11, 17.99, 18) và HATT (ngay dưới, bằng, ngay trên ngưỡng).
- Priority testing cho trường hợp nhiều quy tắc cùng thỏa.
- Validation testing cho dữ liệu thiếu, sai kiểu, ngoài miền.
- Oracle độc lập (TC54) để chống việc test và code cùng sai theo một cách.
- Benchmark chạy bằng script riêng, kết quả ghi vào `TEST_REPORT.md`.

## 7. Entry / Exit Criteria

- **Entry:** `decision-table.md` và `REQUIREMENTS.md` đã chốt; môi trường test dựng được.
- **Exit:** mọi TC từ TC01 đến TC64 đạt; mỗi AC có ít nhất một TC (xem mục 8); p95 < 100 ms; CI xanh trên Pull Request.

## 8. Truy vết AC → Test Case

- AC01 → TC01
- AC02 → TC05–TC14
- AC03 → TC02, TC03
- AC04 → TC04, TC31, TC32, TC44
- AC05 → TC03, TC05–TC08
- AC06 → TC15–TC18
- AC07 → TC19–TC21
- AC08 → TC22–TC25
- AC09 → TC27–TC30, TC37–TC43, TC45
- AC10 → TC35
- AC11 → TC33, TC34, TC36
- AC12 → TC26, TC46
- AC13 → TC46
- AC14 → TC47, TC48
- AC15 → TC49–TC51
- AC16 → TC11, TC52, TC64
- AC17 → TC53
- AC18 → TC56, TC57, TC59
- AC19 → TC58
- AC20 → TC01–TC59 (normal, boundary, invalid, missing), TC54
- AC21 → TC61
- AC22 → TC62
- AC23 → TC60
- AC24 → TC63
- AC25 → TC54, TC55
- AC26 → TC50

## 9. Expected Outcome
- Các test case cho kết quả đúng theo bảng quyết định WAO/EAACI V1.
- Các trường hợp biên và dữ liệu thiếu được xử lý nhất quán theo chính sách ở `REQUIREMENTS.md`.
- Không có trường hợp trả về kết quả trái với thứ tự ưu tiên: R-SOC > R03-PV > R02-PV.

## 10. Điểm phụ thuộc vào xác nhận của TA

Các test case sau phụ thuộc giả định chưa được TA xác nhận (xem `REQUIREMENTS.md` mục 11); nếu TA trả lời khác, cập nhật kỳ vọng tương ứng:
- TC31 (Q1: Tầng 2 đạt nhưng HATT null).
- TC13, TC14 (Q2: miền hợp lệ của tuổi và HATT).
- TC12 (Q3: `tuoi` kiểu `int`).
- TC04 (Q4: trường nullable vắng key).
- TC11 (Q5: trường lạ).
- TC56, TC57 (Q6: nguồn của `User_UUID`).
