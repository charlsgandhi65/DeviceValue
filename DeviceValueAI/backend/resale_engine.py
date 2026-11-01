import os
import re
import math
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime
import httpx
from dotenv import load_dotenv

from resale_store import save_listings, get_stored_listings

load_dotenv()

FREESEA_API_KEY = os.getenv("FREESEA_API_KEY")
FREESEA_API_URL = "https://freesea.dev/v1/search"

# Accessory / Part patterns to exclude from laptop listings
ACCESSORY_PATTERNS = [
    r'\bcharger\b',
    r'\badapter\b',
    r'\bbattery\b',
    r'\bcase\b',
    r'\bcover\b',
    r'\bskin\b',
    r'\bsleeve\b',
    r'\bpouch\b',
    r'\bbag\b',
    r'\bkeyboard\s+replacement\b',
    r'\breplacement\s+(?:screen|display|keyboard|battery|panel)\b',
    r'\b(?:screen|display)\s+replacement\b',
    r'\b(?:screen|display)\s+panel\b',
    r'\bdisplay\s+screen\b',
    r'\bspare\s+parts?\b',
    r'\bmotherboard\b',
    r'\bhinge\b',
    r'\bcooling\s+fan\b',
    r'\bram\s+module\b',
    r'\bdocking\s+station\b',
    r'\bcaddy\b',
]

ACCESSORY_REGEX = re.compile('|'.join(ACCESSORY_PATTERNS), re.IGNORECASE)

# Hardware prefix / suffix regex to reject false-positive numbers
HW_PREFIX_REGEX = re.compile(r'(?:i[3579]-|ryzen\s*\d?\s*|rtx\s*|gtx\s*|radeon\s*|ddr\d?\s*|core\s*|threadripper\s*)$', re.IGNORECASE)
HW_SUFFIX_REGEX = re.compile(r'^(?:hz|p|mah|w|rpm|gb|tb|mhz|k\b)', re.IGNORECASE)


def is_accessory_or_part(title: str, content: str = "") -> bool:
    """Check if title or snippet indicates an accessory or spare part rather than a complete laptop."""
    combined = f"{title} {content}"
    # If explicitly mentioning 'laptop charger' or 'replacement battery', reject
    if ACCESSORY_REGEX.search(combined):
        # Allow if it clearly says 'laptop with charger' or 'comes with charger'
        if re.search(r'laptop\s+(?:with|including|\+)\s+(?:original\s+)?charger', combined, re.IGNORECASE):
            return False
        return True
    return False


def extract_price_from_text(text: str) -> Optional[float]:
    """
    Extract genuine INR price from listing text or title.
    Strictly requires currency identifiers or price context to avoid
    confusing CPU/GPU model numbers (e.g., RTX 3060, i7-11800H) with prices.
    Accepts prices between 4,000 INR and 400,000 INR.
    """
    if not text:
        return None

    # Normalization: replace non-breaking spaces
    clean_text = text.replace('\xa0', ' ')

    # 1. Price pattern with 'k' suffix e.g., ₹45k, Rs 38k, 42k INR, 42k Rs
    k_patterns = [
        r'(?:₹|rs\.?|inr)\s*([0-9]{1,3}(?:\.[0-9]+)?)\s*k\b',
        r'\b([0-9]{1,3}(?:\.[0-9]+)?)\s*k\s*(?:inr|rs\.?|₹)',
        r'₹\s*([0-9]{1,3}(?:\.[0-9]+)?)\s*k\b',
    ]
    for kp in k_patterns:
        k_matches = re.finditer(kp, clean_text, re.IGNORECASE)
        for m in k_matches:
            try:
                val = float(m.group(1)) * 1000
                if 4000 <= val <= 400000:
                    return float(val)
            except ValueError:
                pass

    # 2. Strict currency-anchored patterns
    # e.g., ₹ 45,000, Rs. 35,000, INR 52000, Price: 42,000
    patterns = [
        # ₹ 45,000 or ₹45000 or Rs. 45000 or INR 45,000
        r'(?:₹|rs\.?|inr)\s*([0-9]+(?:,[0-9]+)*(?:\.[0-9]{1,2})?)\b',
        # 45,000 INR or 45000 Rs or 45,000 ₹
        r'\b([0-9]+(?:,[0-9]+)*(?:\.[0-9]{1,2})?)\s*(?:inr|rs\.?|₹)\b',
        # price: 45,000 or price is 45000
        r'(?:price|priced at|cost)\s*[:=]?\s*(?:₹|rs\.?|inr)?\s*([0-9]+(?:,[0-9]+)*(?:\.[0-9]{1,2})?)\b',
    ]

    for pat in patterns:
        for match in re.finditer(pat, clean_text, re.IGNORECASE):
            # Check what immediately preceded the match
            start_pos = match.start()
            prefix = clean_text[max(0, start_pos - 15):start_pos]
            if HW_PREFIX_REGEX.search(prefix):
                continue

            num_str = match.group(1).replace(',', '').strip()
            try:
                price = float(num_str)
                # Check suffix
                end_pos = match.end()
                suffix = clean_text[end_pos:min(len(clean_text), end_pos + 5)].strip()
                if HW_SUFFIX_REGEX.search(suffix):
                    continue

                if 4000 <= price <= 400000:
                    return price
            except ValueError:
                continue

    return None


