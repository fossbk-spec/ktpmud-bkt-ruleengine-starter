import pytest
from rule_engine.classifier import classify

def test_classify_missing_age():
    """Kiểm tra thiếu trường tuổi -> Trả về THEO_DOI."""
    data = {"hatt": 100}
    result = classify(data)
    assert result["muc_do"] == "THEO_DOI"
    assert result["rule_id"] is None

def test_classify_normal_r02_phan_ve():
    """Kiểm tra kịch bản R02 (>= 2 hệ cơ quan, không có da niêm mạc để tránh R01) -> Trả về PHAN_VE."""
    data = {
        "tuoi": 25,
        "hatt": 110,
        "da_niem_mac": False,  # Để False để không bị nhận nhầm sang R01
        "kho_tho": True,       # Hệ hô hấp
        "tieu_hoa": True,      # Hệ tiêu hóa (Tổng = 2 hệ cơ quan -> Thỏa mãn R02)
        "tim_mach": False,
        "di_nguyen_hit": False
    }
    result = classify(data)
    assert result["muc_do"] == "PHAN_VE"
    assert result["rule_id"] == "R02"
    assert "ly_do" in result

def test_classify_boundary_adult_shock():
    """Kiểm tra ranh giới tuổi trưởng thành (>=18) và tụt huyết áp > 30% -> SỐC PHẢN VỆ."""
    data = {
        "tuoi": 18,
        "hatt": 80,       # Dưới mức 90
        "hatt_nen": 130,  # Giảm hơn 30% (130 - 80 = 50 > 39)
        "da_niem_mac": True,
        "tim_mach": True
    }
    result = classify(data)
    assert result["muc_do"] == "SOC_PHAN_VE"
    assert result["rule_id"] in ["R01", "R02", "R03"]

def test_classify_no_match_theo_doi():
    """Kiểm tra trường hợp không đủ điều kiện -> THEO_DOI."""
    data = {
        "tuoi": 10,
        "hatt": 100,
        "da_niem_mac": False,
        "kho_tho": False
    }
    result = classify(data)
    assert result["muc_do"] == "THEO_DOI"