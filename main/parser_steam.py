import requests
import time
import json
import random
import os
from requests.exceptions import RequestException, HTTPError
from datetime import datetime

# =========================
# НАСТРОЙКИ
# =========================
APPID = 730
ITEMS_LIMIT = 50
STEP = 10
STEP_PAUSE = (20, 25)
CATEGORY_PAUSE = (20, 25)
GLOBAL_PAUSE = 60
PRICE_SLEEP = (2.0, 4.0)
BATCH_SIZE = 10
MAX_RETRIES = 5

# =========================
# HEADERS
# =========================
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json,text/plain,*/*",
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8",
    "Referer": "https://steamcommunity.com/market/"
}

SEARCH_URL = "https://steamcommunity.com/market/search/render/"
PRICE_URL = "https://steamcommunity.com/market/priceoverview/"

CATEGORIES = {
    "pistols": "tag_CSGO_Type_Pistol",
    "rifles": "tag_CSGO_Type_Rifle",
    "snipers": "tag_CSGO_Type_SniperRifle",
    "smg": "tag_CSGO_Type_SMG",
    "knives": "tag_CSGO_Type_Knife",
    "cases": "tag_CSGO_Type_WeaponCase"
}

session = requests.Session()
session.headers.update(HEADERS)
PRICE_CACHE = {}

# =========================
# SAFE REQUEST
# =========================
def safe_request(url, params=None):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = session.get(url, params=params, timeout=30)
            r.raise_for_status()
            return r
        except HTTPError as e:
            status = e.response.status_code
            print(f" HTTP {status} | попытка {attempt}/{MAX_RETRIES}")
            if status == 429:
                sleep = 60 + attempt * 30
                print(f" 429 → спим {sleep} сек")
                time.sleep(sleep)
            else:
                time.sleep(10 * attempt)
        except RequestException as e:
            print(f" Сеть: {e}")
            time.sleep(10 * attempt)
    return None

# =========================
# GET PRICE
# =========================
def get_price_safe(hash_name):
    for attempt in range(1, MAX_RETRIES + 1):
        if hash_name in PRICE_CACHE:
            return PRICE_CACHE[hash_name]

        params = {
            "appid": APPID,
            "market_hash_name": hash_name,
            "currency": 5
        }

        r = safe_request(PRICE_URL, params)
        time.sleep(random.uniform(*PRICE_SLEEP))

        if r:
            try:
                data = r.json()
                if data.get("success"):
                    price = {
                        "lowest_price": data.get("lowest_price"),
                        "median_price": data.get("median_price"),
                        "volume": data.get("volume")
                    }
                else:
                    price = {"lowest_price": None, "median_price": None, "volume": None}
                PRICE_CACHE[hash_name] = price
                return price
            except Exception:
                pass

        sleep_time = 15 * attempt
        print(f" Не удалось получить цену, пауза {sleep_time} сек")
        time.sleep(sleep_time)

    return {"lowest_price": None, "median_price": None, "volume": None}

# =========================
# LOAD OR UPDATE ITEMS
# =========================
def load_or_update_items(category, tag):
    filename = f"{category}_items.json"
    items = []

    # Создаём файл, если его нет
    if not os.path.exists(filename):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump([], f)

    # Загружаем текущий файл
    with open(filename, "r", encoding="utf-8") as f:
        try:
            items = json.load(f)
        except Exception:
            items = []

    print(f"Обрабатываем категорию: {category}")

    # Если файл пустой — загружаем новые предметы
    if not items:
        start = 0
        while len(items) < ITEMS_LIMIT:
            count = min(BATCH_SIZE, ITEMS_LIMIT - len(items))
            params = {
                "appid": APPID,
                "category_730_Type[]": tag,
                "norender": 1,
                "start": start,
                "count": count
            }
            r = safe_request(SEARCH_URL, params)
            if not r:
                print(f"Не удалось загрузить предметы {category}")
                break

            results = r.json().get("results", [])
            if not results:
                break

            for item in results:
                hash_name = item["hash_name"]
                price = get_price_safe(hash_name)
                item_data = {
                    "name": item["name"],
                    "hash_name": hash_name,
                    "price": price,  # текущее состояние цены
                    "history": [],    # пустая история при первом создании
                    "image": f"https://steamcommunity-a.akamaihd.net/economy/image/{item['asset_description']['icon_url']}",
                    "url": f"https://steamcommunity.com/market/listings/730/{hash_name}"
                }
                items.append(item_data)
                if len(items) % STEP == 0:
                    pause = random.uniform(*STEP_PAUSE)
                    print(f"Пауза после {len(items)} предметов: {pause:.1f} сек")
                    time.sleep(pause)

            start += count

    else:
        # Файл есть — обновляем цены и добавляем в history
        for i, item in enumerate(items, 1):
            price = get_price_safe(item["hash_name"])
            # Обновляем поле price
            item["price"] = price
            # Добавляем запись в history
            if price["lowest_price"]:
                item.setdefault("history", []).append({
                    "time": datetime.now().isoformat(),
                    "price": price
                })
            if i % STEP == 0:
                pause = random.uniform(*STEP_PAUSE)
                print(f"Пауза после {i} предметов: {pause:.1f} сек")
                time.sleep(pause)

    # Сохраняем файл
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    print(f"{category}: сохранено {len(items)} предметов")

# =========================
# MAIN LOOP
# =========================
if __name__ == "__main__":
    print("Steam Market Collector запущен")

    while True:
        for category, tag in CATEGORIES.items():
            load_or_update_items(category, tag)
            pause = random.uniform(*CATEGORY_PAUSE)
            print(f"Пауза между категориями: {pause:.1f} сек")
            time.sleep(pause)

        print("\nКруг завершён — пауза 1 минута\n")
        time.sleep(GLOBAL_PAUSE)
