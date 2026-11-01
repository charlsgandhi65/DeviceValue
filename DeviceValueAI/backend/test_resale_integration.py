import os
import sys
from starlette.testclient import TestClient

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.dirname(__file__))

import resale_store
import resale_engine
from main import app

client = TestClient(app)


def test_sqlite_store_operations():
    resale_store.init_db()
    initial_count = resale_store.count_listings()

    test_listing = {
        "brand": "Dell",
        "model": "XPS 13 9310",
        "processor": "Intel Core i7-1185G7",
        "ram_gb": 16,
        "storage_gb": 512,
        "storage_type": "SSD",
        "gpu": "Intel Iris Xe",
        "screen_size": 13.4,
        "title": "Dell XPS 13 9310 Core i7 16GB RAM 512GB SSD",
        "price_inr": 62000.0,
        "currency": "INR",
        "condition": "Excellent",
        "source_url": "https://example.com/test-dell-xps-13-1",
        "source_name": "example.com",
        "match_type": "exact",
        "collected_at": "2026-10-26T12:00:00"
    }

    inserted = resale_store.save_listings([test_listing])
    assert inserted in [0, 1]  # 1 if first time, 0 if re-run

    # Test deduplication
    dup_inserted = resale_store.save_listings([test_listing])
    assert dup_inserted == 0, "Duplicate source_url must be ignored"

    # Query listings
    results = resale_store.get_stored_listings(brand="Dell", model="XPS 13")
    assert len(results) >= 1
    found = any(r["source_url"] == "https://example.com/test-dell-xps-13-1" for r in results)
    assert found, "Saved listing must be retrievable by brand and model"


def test_price_extraction_and_hardware_rejection():
    # True positives
    assert resale_engine.extract_price_from_text("Dell XPS 15 for ₹55,000 in Mumbai") == 55000.0
    assert resale_engine.extract_price_from_text("Lenovo Legion 5 - Rs. 68000 only") == 68000.0
    assert resale_engine.extract_price_from_text("HP Pavilion Gaming 48k INR") == 48000.0
    assert resale_engine.extract_price_from_text("MacBook Air M2 Price: ₹74,500") == 74500.0

    # False positive rejection (CPU/GPU numbers without currency anchor)
    assert resale_engine.extract_price_from_text("Dell XPS i7-11800H 16GB RAM 512GB SSD") is None
    assert resale_engine.extract_price_from_text("Lenovo Legion RTX 3060 6GB GPU") is None
    assert resale_engine.extract_price_from_text("Acer Nitro 5 Ryzen 5 5600H") is None
    assert resale_engine.extract_price_from_text("Screen 144Hz 1080p display") is None

    # Price boundary constraints (₹4,000 to ₹400,000)
    assert resale_engine.extract_price_from_text("Cable for ₹500") is None  # Below 4000
    assert resale_engine.extract_price_from_text("Server rack for ₹900,000") is None  # Above 400000


def test_accessory_filtering():
    assert resale_engine.is_accessory_or_part("Dell Inspiron 65W AC Adapter Charger") is True
    assert resale_engine.is_accessory_or_part("Original Battery for Lenovo ThinkPad T480") is True
    assert resale_engine.is_accessory_or_part("HP Laptop Sleeve Bag Cover Case") is True
    assert resale_engine.is_accessory_or_part("MacBook Pro Replacement Display Screen Panel") is True
    assert resale_engine.is_accessory_or_part("Dell XPS 15 9500 Motherboard replacement") is True

    # Real laptop with accessories should be permitted
    assert resale_engine.is_accessory_or_part("Dell XPS 13 laptop with original charger and box") is False


def test_valuation_calculation_logic():
    # 1. Insufficient data (< 3 listings)
    small_batch = [{"price_inr": 35000.0, "match_type": "exact"}]
    res = resale_engine.calculate_resale_metrics(small_batch)
    assert res["status"] == "insufficient_data"
    assert res["has_estimate"] is False

    # 2. Exact match valuation
    exact_batch = [
        {"price_inr": 40000.0, "match_type": "exact"},
        {"price_inr": 42000.0, "match_type": "exact"},
        {"price_inr": 45000.0, "match_type": "exact"},
        {"price_inr": 48000.0, "match_type": "exact"},
        {"price_inr": 50000.0, "match_type": "exact"},
    ]
    res_exact = resale_engine.calculate_resale_metrics(exact_batch)
    assert res_exact["status"] == "success"
    assert res_exact["estimated_value_inr"] == 45000.0  # Median
    assert res_exact["match_quality"] == "exact"
    assert res_exact["confidence_level"] == "high"

    # 3. Mixed match valuation
    mixed_batch = [
        {"price_inr": 30000.0, "match_type": "exact"},
        {"price_inr": 34000.0, "match_type": "similar"},
        {"price_inr": 38000.0, "match_type": "similar"},
        {"price_inr": 42000.0, "match_type": "similar"},
    ]
    res_mixed = resale_engine.calculate_resale_metrics(mixed_batch)
    assert res_mixed["status"] == "success"
    assert res_mixed["match_quality"] == "mixed"
    assert res_mixed["estimated_value_inr"] == 36000.0


def test_api_health_endpoint():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert "model_loaded" in data
    assert "resale_db_listings_count" in data


def test_api_predict_laptop_ml_preserved():
    """Verify that existing ML retail price prediction is unaffected."""
    payload = {
        "brand": "Dell",
        "model": "Inspiron 15",
        "cpu": "Intel Core i5-1135G7",
        "ram": 8,
        "gpu": "Intel Iris Xe",
        "storage_capacity_gb": 512,
        "storage_type": "SSD",
        "screen_size": 15.6
    }
    resp = client.post("/api/predict/laptop", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "price_eur" in data
    assert "price_inr" in data
    assert data["price_inr"] > 10000


def test_api_resale_estimate_endpoint():
    payload = {
        "brand": "Dell",
        "model": "XPS 13 9310",
        "cpu": "Intel Core i7-1185G7",
        "ram": 16,
        "gpu": "Intel Iris Xe",
        "storage_capacity_gb": 512,
        "storage_type": "SSD",
        "screen_size": 13.4
    }
    resp = client.post("/api/resale/estimate", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] in ["success", "insufficient_data"]
    assert "comparable_listings_count" in data
    assert "retrieval_timestamp" in data


if __name__ == "__main__":
    test_sqlite_store_operations()
    print("test_sqlite_store_operations passed")
    test_price_extraction_and_hardware_rejection()
    print("test_price_extraction_and_hardware_rejection passed")
    test_accessory_filtering()
    print("test_accessory_filtering passed")
    test_valuation_calculation_logic()
    print("test_valuation_calculation_logic passed")
    test_api_health_endpoint()
    print("test_api_health_endpoint passed")
    test_api_predict_laptop_ml_preserved()
    print("test_api_predict_laptop_ml_preserved passed")
    test_api_resale_estimate_endpoint()
    print("test_api_resale_estimate_endpoint passed")
    print("\nALL INTEGRATION TESTS PASSED SUCCESSFULLY!")
