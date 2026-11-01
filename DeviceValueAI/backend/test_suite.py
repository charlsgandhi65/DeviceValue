import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from fastapi.testclient import TestClient
from main import app, extract_cpu_features, extract_gpu_features, EUR_TO_INR_RATE

client = TestClient(app)

def test_all():
    print("=== 1. Health Endpoint ===")
    health_res = client.get("/api/health")
    assert health_res.status_code == 200, f"Health failed: {health_res.text}"
    health_data = health_res.json()
    print("Health status:", health_data)
    assert health_data["model_loaded"] is True, "Model not loaded"

    print("\n=== 2. Feature Extraction Check ===")
    gpu_test = extract_gpu_features("Intel Iris Plus Graphics 640")
    print("Known GPU (Intel Iris Plus Graphics 640):", gpu_test)
    assert gpu_test["has_dedicated_gpu"] == "No", f"has_dedicated_gpu should be No, got {gpu_test}"
    assert gpu_test["gpu_family"] == "Intel Iris", f"gpu_family should be Intel Iris, got {gpu_test}"

    gpu_ded = extract_gpu_features("Nvidia GeForce GTX 1050")
    print("Known Dedicated GPU (Nvidia GeForce GTX 1050):", gpu_ded)
    assert gpu_ded["has_dedicated_gpu"] == "Yes", f"has_dedicated_gpu should be Yes, got {gpu_ded}"
    assert gpu_ded["gpu_family"] == "NVIDIA GTX", f"gpu_family should be NVIDIA GTX, got {gpu_ded}"

    cpu_test = extract_cpu_features("Intel Core i5 7200U")
    print("Known CPU (Intel Core i5 7200U):", cpu_test)
    assert cpu_test["cpu_brand"] == "Intel", f"cpu_brand error: {cpu_test}"
    assert cpu_test["cpu_family"] == "Core i5", f"cpu_family error: {cpu_test}"

    print("\n=== 3. Single Laptop Prediction ===")
    laptop_1 = {
        "brand": "Dell",
        "model": "Inspiron 3567",
        "cpu": "Intel Core i5 7200U",
        "ram": 8,
        "gpu": "AMD Radeon R5 M430",
        "storage_capacity_gb": 1024,
        "storage_type": "HDD",
        "screen_size": 15.6
    }
    pred_res = client.post("/api/predict/laptop", json=laptop_1)
    assert pred_res.status_code == 200, f"Predict failed: {pred_res.text}"
    pred_data = pred_res.json()
    print("Single prediction result:", pred_data)
    assert pred_data["price_eur"] > 0, "Price EUR must be positive"
    assert abs(pred_data["price_inr"] - round(pred_data["price_eur"] * EUR_TO_INR_RATE, 2)) < 0.1, "INR conversion mismatch"

    print("\n=== 4. Comparison Batch Prediction (2 Laptops) ===")
    laptop_2 = {
        "brand": "HP",
        "model": "250 G6",
        "cpu": "Intel Core i3 6006U",
        "ram": 4,
        "gpu": "Intel HD Graphics 520",
        "storage_capacity_gb": 500,
        "storage_type": "HDD",
        "screen_size": 15.6
    }
    batch_2_res = client.post("/api/predict/batch", json=[laptop_1, laptop_2])
    assert batch_2_res.status_code == 200, f"Batch (2) failed: {batch_2_res.text}"
    batch_2_data = batch_2_res.json()
    print(f"Batch (2) returned {len(batch_2_data)} predictions:")
    for idx, p in enumerate(batch_2_data):
        print(f"  Laptop {idx + 1}: EUR {p['price_eur']}, INR {p['price_inr']}")
    assert len(batch_2_data) == 2, "Batch count should be 2"

    print("\n=== 5. Comparison Batch Prediction (3 Laptops) ===")
    laptop_3 = {
        "brand": "Apple",
        "model": "MacBook Pro",
        "cpu": "Intel Core i7 7700HQ",
        "ram": 16,
        "gpu": "AMD Radeon Pro 555",
        "storage_capacity_gb": 512,
        "storage_type": "SSD",
        "screen_size": 15.4
    }
    batch_3_res = client.post("/api/predict/batch", json=[laptop_1, laptop_2, laptop_3])
    assert batch_3_res.status_code == 200, f"Batch (3) failed: {batch_3_res.text}"
    batch_3_data = batch_3_res.json()
    print(f"Batch (3) returned {len(batch_3_data)} predictions:")
    for idx, p in enumerate(batch_3_data):
        print(f"  Laptop {idx + 1}: EUR {p['price_eur']}, INR {p['price_inr']}")
    assert len(batch_3_data) == 3, "Batch count should be 3"

    print("\n=== 6. Resale Estimation Error Handling ===")
    resale_req = dict(laptop_1, device_age_years=2, physical_condition="good")
    resale_res = client.post("/api/resale/estimate", json=resale_req)
    print("Resale HTTP Status:", resale_res.status_code)
    resale_data = resale_res.json()
    print("Resale payload:", resale_data)
    assert resale_res.status_code == 200, "Resale endpoint should return 200 with structured status"
    assert resale_data["status"] in ["error", "insufficient_data", "success"], "Invalid status"
    assert "listings" in resale_data, "listings field must be present"

    print("\nALL BACKEND AND ML PIPELINE TESTS PASSED!")

if __name__ == "__main__":
    test_all()
