# KTPMUD BKT-1 (Track A) — Dr May Day: Rule Engine Sprint (Nhóm 62)

> **Disclaimer:** `educational/synthetic — not for clinical use`.  
> Dự án này chỉ phục vụ mục đích học tập và kiểm thử với dữ liệu giả lập (synthetic), tuyệt đối không sử dụng cho chẩn đoán hay điều trị lâm sàng thực tế.

## 1. Giới thiệu
Module Rule Engine độc lập (`rule_engine/classifier.py`) phân loại nguy cơ phản vệ theo bảng quyết định WAO/EAACI V1 tại [`docs/decision-table.md`](docs/decision-table.md) và hướng dẫn tại Issue #15 (`R-SOC > R01-PV > R02-PV > R03-PV`) thành 3 mức:
- `SOC_PHAN_VE` (`rule_id = "R-SOC"`)
- `PHAN_VE` (`rule_id = "R01-PV" | "R02-PV" | "R03-PV"`)
- `THEO_DOI` (`rule_id = null`)

## 2. Cài đặt và Chạy kiểm thử từ Clean Checkout

```bash
python -m venv .venv
# Kích hoạt môi trường ảo trên Windows:
.venv\Scripts\activate
# Hoặc trên macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
pytest -q