import pandas as pd
import random

variants = pd.read_csv("data/phone_variants.csv")
clean = pd.read_csv("data/used_phones_clean.csv")

rows = []

def estimate_launch_price(brand, ram, rom):
    brand = brand.lower()

    premium = {
        "apple": 70000,
        "samsung": 55000,
        "google": 60000,
        "oneplus": 42000
    }

    mid = {
        "xiaomi": 25000,
        "vivo": 28000,
        "oppo": 28000,
        "realme": 22000,
        "motorola": 22000,
        "nothing": 32000,
        "iqoo": 33000,
        "nokia": 18000
    }

    base = premium.get(brand, mid.get(brand, 25000))
    return int(base + ram * 1200 + rom * 18)

def resale_price(launch, age, battery, condition):
    dep = max(0.30, 1 - age * 0.018)

    if condition == "Excellent":
        cond = 1.00
    elif condition == "Good":
        cond = 0.90
    elif condition == "Fair":
        cond = 0.80
    else:
        cond = 0.68

    batt = battery / 100

    val = launch * dep * cond * batt
    return max(2500, int(val))

for _ in range(2000):
    r = variants.sample(1).iloc[0]

    brand = r["brand"]
    model = r["model"]
    ram = int(r["ram"])
    storage = int(r["rom"])

    age = random.randint(1, 48)

    battery = int(max(58, min(100, 100 - age * random.uniform(0.45, 0.95))))

    if battery >= 92:
        condition = random.choice(["Excellent", "Excellent", "Good"])
    elif battery >= 80:
        condition = random.choice(["Excellent", "Good", "Good"])
    elif battery >= 68:
        condition = random.choice(["Good", "Fair"])
    else:
        condition = random.choice(["Fair", "Poor"])

    launch = estimate_launch_price(brand, ram, storage)
    price = resale_price(launch, age, battery, condition)

    rows.append([
        brand, model, ram, storage,
        age, battery, condition,
        launch, price
    ])

new_df = pd.DataFrame(rows, columns=[
    "brand", "model", "ram_gb", "storage_gb",
    "age_months", "battery_health", "condition",
    "launch_price", "price"
])

final_df = pd.concat([clean, new_df], ignore_index=True)

final_df.to_csv("data/used_phones_clean.csv", index=False)

print("Added 2000 rows.")
print("Final rows:", len(final_df))