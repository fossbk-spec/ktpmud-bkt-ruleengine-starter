"""
Rule Engine WAO/EAACI - khung bai tap BKT-1 (Track A), mon KTPMUD.
Sinh vien hien thuc ham classify() theo dac ta trong docs/decision-table.md.
KHONG tu dat nguong/quy tac moi chua co trong dac ta.
"""

import datetime

def classify(data: dict) -> dict:
    """
    Hàm phân loại Rule Engine chính thức cho Track A (Dr May Day).
    Thực hiện kiểm tra hợp lệ, duyệt các kịch bản Tầng 2 (R01, R02, R03) theo thứ tự ưu tiên,
    đối chiếu ngưỡng sụt giảm huyết áp theo 4 nhóm tuổi để phân loại Tầng 1 hoặc Tầng 2.
    """
    # 1. Kiểm tra tính hợp lệ của trường 'tuoi' (Policy thiếu dữ liệu theo issue #15)
    if not isinstance(data, dict) or "tuoi" not in data or data["tuoi"] is None:
        _write_audit("SYSTEM", "CLASSIFY", "FAIL_MISSING_AGE")
        return {
            "muc_do": "THEO_DOI",
            "rule_id": None,
            "ly_do": "Thiếu thông tin tuổi bắt buộc, chuyển về trạng thái theo dõi an toàn."
        }

    tuoi = data["tuoi"]
    if not isinstance(tuoi, (int, float)) or tuoi < 0 or tuoi > 150:
        _write_audit("SYSTEM", "CLASSIFY", "FAIL_INVALID_AGE")
        return {
            "muc_do": "THEO_DOI",
            "rule_id": None,
            "ly_do": "Dữ liệu tuổi không hợp lệ hoặc nằm ngoài khoảng sinh lý."
        }

    # Lấy các thông số huyết áp và triệu chứng đầu vào
    hatt = data.get("hatt", None)
    hatt_nen = data.get("hatt_nen", 120)  # Mặc định 120 mmHg nếu không truyền

    kho_tho = bool(data.get("kho_tho", False))
    tieu_hoa = bool(data.get("tieu_hoa", False))
    da_niem_mac = bool(data.get("da_niem_mac", False))
    tim_mach = bool(data.get("tim_mach", False))
    di_nguyen_hit = bool(data.get("di_nguyen_hit", False))

    # 2. Duyệt các kịch bản Tầng 2 theo thứ tự ưu tiên nghiêm ngặt: R01 > R02 > R03
    matched_rule = None
    rule_desc = ""

    # --- Kịch bản R01 ---
    if da_niem_mac and (kho_tho or tim_mach or tieu_hoa):
        matched_rule = "R01"
        rule_desc = "Kích hoạt R01: Da/niêm mạc kèm theo triệu chứng hô hấp/tuần hoàn/tiêu hóa."

    # --- Kịch bản R02 ---
    elif not matched_rule:
        so_he_co_quan = sum([int(da_niem_mac), int(kho_tho), int(tieu_hoa), int(tim_mach)])
        if so_he_co_quan >= 2:
            matched_rule = "R02"
            rule_desc = f"Kích hoạt R02: Xuất hiện đồng thời từ 2 hệ cơ quan trở lên ({so_he_co_quan} hệ)."

    # --- Kịch bản R03 ---
    elif not matched_rule and di_nguyen_hit and (kho_tho or tim_mach):
        matched_rule = "R03"
        rule_desc = "Kích hoạt R03: Tiếp xúc dị nguyên đường hít kèm triệu chứng hô hấp/tuần hoàn."

    # Nếu không thỏa mãn bất kỳ kịch bản nào -> THEO_DOI
    if not matched_rule:
        _write_audit(data.get("user_uuid", "ANONYMOUS"), "CLASSIFY", "SUCCESS_NO_MATCH")
        return {
            "muc_do": "THEO_DOI",
            "rule_id": None,
            "ly_do": "Triệu chứng đầu vào không đủ điều kiện kích hoạt các kịch bản phản vệ."
        }

    # 3. Kiểm tra điều kiện Tầng 1 (Sốc phản vệ) dựa trên ngưỡng HATT phân theo 4 nhóm tuổi
    is_shock = False

    if hatt is not None and isinstance(hatt, (int, float)):
        if tuoi < 1:
            # Nhóm 1: < 1 tuổi -> HATT < 60
            if hatt < 60:
                is_shock = True
        elif 1 <= tuoi < 11:
            # Nhóm 2: 1 - 10 tuổi -> HATT < 70 + (2 * tuổi)
            if hatt < (70 + 2 * tuoi):
                is_shock = True
        elif 11 <= tuoi < 18:
            # Nhóm 3: 11 - 17 tuổi -> HATT < 90
            if hatt < 90:
                is_shock = True
        else:
            # Nhóm 4: >= 18 tuổi -> HATT < 90 hoặc giảm > 30% so với HATT nền
            giam_30_phantram = hatt_nen * 0.3
            if hatt < 90 or (hatt_nen - hatt) > giam_30_phantram:
                is_shock = True

    # 4. Trả kết quả hoàn thiện kèm theo ly_do và ghi audit log chuẩn 4 trường
    user_uuid = data.get("user_uuid", "ANONYMOUS")
    if is_shock:
        _write_audit(user_uuid, "CLASSIFY", "SUCCESS_SHOCK")
        return {
            "muc_do": "SOC_PHAN_VE",
            "rule_id": matched_rule,
            "ly_do": f"Đạt Tầng 1 (Sốc phản vệ) do thỏa {matched_rule} và tụt huyết áp ngưỡng tuổi. Chi tiết: {rule_desc}"
        }
    else:
        _write_audit(user_uuid, "CLASSIFY", "SUCCESS_ANAPHYLAXIS")
        return {
            "muc_do": "PHAN_VE",
            "rule_id": matched_rule,
            "ly_do": f"Đạt Tầng 2 (Phản vệ). Chi tiết: {rule_desc}"
        }

def _write_audit(user_uuid: str, action_type: str, status: str):
    """
    Hàm ghi nhận audit log bắt buộc tuân thủ đúng 4 trường theo yêu cầu đề bài:
    [Timestamp, User_UUID, Action_Type, Status]
    Cam kết tuyệt đối không ghi nhận PII hay triệu chứng thô.
    """
    audit_record = [
        datetime.datetime.utcnow().isoformat(),
        str(user_uuid),
        str(action_type),
        str(status)
    ]
    # In ra luồng log tiêu chuẩn (hoặc cơ chế lưu trữ an toàn)
    print(f"[AUDIT_TRAIL] {audit_record}")