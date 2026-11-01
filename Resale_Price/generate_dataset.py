# generate_dataset.py
# Creates a realistic 5000-row used smartphone resale dataset for India-focused ML training

import os
import pandas as pd
import random
from datetime import datetime

random.seed(42)

rows = []

# ---------------------------------------------------
# Brand / Model Catalog
# base_price = approximate launch price in INR
# ---------------------------------------------------

catalog = {
    "Apple": [
        ("iPhone 17 Pro Max", 169900), ("iPhone 17 Pro", 144900), ("iPhone 17 Plus", 99900), ("iPhone 17", 89900),
        ("iPhone 16 Pro Max", 159900), ("iPhone 16 Pro", 134900), ("iPhone 16 Plus", 89900), ("iPhone 16", 79900),
        ("iPhone 15 Pro Max", 159900), ("iPhone 15 Pro", 134900), ("iPhone 15 Plus", 89900), ("iPhone 15", 79900),
        ("iPhone 14 Pro Max", 139900), ("iPhone 14 Pro", 129900), ("iPhone 14 Plus", 89900), ("iPhone 14", 79900),
        ("iPhone 13 Pro Max", 129000), ("iPhone 13 Pro", 119900), ("iPhone 13 Mini", 69900), ("iPhone 13", 79900),
        ("iPhone 12 Pro Max", 129900), ("iPhone 12 Pro", 119000), ("iPhone 12 Mini", 69900), ("iPhone 12", 79900),
        ("iPhone 11 Pro Max", 109900), ("iPhone 11 Pro", 99900), ("iPhone 11", 64900),
        ("iPhone XS Max", 109900), ("iPhone XS", 99900), ("iPhone XR", 76900), ("iPhone X", 89000),
        ("iPhone SE 2022", 43900), ("iPhone SE 2020", 42500)
    ],
    "Samsung": [
        ("Galaxy S24 Ultra", 129999), ("Galaxy S24+", 99999), ("Galaxy S24", 79999),
        ("Galaxy S23 Ultra", 124999), ("Galaxy S23 FE", 59999), ("Galaxy S22 Ultra", 109999),
        ("Galaxy Z Fold 5", 154999), ("Galaxy Z Flip 5", 99999), ("Galaxy A55", 39999),
        ("Galaxy A35", 30999), ("Galaxy M55", 26999), ("Galaxy F54", 29999), ("Galaxy Note 20 Ultra", 104999)
    ],
    "Xiaomi": [
        ("Xiaomi 14 Ultra", 99999), ("Xiaomi 14", 69999), ("Xiaomi 13 Pro", 79999),
        ("Redmi Note 13 Pro+", 31999), ("Redmi Note 13 Pro", 25999), ("Redmi Note 12 Pro", 23999),
        ("Poco F6", 29999), ("Poco X6 Pro", 25999), ("Poco M6 Pro", 14999), ("Xiaomi Pad 6", 26999)
    ],
    "OnePlus": [
        ("OnePlus 12", 64999), ("OnePlus 12R", 39999), ("OnePlus 11", 56999), ("OnePlus 11R", 37999),
        ("OnePlus 10 Pro", 61999), ("OnePlus Nord 4", 29999), ("OnePlus Nord CE 4", 24999), ("OnePlus Open", 139999)
    ],
    "Google": [
        ("Pixel 9 Pro XL", 124999), ("Pixel 9", 79999), ("Pixel 8 Pro", 106999), ("Pixel 8", 75999),
        ("Pixel 8a", 52999), ("Pixel 7 Pro", 84999), ("Pixel 7a", 43999), ("Pixel 6a", 29999)
    ],
    "Vivo": [
        ("Vivo X100 Pro", 89999), ("Vivo X90", 59999), ("Vivo V30 Pro", 41999), ("Vivo V29", 32999),
        ("Vivo T3", 19999), ("Vivo Y200", 21999)
    ],
    "Oppo": [
        ("Oppo Find X7 Ultra", 74999), ("Oppo Reno 11 Pro", 37999), ("Oppo F25 Pro", 23999), ("Oppo A79", 19999)
    ],
    "Realme": [
        ("Realme GT 6T", 30999), ("Realme 12 Pro+", 29999), ("Realme 11 Pro", 23999), ("Realme Narzo 70 Pro", 19999)
    ],
    "Motorola": [
        ("Moto Edge 50 Ultra", 54999), ("Moto Edge 50 Pro", 31999), ("Moto Razr 40 Ultra", 89999), ("Moto G85", 17999)
    ],
    "Nothing": [
        ("Nothing Phone 2", 44999), ("Nothing Phone 1", 29999), ("Nothing Phone 2a", 23999)
    ],
    "IQOO": [
        ("IQOO 12", 52999), ("IQOO Neo 9 Pro", 35999), ("IQOO Z9", 19999)
    ],
    "Nokia": [
        ("Nokia G42 5G", 12999), ("Nokia X30", 36999), ("Nokia G21", 12499)
    ]
}

