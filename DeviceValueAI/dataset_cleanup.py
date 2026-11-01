import pandas as pd
from pathlib import Path

# ============================================================
# 1. FILE PATHS
# ============================================================

project_dir = Path(__file__).resolve().parent

dataset1_path = project_dir / "laptop_price - dataset.csv"
dataset2_path = project_dir / "laptops.csv"

output_path = project_dir / "combined_laptop_prices.csv"


# ============================================================
# 2. LOAD DATASETS
# ============================================================

df1 = pd.read_csv(dataset1_path)
df2 = pd.read_csv(dataset2_path)

print("Dataset 1 shape:", df1.shape)
print("Dataset 2 shape:", df2.shape)

print("\nDataset 1 columns:")
print(df1.columns.tolist())

print("\nDataset 2 columns:")
print(df2.columns.tolist())


# ============================================================
# 3. STANDARDIZE COLUMN NAMES
# ============================================================

df1.columns = df1.columns.str.strip()
df2.columns = df2.columns.str.strip()


# ============================================================
# 4. RENAME COLUMNS TO COMMON NAMES
# ============================================================

# -------------------------
# Dataset 1
# -------------------------

rename_df1 = {
    "Company": "brand",
    "Product": "model",
    "TypeName": "device_type",
    "Inches": "screen_size",
    "ScreenResolution": "screen_resolution",
    "CPU_Company": "cpu_company",
    "CPU_Type": "cpu_type",
    "RAM (GB)": "ram",
    "Memory": "storage",
    "GPU_Company": "gpu_company",
    "GPU_Type": "gpu_type",
    "OpSys": "operating_system",
    "Weight": "weight",
    "Price (Euro)": "price"
}

df1 = df1.rename(columns=rename_df1)
df1["cpu"] = (
    df1["cpu_company"].fillna("").astype(str).str.strip()
    + " "
    + df1["cpu_type"].fillna("").astype(str).str.strip()
).str.strip()
df1["gpu"] = (
    df1["gpu_company"].fillna("").astype(str).str.strip()
    + " "
    + df1["gpu_type"].fillna("").astype(str).str.strip()
).str.strip()


# -------------------------
# Dataset 2
# -------------------------

rename_df2 = {
    "Brand": "brand",
    "Model": "model",
    "CPU": "cpu",
    "RAM": "ram",
    "Storage": "storage",
    "GPU": "gpu",
    "Screen": "screen_size",
    "Final Price": "price"
}

df2 = df2.rename(columns=rename_df2)


# ============================================================
# 5. KEEP ONLY COMMON FEATURES
# ============================================================

common_columns = [
    "brand",
    "model",
    "cpu",
    "ram",
    "storage",
    "gpu",
    "screen_size",
    "price"
]

# Check that required columns exist before selecting them.
missing_df1 = [col for col in common_columns if col not in df1.columns]
missing_df2 = [col for col in common_columns if col not in df2.columns]

if missing_df1 or missing_df2:
    missing_messages = []
    if missing_df1:
        missing_messages.append(f"Dataset 1: {missing_df1}")
    if missing_df2:
        missing_messages.append(f"Dataset 2: {missing_df2}")
    raise ValueError(
        "Required columns are missing after renaming: "
        + "; ".join(missing_messages)
    )

# Keep only common columns
df1 = df1[common_columns]
df2 = df2[common_columns]


# ============================================================
# 6. HANDLE GPU VALUES
# ============================================================

# Dataset 2 has many blank GPU values.
# We interpret these as laptops without a dedicated GPU.

df2["gpu"] = df2["gpu"].fillna("").astype(str).str.strip()
df2.loc[
    df2["gpu"].isin(["", "nan", "NaN", "None"]),
    "gpu"
] = "No Dedicated GPU"

# Also handle missing GPU values in Dataset 1,
# if any exist.

df1["gpu"] = df1["gpu"].fillna("").astype(str).str.strip()
df1.loc[
    df1["gpu"].isin(["", "nan", "NaN", "None"]),
    "gpu"
] = "No Dedicated GPU"


# ============================================================
# 7. STANDARDIZE RAM
# ============================================================

# Convert values such as:
# "8GB" -> 8
# "16GB" -> 16

df1["ram"] = (
    df1["ram"]
    .astype(str)
    .str.replace("GB", "", regex=False)
    .str.strip()
)

df2["ram"] = (
    df2["ram"]
    .astype(str)
    .str.replace("GB", "", regex=False)
    .str.strip()
)

df1["ram"] = pd.to_numeric(df1["ram"], errors="coerce")
df2["ram"] = pd.to_numeric(df2["ram"], errors="coerce")


# ============================================================
# 8. STANDARDIZE SCREEN SIZE
# ============================================================

df1["screen_size"] = pd.to_numeric(
    df1["screen_size"],
    errors="coerce"
)

# Dataset 2 screen values may contain units such as inches.
df2["screen_size"] = (
    df2["screen_size"]
    .astype(str)
    .str.replace('"', "", regex=False)
    .str.replace("inch", "", case=False, regex=False)
    .str.replace("inches", "", case=False, regex=False)
    .str.strip()
)

df2["screen_size"] = pd.to_numeric(
    df2["screen_size"],
    errors="coerce"
)


# ============================================================
# 9. STANDARDIZE PRICE
# ============================================================

df1["price"] = pd.to_numeric(
    df1["price"],
    errors="coerce"
)

df2["price"] = pd.to_numeric(
    df2["price"],
    errors="coerce"
)


# ============================================================
# 10. REMOVE ROWS WITHOUT A PRICE
# ============================================================

df1 = df1.dropna(subset=["price"])
df2 = df2.dropna(subset=["price"])


# ============================================================
# 11. ADD SOURCE COLUMN
# ============================================================

# This is useful for checking the merged dataset later.

df1["source"] = "Dataset 1"
df2["source"] = "Dataset 2"


# ============================================================
# 12. COMBINE DATASETS
# ============================================================

combined_df = pd.concat(
    [df1, df2],
    ignore_index=True
)


# ============================================================
# 13. REMOVE EXACT DUPLICATE ROWS
# ============================================================

before_duplicates = len(combined_df)

combined_df = combined_df.drop_duplicates()

after_duplicates = len(combined_df)

duplicates_removed = (
    before_duplicates - after_duplicates
)


# ============================================================
# 14. RESET INDEX
# ============================================================

combined_df = combined_df.reset_index(drop=True)


# ============================================================
# 15. DISPLAY INFORMATION
# ============================================================

print("\n========================================")
print("COMBINATION COMPLETED")
print("========================================")

print("\nDataset 1 records:", len(df1))
print("Dataset 2 records:", len(df2))
print("Duplicates removed:", duplicates_removed)
print("Final records:", len(combined_df))

print("\nFinal columns:")
print(combined_df.columns.tolist())

print("\nFinal dataset shape:")
print(combined_df.shape)

print("\nFirst 10 rows:")
print(combined_df.head(10))

print("\nMissing values:")
print(combined_df.isnull().sum())

print("\nPrice statistics:")
print(combined_df["price"].describe())


# ============================================================
# 16. SAVE FINAL DATASET
# ============================================================

combined_df.to_csv(
    output_path,
    index=False
)

print("\n========================================")
print("FILE SAVED")
print("========================================")

print("Saved as:", output_path)