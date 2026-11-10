"""Bo test suite kiem thu dac ta Rule Engine Track A (Dr May Day).

Bao phu day du cac nhom ca theo yeu cau cua giang vien va Issue #15:
- 4 rule: R01-PV, R02-PV, R03-PV, R-SOC va THEO_DOI
- Boundary tuoi va HATT (+-1 tai moi ranh gioi)
- Ca giam dung 30% va tren 30% voi nguoi >= 18 tuoi
- Nhanh loai tru di nguyen qua duong hit cua R03
- Xung dot nhieu rule cung thoa (R02 + R03 -> R02-PV)
- Xu ly thieu du lieu (thieu tuoi, thieu HATT, thieu HATT nen, thieu khoa bool)
"""
import pytest
from rule_engine.classifier import classify


# ============================================================================
# 1. NHOM TEST CAC RULE CO BAN (NORMAL CASES)
# ============================================================================

def test_r01_normal():
    """R01: Khong ro di nguyen + ton thuong da + ho hap."""
    res = classify({
        "tuoi": 25.0,
        "huyet_ap_tam_thu": 120,
        "co_di_nguyen_nghi_ngo": False,
        "co_ton_thuong_da_niem_mac": True,
        "co_trieu_chung_ho_hap": True,
    })
    assert res["muc_do"] == "PHAN_VE"
    assert res["rule_id"] == "R01-PV"


def test_r02_normal():
    """R02: Co di nguyen nghi ngo + 2/4 he co quan (da + tieu hoa nang)."""
    res = classify({
        "tuoi": 30.0,
        "huyet_ap_tam_thu": 115,
        "co_di_nguyen_nghi_ngo": True,
        "co_ton_thuong_da_niem_mac": True,
        "co_trieu_chung_tieu_hoa_nang": True,
    })
    assert res["muc_do"] == "PHAN_VE"
    assert res["rule_id"] == "R02-PV"


def test_r03_normal():
    """R03: Co di nguyen da biet, khong qua duong hit + ho hap."""
    res = classify({
        "tuoi": 22.0,
        "huyet_ap_tam_thu": 110,
        "co_di_nguyen_nghi_ngo": True,
        "di_nguyen_qua_duong_hit": False,
        "co_trieu_chung_ho_hap": True,
    })
    assert res["muc_do"] == "PHAN_VE"
    assert res["rule_id"] == "R03-PV"


# ============================================================================
# 2. NHOM TEST BOUNDARY TUOI VA HUYET AP (+-1 TAI RANH GIOI)
# ============================================================================

def test_boundary_age_under_1_shock():
    """Tuoi 0.9: Nguong HATT < 70 -> HATT 69 dat soc."""
    res = classify({
        "tuoi": 0.9,
        "huyet_ap_tam_thu": 69,
        "co_di_nguyen_nghi_ngo": False,
        "co_ton_thuong_da_niem_mac": True,
        "co_trieu_chung_ho_hap": True,
    })
    assert res["muc_do"] == "SOC_PHAN_VE"
    assert res["rule_id"] == "R-SOC"


def test_boundary_age_under_1_no_shock():
    """Tuoi 0.9: HATT 70 (cham bien < 70) -> khong soc."""
    res = classify({
        "tuoi": 0.9,
        "huyet_ap_tam_thu": 70,
        "co_di_nguyen_nghi_ngo": False,
        "co_ton_thuong_da_niem_mac": True,
        "co_trieu_chung_ho_hap": True,
    })
    assert res["muc_do"] == "PHAN_VE"
    assert res["rule_id"] == "R01-PV"


def test_boundary_age_1_0_shock():
    """Tuoi 1.0: Nguong 70 + 2*1 = 72. HATT 71 dat soc."""
    res = classify({
        "tuoi": 1.0,
        "huyet_ap_tam_thu": 71,
        "co_di_nguyen_nghi_ngo": False,
        "co_ton_thuong_da_niem_mac": True,
        "co_trieu_chung_ho_hap": True,
    })
    assert res["muc_do"] == "SOC_PHAN_VE"
    assert res["rule_id"] == "R-SOC"


def test_boundary_age_1_0_no_shock():
    """Tuoi 1.0: HATT 72 (cham bien < 72) -> khong soc."""
    res = classify({
        "tuoi": 1.0,
        "huyet_ap_tam_thu": 72,
        "co_di_nguyen_nghi_ngo": False,
        "co_ton_thuong_da_niem_mac": True,
        "co_trieu_chung_ho_hap": True,
    })
    assert res["muc_do"] == "PHAN_VE"
    assert res["rule_id"] == "R01-PV"


def test_boundary_age_10_9_shock():
    """Tuoi 10.9: Nguong 70 + 2*10.9 = 91.8. HATT 91 dat soc."""
    res = classify({
        "tuoi": 10.9,
        "huyet_ap_tam_thu": 91,
        "co_di_nguyen_nghi_ngo": False,
        "co_ton_thuong_da_niem_mac": True,
        "co_trieu_chung_ho_hap": True,
    })
    assert res["muc_do"] == "SOC_PHAN_VE"
    assert res["rule_id"] == "R-SOC"


