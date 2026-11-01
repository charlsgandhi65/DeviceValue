import sqlite3
import os
from typing import List, Dict, Optional, Any
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "resale_listings.db")


def get_db_connection():
    """Create and return a database connection with row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the SQLite database schema for resale listings."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resale_listings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand TEXT NOT NULL,
            model TEXT,
            processor TEXT,
            ram_gb INTEGER,
            storage_gb INTEGER,
            storage_type TEXT,
            gpu TEXT,
            screen_size REAL,
            title TEXT NOT NULL,
            price_inr REAL,
            currency TEXT DEFAULT 'INR',
            condition TEXT,
            source_url TEXT UNIQUE NOT NULL,
            source_name TEXT NOT NULL,
            listing_date TEXT,
            match_type TEXT DEFAULT 'exact',
            raw_content TEXT,
            collected_at TEXT NOT NULL
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_resale_brand_model ON resale_listings(brand, model);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_resale_price ON resale_listings(price_inr);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_resale_match_type ON resale_listings(match_type);")
    conn.commit()
    conn.close()


def save_listings(listings: List[Dict[str, Any]]) -> int:
    """
    Save validated listing records to SQLite database.
    Deduplicates by source_url (ON CONFLICT IGNORE).
    Returns the number of newly inserted listings.
    """
    if not listings:
        return 0

    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    inserted_count = 0

    for item in listings:
        url = item.get("source_url")
        if not url:
            continue

        collected_at = item.get("collected_at") or datetime.utcnow().isoformat()
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO resale_listings (
                    brand, model, processor, ram_gb, storage_gb, storage_type,
                    gpu, screen_size, title, price_inr, currency, condition,
                    source_url, source_name, listing_date, match_type,
                    raw_content, collected_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item.get("brand", "").strip(),
                item.get("model", "").strip() or None,
                item.get("processor", "").strip() or None,
                item.get("ram_gb"),
                item.get("storage_gb"),
                item.get("storage_type"),
                item.get("gpu", "").strip() or None,
                item.get("screen_size"),
                item.get("title", "").strip(),
                item.get("price_inr"),
                item.get("currency", "INR"),
                item.get("condition"),
                url.strip(),
                item.get("source_name", "Unknown").strip(),
                item.get("listing_date"),
                item.get("match_type", "exact"),
                item.get("raw_content", ""),
                collected_at
            ))
            if cursor.rowcount > 0:
                inserted_count += 1
        except Exception as e:
            print(f"Error saving listing to DB: {e}")

    conn.commit()
    conn.close()
    return inserted_count


def get_stored_listings(
    brand: str,
    model: Optional[str] = None,
    ram_gb: Optional[int] = None,
    min_price: float = 4000.0,
    max_price: float = 400000.0
) -> List[Dict[str, Any]]:
    """Retrieve stored comparable listings from the database."""
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM resale_listings WHERE price_inr >= ? AND price_inr <= ?"
    params: List[Any] = [min_price, max_price]

    if brand:
        query += " AND LOWER(brand) = LOWER(?)"
        params.append(brand.strip())

    if model:
        # Search for model keyword inside model or title
        query += " AND (LOWER(model) LIKE ? OR LOWER(title) LIKE ?)"
        model_term = f"%{model.strip().lower()}%"
        params.extend([model_term, model_term])

    if ram_gb:
        query += " AND (ram_gb = ? OR ram_gb IS NULL)"
        params.append(ram_gb)

    query += " ORDER BY collected_at DESC LIMIT 50"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    results = [dict(row) for row in rows]
    conn.close()
    return results


def count_listings() -> int:
    """Return total number of saved resale listings."""
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM resale_listings")
    count = cursor.fetchone()[0]
    conn.close()
    return count
