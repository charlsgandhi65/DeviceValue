
import pandas as pd
from pathlib import Path

INPUT_FILE = Path("laptop_storage_features.csv")
OUTPUT_FILE = Path("laptop_storage_features_cleaned.csv")

# Check that the dataset exists
if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"Cannot find {INPUT_FILE.resolve()}. "
        "Keep this script in the same folder as your dataset."
    )

# Load dataset
df = pd.read_csv(INPUT_FILE)

print("Original dataset shape:", df.shape)

# Clean RAM values such as 8GB, 16GB, and 32 GB
df["ram"] = (
    df["ram"]
    .astype("string")
    .str.strip()
    .str.replace(r"\s*GB\s*", "", regex=True, case=False)
)

df["ram"] = pd.to_numeric(df["ram"], errors="coerce")

# Verify RAM values
print("\nRAM data type:", df["ram"].dtype)
print("RAM values:", sorted(df["ram"].dropna().unique()))

# Report any RAM values that could not be converted
print("Missing RAM values:", df["ram"].isna().sum())

# Save the cleaned dataset separately
df.to_csv(OUTPUT_FILE, index=False)

print("\nCleaned dataset saved successfully!")
print("Output file:", OUTPUT_FILE.resolve())
print("Dataset shape:", df.shape)
