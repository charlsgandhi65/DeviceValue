from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
import os
import httpx
import re
import joblib
import pandas as pd
import subprocess
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

from resale_store import init_db as init_resale_db, get_stored_listings, save_listings
from resale_engine import (
    collect_and_match_resale_listings,
    calculate_resale_metrics,
    extract_price_from_text,
    is_accessory_or_part
)

# Load environment variables
load_dotenv()

app = FastAPI(title="DeviceValue AI Backend", version="1.0.0")


@app.get("/", include_in_schema=False)
async def frontend_redirect():
    """Open the Vite frontend when the backend URL is visited directly."""
    return RedirectResponse(url="http://127.0.0.1:5173/")

# Load the trained ML model
MODEL_PATH = os.path.join(os.path.dirname(__file__), "final_laptop_price_model.joblib")
try:
    model = joblib.load(MODEL_PATH)
    model_loaded = True
except Exception as e:
    print(f"Warning: Could not load model: {e}")
    model = None
    model_loaded = False

# Load reference dataset mappings if available to match training categories with 100% precision
CSV_FEATURE_PATH = os.path.join(os.path.dirname(__file__), "..", "laptop_storage_features.csv")
GPU_FEATURE_LOOKUP = {}
CPU_FEATURE_LOOKUP = {}

if os.path.exists(CSV_FEATURE_PATH):
    try:
        ref_df = pd.read_csv(CSV_FEATURE_PATH)
        if all(col in ref_df.columns for col in ['gpu', 'gpu_brand', 'gpu_family', 'has_dedicated_gpu']):
            GPU_FEATURE_LOOKUP = (
                ref_df[['gpu', 'gpu_brand', 'gpu_family', 'has_dedicated_gpu']]
                .drop_duplicates(subset=['gpu'])
                .set_index('gpu')
                .to_dict('index')
            )
        if all(col in ref_df.columns for col in ['cpu', 'cpu_brand', 'cpu_family', 'cpu_model']):
            CPU_FEATURE_LOOKUP = (
                ref_df[['cpu', 'cpu_brand', 'cpu_family', 'cpu_model']]
                .drop_duplicates(subset=['cpu'])
                .set_index('cpu')
                .to_dict('index')
            )
    except Exception as e:
        print(f"Notice: Reference feature dataset load skipped: {e}")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FREESEA_API_KEY = os.getenv("FREESEA_API_KEY")
FREESEA_API_URL = "https://freesea.dev/v1/search"

# Currency conversion rate (EUR to INR)
EUR_TO_INR_RATE = 90.0


# Pydantic models for ML prediction
class PredictionRequest(BaseModel):
    brand: str = Field(..., description="Laptop brand (e.g., Dell, HP, Apple)")
    model: str = Field(..., description="Laptop model (e.g., XPS 15, MacBook Pro)")
    cpu: str = Field(..., description="CPU/Processor (e.g., Intel Core i7-12700H)")
    ram: int = Field(..., description="RAM in GB")
    gpu: str = Field(..., description="GPU (e.g., NVIDIA RTX 3060)")
    storage_capacity_gb: int = Field(..., description="Storage capacity in GB")
    storage_type: str = Field(..., description="Storage type (SSD or HDD)")
    screen_size: float = Field(..., description="Screen size in inches")


class PredictionResponse(BaseModel):
    price_eur: float
    price_inr: float
    currency: str = "EUR"
    specifications: dict


# Pydantic models for resale estimation
class ResaleRequest(BaseModel):
    brand: str = Field(..., description="Laptop brand (e.g., Dell, HP, Apple)")
    model: str = Field(..., description="Laptop model (e.g., XPS 15, MacBook Pro)")
    cpu: str = Field(..., description="CPU/Processor (e.g., Intel Core i7-12700H)")
    ram: int = Field(..., description="RAM in GB")
    gpu: str = Field(..., description="GPU (e.g., NVIDIA RTX 3060)")
    storage_capacity_gb: int = Field(..., description="Storage capacity in GB")
    storage_type: str = Field(..., description="Storage type (SSD or HDD)")
    screen_size: float = Field(..., description="Screen size in inches")
    device_age_years: Optional[float] = Field(None, description="Device age in years")
    physical_condition: Optional[str] = Field(None, description="Physical condition (e.g., excellent, good, fair, poor)")
    battery_health: Optional[str] = Field(None, description="Battery health percentage or condition")


