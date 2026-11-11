# PROGRESS — Nhóm 18 + 19 — Track A

- Starter: fossbk-spec/ktpmud-bkt-ruleengine-starter · tag bkt-2026-v1
- Fork: https://github.com/levanquan-070106/ktpmud-bkt-ruleengine-starter

## PC-1 — 11/11/2026

### 1.1. Tiến độ theo acceptance criteria
| Mã | Trạng thái (Chưa / Đang / Xong) | Bằng chứng (commit / CI / file) | Ghi chú |
|---|---|---|---|
| A-01 | Xong | `rule_engine/classifier.py` | In-memory rule engine, Pure Python, không phụ thuộc thư viện ngoài |
| A-02 | Xong | Commit `316e53f`, `tests/test_classifier.py` | Phân loại tất định 2 tầng (Tầng 1 Sốc, Tầng 2 R01-R03) |
| A-03 | Xong | `rule_engine/classifier.py::is_shock()` | Đầy đủ ngưỡng tuổi, HATT < 90 và giảm > 30% HATT nền |
| A-04 | Xong | `artifacts/REQUIREMENTS.md` Mục 3, `tests/test_classifier.py` | Bảng policy chi tiết từng trường khớp quy định Issue #15 |
| A-05 | Xong | `artifacts/DECISIONS.md` ADR-01, `rule_engine/classifier.py` | Thứ tự ưu tiên R01-PV > R02-PV > R03-PV khi thỏa nhiều rule |
| A-06 | Đang | Thiết kế schema `[Timestamp, User_UUID, Action_Type, Status]` | Đang tích hợp vào module log, hoàn thành trước CP2 (15/11) |
| A-07 | Đang | `tests/test_classifier.py` (24 test chạy trong 0.04s) | Đang chuẩn bị kịch bản đo benchmark 1.000 ca chạy sau warm-up |
| A-08 | Xong | `tests/test_classifier.py`, `artifacts/REQUIREMENTS.md` | Dữ liệu hoàn toàn synthetic, tuân thủ nguyên tắc Zero PII |
| A-09 | Đang | `.github/workflows/python-test.yml` | Workflow CI tự động chạy pytest trên các nhánh và PR |
| A-10 | Xong | Commit `316e53f`, `0d52ce0` | Hoàn thiện đặc tả REQUIREMENTS.md và ADR-01 DECISIONS.md |
| A-11 | Xong | `artifacts/AI_USE.md` | Ghi nhận nhật ký sử dụng AI minh bạch theo Mục 5.3 đề thi |

### 1.2. Sửa đổi bắt buộc từ Checkpoint 1
| Mục | Trạng thái | Bằng chứng |
|---|---|---|
| 1. Acceptance criteria kiểm được cho từng rule (R-SOC, R01, R02, R03, THEO_DOI) | Xong | `artifacts/REQUIREMENTS.md` Mục 4.1 (các mã `AC-R01` đến `AC-NONE`) |
| 2. Kế hoạch test bổ sung các ca biên ±1 tuổi/HATT, giảm đúng 30% vs > 30%, R03 loại trừ đường hít, nhiều rule, thiếu dữ liệu | Xong | `artifacts/REQUIREMENTS.md` Mục 5 và `tests/test_classifier.py` (24/24 ca passed) |
| 3. Bảng policy A-04 theo từng trường khớp Issue #15 (thiếu HATT thỏa Tầng 2 -> PHAN_VE; thiếu khóa bool không lỗi) | Xong | `artifacts/REQUIREMENTS.md` Mục 3 (Bảng chính sách xử lý dữ liệu thiếu và không hợp lệ) |
| 4. ADR-01 so sánh Layered Pipeline vs Table-driven/Rule data structure, bỏ văn phong y khoa | Xong | `artifacts/DECISIONS.md` (ADR-01 viết lại hoàn toàn theo tiêu chí Hợp đồng kỹ thuật phần mềm) |
| 5. Thứ tự ưu tiên rule ghi rõ trong tài liệu và dẫn link Issue #15 | Xong | `artifacts/REQUIREMENTS.md` Mục 2 và `artifacts/DECISIONS.md` Mục 1.4 |

