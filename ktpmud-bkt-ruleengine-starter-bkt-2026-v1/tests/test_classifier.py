"""Vi du minh hoa dinh dang test - KHONG phai bo test an dung de cham diem.
Sinh vien tu viet them test cho du cac muc do theo dac ta (docs/decision-table.md).
"""
import pytest

from rule_engine.classifier import classify


def test_classify_is_implemented():
    """Vi du khung: thay bang case that theo Data Dictionary khi lam bai."""
    with pytest.raises(NotImplementedError):
        classify({
            "tuoi": 0,
            "huyet_ap_tam_thu": None,
            "co_di_nguyen_nghi_ngo": False,
            "co_ton_thuong_da_niem_mac": False,
        })