class Listing(BaseModel):
    title: str
    price_inr: Optional[float] = None
    source_url: str
    source_name: str
    condition: Optional[str] = None
    listing_date: Optional[str] = None
    match_type: Optional[str] = "exact"


class ResaleResponse(BaseModel):
    status: Literal["success", "insufficient_data", "error"]
    estimated_value_inr: Optional[float] = None
    estimated_range_min: Optional[float] = None
    estimated_range_max: Optional[float] = None
    estimated_range_min_inr: Optional[float] = None
    estimated_range_max_inr: Optional[float] = None
    currency: str = "INR"
    comparable_listings_count: int = 0
    exact_matches_count: int = 0
    similar_matches_count: int = 0
    match_quality: Optional[Literal["exact", "similar", "mixed"]] = None
    confidence_level: Optional[Literal["high", "medium", "low"]] = None
    listings: List[Listing] = []
    retrieval_timestamp: str
    limitations: List[str] = []
    error_message: Optional[str] = None


def extract_price_from_text(text: str) -> Optional[float]:
    """Extract INR price from text using regex patterns."""
    if not text:
        return None

    # Pattern for INR with various formats: ₹50,000, 50000, 50,000, 50k, Rs. 50000
    patterns = [
        r'[₹Rs\.\s]*([0-9,]+(?:\.[0-9]{1,2})?)\s*(?:INR|Rs\.?|₹)?',
        r'([0-9,]+(?:\.[0-9]{1,2})?)\s*(?:INR|Rs\.?|₹)',
        r'₹\s*([0-9,]+(?:\.[0-9]{1,2})?)',
    ]

    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            # Clean the number (remove commas)
            cleaned = match.replace(',', '').replace(' ', '')
            try:
                price = float(cleaned)
                # Filter out unrealistic prices
                if 1000 <= price <= 500000:
                    return price
            except ValueError:
                continue

    return None


def build_search_query(brand: str, model: str, cpu: str, ram: int, gpu: str, storage: str) -> str:
    """Build a search query for used laptop listings."""
    query_parts = [
        f'"{brand}"',
        f'"{model}"' if model else '',
        cpu if cpu else '',
        f'{ram}GB RAM',
        gpu if gpu else '',
        storage if storage else '',
        'used',
        'second hand',
        'India',
        'price',
    ]
    return ' '.join([p for p in query_parts if p])


async def search_freesea(query: str) -> List[dict]:
    """Search freesea API for laptop listings."""
    if not FREESEA_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="FREESEA_API_KEY not configured on the server."
        )

    headers = {
        "Authorization": f"Bearer {FREESEA_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "query": query,
        "max_results": 15,
        "search_depth": "basic",
        "country": "IN"
    }

    async with httpx.AsyncClient(timeout=20.0) as client:
        try:
            response = await client.post(FREESEA_API_URL, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            if isinstance(data, dict):
                return data.get("results", [])
            return []
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Freesea API returned error {e.response.status_code}"
            )
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=502,
                detail=f"Network connection to search API failed: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Search request failed: {str(e)}"
            )


def extract_listings_from_results(results: List[dict]) -> List[Listing]:
    """Extract and validate listing information from search results."""
    listings = []
    seen_urls = set()

    for result in results:
        if result.get("type") == "sponsored":
            continue

        url = result.get("url", "")
        if url in seen_urls:
            continue
        seen_urls.add(url)

        title = result.get("title", "")
        content = result.get("content", "")

        # Extract price
        price = extract_price_from_text(title) or extract_price_from_text(content)

        # Extract domain as source name
        domain = result.get("domain", url.split('/')[2] if '/' in url else "Unknown")

        # Try to extract condition from content
        condition = None
        condition_keywords = ["excellent", "good", "fair", "poor", "like new", "brand new", "used"]
        for keyword in condition_keywords:
            if keyword.lower() in content.lower():
                condition = keyword.capitalize()
                break

        # Extract published date if available
        listing_date = result.get("published_date")

        listing = Listing(
            title=title,
            price_inr=price,
            source_url=url,
            source_name=domain,
            condition=condition,
            listing_date=listing_date
        )
        listings.append(listing)

    return listings


