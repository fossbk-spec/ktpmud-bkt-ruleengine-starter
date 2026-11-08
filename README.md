# KTPMUD BKT-1 (Track A) — Dr May Day: Rule Engine Sprint — Starter

Khung project khoi dong cho **Bai kiem tra Hackathon BKT-1 (Track A)**, mon
Ky thuat Phan mem Ung dung (KTPMUD). **Day la skeleton rong**, khong phai loi
giai mau — sinh vien fork repo nay va hien thuc `rule_engine/classifier.py`.

## Boi canh

**Dac ta chinh thuc (Data Dictionary + bang quyet dinh V1) nam o
[`docs/decision-table.md`](docs/decision-table.md) trong chinh repo nay.**
`do_an_mon_hoc.md` cua KTPMUD chi yeu cau tuan thu chuan WAO/EAACI, khong co
bang chi tiet - dung dung `docs/decision-table.md` lam nguon duy nhat.

**Khong tu suy dien nguong/quy tac lam sang moi ngoai `docs/decision-table.md`.**

## Cach chay

```bash
pip install -r requirements.txt
pytest -q
```

## MVP bat buoc

- Ham `classify()` trong `rule_engine/classifier.py` chay dung theo dac ta.
- Co bo test tu dong (`pytest`) voi it nhat 1 ca cho moi muc nguy co.
- Benchmark latency < 100ms (tu do, ghi vao bao cao np).
- Audit trail `[Timestamp, User_UUID, Action_Type, Status]` cho moi lan phan loai.

## Luu y

- Day la khung khoi dong — **khong chua bo test an dung de cham diem**
  (xem BKT-PR-2b trong de xuat KTPMUD). GV/TA se cham bang bo test rieng.
- Nop bai qua `ktpmud-project` theo dung huong dan `nop_bai.md` cua KTPMUD,
  khong tao ha tang nop bai moi.
  educational/synthetic — not for clinical use