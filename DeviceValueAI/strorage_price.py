import pandas as pd
import re

# Load the cleaned dataset
df = pd.read_csv("combined_laptop_prices.csv")

# Extract storage capacity in GB
def extract_storage_capacity(storage):
    storage = str(storage).upper()

    capacities = re.findall(
        r'(\d+(?:\.\d+)?)\s*(TB|GB)',
        storage
    )

    total_gb = 0

    for value, unit in capacities:
        value = float(value)

        if unit == "TB":
            total_gb += value * 1024
        else:
            total_gb += value

    return total_gb if total_gb > 0 else None


# Identify storage type
def extract_storage_type(storage):
    storage = str(storage).upper()

    if "SSD" in storage:
        return "SSD"
    elif "HDD" in storage:
        return "HDD"
    elif "FLASH" in storage:
        return "Flash Storage"
    elif "EMMC" in storage:
        return "eMMC"
    else:
        return "Other"


# Create engineered features
df["storage_capacity_gb"] = df["storage"].apply(
    extract_storage_capacity
)

df["storage_type"] = df["storage"].apply(
    extract_storage_type
)

# Inspect the extracted features
print("Storage Feature Examples:")
print(df[["storage", "storage_capacity_gb", "storage_type"]].head(15))

print("\nStorage Type Counts:")
print(df["storage_type"].value_counts())

print("\nMissing Storage Capacities:")
print(df["storage_capacity_gb"].isna().sum())

# Save as a new file
df.to_csv("laptop_storage_features.csv", index=False)

print("\nSaved as laptop_storage_features.csv")