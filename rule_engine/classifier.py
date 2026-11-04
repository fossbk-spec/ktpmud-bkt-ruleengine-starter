"""Rule Engine WAO/EAACI - khung bai tap BKT-1 (Track A), mon KTPMUD.

Sinh vien hien thuc ham classify() theo dac ta trong docs/decision-table.md.
KHONG tu dat nguong/quy tac moi chua co trong dac ta.
"""
from __future__ import annotations

from typing import Optional, TypedDict


class PatientInput(TypedDict, total=False):
    """Input theo dung Data Dictionary trong docs/decision-table.md."""
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
    muc_do: str  # "SOC_PHAN_VE" | "PHAN_VE" | "THEO_DOI" - dung dung nhan theo docs/decision-table.md
    rule_id: Optional[str]  # "R-SOC" | "R01-PV" | "R02-PV" | "R03-PV" | None
    ly_do: str


def classify(patient: PatientInput) -> ClassificationResult:
    """Phan loai muc do theo docs/decision-table.md.

    TODO (sinh vien): hien thuc dung logic theo Tang 1 (Soc phan ve) va
    Tang 2 (Phan ve, 3 kich ban R01/R02/R03) trong dac ta.
    """
    raise NotImplementedError("Sinh vien hien thuc ham nay theo docs/decision-table.md")
