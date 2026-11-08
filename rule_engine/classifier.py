"""Rule Engine WAO/EAACI - khung bai tap BKT-1 (Track A), mon KTPMUD.

Sinh vien hien thuc ham classify() theo dac ta trong docs/decision-table.md.
KHONG tu dat nguong/quy tac moi chua co trong dac ta.
"""
from __future__ import annotations
from typing import Optional, TypedDict
import datetime
import uuid

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
    muc_do: str 
    rule_id: Optional[str]  
    ly_do: str


def _ghi_audit(action_type: str, status: str) -> None:
    """Ghi audit trail theo tieu chi A-06. KHONG log du lieu lam sang."""
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    user_uuid = str(uuid.uuid4())
    print(f"[{timestamp}, {user_uuid}, {action_type}, {status}]")


def classify(patient: PatientInput) -> ClassificationResult:
    """Phan loai muc do theo docs/decision-table.md."""
    if not isinstance(patient, dict):
        _ghi_audit("CLASSIFY_EVAL", "ERROR_INVALID_INPUT")
        return {"muc_do": "THEO_DOI", "rule_id": None, "ly_do": "Input không hợp lệ"}

    tuoi = patient.get("tuoi")
    if tuoi is None or not isinstance(tuoi, (int, float)) or tuoi < 0:
        _ghi_audit("CLASSIFY_EVAL", "MISSING_OR_INVALID_AGE")
        return {"muc_do": "THEO_DOI", "rule_id": None, "ly_do": "Thiếu dữ kiện tuổi để đánh giá"}
    hatt = patient.get("huyet_ap_tam_thu")
    hatt_nen = patient.get("huyet_ap_tam_thu_nen")
    
    di_nguyen = patient.get("co_di_nguyen_nghi_ngo", False)
    di_nguyen_hit = patient.get("di_nguyen_qua_duong_hit", False)
    da_niem_mac = patient.get("co_ton_thuong_da_niem_mac", False)
    ho_hap = patient.get("co_trieu_chung_ho_hap", False)
    tuan_hoan = patient.get("co_trieu_chung_tuan_hoan", False)
    tieu_hoa = patient.get("co_trieu_chung_tieu_hoa_nang", False)
    tut_huyet_ap = False
    if hatt is not None:
        if tuoi < 1.0:
            tut_huyet_ap = (hatt < 70)
        elif 1.0 <= tuoi < 11.0:
            tut_huyet_ap = (hatt < 70 + 2 * tuoi)
        elif 11.0 <= tuoi < 18.0:
            tut_huyet_ap = (hatt < 90)
        else:  # >= 18 tuoi
            if hatt < 90:
                tut_huyet_ap = True
            elif hatt_nen is not None and hatt_nen > 0:
                # Giam > 30% so voi huyet ap nen
                if (hatt_nen - hatt) > (0.3 * hatt_nen):
                    tut_huyet_ap = True
    rule_matched = None
    if (not di_nguyen) and da_niem_mac and (ho_hap or tuan_hoan):
        rule_matched = "R01-PV"
    if not rule_matched:
        so_trieu_chung = sum([da_niem_mac, ho_hap, tuan_hoan, tieu_hoa])
        if di_nguyen and so_trieu_chung >= 2:
            rule_matched = "R02-PV"
    if not rule_matched:
        if di_nguyen and ((not di_nguyen_hit and ho_hap) or tuan_hoan):
            rule_matched = "R03-PV"
    if rule_matched:
        _ghi_audit("CLASSIFY_EVAL", "SUCCESS")
        if tut_huyet_ap:
            return {
                "muc_do": "SOC_PHAN_VE", 
                "rule_id": "R-SOC", 
                "ly_do": f"Thỏa mãn kịch bản {rule_matched} kết hợp tụt huyết áp theo tuổi"
            }
        else:
            return {
                "muc_do": "PHAN_VE", 
                "rule_id": rule_matched, 
                "ly_do": f"Thỏa mãn kịch bản {rule_matched} của chuẩn WAO"
            }
    _ghi_audit("CLASSIFY_EVAL", "SUCCESS")
    return {
        "muc_do": "THEO_DOI", 
        "rule_id": None, 
        "ly_do": "Chưa đủ dữ kiện kết luận phản vệ theo WAO 2020"
    }