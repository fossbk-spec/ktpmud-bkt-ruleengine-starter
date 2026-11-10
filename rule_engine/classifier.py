"""
Rule Engine phân loại Phản vệ và Sốc phản vệ theo bảng quyết định WAO/EAACI V1.
Disclaimer: educational/synthetic — not for clinical use.
"""
from __future__ import annotations

from datetime import datetime, timezone
import math
from typing import Any, Dict, List, Optional
import uuid

# 9 trường chuẩn theo Data Dictionary trong docs/decision-table.md
REQUIRED_BOOL_FIELDS = (
    "co_di_nguyen_nghi_ngo",
    "di_nguyen_qua_duong_hit",
    "co_ton_thuong_da_niem_mac",
    "co_trieu_chung_ho_hap",
    "co_trieu_chung_tuan_hoan",
    "co_trieu_chung_tieu_hoa_nang",
)
OPTIONAL_BP_FIELDS = (
    "huyet_ap_tam_thu",
    "huyet_ap_tam_thu_nen",
)
KNOWN_FIELDS = frozenset(("tuoi",) + REQUIRED_BOOL_FIELDS + OPTIONAL_BP_FIELDS)

# Ngưỡng miền hợp lệ và ngưỡng lâm sàng tập trung (NFR-06)
MIN_AGE = 0.0
MAX_AGE = 120.0
MIN_BP = 1
MAX_BP = 300

AGE_INFANT_UPPER = 1.0
AGE_CHILD_UPPER = 11.0
AGE_TEEN_UPPER = 18.0

BP_THRESHOLD_INFANT = 70
BP_BASE_CHILD = 70
BP_SLOPE_CHILD = 2
BP_THRESHOLD_STANDARD = 90

DEFAULT_OPERATOR_UUID = "00000000-0000-4000-8000-000000000062"

# Chuỗi ly_do chuẩn hóa: không chứa dữ liệu lâm sàng thô, không đưa lời khuyên điều trị
LY_DO_INVALID_INPUT = (
    "Chưa đủ dữ kiện kết luận: dữ liệu đầu vào thiếu thông tin bắt buộc, "
    "sai kiểu hoặc ngoài miền giá trị hợp lệ."
)
LY_DO_NO_MATCH = (
    "Chưa đủ dữ kiện kết luận: các tiêu chí hiện tại chưa khớp quy tắc phản vệ hoặc sốc phản vệ."
)
LY_DO_RULES = {
    "R-SOC": "Kích hoạt quy tắc R-SOC: đạt tiêu chí phản vệ Tầng 2 kèm tụt huyết áp tâm thu theo tuổi.",
    "R01-PV": "Kích hoạt quy tắc R01-PV: tổn thương da-niêm mạc kèm triệu chứng hô hấp hoặc tuần hoàn.",
    "R02-PV": "Kích hoạt quy tắc R02-PV: có dị nguyên nghi ngờ kèm biểu hiện từ hai hệ cơ quan trở lên.",
    "R03-PV": "Kích hoạt quy tắc R03-PV: có dị nguyên nghi ngờ kèm triệu chứng hô hấp hoặc tuần hoàn hợp lệ.",
}

_AUDIT_TRAIL: List[Dict[str, str]] = []


def get_audit_logs() -> List[Dict[str, str]]:
    """Trả về bản sao danh sách các bản ghi audit."""
    return list(_AUDIT_TRAIL)


def clear_audit_logs() -> None:
    """Xóa danh sách audit trong bộ nhớ (phục vụ kiểm thử)."""
    _AUDIT_TRAIL.clear()


def _resolve_operator_uuid(user_uuid: Optional[str]) -> str:
    if user_uuid is None:
        return DEFAULT_OPERATOR_UUID
    try:
        return str(uuid.UUID(str(user_uuid)))
    except (ValueError, TypeError, AttributeError):
        return DEFAULT_OPERATOR_UUID