def extract_condition(text: str) -> Optional[str]:
    """Extract laptop physical/operational condition from text."""
    if not text:
        return None
    lower = text.lower()
    if "open box" in lower or "like new" in lower or "mint condition" in lower:
        return "Like New"
    if "refurbished" in lower or "certified refurbished" in lower:
        return "Refurbished"
    if "excellent condition" in lower:
        return "Excellent"
    if "good condition" in lower or "working condition" in lower:
        return "Good"
    if "fair condition" in lower or "used" in lower or "second hand" in lower or "pre-owned" in lower:
        return "Used"
    return None


async def query_freesea_api(query: str, max_results: int = 15) -> List[Dict[str, Any]]:
    """Execute live web search via Freesea API."""
    if not FREESEA_API_KEY:
        return []

    headers = {
        "Authorization": f"Bearer {FREESEA_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "query": query,
        "max_results": max_results,
        "search_depth": "basic",
        "country": "IN"
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(FREESEA_API_URL, json=payload, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, dict):
                    return data.get("results", [])
    except Exception as e:
        print(f"Freesea search error for query '{query}': {e}")

    return []


def parse_and_validate_listings(
    raw_results: List[Dict[str, Any]],
    brand: str,
    model: str,
    match_type: str = "exact",
    specs: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """Parse raw search results, filter accessories, extract prices, and structure listings."""
    validated = []
    seen_urls = set()

    for item in raw_results:
        # Ignore sponsored ads
        if item.get("type") == "sponsored":
            continue

        url = item.get("url", "").strip()
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)

        title = item.get("title", "").strip()
        content = item.get("content", "").strip()

        # Reject accessories / spare parts
        if is_accessory_or_part(title, content):
            continue

        # Extract price from title first, then content
        price = extract_price_from_text(title)
        if price is None:
            price = extract_price_from_text(content)

        domain = item.get("domain", "")
        if not domain and "/" in url:
            try:
                domain = url.split("/")[2]
            except Exception:
                domain = "Web Listing"

        condition = extract_condition(f"{title} {content}")
        listing_date = item.get("published_date")

        specs_dict = specs or {}

        validated.append({
            "brand": brand,
            "model": model,
            "processor": specs_dict.get("cpu"),
            "ram_gb": specs_dict.get("ram"),
            "storage_gb": specs_dict.get("storage_capacity_gb"),
            "storage_type": specs_dict.get("storage_type"),
            "gpu": specs_dict.get("gpu"),
            "screen_size": specs_dict.get("screen_size"),
            "title": title,
            "price_inr": price,
            "currency": "INR",
            "condition": condition,
            "source_url": url,
            "source_name": domain,
            "listing_date": listing_date,
            "match_type": match_type,
            "raw_content": content[:500],
            "collected_at": datetime.utcnow().isoformat()
        })

    return validated


def get_processor_family_keyword(cpu: str) -> str:
    """Extract a broad search keyword for similar processor fallback."""
    if not cpu:
        return ""
    cpu_lower = cpu.lower()
    if "i9" in cpu_lower:
        return "Core i9"
    if "i7" in cpu_lower:
        return "Core i7"
    if "i5" in cpu_lower:
        return "Core i5"
    if "i3" in cpu_lower:
        return "Core i3"
    if "ryzen 9" in cpu_lower:
        return "Ryzen 9"
    if "ryzen 7" in cpu_lower:
        return "Ryzen 7"
    if "ryzen 5" in cpu_lower:
        return "Ryzen 5"
    if "ryzen 3" in cpu_lower:
        return "Ryzen 3"
    if "m2" in cpu_lower:
        return "Apple M2"
    if "m1" in cpu_lower:
        return "Apple M1"
    return cpu.split()[0] if cpu.split() else ""


async def collect_and_match_resale_listings(
    brand: str,
    model: str,
    cpu: str,
    ram: int,
    gpu: str,
    storage_capacity_gb: int,
    storage_type: str,
    screen_size: float
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Two-stage search and matching:
    1. Exact Model Search.
    2. Fallback Similar Specification Search if exact priced listings < 3.
    3. Persist valid listings to SQLite database and query existing stored listings.
    """
    specs = {
        "brand": brand,
        "model": model,
        "cpu": cpu,
        "ram": ram,
        "gpu": gpu,
        "storage_capacity_gb": storage_capacity_gb,
        "storage_type": storage_type,
        "screen_size": screen_size
    }

    all_listings: List[Dict[str, Any]] = []
    seen_urls = set()

    # Stage 1: Search Exact Model online
    exact_query = f'"{brand}" "{model}" used laptop price India'
    exact_raw = await query_freesea_api(exact_query, max_results=15)
    exact_parsed = parse_and_validate_listings(
        exact_raw, brand=brand, model=model, match_type="exact", specs=specs
    )

    for l in exact_parsed:
        if l["source_url"] not in seen_urls:
            seen_urls.add(l["source_url"])
            all_listings.append(l)

    # Check local SQLite store for exact matches
    stored_exact = get_stored_listings(brand=brand, model=model)
    for l in stored_exact:
        if l["source_url"] not in seen_urls:
            seen_urls.add(l["source_url"])
            l["match_type"] = "exact"
            all_listings.append(l)

    # Count priced exact listings
    priced_exact = [l for l in all_listings if l.get("price_inr") is not None and l.get("match_type") == "exact"]

    # Stage 2: If exact priced listings < 3, run Similar Specification Search
    if len(priced_exact) < 3:
        cpu_kw = get_processor_family_keyword(cpu)
        sim_query = f'"{brand}" {cpu_kw} {ram}GB used laptop price India'.strip()
        sim_raw = await query_freesea_api(sim_query, max_results=15)
        sim_parsed = parse_and_validate_listings(
            sim_raw, brand=brand, model=model, match_type="similar", specs=specs
        )

        for l in sim_parsed:
            if l["source_url"] not in seen_urls:
                seen_urls.add(l["source_url"])
                all_listings.append(l)

        # Also check local SQLite store for similar matches by brand and ram
        stored_sim = get_stored_listings(brand=brand, ram_gb=ram)
        for l in stored_sim:
            if l["source_url"] not in seen_urls:
                seen_urls.add(l["source_url"])
                l["match_type"] = "similar"
                all_listings.append(l)

    # Save newly retrieved listings to SQLite DB for persistent storage
    save_listings(all_listings)

    # Calculate valuation metrics
    valuation = calculate_resale_metrics(all_listings)
    return all_listings, valuation


def calculate_resale_metrics(listings: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate median asking price, price range, match quality, and confidence level.
    Requires at least 3 comparable listings with valid prices.
    """
    priced_listings = [l for l in listings if l.get("price_inr") is not None]

    exact_priced = [l for l in priced_listings if l.get("match_type") == "exact"]
    similar_priced = [l for l in priced_listings if l.get("match_type") == "similar"]

    exact_count = len(exact_priced)
    similar_count = len(similar_priced)
    total_priced = len(priced_listings)

    if total_priced < 3:
        return {
            "has_estimate": False,
            "status": "insufficient_data",
            "comparable_count": total_priced,
            "exact_matches_count": exact_count,
            "similar_matches_count": similar_count,
            "reason": f"Insufficient comparable listings with valid prices (found {total_priced}, minimum 3 required)."
        }

    prices = sorted([float(l["price_inr"]) for l in priced_listings])
    n = len(prices)

    # Calculate median
    if n % 2 == 1:
        median_price = prices[n // 2]
    else:
        median_price = (prices[n // 2 - 1] + prices[n // 2]) / 2.0

    # Calculate IQR-based or quantile price range
    # Q1 (25th percentile) and Q3 (75th percentile)
    if n == 3:
        range_min = prices[0]
        range_max = prices[-1]
    else:
        q1_idx = max(0, int(math.floor(0.25 * (n - 1))))
        q3_idx = min(n - 1, int(math.ceil(0.75 * (n - 1))))
        range_min = prices[q1_idx]
        range_max = prices[q3_idx]

    # Ensure range has a sensible minimum spread (at least 5% around median)
    if range_max <= range_min:
        range_min = round(median_price * 0.92, -2)
        range_max = round(median_price * 1.08, -2)

    # Determine match quality
    if exact_count > 0 and similar_count == 0:
        match_quality = "exact"
    elif exact_count == 0 and similar_count > 0:
        match_quality = "similar"
    else:
        match_quality = "mixed"

    # Determine confidence level
    # High: >= 5 exact matches with tight spread
    # Medium: 3-4 exact matches OR >= 5 mixed/similar
    # Low: 3-4 similar/mixed or high price dispersion
    spread_ratio = (range_max - range_min) / median_price if median_price > 0 else 1.0

    if exact_count >= 5 and spread_ratio <= 0.40:
        confidence_level = "high"
    elif exact_count >= 3 or (total_priced >= 5 and spread_ratio <= 0.60):
        confidence_level = "medium"
    else:
        confidence_level = "low"

    return {
        "has_estimate": True,
        "status": "success",
        "estimated_value_inr": round(median_price, -2) if median_price > 1000 else round(median_price, 2),
        "estimated_range_min_inr": round(range_min, -2) if range_min > 1000 else round(range_min, 2),
        "estimated_range_max_inr": round(range_max, -2) if range_max > 1000 else round(range_max, 2),
        "comparable_count": total_priced,
        "exact_matches_count": exact_count,
        "similar_matches_count": similar_count,
        "match_quality": match_quality,
        "confidence_level": confidence_level,
    }
