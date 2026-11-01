"""
predict.py
----------
Provides a simple predict_price() function used by the Streamlit app.
Loads the saved model and encoders, transforms input, returns a price.
"""

import os
import numpy as np
import joblib

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model", "model.pkl")
ENC_PATH = os.path.join(BASE_DIR, "model", "encoders.pkl")


def load_artifacts():
    """Load and return (model, encoders) from disk."""
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"Model not found at {MODEL_PATH}.\n" "Please run:  python train_model.py"
        )
    model = joblib.load(MODEL_PATH)
    encoders = joblib.load(ENC_PATH)
    return model, encoders


def predict_price(
    model_obj,
    encoders: dict,
    brand: str,
    model_name: str,
    ram_gb: int,
    storage_gb: int,
    age_months: int,
    battery_health: int,
    condition: str,
    launch_price: int,
) -> float:
    """
    Predict the resale price (INR) for a used phone.

    Parameters
    ----------
    model_obj      : Trained Random Forest model
    encoders       : Dict of LabelEncoders
    brand          : Phone brand (e.g. "Samsung", "Apple")
    model_name     : Specific model (e.g. "Galaxy S23", "iPhone 14")
    ram_gb         : RAM in GB
    storage_gb     : Internal storage in GB
    age_months     : Age of the phone in months
    battery_health : Battery health % (0-100)
    condition      : "Excellent" | "Good" | "Fair" | "Poor"
    launch_price  : Original launch price in INR

    Returns
    -------
    Predicted price in INR (float)
    """
    # Encode categoricals the same way as training
    try:
        brand_enc = encoders["brand"].transform([brand])[0]
    except ValueError:
        known_brands = encoders["brand"].classes_

        similar_brands = [
            b
            for b in known_brands
            if brand.lower() in b.lower() or b.lower() in brand.lower()
        ]

        fallback_brand = similar_brands[0] if similar_brands else known_brands[0]

        brand_enc = encoders["brand"].transform([fallback_brand])[0]

    try:
        model_enc = encoders["model"].transform([model_name])[0]
    except ValueError:
        # Fallback for unseen models
        known_models = encoders["model"].classes_
        similar_models = [
            m for m in known_models if model_name.lower().split()[0] in m.lower()
        ]
        fallback_model = similar_models[0] if similar_models else known_models[0]
        model_enc = encoders["model"].transform([fallback_model])[0]

    condition_enc = encoders["condition"].transform([condition])[0]

    features = np.array(
        [
            [
                brand_enc,
                model_enc,
                ram_gb,
                storage_gb,
                age_months,
                battery_health,
                condition_enc,
                launch_price,
            ]
        ]
    )

    price = model_obj.predict(features)[0]

    # ---------- Premium Flagship Market Corrections ----------
    # Normalize inputs for robust comparison
    m_name_low = str(model_name).lower()
    brand_low = str(brand).lower()
    cond_low = str(condition).lower()

    # 1. Samsung Ultra correction
    if brand_low == "samsung" and "ultra" in m_name_low:
        if age_months >= 24:
            price *= 0.78
        elif age_months >= 12:
            price *= 0.84
        else:
            price *= 0.92

    # 2. Samsung FE correction
    if brand_low == "samsung" and "fe" in m_name_low:
        if age_months >= 24:
            price *= 0.88
        else:
            price *= 0.94

    # 3. Apple Pro / Pro Max correction
    if brand_low == "apple" and ("pro max" in m_name_low or "pro" in m_name_low):
        if age_months >= 24:
            price *= 0.82
        elif age_months >= 12:
            price *= 0.88
        else:
            price *= 0.94

    # 4. Battery health adjustment
    if battery_health < 85:
        price *= 0.93
    elif battery_health < 90:
        price *= 0.97
    elif battery_health >= 95:
        price *= 1.02

    # 5. Visual condition adjustment
    if cond_low == "fair":
        price *= 0.88
    elif cond_low == "good":
        price *= 0.95
    elif cond_low == "excellent":
        price *= 1.03

    # 6. Extra depreciation after 12 months
    if age_months > 12:
        price *= 1 - (age_months - 12) * 0.005  # 0.5% per month after 1 year

    # 7. Prevent unrealistic overpricing vs launch price
    if age_months >= 12:
        price = min(price, launch_price * 0.78)

    if age_months >= 24:
        price = min(price, launch_price * 0.62)

    if age_months >= 36:
        price = min(price, launch_price * 0.48)

    # 8. Minimum floor price protection
    price = max(price, launch_price * 0.12)

    return float(int(price))  # Final integer output cast to float for consistency


def get_known_brands(encoders: dict) -> list:
    """Return the list of brands the model was trained on."""
    return list(encoders["brand"].classes_)


def get_known_conditions(encoders: dict) -> list:
    """Return the list of conditions the model was trained on."""
    return list(encoders["condition"].classes_)


def get_known_models(encoders: dict) -> list:
    """Return the list of phone models the model was trained on."""
    return list(encoders["model"].classes_)