def test_boundary_age_10_9_no_shock():
    """Tuoi 10.9: HATT 92 (lon hon 91.8) -> khong soc."""
    res = classify({
        "tuoi": 10.9,
        "huyet_ap_tam_thu": 92,
        "co_di_nguyen_nghi_ngo": False,
        "co_ton_thuong_da_niem_mac": True,
        "co_trieu_chung_ho_hap": True,
    })
    assert res["muc_do"] == "PHAN_VE"
    assert res["rule_id"] == "R01-PV"


def test_boundary_age_11_0_shock():
    """Tuoi 11.0: Nguong HATT < 90. HATT 89 dat soc."""
    res = classify({
        "tuoi": 11.0,
        "huyet_ap_tam_thu": 89,
        "co_di_nguyen_nghi_ngo": False,
        "co_ton_thuong_da_niem_mac": True,
        "co_trieu_chung_ho_hap": True,
    })
    assert res["muc_do"] == "SOC_PHAN_VE"
    assert res["rule_id"] == "R-SOC"


def test_boundary_age_11_0_no_shock():
    """Tuoi 11.0: HATT 90 (cham bien < 90) -> khong soc."""
    res = classify({
        "tuoi": 11.0,
        "huyet_ap_tam_thu": 90,
        "co_di_nguyen_nghi_ngo": False,
        "co_ton_thuong_da_niem_mac": True,
        "co_trieu_chung_ho_hap": True,
    })
    assert res["muc_do"] == "PHAN_VE"
    assert res["rule_id"] == "R01-PV"


def test_boundary_age_17_9_shock():
    """Tuoi 17.9: HATT 89 dat soc (< 90)."""
    res = classify({
        "tuoi": 17.9,
        "huyet_ap_tam_thu": 89,
        "co_di_nguyen_nghi_ngo": False,
        "co_ton_thuong_da_niem_mac": True,
        "co_trieu_chung_ho_hap": True,
    })
    assert res["muc_do"] == "SOC_PHAN_VE"
    assert res["rule_id"] == "R-SOC"


def test_boundary_age_17_9_no_shock():
    """Tuoi 17.9: HATT 90 khong soc."""
    res = classify({
        "tuoi": 17.9,
        "huyet_ap_tam_thu": 90,
        "co_di_nguyen_nghi_ngo": False,
        "co_ton_thuong_da_niem_mac": True,
        "co_trieu_chung_ho_hap": True,
    })
    assert res["muc_do"] == "PHAN_VE"
    assert res["rule_id"] == "R01-PV"


# ============================================================================
# 3. NHOM TEST GIAM DUNG 30% VA TREN 30% (NGUOI LON >= 18 TUOI)
# ============================================================================

def test_adult_drop_exactly_30_percent_no_shock():
    """Nguoi lon: HATT nen 140, HATT 98 (giam dung 30% = (140-98)/140 = 0.3) -> Khong dat vi yeu cau > 30%."""
    res = classify({
        "tuoi": 25.0,
        "huyet_ap_tam_thu": 98,
        "huyet_ap_tam_thu_nen": 140,
        "co_di_nguyen_nghi_ngo": False,
        "co_ton_thuong_da_niem_mac": True,
        "co_trieu_chung_ho_hap": True,
    })
    assert res["muc_do"] == "PHAN_VE"
    assert res["rule_id"] == "R01-PV"


def test_adult_drop_over_30_percent_shock():
    """Nguoi lon: HATT nen 140, HATT 97 (giam > 30%, 97 < 140*0.7=98) -> Dat soc R-SOC."""
    res = classify({
        "tuoi": 25.0,
        "huyet_ap_tam_thu": 97,
        "huyet_ap_tam_thu_nen": 140,
        "co_di_nguyen_nghi_ngo": False,
        "co_ton_thuong_da_niem_mac": True,
        "co_trieu_chung_ho_hap": True,
    })
    assert res["muc_do"] == "SOC_PHAN_VE"
    assert res["rule_id"] == "R-SOC"


# ============================================================================
# 4. NHOM TEST NHANH LOAI TRU CUA R03 (DI NGUYEN QUA DUONG HIT)
# ============================================================================

def test_r03_inhalation_excluded():
    """R03: Di nguyen QUA duong hit -> khong thoa nhanh ho hap cua R03 -> THEO_DOI."""
    res = classify({
        "tuoi": 20.0,
        "huyet_ap_tam_thu": 110,
        "co_di_nguyen_nghi_ngo": True,
        "di_nguyen_qua_duong_hit": True,
        "co_trieu_chung_ho_hap": True,
        # Cac trieu chung khac false
        "co_ton_thuong_da_niem_mac": False,
        "co_trieu_chung_tuan_hoan": False,
        "co_trieu_chung_tieu_hoa_nang": False,
    })
    assert res["muc_do"] == "THEO_DOI"
    assert res["rule_id"] is None