def extract_cpu_features(cpu: str) -> dict:
    """Extract CPU brand, family, and model from CPU string matching trained categories."""
    if cpu in CPU_FEATURE_LOOKUP:
        rec = CPU_FEATURE_LOOKUP[cpu]
        return {
            "cpu_brand": rec.get("cpu_brand"),
            "cpu_family": rec.get("cpu_family"),
            "cpu_model": rec.get("cpu_model", cpu)
        }

    cpu_lower = cpu.lower()

    # CPU brand: ['AMD', 'Apple', 'Intel', 'Microsoft', 'Qualcomm', 'Samsung']
    cpu_brand = "Intel"
    if "intel" in cpu_lower:
        cpu_brand = "Intel"
    elif "amd" in cpu_lower:
        cpu_brand = "AMD"
    elif "apple" in cpu_lower or any(m in cpu_lower for m in ["m1", "m2", "m3"]):
        cpu_brand = "Apple"
    elif "snapdragon" in cpu_lower or "qualcomm" in cpu_lower:
        cpu_brand = "Qualcomm"
    elif "microsoft" in cpu_lower:
        cpu_brand = "Microsoft"
    elif "samsung" in cpu_lower:
        cpu_brand = "Samsung"

    # CPU family matching trained categories:
    # ['AMD 3015e', 'AMD 3020e', 'AMD A-Series', 'AMD Athlon', 'AMD E-Series',
    #  'AMD FX-Series', 'AMD Radeon', 'Atom', 'Celeron', 'Core M', 'Core i3', 'Core i5',
    #  'Core i7', 'Core i9', 'M1', 'M2', 'Microsoft SQ', 'Pentium', 'Ryzen 1600', 'Ryzen 1700',
    #  'Ryzen 3', 'Ryzen 5', 'Ryzen 7', 'Ryzen 9', 'Samsung ARM', 'Snapdragon 7', 'Snapdragon 8', 'Xeon']
    cpu_family = None
    if "i3" in cpu_lower:
        cpu_family = "Core i3"
    elif "i5" in cpu_lower:
        cpu_family = "Core i5"
    elif "i7" in cpu_lower:
        cpu_family = "Core i7"
    elif "i9" in cpu_lower:
        cpu_family = "Core i9"
    elif "ryzen 3" in cpu_lower:
        cpu_family = "Ryzen 3"
    elif "ryzen 5" in cpu_lower:
        cpu_family = "Ryzen 5"
    elif "ryzen 7" in cpu_lower:
        cpu_family = "Ryzen 7"
    elif "ryzen 9" in cpu_lower:
        cpu_family = "Ryzen 9"
    elif "m1" in cpu_lower:
        cpu_family = "M1"
    elif "m2" in cpu_lower:
        cpu_family = "M2"
    elif "celeron" in cpu_lower:
        cpu_family = "Celeron"
    elif "pentium" in cpu_lower:
        cpu_family = "Pentium"
    elif "atom" in cpu_lower:
        cpu_family = "Atom"
    elif "core m" in cpu_lower:
        cpu_family = "Core M"
    elif "xeon" in cpu_lower:
        cpu_family = "Xeon"
    elif "athlon" in cpu_lower:
        cpu_family = "AMD Athlon"
    elif any(k in cpu_lower for k in ["a-series", "a4", "a6", "a9", "a10", "a12"]):
        cpu_family = "AMD A-Series"
    elif any(k in cpu_lower for k in ["e-series", "e2", "e1"]):
        cpu_family = "AMD E-Series"

    return {
        "cpu_brand": cpu_brand,
        "cpu_family": cpu_family,
        "cpu_model": cpu
    }


