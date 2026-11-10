# BÁO CÁO TIẾN ĐỘ — PROGRESS CHECK 1 (PC-1)

* **Track:** Track A — Dr May Day: Rule Engine Sprint
* **Mã nhóm:** Nhom_62
* **Repository:** https://github.com/thaihop06/ktpmud-bkt-ruleengine-starter
* **Nhánh làm việc:** `develop`
* **Ngày cập nhật:** 11/11/2026

---

## 1. Kết quả Checkpoint 1 & Các hạng mục đã hoàn thành (Có bằng chứng)

- [x] **Duyệt Scope Checkpoint 1: Xong (Đã được chấp nhận)**
  * *Bằng chứng:* Nhận xét của Giảng viên trên PR Checkpoint 1; nhóm đã hoàn thành toàn bộ 4 mục sửa đổi bắt buộc (`❗`) ngay trong ngày 10–11/11/2026.
- [x] **Cập nhật Đặc tả, Tiêu chí nghiệm thu, Test Plan & ADR theo Issue #15: Xong**
  * *Bằng chứng:*
    - `REQUIREMENTS.md`: Đổi thứ tự ưu tiên thành `R-SOC > R01-PV > R02-PV > R03-PV` (FR-08); cập nhật nguyên tắc "không hạ mức" cho cờ bool thiếu/null, trường lạ và HATT ngoài miền; cập nhật trạng thái Q1, Q4.
    - `docs/acceptance-criteria.md`: Cập nhật AC02–AC05, AC11, AC16.
    - `docs/test-plan.md`: Cập nhật kỳ vọng `TC03`, `TC05`, `TC08`, `TC11`, `TC14`, `TC33`, `TC34` (`PHAN_VE / R02-PV`).
    - `docs/adr/ADR-001-rule-based-engine.md`: Ghi rõ phân tích đánh đổi giữa an toàn PII và rủi ro hạ mức lâm sàng.
- [x] **Hiện thực hóa Rule Engine & Audit Trail (M2): Xong**
  * *Bằng chứng:* File `rule_engine/classifier.py` hiện thực đầy đủ phân loại 2 tầng, tính giảm 30% HATT bằng số nguyên, lọc trắng 9 trường và ghi Audit Trail 4 trường `[Timestamp, User_UUID, Action_Type, Status]`.
- [x] **Bộ kiểm thử tự động TC01–TC64 & Hàm Oracle độc lập: Xong**
  * *Bằng chứng:* File `tests/test_classifier.py` chạy đạt 100% qua lệnh `pytest -q` từ clean checkout.
- [x] **Benchmark độ trễ (Latency < 100 ms): Xong**
  * *Bằng chứng:* Script `benchmarks/run_benchmark.py` và `TEST_REPORT.md` (100 lần warm-up + 1.000 lần đo, `p95 < 1 ms`).

---

## 2. Timeline dự kiến đến khi hoàn thành (11/11 – 21/11/2026)

| Mốc thời gian | Nội dung công việc | Đầu ra dự kiến |
| :--- | :--- | :--- |
| **11/11 (PC-1)** | Báo cáo tiến độ PC-1 tại lớp và xác nhận commit SHA trên Issue #17. | Hoàn thành PC-1. |
| **12/11 – 15/11 (CP2)** | Rà soát kiểm thử chéo toàn bộ tài liệu và code trước hạn 23:59 15/11/2026; Demo nội bộ 5 phút (Checkpoint 2). | Bản Checkpoint 2 hoàn chỉnh. |
| **16/11 – 18/11 (PC-2)** | Rà soát `SECURITY_PRIVACY_CHECKLIST.md`, `AI_USE.md`, `CONTRIBUTIONS.md`, `TEST_REPORT.md`; báo cáo PC-2 (18/11) trên Issue #18. | Hoàn thành PC-2. |
| **19/11 (23:59 — Freeze)** | Đóng băng mã nguồn trên fork, gắn release tag `bkt-2026-nhom62-rc1`. | Tag & Commit SHA cuối cùng. |
| **20/11 (M4 — Submit)** | Mở Pull Request mới vào `fossbk-spec/ktpmud-project` theo đúng erratum #25 (chỉ thay đổi trong `submissions/may_day_sprint_nhom62/`). | Pull Request xanh CI. |
| **21/11 (Demo/Viva)** | Demo công khai (7 phút) và vấn đáp cá nhân (8 phút). | Slide & Kịch bản demo. |

---

## 3. Câu hỏi của nhóm gửi Giảng viên / TA tại buổi PC-1

1. Không