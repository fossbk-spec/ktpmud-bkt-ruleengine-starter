# Bảng quyết định WAO/EAACI — Đề bài Track A (V1, KTPMUD Hack Marathon 2026)

> Phạm vi V1: Sốc phản vệ + Phản vệ (đúng yêu cầu "Rule Engine cảnh báo phản
> vệ" của `do_an_mon_hoc.md`). Dựa trên tiêu chí WAO 2020 (Cardona et al.,
> đã trích dẫn trong sách KTPMUD Chương 9) — là bảng V1 dùng cho kỳ thi năm
> nay, có thể được tinh chỉnh thêm ở các khoá sau.

## Data Dictionary

| Trường | Kiểu | Ghi chú |
|---|---|---|
| `tuoi` | float (năm) | Cho phép số lẻ (vd 0.5 = 6 tháng tuổi) |
| `huyet_ap_tam_thu` | int \| null | mmHg, null nếu không đo được |
| `huyet_ap_tam_thu_nen` | int \| null | mmHg, chỉ cần khi `tuoi >= 18` và muốn dùng tiêu chí giảm 30% |
| `co_di_nguyen_nghi_ngo` | bool | Có tiếp xúc/nghi ngờ thức ăn, thuốc, côn trùng đốt, hoặc tác nhân khác |
| `di_nguyen_qua_duong_hit` | bool | Tác nhân hít vào (ảnh hưởng kịch bản R03) |
| `co_ton_thuong_da_niem_mac` | bool | Phù mạch / sẩn phù / ban dát sẩn |
| `co_trieu_chung_ho_hap` | bool | Khó thở / khò khè / khàn giọng / tiếng rít / ngừng thở |
| `co_trieu_chung_tuan_hoan` | bool | Tụt HA-sốc / tím tái / ngất |
| `co_trieu_chung_tieu_hoa_nang` | bool | Đau bụng quặn thắt hoặc nôn ≥2 lần |

**Zero PII:** input chỉ gồm các trường trên — không được thêm tên/CCCD/SĐT/
địa chỉ hay bất kỳ trường định danh nào.

## Tầng 1 — Sốc phản vệ (ưu tiên cấp cứu tối khẩn)

**Điều kiện:** đạt tiêu chí Phản vệ ở Tầng 2 (bất kỳ 1 trong 3 kịch bản)
**VÀ** tụt huyết áp tâm thu theo tuổi:

| Nhóm tuổi | Ngưỡng tụt huyết áp tâm thu (HATT) |
|---|---|
| 0 – <1 tuổi | HATT < 70 mmHg |
| 1 – <11 tuổi | HATT < 70 + 2×tuổi (mmHg) |
| 11 – <18 tuổi | HATT < 90 mmHg |
| ≥18 tuổi | HATT < 90 mmHg **hoặc** giảm > 30% so với `huyet_ap_tam_thu_nen` |

## Tầng 2 — Phản vệ (3 kịch bản, chỉ cần khớp 1)

| Kịch bản | Điều kiện |
|---|---|
| **R01 — Không rõ dị nguyên** | `co_di_nguyen_nghi_ngo = false` **VÀ** `co_ton_thuong_da_niem_mac = true` **VÀ** (`co_trieu_chung_ho_hap = true` **HOẶC** `co_trieu_chung_tuan_hoan = true`) |
| **R02 — Dị nguyên nghi ngờ, ≥2/4 hệ cơ quan** | `co_di_nguyen_nghi_ngo = true` **VÀ** tổng số (`co_ton_thuong_da_niem_mac`, `co_trieu_chung_ho_hap`, `co_trieu_chung_tuan_hoan`, `co_trieu_chung_tieu_hoa_nang`) là `true` ≥ 2 |
| **R03 — Dị nguyên đã biết** | `co_di_nguyen_nghi_ngo = true` **VÀ** ((`di_nguyen_qua_duong_hit = false` **VÀ** `co_trieu_chung_ho_hap = true`) **HOẶC** `co_trieu_chung_tuan_hoan = true`) |

Nếu không khớp Tầng 1 lẫn Tầng 2 → kết quả **`THEO_DOI`** (không phải một
mức nguy cơ — là trạng thái "chưa đủ dữ kiện kết luận", bao gồm cả trường
hợp thiếu trường `tuoi`).

## Output bắt buộc

```json
{ "muc_do": "SOC_PHAN_VE" | "PHAN_VE" | "THEO_DOI",
  "rule_id": "R-SOC" | "R01-PV" | "R02-PV" | "R03-PV" | null,
  "ly_do": "chuỗi giải thích ngắn, không chứa dữ liệu lâm sàng thô" }
```

## Lưu ý về nguồn

Bảng này tổng hợp từ (1) ví dụ WAO-1/WAO-3b có trích dẫn nguồn WAO 2020 thật
trong sách KTPMUD, và (2) một rule engine tham khảo độc lập. Đây là V1 dùng
cho kỳ thi năm nay — không coi là chuẩn y khoa tuyệt đối, chỉ là contract kỹ
thuật đã khoá cho bài thi. Không tự ý đổi ngưỡng/thêm quy tắc ngoài bảng này.
