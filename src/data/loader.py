import os
import re
import unicodedata
import uuid
import logging
from typing import List, Optional
import pandas as pd
from datasets import load_dataset
from src.models.restaurant import Restaurant

logger = logging.getLogger(__name__)

CACHE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'restaurants.parquet')

TEXT_COLUMNS_TO_CLEAN = ['name', 'location', 'cuisines', 'address']
DEDUPE_KEY = ['name', 'location', 'address']

def _fix_mojibake(text: str) -> str:
    """Reverse UTF-8 bytes that were mistakenly decoded as Latin-1, possibly
    several times over (a known artifact of this source dataset, e.g. 'Cafe'
    with an accented e turning into 'CafÃÂÂ©'). Safe no-op on clean text."""
    previous = None
    attempts = 0
    while text != previous and attempts < 10:
        previous = text
        try:
            text = text.encode('latin1').decode('utf-8')
        except (UnicodeDecodeError, UnicodeEncodeError):
            break
        attempts += 1
    return text

def clean_text(value: object) -> object:
    """Repair mojibake and transliterate to plain English letters/numbers/punctuation."""
    if not isinstance(value, str):
        return value
    fixed = _fix_mojibake(value)
    ascii_text = unicodedata.normalize('NFKD', fixed).encode('ascii', 'ignore').decode('ascii')
    return re.sub(r'\s+', ' ', ascii_text).strip()

def _normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Clean display text and collapse duplicate listings.

    The source dataset repeats each physical restaurant once per Zomato
    listing category (Delivery, Dine-out, Desserts, ...), so the same
    name/location/address combination can appear many times. Keep the
    most-voted (then highest-rated) row for each.
    """
    for col in TEXT_COLUMNS_TO_CLEAN:
        if col in df.columns:
            df[col] = df[col].apply(clean_text)

    df = df.sort_values(['votes', 'rating'], ascending=[False, False])
    df = df.drop_duplicates(subset=DEDUPE_KEY, keep='first')
    return df.reset_index(drop=True)

def parse_rating(rate_str: str) -> float:
    """Parse rating from strings like '4.1/5', 'NEW', '-'"""
    if not isinstance(rate_str, str):
        return 0.0
    rate_str = rate_str.strip()
    if rate_str in ("NEW", "-", ""):
        return 0.0
    try:
        return float(rate_str.split('/')[0].strip())
    except Exception:
        return 0.0

def parse_cost(cost_str: str) -> int:
    """Parse cost from strings like '800', '1,200'"""
    if not isinstance(cost_str, str):
        if pd.isna(cost_str):
            return 0
        return int(cost_str)
    cost_str = cost_str.replace(',', '').strip()
    if not cost_str:
        return 0
    try:
        return int(cost_str)
    except Exception:
        return 0

def get_budget_tier(cost: int) -> str:
    """Derive budget tier from cost"""
    if cost <= 300:
        return "low"
    elif cost <= 700:
        return "medium"
    else:
        return "high"

def load_zomato_dataset() -> List[Restaurant]:
    """Loads dataset from Parquet cache if available, else from Hugging Face."""
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)

    if os.path.exists(CACHE_PATH):
        logger.info(f"Loading dataset from cache: {CACHE_PATH}")
        df = pd.read_parquet(CACHE_PATH)
        rows_before = len(df)
        df = _normalize_dataframe(df)
        if len(df) != rows_before:
            logger.info(
                f"Cache had {rows_before} rows; cleaned text and removed duplicate "
                f"listings, leaving {len(df)}. Re-saving cache."
            )
            df.to_parquet(CACHE_PATH, index=False)
    else:
        logger.info("Downloading dataset from Hugging Face...")
        dataset = load_dataset("ManikaSaini/zomato-restaurant-recommendation")
        df = dataset['train'].to_pandas()

        logger.info("Cleaning and normalizing data...")
        df['id'] = [str(uuid.uuid4()) for _ in range(len(df))]
        df['rating'] = df['rate'].apply(parse_rating)
        df['cost_for_two'] = df['approx_cost(for two people)'].apply(parse_cost)
        df['budget_tier'] = df['cost_for_two'].apply(get_budget_tier)

        # Fill NA values
        df['name'] = df['name'].fillna("Unknown")
        df['location'] = df['location'].fillna("Unknown")
        df['cuisines'] = df['cuisines'].fillna("Unknown")
        df['address'] = df['address'].fillna("")
        df['votes'] = df['votes'].fillna(0)
        df['listed_in(city)'] = 'Bangalore'

        df = _normalize_dataframe(df)

        logger.info(f"Saving dataset to cache: {CACHE_PATH}")
        df.to_parquet(CACHE_PATH, index=False)

    restaurants = []
    for _, row in df.iterrows():
        # skip rows without names
        if row['name'] == "Unknown" or not row['name']:
            continue
            
        restaurants.append(
            Restaurant(
                id=str(row['id']),
                name=str(row['name']),
                location=str(row['location']),
                cuisine=str(row['cuisines']),
                rating=float(row['rating']),
                cost_for_two=int(row['cost_for_two']),
                budget_tier=str(row['budget_tier']),
                address=str(row['address']) if row['address'] else None,
                votes=int(row['votes']) if pd.notna(row['votes']) else 0
            )
        )
    
    logger.info(f"Loaded {len(restaurants)} restaurants")
    return restaurants