def extract_gpu_features(gpu: str) -> dict:
    """Extract GPU brand, family, and has_dedicated_gpu from GPU string matching trained categories."""
    if gpu in GPU_FEATURE_LOOKUP:
        rec = GPU_FEATURE_LOOKUP[gpu]
        return {
            "gpu_brand": rec.get("gpu_brand"),
            "gpu_family": rec.get("gpu_family"),
            "gpu": gpu,
            "has_dedicated_gpu": str(rec.get("has_dedicated_gpu", "No"))
        }

    gpu_lower = gpu.lower()

    # GPU brand: ['AMD', 'ARM', 'Integrated', 'Intel', 'NVIDIA', 'Other']
    gpu_brand = "Other"
    if "no dedicated" in gpu_lower or "integrated" in gpu_lower:
        gpu_brand = "Integrated"
    elif any(k in gpu_lower for k in ["nvidia", "geforce", "rtx", "gtx", "quadro", "mx"]):
        gpu_brand = "NVIDIA"
    elif any(k in gpu_lower for k in ["amd", "radeon", "firepro"]):
        gpu_brand = "AMD"
    elif any(k in gpu_lower for k in ["intel", "iris", "uhd", "hd graphics"]):
        gpu_brand = "Intel"
    elif "mali" in gpu_lower or "arm" in gpu_lower:
        gpu_brand = "ARM"

    # GPU family:
    # ['AMD Legacy GPU', 'AMD Professional', 'AMD Radeon Legacy', 'AMD Radeon Other',
    #  'AMD Radeon R-Series', 'AMD Radeon RX', 'Integrated/No Dedicated GPU', 'Intel Graphics',
    #  'Intel HD Graphics', 'Intel Iris', 'Intel UHD', 'NVIDIA GTX', 'NVIDIA GeForce MX',
    #  'NVIDIA GeForce Other', 'NVIDIA Legacy GPU', 'NVIDIA Professional', 'NVIDIA RTX', 'Professional GPU']
    gpu_family = None
    if "no dedicated" in gpu_lower or gpu_brand == "Integrated":
        gpu_family = "Integrated/No Dedicated GPU"
    elif "rtx" in gpu_lower:
        gpu_family = "NVIDIA RTX"
    elif "gtx" in gpu_lower:
        gpu_family = "NVIDIA GTX"
    elif "mx" in gpu_lower:
        gpu_family = "NVIDIA GeForce MX"
    elif "quadro" in gpu_lower:
        gpu_family = "Professional GPU"
    elif gpu_brand == "NVIDIA":
        gpu_family = "NVIDIA GeForce Other"
    elif "iris" in gpu_lower:
        gpu_family = "Intel Iris"
    elif "uhd" in gpu_lower:
        gpu_family = "Intel UHD"
    elif "hd graphics" in gpu_lower:
        gpu_family = "Intel HD Graphics"
    elif gpu_brand == "Intel":
        gpu_family = "Intel Graphics"
    elif "rx" in gpu_lower:
        gpu_family = "AMD Radeon RX"
    elif "firepro" in gpu_lower or "pro" in gpu_lower:
        gpu_family = "AMD Professional"
    elif any(k in gpu_lower for k in ["r2", "r3", "r4", "r5", "r7", "r-series"]):
        gpu_family = "AMD Radeon R-Series"
    elif gpu_brand == "AMD":
        gpu_family = "AMD Radeon Other"

    # has_dedicated_gpu must be exact string 'Yes' or 'No' (matching categories ['No', 'Unknown', 'Yes'])
    has_dedicated_gpu = "No"
    if gpu_brand in ["NVIDIA", "AMD"] and "no dedicated" not in gpu_lower:
        has_dedicated_gpu = "Yes"
    elif "no dedicated" in gpu_lower or "integrated" in gpu_lower or gpu_brand == "Intel":
        has_dedicated_gpu = "No"

    return {
        "gpu_brand": gpu_brand,
        "gpu_family": gpu_family,
        "gpu": gpu,
        "has_dedicated_gpu": has_dedicated_gpu
    }