def test_r03_inhalation_valid_non_hit():
    """R03: Di nguyen KHONG qua duong hit + ho hap -> thoa R03-PV."""
    res = classify({
        "tuoi": 20.0,
        "huyet_ap_tam_thu": 110,
        "co_di_nguyen_nghi_ngo": True,
        "di_nguyen_qua_duong_hit": False,
        "co_trieu_chung_ho_hap": True,
    })
    assert res["muc_do"] == "PHAN_VE"
    assert res["rule_id"] == "R03-PV"


# ============================================================================
# 5. NHOM TEST XUNG DOT NHIEU RULE (THU TU UU TIEN R01 > R02 > R03)
# ============================================================================

def test_multiple_rules_r02_and_r03():
    """Thoa ca R02 (da + ho hap >=2) va R03 (khong duong hit + ho hap) -> uu tien R02-PV."""
    res = classify({
        "tuoi": 25.0,
        "huyet_ap_tam_thu": 120,
        "co_di_nguyen_nghi_ngo": True,
        "di_nguyen_qua_duong_hit": False,
        "co_ton_thuong_da_niem_mac": True,
        "co_trieu_chung_ho_hap": True,
    })
    assert res["muc_do"] == "PHAN_VE"
    assert res["rule_id"] == "R02-PV"
    assert "dong thoi thoa R03" in res["ly_do"]


# ============================================================================
# 6. NHOM TEST KHUYET THIEU DU LIEU (A-04 POLICY THEO ISSUE #15)
# ============================================================================

def test_missing_age_returns_theo_doi():
    """Thieu tuoi -> THEO_DOI du trieu chung thoa man."""
    res = classify({
        "huyet_ap_tam_thu": 120,
        "co_di_nguyen_nghi_ngo": False,
        "co_ton_thuong_da_niem_mac": True,
        "co_trieu_chung_ho_hap": True,
    })
    assert res["muc_do"] == "THEO_DOI"
    assert res["rule_id"] is None


def test_missing_hatt_with_tier2_returns_phan_ve():
    """Thieu HATT nhung da thoa Tang 2 -> PHAN_VE (khong ha xuong THEO_DOI)."""
    res = classify({
        "tuoi": 25.0,
        "huyet_ap_tam_thu": None,
        "co_di_nguyen_nghi_ngo": False,
        "co_ton_thuong_da_niem_mac": True,
        "co_trieu_chung_ho_hap": True,
    })
    assert res["muc_do"] == "PHAN_VE"
    assert res["rule_id"] == "R01-PV"
    assert "thieu so do huyet ap tam thu" in res["ly_do"]


def test_missing_baseline_hatt_adult_above_90():
    """Nguoi lon HATT 110 >= 90 va thieu HATT nen -> PHAN_VE (R01-PV)."""
    res = classify({
        "tuoi": 30.0,
        "huyet_ap_tam_thu": 110,
        "huyet_ap_tam_thu_nen": None,
        "co_di_nguyen_nghi_ngo": False,
        "co_ton_thuong_da_niem_mac": True,
        "co_trieu_chung_ho_hap": True,
    })
    assert res["muc_do"] == "PHAN_VE"
    assert res["rule_id"] == "R01-PV"
    assert "thieu huyet ap tam thu nen" in res["ly_do"]


def test_missing_boolean_keys_safe():
    """Khong truyen cac khoa bool con lai van chay binh thuong khong gap loi."""
    res = classify({
        "tuoi": 20.0,
        "huyet_ap_tam_thu": 110,
        "co_di_nguyen_nghi_ngo": False,
        "co_ton_thuong_da_niem_mac": True,
        "co_trieu_chung_ho_hap": True,
    })
    assert res["muc_do"] == "PHAN_VE"
    assert res["rule_id"] == "R01-PV"


def test_symptoms_insufficient_returns_theo_doi():
    """Co trieu chung nhung khong du rule nao (chi co 1/4 he co quan)."""
    res = classify({
        "tuoi": 20.0,
        "huyet_ap_tam_thu": 110,
        "co_di_nguyen_nghi_ngo": True,
        "co_ton_thuong_da_niem_mac": True,
    })
    assert res["muc_do"] == "THEO_DOI"
    assert res["rule_id"] is None


def test_invalid_negative_age():
    """Tuoi am -> THEO_DOI."""
    res = classify({
        "tuoi": -5.0,
        "huyet_ap_tam_thu": 110,
        "co_di_nguyen_nghi_ngo": False,
        "co_ton_thuong_da_niem_mac": True,
        "co_trieu_chung_ho_hap": True,
    })
    assert res["muc_do"] == "THEO_DOI"
    assert res["rule_id"] is None