brand_weights = {
    "Samsung": 350, "Apple": 300, "Xiaomi": 280, "OnePlus": 200,
    "Realme": 200, "Vivo": 150, "Oppo": 150, "Google": 100,
    "Motorola": 100, "Nothing": 60, "IQOO": 60, "Nokia": 50
}

conditions = ["Excellent", "Good", "Fair", "Poor"]
condition_weights = [0.35, 0.40, 0.18, 0.07]

# ---------------------------------------------------
# Helper functions
# ---------------------------------------------------

def choose_specs(price):
    if price >= 100000:
        ram = random.choice([12, 16, 24]) # Ultra-premium
        storage = random.choice([256, 512, 1024])
    elif price >= 70000:
        ram = random.choice([8, 12, 16])
        storage = random.choice([128, 256, 512])
    elif price >= 35000:
        ram = random.choice([6, 8, 12])
        storage = random.choice([128, 256])
    elif price >= 18000:
        ram = random.choice([6, 8])
        storage = random.choice([64, 128, 256])
    else:
        ram = random.choice([4, 6])
        storage = random.choice([64, 128])
    return ram, storage


def resale_price(launch_price, age, battery, condition, brand):
    # monthly depreciation
    price = launch_price * (0.97 ** age)

    # battery effect
    if battery < 80:
        price *= 0.88
    elif battery < 90:
        price *= 0.95

    # condition effect
    if condition == "Excellent":
        price *= 1.00
    elif condition == "Good":
        price *= 0.92
    elif condition == "Fair":
        price *= 0.80
    else:
        price *= 0.65

    # brand retention
    if brand == "Apple":
        price *= 1.18
    elif brand == "Samsung":
        price *= 1.05
    elif brand == "Google":
        price *= 1.10
    elif brand in ["OnePlus", "Nothing"]:
        price *= 1.03
    elif brand in ["Xiaomi", "Realme", "IQOO"]:
        price *= 0.96
    elif brand in ["Vivo", "Oppo", "Motorola"]:
        price *= 0.94
    elif brand == "Nokia":
        price *= 0.92

    # noise
    noise = random.uniform(0.95, 1.05)
    price *= noise

    return max(3000, round(price, -2))


# ---------------------------------------------------
# Generate 10000 rows
# ---------------------------------------------------

brand_pool = []
for b, count in brand_weights.items():
    brand_pool.extend([b] * count)

for _ in range(10000):
    brand = random.choice(brand_pool)
    model, launch_price = random.choice(catalog[brand])

    ram, storage = choose_specs(launch_price)

    age_months = random.randint(1, 48)
    battery_health = max(55, min(100, int(random.gauss(95 - age_months * 0.6, 6))))

    condition = random.choices(conditions, weights=condition_weights)[0]

    price = resale_price(
        launch_price,
        age_months,
        battery_health,
        condition,
        brand
    )

    rows.append({
        "brand": brand,
        "model": model,
        "ram_gb": ram,
        "storage_gb": storage,
        "age_months": age_months,
        "battery_health": battery_health,
        "condition": condition,
        "launch_price": launch_price,
        "price": price
    })

# ---------------------------------------------------
# Save CSV
# ---------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)
SAVE_PATH = os.path.join(DATA_DIR, "used_phones_clean.csv")

df = pd.DataFrame(rows)
df.to_csv(SAVE_PATH, index=False)

print(f"Created {SAVE_PATH} with {len(df)} rows")