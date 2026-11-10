from rule_engine.classifier import classify

def run_demo():
    print("=== DEMO RULE ENGINE TRACK A - NHÓM 49 ===")
    
    # Ca 1: Sốc phản vệ (R-SOC)
    ca_1 = {
        "tuoi": 11.0, "huyet_ap_tam_thu": 89, 
        "co_di_nguyen_nghi_ngo": True, "di_nguyen_qua_duong_hit": False,
        "co_trieu_chung_tuan_hoan": True
    }
    print("\n[Ca 1] Trẻ 11 tuổi, HA 89, có dị nguyên, có triệu chứng tuần hoàn:")
    print(f"-> Kết quả: {classify(ca_1)}")

    # Ca 2: Phản vệ (R01-PV)
    ca_2 = {
        "tuoi": 25.0, "huyet_ap_tam_thu": 110,
        "co_di_nguyen_nghi_ngo": False, "co_ton_thuong_da_niem_mac": True,
        "co_trieu_chung_ho_hap": True
    }
    print("\n[Ca 2] 25 tuổi, HA bình thường, không rõ dị nguyên, tổn thương da & hô hấp:")
    print(f"-> Kết quả: {classify(ca_2)}")

    # Ca 3: Lỗi đầu vào (Missing/Invalid)
    ca_3 = {"tuoi": -5}
    print("\n[Ca 3] Bệnh nhân nhập sai tuổi (âm):")
    print(f"-> Kết quả: {classify(ca_3)}")

if __name__ == "__main__":
    run_demo()