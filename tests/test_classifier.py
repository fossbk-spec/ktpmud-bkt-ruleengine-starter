import copy
import math
import time
import uuid
import pytest

from rule_engine.classifier import (
    classify,
    get_audit_logs,
    clear_audit_logs,
)


@pytest.fixture(autouse=True)
def _clean_audit():
    clear_audit_logs()
    yield
    clear_audit_logs()


def make_b0(**overrides):
    base = {
        "tuoi": 30.0,
        "huyet_ap_tam_thu": 120,
        "huyet_ap_tam_thu_nen": None,
        "co_di_nguyen_nghi_ngo": False,
        "di_nguyen_qua_duong_hit": False,
        "co_ton_thuong_da_niem_mac": False,
        "co_trieu_chung_ho_hap": False,
        "co_trieu_chung_tuan_hoan": False,
        "co_trieu_chung_tieu_hoa_nang": False,
    }
    base.update(overrides)
    return base


def make_p3(**overrides):
    base = make_b0(co_di_nguyen_nghi_ngo=True, co_trieu_chung_tuan_hoan=True)
    base.update(overrides)
    return base


def test_tc01_valid_full_9_fields():
    res = classify(make_b0())
    assert res["muc_do"] == "THEO_DOI" and res["rule_id"] is None
    assert get_audit_logs()[-1]["Status"] == "SUCCESS"


def test_tc02_missing_tuoi():
    data = make_p3()
    del data["tuoi"]
    res = classify(data)
    assert res["muc_do"] == "THEO_DOI" and res["rule_id"] is None


def test_tc03_missing_bool_key_no_downgrade():
    data_satisfied = make_p3()
    del data_satisfied["co_trieu_chung_ho_hap"]
    res_ok = classify(data_satisfied)
    assert (res_ok["muc_do"], res_ok["rule_id"]) == ("PHAN_VE", "R03-PV")


def test_tc04_missing_nullable_bp_keys():
    data = make_b0()
    del data["huyet_ap_tam_thu"]
    del data["huyet_ap_tam_thu_nen"]
    res = classify(data)
    assert res["muc_do"] == "THEO_DOI" and res["rule_id"] is None


@pytest.mark.parametrize("bad_bool", ["true", 1, 0, [True]])
def test_tc05_bool_wrong_type(bad_bool):
    res = classify(make_p3(co_trieu_chung_ho_hap=bad_bool))
    assert res["muc_do"] == "THEO_DOI" and res["rule_id"] is None
    assert get_audit_logs()[-1]["Status"] == "INVALID_INPUT"


@pytest.mark.parametrize("bad_age", ["30", [10], {"tuoi": 30}])
def test_tc06_invalid_tuoi_type(bad_age):
    res = classify(make_b0(tuoi=bad_age))
    assert res["muc_do"] == "THEO_DOI" and res["rule_id"] is None
    assert get_audit_logs()[-1]["Status"] == "INVALID_INPUT"


def test_tc11_unknown_field_stripped():
    data = make_p3(ho_ten="Nguyen Van Test", cccd="012345678901")
    res = classify(data)
    assert (res["muc_do"], res["rule_id"]) == ("PHAN_VE", "R03-PV")
    assert "ho_ten" not in res["ly_do"]
    assert "012345678901" not in str(get_audit_logs()[-1])


def test_tc12_int_tuoi_accepted():
    res = classify(make_p3(tuoi=30))
    assert res["muc_do"] == "PHAN_VE" and res["rule_id"] == "R03-PV"


def test_tc15_to_tc25_rules():
    assert classify(make_b0(co_ton_thuong_da_niem_mac=True, co_trieu_chung_ho_hap=True))["rule_id"] == "R01-PV"
    assert classify(make_b0(co_ton_thuong_da_niem_mac=True, co_trieu_chung_tuan_hoan=True))["rule_id"] == "R01-PV"
    assert classify(make_b0(co_di_nguyen_nghi_ngo=True, co_ton_thuong_da_niem_mac=True, co_trieu_chung_tieu_hoa_nang=True))["rule_id"] == "R02-PV"
    assert classify(make_b0(co_di_nguyen_nghi_ngo=True, co_trieu_chung_ho_hap=True))["rule_id"] == "R03-PV"
    assert classify(make_p3())["rule_id"] == "R03-PV"


def test_tc33_tc34_priority_r02_over_r03():
    r33 = classify(make_b0(
        co_di_nguyen_nghi_ngo=True,
        di_nguyen_qua_duong_hit=False,
        co_ton_thuong_da_niem_mac=True,
        co_trieu_chung_ho_hap=True,
        huyet_ap_tam_thu=120,
    ))
    assert (r33["muc_do"], r33["rule_id"]) == ("PHAN_VE", "R02-PV")


@pytest.mark.parametrize(
    "tuoi,hatt_shock,hatt_no_shock",
    [
        (0.0, 69, 70), (0.99, 69, 70),
        (1.0, 71, 72), (5.0, 79, 80),
        (10.99, 91, 92), (11.0, 89, 90),
        (18.0, 89, 90),
    ],
)
def test_shock_boundaries(tuoi, hatt_shock, hatt_no_shock):
    assert classify(make_p3(tuoi=tuoi, huyet_ap_tam_thu=hatt_shock))["muc_do"] == "SOC_PHAN_VE"
    assert classify(make_p3(tuoi=tuoi, huyet_ap_tam_thu=hatt_no_shock))["muc_do"] == "PHAN_VE"


def test_audit_compliance():
    uid = str(uuid.uuid4())
    classify(make_p3(huyet_ap_tam_thu=75), user_uuid=uid)
    log = get_audit_logs()[-1]
    assert set(log.keys()) == {"Timestamp", "User_UUID", "Action_Type", "Status"}
    assert log["User_UUID"] == uid
    assert "75" not in str(log)


def test_performance_p95():
    s = make_p3(huyet_ap_tam_thu=80)
    for _ in range(100):
        classify(s)
    times = []
    for _ in range(1000):
        t0 = time.perf_counter()
        classify(s)
        t1 = time.perf_counter()
        times.append((t1 - t0) * 1000.0)
    times.sort()
    assert times[int(0.95 * 1000) - 1] < 100.0