def _record_audit(user_uuid: Optional[str], status: str) -> Dict[str, str]:
    """Ghi nhận đúng 4 trường: [Timestamp, User_UUID, Action_Type, Status]."""
    entry = {
        "Timestamp": datetime.now(timezone.utc).isoformat(),
        "User_UUID": _resolve_operator_uuid(user_uuid),
        "Action_Type": "CLASSIFY",
        "Status": status,
    }
    _AUDIT_TRAIL.append(entry)
    return entry


def _validate_tuoi(clean_data: Dict[str, Any]) -> Optional[float]:
    """Kiểm tra trường 'tuoi': bắt buộc, kiểu int/float (không phải bool), trong [0, 120]."""
    if "tuoi" not in clean_data or clean_data["tuoi"] is None:
        return None
    raw_tuoi = clean_data["tuoi"]
    if isinstance(raw_tuoi, bool) or not isinstance(raw_tuoi, (int, float)):
        return None
    if math.isnan(raw_tuoi) or math.isinf(raw_tuoi):
        return None
    if raw_tuoi < MIN_AGE or raw_tuoi > MAX_AGE:
        return None
    return float(raw_tuoi)


def _extract_valid_bp(clean_data: Dict[str, Any], key: str) -> tuple[Optional[int], bool]:
    """
    Trích xuất giá trị huyết áp.
    Trả về (gia_tri_hop_le_hoac_None, co_loi_kieu_hoac_ngoai_mien).
    Nếu HATT sai kiểu hoặc ngoài miền [1, 300], trả về (None, True) để không làm hạ mức
    ca phản vệ đã thỏa Tầng 2 (theo Issue #15 và ADR-001).
    """
    if key not in clean_data or clean_data[key] is None:
        return None, False
    val = clean_data[key]
    if isinstance(val, bool) or not isinstance(val, int):
        return None, True
    if val < MIN_BP or val > MAX_BP:
        return None, True
    return val, False


def _is_hypotension(tuoi: float, hatt: Optional[int], hatt_nen: Optional[int]) -> bool:
    """Đánh giá điều kiện tụt HATT theo tuổi (Tầng 1)."""
    if hatt is None:
        return False

    if tuoi < AGE_INFANT_UPPER:
        return hatt < BP_THRESHOLD_INFANT

    if tuoi < AGE_CHILD_UPPER:
        return hatt < (BP_BASE_CHILD + BP_SLOPE_CHILD * tuoi)

    if tuoi < AGE_TEEN_UPPER:
        return hatt < BP_THRESHOLD_STANDARD

    # Người lớn (tuoi >= 18): HATT < 90 hoặc giảm > 30% so với HATT nền (10 * HATT < 7 * HATT_nen)
    if hatt < BP_THRESHOLD_STANDARD:
        return True
    if hatt_nen is not None and (10 * hatt < 7 * hatt_nen):
        return True

    return False


