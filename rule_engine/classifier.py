"""Rule Engine WAO/EAACI - BKT-1 (Track A), mon KTPMUD.

Hien thuc ham classify() theo dac ta ky thuat trong docs/decision-table.md
va quy dinh lam ro tai Issue #15 (fossbk-spec/ktpmud-project#15).
"""
from __future__ import annotations

from typing import Optional, Tuple, TypedDict


class PatientInput(TypedDict, total=False):
    """Input theo Data Dictionary trong docs/decision-table.md."""
    tuoi: float
    huyet_ap_tam_thu: Optional[int]
    huyet_ap_tam_thu_nen: Optional[int]
    co_di_nguyen_nghi_ngo: bool
    di_nguyen_qua_duong_hit: bool
    co_ton_thuong_da_niem_mac: bool
    co_trieu_chung_ho_hap: bool
    co_trieu_chung_tuan_hoan: bool
    co_trieu_chung_tieu_hoa_nang: bool


class ClassificationResult(TypedDict):
    muc_do: str  # "SOC_PHAN_VE" | "PHAN_VE" | "THEO_DOI"
    rule_id: Optional[str]  # "R-SOC" | "R01-PV" | "R02-PV" | "R03-PV" | None
    ly_do: str


def _kiem_tra_tut_huyet_ap(
    tuoi: float,
    hatt: Optional[int],
    hatt_nen: Optional[int],
) -> Tuple[bool, Optional[str]]:
    """Kiem tra tieu chi tut huyet ap theo tung nhom tuoi.

    Tra ve: (co_tut_ha, ghi_chu_neu_thieu_du_lieu)
    """
    if hatt is None or not isinstance(hatt, (int, float)) or hatt <= 0:
        return False, "chua danh gia duoc tieu chi soc do thieu so do huyet ap tam thu"

    if 0 <= tuoi < 1:
        return (hatt < 70), None

    if 1 <= tuoi < 11:
        nguong = 70 + 2 * tuoi
        return (hatt < nguong), None

    if 11 <= tuoi < 18:
        return (hatt < 90), None

    # Nhom tuoi >= 18
    if hatt < 90:
        return True, None

    if hatt_nen is not None and isinstance(hatt_nen, (int, float)) and hatt_nen > 0:
        # Giam > 30% nghiem ngat: hatt < 0.7 * hatt_nen
        if hatt < 0.7 * hatt_nen:
            return True, None
        return False, None

    # HATT >= 90 va thieu HATT nen -> khong danh gia duoc nhanh giam > 30%
    return False, "tieu chi giam >30% chua danh gia duoc do thieu huyet ap tam thu nen"


def _danh_gia_tang_2(patient: PatientInput) -> Optional[Tuple[str, str]]:
    """Danh gia 3 kich ban phan ve Tang 2 theo thu tu uu tien: R01 > R02 > R03."""
    co_di_nguyen = bool(patient.get("co_di_nguyen_nghi_ngo"))
    di_nguyen_hit = bool(patient.get("di_nguyen_qua_duong_hit"))
    da = bool(patient.get("co_ton_thuong_da_niem_mac"))
    ho_hap = bool(patient.get("co_trieu_chung_ho_hap"))
    tuan_hoan = bool(patient.get("co_trieu_chung_tuan_hoan"))
    tieu_hoa = bool(patient.get("co_trieu_chung_tieu_hoa_nang"))

    # Kich ban R01 - Khong ro di nguyen
    thoa_r01 = (not co_di_nguyen) and da and (ho_hap or tuan_hoan)

    # Kich ban R02 - Di nguyen nghi ngo, >= 2/4 he co quan
    so_co_quan = sum([da, ho_hap, tuan_hoan, tieu_hoa])
    thoa_r02 = co_di_nguyen and (so_co_quan >= 2)

    # Kich ban R03 - Di nguyen da biet
    thoa_r03 = co_di_nguyen and (((not di_nguyen_hit) and ho_hap) or tuan_hoan)

    # Uu tien theo Issue #15: R01 > R02 > R03
    if thoa_r01:
        return "R01-PV", "Thoa man kich ban R01 (khong ro di nguyen, ton thuong da va ho hap hoac tuan hoan)"

    if thoa_r02:
        ly_do = "Thoa man kich ban R02 (co di nguyen nghi ngo, ton thuong tu 2 he co quan tro len)"
        if thoa_r03:
            ly_do += " (dong thoi thoa R03)"
        return "R02-PV", ly_do

    if thoa_r03:
        return "R03-PV", "Thoa man kich ban R03 (di nguyen da biet khong qua duong hit kem ho hap hoac tuan hoan)"

    return None


def classify(patient: PatientInput) -> ClassificationResult:
    """Phan loai muc do theo docs/decision-table.md va Issue #15."""
    # 1. Kiem tra tinh hop le cua truong tuoi (Policy A-04)
    tuoi_raw = patient.get("tuoi")
    if tuoi_raw is None or not isinstance(tuoi_raw, (int, float)) or tuoi_raw < 0:
        return {
            "muc_do": "THEO_DOI",
            "rule_id": None,
            "ly_do": "Chua du du kien ket luan: thieu hoac sai gia tri truong tuoi",
        }

    tuoi = float(tuoi_raw)

    # 2. Danh gia Tang 2 (Phan ve)
    ket_qua_tang_2 = _danh_gia_tang_2(patient)

    # Neu khong thoa bat ky rule Tang 2 nao -> THEO_DOI
    if ket_qua_tang_2 is None:
        return {
            "muc_do": "THEO_DOI",
            "rule_id": None,
            "ly_do": "Chua du du kien: khong thoa man bat ky kich ban phan ve nao",
        }

    rule_id_t2, ly_do_t2 = ket_qua_tang_2

    # 3. Danh gia Tang 1 (Soc phan ve)
    hatt = patient.get("huyet_ap_tam_thu")
    hatt_nen = patient.get("huyet_ap_tam_thu_nen")
    co_tut_ha, ghi_chu_ha = _kiem_tra_tut_huyet_ap(tuoi, hatt, hatt_nen)

    if co_tut_ha:
        return {
            "muc_do": "SOC_PHAN_VE",
            "rule_id": "R-SOC",
            "ly_do": f"Soc phan ve: thoa man tieu chi phan ve ({rule_id_t2}) va tut huyet ap theo tuoi",
        }

    # Khong dat soc: giu nguyen muc PHAN_VE theo rule Tang 2
    ly_do_final = ly_do_t2
    if ghi_chu_ha:
        ly_do_final += f". {ghi_chu_ha.capitalize()}"

    return {
        "muc_do": "PHAN_VE",
        "rule_id": rule_id_t2,
        "ly_do": ly_do_final,
    }
