"""
Script đo hiệu năng Rule Engine (TC60 / AC23 / A-10).
Chạy 100 lần warm-up và 1.000 lần đo chính thức bằng time.perf_counter.
"""
import platform
import statistics
import sys
import time
from pathlib import Path

# Tự động thêm thư mục gốc dự án vào đường dẫn tìm kiếm của Python
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rule_engine.classifier import classify, clear_audit_logs

WARMUP_RUNS = 100
BENCHMARK_RUNS = 1000

SAMPLES = [
    {
        "tuoi": 30.0,
        "huyet_ap_tam_thu": 80,
        "huyet_ap_tam_thu_nen": None,
        "co_di_nguyen_nghi_ngo": True,
        "di_nguyen_qua_duong_hit": False,
        "co_ton_thuong_da_niem_mac": False,
        "co_trieu_chung_ho_hap": False,
        "co_trieu_chung_tuan_hoan": True,
        "co_trieu_chung_tieu_hoa_nang": False,
    },
    {
        "tuoi": 25.0,
        "huyet_ap_tam_thu": 120,
        "huyet_ap_tam_thu_nen": None,
        "co_di_nguyen_nghi_ngo": False,
        "di_nguyen_qua_duong_hit": False,
        "co_ton_thuong_da_niem_mac": True,
        "co_trieu_chung_ho_hap": True,
        "co_trieu_chung_tuan_hoan": False,
        "co_trieu_chung_tieu_hoa_nang": False,
    },
    {
        "tuoi": 40.0,
        "huyet_ap_tam_thu": 120,
        "huyet_ap_tam_thu_nen": None,
        "co_di_nguyen_nghi_ngo": False,
        "di_nguyen_qua_duong_hit": False,
        "co_ton_thuong_da_niem_mac": False,
        "co_trieu_chung_ho_hap": False,
        "co_trieu_chung_tuan_hoan": False,
        "co_trieu_chung_tieu_hoa_nang": False,
    },
    {"tuoi": "invalid_input"},
]


def main() -> None:
    clear_audit_logs()
    for i in range(WARMUP_RUNS):
        classify(SAMPLES[i % len(SAMPLES)])

    clear_audit_logs()
    latencies_ms = []
    for i in range(BENCHMARK_RUNS):
        sample = SAMPLES[i % len(SAMPLES)]
        t0 = time.perf_counter()
        classify(sample)
        t1 = time.perf_counter()
        latencies_ms.append((t1 - t0) * 1000.0)

    latencies_ms.sort()
    p50 = statistics.median(latencies_ms)
    p95 = latencies_ms[int(0.95 * BENCHMARK_RUNS) - 1]

    print("=== BENCHMARK REPORT (Nhom 62) ===")
    print(f"OS: {platform.system()} {platform.release()} | Python: {sys.version.split()[0]}")
    print(f"Warm-up: {WARMUP_RUNS} runs | Measured: {BENCHMARK_RUNS} runs")
    print(f"p50 latency: {p50:.4f} ms")
    print(f"p95 latency: {p95:.4f} ms")
    assert p95 < 100.0, f"p95 ({p95:.4f} ms) vuot nguong 100 ms!"
    print("Result: PASS (p95 < 100 ms)")


if __name__ == "__main__":
    main()