### 1.3. Timeline dự kiến đến khi hoàn thành
| Việc | Vai trò phụ trách | Mốc (CP2 15/11 · M3 · Freeze 19/11 · M4 20/11) | Ngày dự kiến |
|---|---|---|---|
| Hiện thực module ghi Audit Trail chuẩn 4 trường (A-06) | Lead, BE-1 | M2 / CP2 | 13/11/2026 |
| Xây dựng script benchmark p95 với 1.000 ca kiểm thử (A-07) và lập TEST_REPORT.md | QA | CP2 | 14/11/2026 |
| Rà soát và hoàn thiện Checkpoint 2 trên fork nhóm | Cả nhóm | CP2 (Hạn 23:59 15/11/2026) | 15/11/2026 |
| Soạn thảo SECURITY_PRIVACY_CHECKLIST.md & CONTRIBUTIONS.md | Lead, BE-2 | M3 | 17/11/2026 |
| Tham gia kiểm tra tiến độ PC-2 tại lớp | Cả nhóm | PC-2 (9:30–11:30 18/11/2026) | 18/11/2026 |
| Đóng băng mã nguồn (Freeze) và gắn tag `bkt-2026-nhom18-19-rc1` | Lead | Freeze (Hạn 23:59 19/11/2026) | 19/11/2026 |
| Chuẩn bị slide / demo script (<= 7 phút) và nộp PR tổng kết | Cả nhóm | M4 (20/11/2026) | 20/11/2026 |

### 1.4. Rủi ro / đang vướng
- Không có vướng mắc về logic phân loại; 24/24 ca kiểm thử đã pass hoàn toàn.
- Cần hiệu chuẩn kịch bản benchmark latency để đảm bảo p95 luôn dưới 100ms khi chạy trên nhiều môi trường khác nhau.

### 1.5. Câu hỏi cho GV
- Q1: Trường `ly_do` trong kết quả của hàm `classify()` có yêu cầu định dạng văn bản theo cú pháp cố định (để hệ thống chấm tự động so khớp regex) hay chỉ cần nêu rõ căn cứ logic theo ngôn ngữ tự nhiên?

### 1.6. Phân công (alias hoặc vai trò, KHÔNG ghi họ tên/MSSV)
| Alias / vai trò | Đầu việc chính | Commit/PR tiêu biểu |
|---|---|---|
| `Lead` | Điều phối chung, kiến trúc hệ thống, rà soát ADR-01 và REQUIREMENTS.md | Commit `316e53f`, `0d52ce0` |
| `BE-1` | Hiện thực logic phân loại 2 tầng, điều kiện tụt HATT và xử lý dữ liệu thiếu A-04 | Commit `316e53f` |
| `BE-2` | Hiện thực module Audit Trail (A-06) và biên soạn tài liệu bảo mật | Đang thực hiện |
| `QA` | Thiết kế bộ test suite 24 ca biên, kịch bản benchmark và chạy kiểm thử tự động | Commit `316e53f` |

## PC-2 — 18/11/2026

### 2.1. Đối chiếu timeline PC-1
| Việc (theo bảng 1.3) | Kế hoạch | Thực tế | Lệch & lý do |
|---|---|---|---|
| | | | |

### 2.2. Tiến độ theo acceptance criteria (cập nhật toàn bộ bảng 1.1)
| Mã | Trạng thái | Bằng chứng | Ghi chú |
|---|---|---|---|
| | | | |

### 2.3. Sẵn sàng nộp bài (đề thi Mục 6)
| Deliverable | Có / Chưa | Đường dẫn |
|---|---|---|
| README.md (cài đặt / chạy / test) | | |
| REQUIREMENTS.md | | |
| DECISIONS.md / ADR | | |
| Test tự động + CI xanh | | |
| TEST_REPORT.md | | |
| SECURITY_PRIVACY_CHECKLIST.md | | |
| AI_USE.md | | |
| CONTRIBUTIONS.md | | |
| Slide / demo script ≤ 7 phút | | |

### 2.4. Việc còn lại đến Freeze (23:59 19/11)
| Việc | Vai trò phụ trách | Hạn |
|---|---|---|
| | | |

### 2.5. Rủi ro / câu hỏi cho GV
- 

## Kết quả cuối — Freeze 19/11/2026
- Tag: bkt-2026-<mã nhóm>-rc1 · SHA: 
- Trạng thái cuối từng mã AC: (cập nhật bảng 2.2 hoặc ghi "như 2.2 trừ: …")
- Những việc trong timeline chưa hoàn thành và lý do:
