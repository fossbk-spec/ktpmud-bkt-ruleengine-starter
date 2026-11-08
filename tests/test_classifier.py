"""Vi du minh hoa dinh dang test - KHONG phai bo test an dung de cham diem.
Sinh vien tu viet them test cho du cac muc do theo dac ta (docs/decision-table.md).
"""
import pytest

from rule_engine.classifier import classify


def test_missing_and_invalid_input():
    """Kiểm tra kịch bản thiếu biến và sai kiểu (Missing/Invalid)."""
    assert classify({})["muc_do"] == "THEO_DOI"
    assert classify({"tuoi": -1.5})["muc_do"] == "THEO_DOI"
    assert classify(None)["muc_do"] == "THEO_DOI"

def test_normal_r01_phan_ve():
    """Kiểm tra kịch bản thông thường (Normal): R01-PV không tụt huyết áp."""
    patient_mock = {
        "tuoi": 25.0,
        "huyet_ap_tam_thu": 110,
        "co_di_nguyen_nghi_ngo": False,
        "co_ton_thuong_da_niem_mac": True,
        "co_trieu_chung_ho_hap": True
    }
    ket_qua = classify(patient_mock)
    assert ket_qua["muc_do"] == "PHAN_VE"
    assert ket_qua["rule_id"] == "R01-PV"

def test_boundary_r_soc():
    """Kiểm tra kịch bản ranh giới (Boundary): Trẻ em vừa tròn 11 tuổi sát mốc tụt HATT."""
    patient_mock = {
        "tuoi": 11.0,
        "huyet_ap_tam_thu": 89, 
        "co_di_nguyen_nghi_ngo": True,
        "di_nguyen_qua_duong_hit": False,
        "co_trieu_chung_tuan_hoan": True 
    }
    ket_qua = classify(patient_mock)
    assert ket_qua["muc_do"] == "SOC_PHAN_VE"
    assert ket_qua["rule_id"] == "R-SOC"

def test_normal_r02_phan_ve():
    """Kiểm tra kịch bản R02-PV: Có dị nguyên và >= 2 cơ quan."""
    patient_mock = {
        "tuoi": 40.0,
        "co_di_nguyen_nghi_ngo": True,
        "co_ton_thuong_da_niem_mac": True,
        "co_trieu_chung_tieu_hoa_nang": True,
        "co_trieu_chung_ho_hap": False,
        "co_trieu_chung_tuan_hoan": False
    }
    ket_qua = classify(patient_mock)
    assert ket_qua["muc_do"] == "PHAN_VE"
    assert ket_qua["rule_id"] == "R02-PV"