def calculate_resale_estimate(listings: List[Listing]) -> dict:
    """Calculate resale value estimate from comparable listings."""
    # Filter listings with valid prices
    priced_listings = [l for l in listings if l.price_inr is not None]

    if len(priced_listings) < 3:
        return {
            "has_estimate": False,
            "reason": f"Insufficient comparable listings with prices (found {len(priced_listings)}, need at least 3)"
        }

    # Calculate median
    prices = sorted([l.price_inr for l in priced_listings])
    n = len(prices)
    if n % 2 == 0:
        median = (prices[n//2 - 1] + prices[n//2]) / 2
    else:
        median = prices[n//2]

    # Calculate range (interquartile-like range)
    lower_bound = prices[max(0, n//4)]
    upper_bound = prices[min(n-1, 3*n//4)]

    return {
        "has_estimate": True,
        "median": median,
        "range_min": lower_bound,
        "range_max": upper_bound,
        "comparable_count": len(priced_listings)
    }


@app.on_event("startup")
async def startup_event():
    """Initialize database and resources on startup."""
    init_resale_db()


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    from resale_store import count_listings
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "freesea_configured": bool(FREESEA_API_KEY),
        "model_loaded": model_loaded,
        "resale_db_listings_count": count_listings()
    }


@app.post("/api/predict/laptop", response_model=PredictionResponse)
async def predict_laptop_price(request: PredictionRequest):
    """Predict laptop price using the trained ML model."""
    if not model_loaded or model is None:
        raise HTTPException(
            status_code=503,
            detail="ML model not loaded. Please ensure the model file exists."
        )

    try:
        # Extract CPU features
        cpu_features = extract_cpu_features(request.cpu)

        # Extract GPU features
        gpu_features = extract_gpu_features(request.gpu)

        # Build input DataFrame matching model's expected features
        input_data = pd.DataFrame([{
            "brand": request.brand,
            "model": request.model,
            "ram": request.ram,
            "screen_size": request.screen_size,
            "storage_capacity_gb": request.storage_capacity_gb,
            "storage_type": request.storage_type,
            "cpu_brand": cpu_features["cpu_brand"],
            "cpu_family": cpu_features["cpu_family"],
            "cpu_model": cpu_features["cpu_model"],
            "gpu_brand": gpu_features["gpu_brand"],
            "gpu_family": gpu_features["gpu_family"],
            "has_dedicated_gpu": gpu_features["has_dedicated_gpu"],
            "gpu": gpu_features["gpu"]
        }])

        # Make prediction
        prediction = model.predict(input_data)[0]

        # Convert to INR
        price_eur = float(prediction)
        price_inr = price_eur * EUR_TO_INR_RATE

        return PredictionResponse(
            price_eur=round(price_eur, 2),
            price_inr=round(price_inr, 2),
            currency="EUR",
            specifications={
                "brand": request.brand,
                "model": request.model,
                "cpu": request.cpu,
                "ram": request.ram,
                "gpu": request.gpu,
                "storage": f"{request.storage_capacity_gb}GB {request.storage_type}",
                "screen_size": request.screen_size
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )


@app.post("/api/predict/batch", response_model=List[PredictionResponse])
async def predict_batch_laptops(requests: List[PredictionRequest]):
    """Predict prices for multiple laptops (for comparison feature)."""
    if not model_loaded or model is None:
        raise HTTPException(
            status_code=503,
            detail="ML model not loaded. Please ensure the model file exists."
        )

    try:
        results = []
        for req in requests:
            cpu_features = extract_cpu_features(req.cpu)
            gpu_features = extract_gpu_features(req.gpu)

            input_data = pd.DataFrame([{
                "brand": req.brand,
                "model": req.model,
                "ram": req.ram,
                "screen_size": req.screen_size,
                "storage_capacity_gb": req.storage_capacity_gb,
                "storage_type": req.storage_type,
                "cpu_brand": cpu_features["cpu_brand"],
                "cpu_family": cpu_features["cpu_family"],
                "cpu_model": cpu_features["cpu_model"],
                "gpu_brand": gpu_features["gpu_brand"],
                "gpu_family": gpu_features["gpu_family"],
                "has_dedicated_gpu": gpu_features["has_dedicated_gpu"],
                "gpu": gpu_features["gpu"]
            }])

            prediction = model.predict(input_data)[0]
            price_eur = float(prediction)
            price_inr = price_eur * EUR_TO_INR_RATE

            results.append(PredictionResponse(
                price_eur=round(price_eur, 2),
                price_inr=round(price_inr, 2),
                currency="EUR",
                specifications={
                    "brand": req.brand,
                    "model": req.model,
                    "cpu": req.cpu,
                    "ram": req.ram,
                    "gpu": req.gpu,
                    "storage": f"{req.storage_capacity_gb}GB {req.storage_type}",
                    "screen_size": req.screen_size
                }
            ))

        return results

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Batch prediction failed: {str(e)}"
        )


@app.post("/api/resale/estimate", response_model=ResaleResponse)
async def estimate_resale_value(request: ResaleRequest):
    """Estimate resale value for a laptop based on market listings."""
    timestamp = datetime.utcnow().isoformat()

    try:
        all_listings, valuation = await collect_and_match_resale_listings(
            brand=request.brand,
            model=request.model,
            cpu=request.cpu,
            ram=request.ram,
            gpu=request.gpu,
            storage_capacity_gb=request.storage_capacity_gb,
            storage_type=request.storage_type,
            screen_size=request.screen_size
        )

        listing_models = [
            Listing(
                title=l["title"],
                price_inr=l.get("price_inr"),
                source_url=l["source_url"],
                source_name=l.get("source_name", "Marketplace"),
                condition=l.get("condition"),
                listing_date=l.get("listing_date"),
                match_type=l.get("match_type", "exact")
            )
            for l in all_listings
        ]

        if not valuation.get("has_estimate", False):
            limitations = [
                "Estimates based on asking prices, not confirmed final sale prices",
                "Results from live web search may include outdated or unavailable listings",
                valuation.get("reason", "Insufficient comparable listings with valid prices (need at least 3).")
            ]
            if not FREESEA_API_KEY:
                limitations.append("FREESEA_API_KEY is not configured in backend/.env; live search is disabled.")

            return ResaleResponse(
                status="insufficient_data",
                comparable_listings_count=valuation.get("comparable_count", len([l for l in listing_models if l.price_inr is not None])),
                exact_matches_count=valuation.get("exact_matches_count", 0),
                similar_matches_count=valuation.get("similar_matches_count", 0),
                listings=listing_models[:10],
                retrieval_timestamp=timestamp,
                limitations=limitations
            )

        return ResaleResponse(
            status="success",
            estimated_value_inr=valuation["estimated_value_inr"],
            estimated_range_min=valuation["estimated_range_min_inr"],
            estimated_range_max=valuation["estimated_range_max_inr"],
            estimated_range_min_inr=valuation["estimated_range_min_inr"],
            estimated_range_max_inr=valuation["estimated_range_max_inr"],
            currency="INR",
            comparable_listings_count=valuation["comparable_count"],
            exact_matches_count=valuation["exact_matches_count"],
            similar_matches_count=valuation["similar_matches_count"],
            match_quality=valuation.get("match_quality"),
            confidence_level=valuation.get("confidence_level"),
            listings=listing_models[:15],
            retrieval_timestamp=timestamp,
            limitations=[
                "Estimates based on asking prices from comparable market listings, not confirmed sale transactions",
                f"Derived from {valuation['comparable_count']} validated listings ({valuation['exact_matches_count']} exact, {valuation['similar_matches_count']} similar)",
                "Hardware resale valuation is completely separate from new retail ML price prediction",
                "Physical condition and battery wear may cause variance in final agreed sale price"
            ]
        )

    except Exception as e:
        return ResaleResponse(
            status="error",
            error_message=f"Unable to estimate resale value: {str(e)}",
            comparable_listings_count=0,
            listings=[],
            retrieval_timestamp=timestamp,
            limitations=[]
        )


def start_frontend() -> subprocess.Popen:
    """Start the Vite development server used by the local frontend."""
    frontend_dir = Path(__file__).resolve().parent.parent / "Frontend"
    package_json = frontend_dir / "package.json"

    if not package_json.is_file():
        raise FileNotFoundError(f"Frontend package.json not found: {package_json}")

    npm_command = "npm.cmd" if os.name == "nt" else "npm"
    try:
        process = subprocess.Popen(
            [npm_command, "run", "dev", "--", "--host", "127.0.0.1"],
            cwd=frontend_dir,
        )
    except FileNotFoundError as exc:
        raise RuntimeError(
            "npm was not found. Install Node.js and ensure npm is available on PATH."
        ) from exc

    print("Frontend starting at http://127.0.0.1:5173")
    return process


def stop_frontend(process: subprocess.Popen | None) -> None:
    """Stop the Vite process when the backend shuts down."""
    if process is None or process.poll() is not None:
        return

    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()


if __name__ == "__main__":
    import uvicorn

    frontend_process = start_frontend()
    try:
        print("Backend starting at http://127.0.0.1:8000")
        uvicorn.run(app, host="127.0.0.1", port=8000)
    finally:
        stop_frontend(frontend_process)
