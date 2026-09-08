import requests
import time
import os

API_URL = "http://localhost:8000/api/upload"
TEST_FILE = "test_logs/log_10mb.bfl"


def test_api_upload():
    if not os.path.exists(TEST_FILE):
        print("Файл для тесту не знайдено.")
        return

    print(f"Починаємо стрес-тест API завантаження файлу: {TEST_FILE}...")

    start_time = time.time()

    with open(TEST_FILE, "rb") as f:
        files = {"log_file": (os.path.basename(TEST_FILE), f, "application/octet-stream")}

        response = requests.post(API_URL, files=files)

    end_time = time.time()

    if response.status_code == 200:
        data = response.json()
        print(f"Успішно! ID польоту: {data.get('flight_id')}")
        print(f"Загальний час (Мережа + Парсинг + БД): {end_time - start_time:.3f} секунд")
    else:
        print(f"Помилка {response.status_code}: {response.text}")


if __name__ == "__main__":
    for i in range(3):
        print(f"\n--- Ітерація {i + 1} ---")
        test_api_upload()