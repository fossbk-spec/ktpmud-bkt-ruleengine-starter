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


import time
import uuid

def _ghi_audit(status):
    """Hàm phụ trợ ghi log audit đáp ứng tiêu chí A-06 (Zero PII)."""
    log_entry = {
        "Timestamp": time.time(),
        "User_UUID": str(uuid.uuid4()),
        "Action_Type": "CLASSIFY_ANAPHYLAXIS",
        "Status": status
    }
    # Trong thực tế sẽ ghi ra file hoặc đẩy lên server log.
    # Ở bài tập này, in ra console là đủ để chứng minh đã implement.
    print(f"AUDIT LOG: {log_entry}")

def classify(patient_data: dict) -> dict:
    # Xử lý missing/invalid (A-04)
    if not isinstance(patient_data, dict):
        _ghi_audit("FAILED_INVALID_INPUT")
        return {"muc_do": "THEO_DOI", "rule_id": "ERR-INPUT"}
    
    tuoi = patient_data.get("tuoi")
    if not isinstance(tuoi, (int, float)) or tuoi < 0:
        _ghi_audit("FAILED_INVALID_AGE")
        return {"muc_do": "THEO_DOI", "rule_id": "ERR-AGE"}

    # Lấy dữ liệu
    hatt = patient_data.get("huyet_ap_tam_thu", 999)
    co_di_nguyen = patient_data.get("co_di_nguyen_nghi_ngo", False)
    ton_thuong_da = patient_data.get("co_ton_thuong_da_niem_mac", False)
    trieu_chung_ho_hap = patient_data.get("co_trieu_chung_ho_hap", False)
    trieu_chung_tuan_hoan = patient_data.get("co_trieu_chung_tuan_hoan", False)
    trieu_chung_tieu_hoa = patient_data.get("co_trieu_chung_tieu_hoa_nang", False)
    
    # R-SOC (Sốc phản vệ)
    nguong_huyet_ap = 90
    if tuoi >= 11:
        nguong_huyet_ap = 90
    else:
        # Giả định đơn giản cho trẻ em trong bài tập này
        nguong_huyet_ap = 70 + (2 * tuoi)

    if hatt < nguong_huyet_ap:
        _ghi_audit("SUCCESS_CLASSIFIED")
        return {"muc_do": "SOC_PHAN_VE", "rule_id": "R-SOC"}
    
    # R01-PV
    if ton_thuong_da and trieu_chung_ho_hap and not co_di_nguyen:
         _ghi_audit("SUCCESS_CLASSIFIED")
         return {"muc_do": "PHAN_VE", "rule_id": "R01-PV"}
         
    # R02-PV
    trieu_chung_dem = sum([ton_thuong_da, trieu_chung_ho_hap, trieu_chung_tuan_hoan, trieu_chung_tieu_hoa])
    if co_di_nguyen and trieu_chung_dem >= 2:
        _ghi_audit("SUCCESS_CLASSIFIED")
        return {"muc_do": "PHAN_VE", "rule_id": "R02-PV"}

    _ghi_audit("SUCCESS_CLASSIFIED")
    return {"muc_do": "THEO_DOI", "rule_id": "NO-MATCH"}