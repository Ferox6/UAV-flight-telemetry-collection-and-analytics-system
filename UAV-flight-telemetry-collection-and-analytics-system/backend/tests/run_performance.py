import time
import tracemalloc
import os
from app.services.parser import parse_log_file


TEST_FILES = [
    "tests/test_logs/log_1mb.bfl",
    "tests/test_logs/log_5mb.bfl",
    "tests/test_logs/log_10mb.bfl",
    "tests/test_logs/log_25mb.bfl",
    "tests/test_logs/log_50mb.bfl"
]


def run_performance_test():
    mem_header = "Пік пам'яті (МБ)"
    print(f"{'Файл':<20} | {'Розмір (МБ)':<12} | {'Час (с)':<10} | {'Точок':<10} | {mem_header:<15}")
    print("-" * 75)

    for file_path in TEST_FILES:
        if not os.path.exists(file_path):
            print(f"Файл {file_path} не знайдено!")
            continue

        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        tracemalloc.start()
        start_time = time.perf_counter()
        data, meta = parse_log_file(file_path)
        end_time = time.perf_counter()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        execution_time = end_time - start_time
        peak_memory_mb = peak / (1024 * 1024)
        total_points = len(data)

        print(
            f"{os.path.basename(file_path):<20} | {file_size_mb:<12.2f} | {execution_time:<10.3f} | {total_points:<10} | {peak_memory_mb:<15.2f}")


if __name__ == "__main__":
    run_performance_test()