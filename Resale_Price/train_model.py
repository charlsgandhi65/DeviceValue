"""
train_model.py
--------------
Loads sample data, trains a Random Forest regression model,
and saves the trained model + encoder to disk.

Run this once before using the app:
    python train_model.py
"""

import os
import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, r2_score


# ── Paths ───────────────────────────────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "used_phones_clean.csv")
MODEL_DIR = os.path.join(BASE_DIR, "model")
MODEL_PATH = os.path.join(MODEL_DIR, "model.pkl")
ENC_PATH = os.path.join(MODEL_DIR, "encoders.pkl")
os.makedirs(MODEL_DIR, exist_ok=True)


def load_data(path: str) -> pd.DataFrame:
    """Load the CSV dataset."""
    df = pd.read_csv(path)
    print(f"[OK] Loaded {len(df)} records from {path}")
    return df


def encode_categoricals(df: pd.DataFrame):
    """
    Label-encode 'brand', 'model', and 'condition'.
    Returns the encoded DataFrame and a dict of fitted encoders.
    """
    encoders = {}
    for col in ["brand", "model", "condition"]:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        encoders[col] = le
    return df, encoders


def train(df: pd.DataFrame):
    """Split data, train a Random Forest, return model + metrics."""
    feature_cols = ["brand", "model", "ram_gb", "storage_gb",
                    "age_months", "battery_health", "condition", "launch_price"]
    target_col   = "price"

    X = df[feature_cols]
    y = df[target_col]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)

    # Evaluate
    preds = model.predict(X_test)
    mae   = mean_absolute_error(y_test, preds)
    r2    = r2_score(y_test, preds)

    print(f"[STAT] MAE  : Rs.{mae:,.0f}")
    print(f"[STAT] R2   : {r2:.3f}")

    return model


def main():
    df               = load_data(DATA_PATH)
    df, encoders     = encode_categoricals(df)
    model            = train(df)

    joblib.dump(model,    MODEL_PATH)
    joblib.dump(encoders, ENC_PATH)

    print(f"[SAVE] Model saved   -> {MODEL_PATH}")
    print(f"[SAVE] Encoders saved -> {ENC_PATH}")
    print("\n[DONE] Training complete! You can now run the Streamlit app.")


if __name__ == "__main__":
    main()
