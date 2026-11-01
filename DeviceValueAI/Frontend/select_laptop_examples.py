
import pandas as pd
import joblib
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

# File paths — update these if your files are elsewhere
DATASET_FILE = Path("laptop_storage_features_cleaned.csv")
MODEL_FILE = Path("backend/final_laptop_price_model.joblib")

if not DATASET_FILE.exists():
    raise FileNotFoundError(f"Dataset not found: {DATASET_FILE.resolve()}")

if not MODEL_FILE.exists():
    raise FileNotFoundError(f"Model not found: {MODEL_FILE.resolve()}")

# Load dataset
df = pd.read_csv(DATASET_FILE)

# Required model features
feature_columns = [
    "brand",
    "model",
    "ram",
    "screen_size",
    "storage_capacity_gb",
    "storage_type",
    "cpu_brand",
    "cpu_family",
    "cpu_model",
    "gpu",
    "gpu_brand",
    "gpu_family",
    "has_dedicated_gpu"
]

required_columns = feature_columns + ["price"]
missing = [col for col in required_columns if col not in df.columns]

if missing:
    raise ValueError(f"Missing columns: {missing}")

# Convert numeric columns safely
for col in ["ram", "screen_size", "storage_capacity_gb", "price"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna(subset=["price"]).copy()

X = df[feature_columns]
y = df["price"]

# Reproduce the same split used in training
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42
)

# Load saved model and generate predictions
model = joblib.load(MODEL_FILE)
predictions = model.predict(X_test)

# Evaluate the saved model on this test split
print("Test MAE:", round(mean_absolute_error(y_test, predictions), 2))
print("Test R²:", round(r2_score(y_test, predictions), 4))

# Select low-priced examples with the smallest errors
results = X_test.copy()
results["Actual Price (EUR)"] = y_test
results["Predicted Price (EUR)"] = predictions
results["Absolute Error (EUR)"] = (
    results["Actual Price (EUR)"] -
    results["Predicted Price (EUR)"]
).abs()

examples = results[
    results["Actual Price (EUR)"].between(0, 1000)
].sort_values("Absolute Error (EUR)").head(10)

if examples.empty:
    print("No test examples found with prices between €0 and €1,000.")
else:
    print("\nBest low-priced examples:")
    print(examples.round(2).to_string())

    output_file = Path("presentation_laptop_examples.csv")
    examples.to_csv(output_file, index=False)
    print(f"\nSaved examples to: {output_file.resolve()}")
