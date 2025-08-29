"""
Unified configuration for Etsy scraper.
Merges all configuration settings into a single source of truth.
"""

import os
import random
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
CACHE_DIR = DATA_DIR / "cache"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
CACHE_DIR.mkdir(exist_ok=True)

# URLs for scraping
URLS = {
    "base": "https://www.etsy.com",
    "templates": "https://www.etsy.com/c/paper-and-party-supplies/paper/stationery/design-and-templates/templates/personal-finance-templates?explicit=1&ref=catcard-12487-1840465169",
}

# Request headers for curl-cffi
HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=0, i",
    "sec-ch-ua": '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
}

# curl-cffi configuration
CURL_CONFIG = {
    "impersonate": "chrome124",
    "timeout": 30,
    "verify": True,
    "allow_redirects": True,
    "http2": True
}

# Timing settings (in seconds)
TIMING = {
    "page_min": 1.0,
    "page_max": 3.0,
    "retry_min": 5,
    "retry_max": 10,
    "block_recovery_min": 30,
    "block_recovery_max": 60
}

def get_random_delay(delay_type="page"):
    """Get random delay for human-like behavior."""
    if delay_type == "page":
        return random.uniform(TIMING["page_min"], TIMING["page_max"])
    elif delay_type == "retry":
        return random.uniform(TIMING["retry_min"], TIMING["retry_max"])
    else:
        return random.uniform(TIMING["block_recovery_min"], TIMING["block_recovery_max"])

# Session settings
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
MAX_REQUESTS_PER_SESSION = 50
MAX_SESSION_AGE = 300  # 5 minutes

# Validation settings
VALIDATION = {
    "blocked_status_codes": [403, 429, 503],
    "datadome_indicators": ["x-datadome", "datadome-captcha", "dd-protection"],
    "success_indicators": {
        "templates_page": ["personal-finance-templates", "templates"],
        "listing_page": ["listing-id"],
        "shop_page": ["shop-name"]
    }
}

# CSV field names
PRODUCT_FIELDS = [
    'listing_id', 'url', 'title', 'shop_name', 'shop_url',
    'sale_price', 'original_price', 'discount_percentage', 'is_on_sale',
    'is_advertisement', 'is_digital_download', 'is_bestseller', 'is_star_seller',
    'rating', 'review_count', 'free_shipping',
    'page_number', 'extraction_date', 'position_on_page'
]

SHOP_FIELDS = [
    'shop_name', 'shop_url', 'total_sales', 'admirers',
    'extraction_date', 'url_valid'
]

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Environment-based settings
PROXY_URL = os.getenv("PROXY_URL")
MAX_PAGES = int(os.getenv("MAX_PAGES_TO_SCRAPE", "0"))  # 0 means all pages