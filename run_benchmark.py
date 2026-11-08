import time
from rule_engine.classifier import classify

def run_benchmark():
    # 1. Dữ liệu mẫu 
    patient_mock = {
        "tuoi": 25.0,
        "huyet_ap_tam_thu": 110,
        "co_di_nguyen_nghi_ngo": True,
        "co_ton_thuong_da_niem_mac": True,
        "co_trieu_chung_ho_hap": True
    }

    # 2. Warm-up: Chạy nháp vài lần để hệ thống nạp memory
    for _ in range(10):
        classify(patient_mock)

    # 3. Chạy chính thức 1000 lần và ghi nhận thời gian
    latencies = []
    for _ in range(1000):
        start = time.perf_counter()
        classify(patient_mock)
        end = time.perf_counter()
        # Đổi s->ms
        latencies.append((end - start) * 1000)

    # 4. Tính toán p50 và p95
    latencies.sort()
    p50 = latencies[int(len(latencies) * 0.50)]
    p95 = latencies[int(len(latencies) * 0.95)]

    print("=== BÁO CÁO BENCHMARK TRACK A ===")
    print(f"Tổng số vòng lặp: 1000")
    print(f"Độ trễ trung vị (p50): {p50:.4f} ms")
    print(f"Độ trễ bách phân vị 95 (p95): {p95:.4f} ms")
    
    if p95 < 100:
        print("-> TRẠNG THÁI: ĐẠT YÊU CẦU (p95 < 100 ms)")
    else:
        print("-> TRẠNG THÁI: KHÔNG ĐẠT YÊU CẦU")

if __name__ == "__main__":
    run_benchmark()