def classify(
    data: Any = None,
    user_uuid: Optional[str] = None,
    **kwargs: Any,
) -> Dict[str, Optional[str]]:
    """
    Phân loại nguy cơ phản vệ / sốc phản vệ theo bảng quyết định WAO/EAACI V1.
    - Thứ tự ưu tiên: R-SOC > R01-PV > R02-PV > R03-PV (Issue #15).
    - Tinh thần không hạ mức: thiếu khóa bool, trường lạ hoặc HATT ngoài miền
      không làm hạ mức khi dữ liệu hợp lệ hiện có đã thỏa trọn một quy tắc.
    """
    if data is None and kwargs:
        if "record" in kwargs and len(kwargs) == 1:
            data = kwargs["record"]
        elif "input_data" in kwargs and len(kwargs) == 1:
            data = kwargs["input_data"]
        else:
            data = kwargs

    if not isinstance(data, dict):
        _record_audit(user_uuid=user_uuid, status="INVALID_INPUT")
        return {"muc_do": "THEO_DOI", "rule_id": None, "ly_do": LY_DO_INVALID_INPUT}

    # Lọc bỏ mọi trường lạ ngoài 9 trường để bảo vệ Zero PII mà không hạ mức (ADR-001)
    clean_data = {k: v for k, v in data.items() if k in KNOWN_FIELDS}

    # 1. Kiểm tra trường bắt buộc 'tuoi' (thiếu hoặc sai kiểu/ngoài miền -> THEO_DOI)
    tuoi = _validate_tuoi(clean_data)
    if tuoi is None:
        _record_audit(user_uuid=user_uuid, status="INVALID_INPUT")
        return {"muc_do": "THEO_DOI", "rule_id": None, "ly_do": LY_DO_INVALID_INPUT}

    # 2. Kiểm tra kiểu của các trường bool có mặt (sai kiểu như "true", 1 -> không hợp lệ)
    has_missing_or_null_bool = False
    for b_key in REQUIRED_BOOL_FIELDS:
        if b_key not in clean_data or clean_data[b_key] is None:
            has_missing_or_null_bool = True
        elif not isinstance(clean_data[b_key], bool):
            _record_audit(user_uuid=user_uuid, status="INVALID_INPUT")
            return {"muc_do": "THEO_DOI", "rule_id": None, "ly_do": LY_DO_INVALID_INPUT}

    # 3. Trích xuất huyết áp (nếu ngoài miền/sai kiểu thì coi như không đo được khi xét Tầng 2)
    hatt, hatt_invalid = _extract_valid_bp(clean_data, "huyet_ap_tam_thu")
    hatt_nen, nen_invalid = _extract_valid_bp(clean_data, "huyet_ap_tam_thu_nen")

    # 4. Đánh giá 3 kịch bản Tầng 2 theo logic 3 giá trị (True / False / None)
    nn = clean_data.get("co_di_nguyen_nghi_ngo")
    hit = clean_data.get("di_nguyen_qua_duong_hit")
    da = clean_data.get("co_ton_thuong_da_niem_mac")
    hh = clean_data.get("co_trieu_chung_ho_hap")
    th = clean_data.get("co_trieu_chung_tuan_hoan")
    td = clean_data.get("co_trieu_chung_tieu_hoa_nang")

    match_r01 = (nn is False) and (da is True) and ((hh is True) or (th is True))
    organ_count = int(da is True) + int(hh is True) + int(th is True) + int(td is True)
    match_r02 = (nn is True) and (organ_count >= 2)
    match_r03 = (nn is True) and (((hit is False) and (hh is True)) or (th is True))

    # Thứ tự ưu tiên Tầng 2 theo Issue #15: R01-PV > R02-PV > R03-PV
    matched_t2_rule: Optional[str] = None
    if match_r01:
        matched_t2_rule = "R01-PV"
    elif match_r02:
        matched_t2_rule = "R02-PV"
    elif match_r03:
        matched_t2_rule = "R03-PV"

    # 5. Nếu chưa thỏa kịch bản Tầng 2 nào
    if matched_t2_rule is None:
        if has_missing_or_null_bool or hatt_invalid or nen_invalid:
            _record_audit(user_uuid=user_uuid, status="INVALID_INPUT")
            return {"muc_do": "THEO_DOI", "rule_id": None, "ly_do": LY_DO_INVALID_INPUT}
        _record_audit(user_uuid=user_uuid, status="SUCCESS")
        return {"muc_do": "THEO_DOI", "rule_id": None, "ly_do": LY_DO_NO_MATCH}

    # 6. Đã thỏa Tầng 2 -> Kiểm tra Tầng 1 (R-SOC) nếu có HATT hợp lệ
    if _is_hypotension(tuoi=tuoi, hatt=hatt, hatt_nen=hatt_nen):
        _record_audit(user_uuid=user_uuid, status="SUCCESS")
        return {
            "muc_do": "SOC_PHAN_VE",
            "rule_id": "R-SOC",
            "ly_do": LY_DO_RULES["R-SOC"],
        }

    _record_audit(user_uuid=user_uuid, status="SUCCESS")
    return {
        "muc_do": "PHAN_VE",
        "rule_id": matched_t2_rule,
        "ly_do": LY_DO_RULES[matched_t2_rule],
    }