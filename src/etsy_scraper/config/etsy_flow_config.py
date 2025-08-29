"""
Configuration for Etsy flow replication
Extracted from HAR file analysis
"""

import random
from typing import Dict, List

# URLs for scraping
URLS = {
    "templates": "https://www.etsy.com/c/paper-and-party-supplies/paper/stationery/design-and-templates/templates/personal-finance-templates?explicit=1&ref=catcard-12487-1840465169",
    # Base URL for templates category - pagination will be added dynamically
}

# Critical headers from HAR file
HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=0, i",
    "sec-ch-dpr": "1.25",
    "sec-ch-ua": '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
    "sec-ch-ua-arch": '"x86"',
    "sec-ch-ua-bitness": '"64"',
    "sec-ch-ua-full-version-list": '"Not;A=Brand";v="99.0.0.0", "Google Chrome";v="139.0.7258.66", "Chromium";v="139.0.7258.66"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-ch-ua-platform-version": '"19.0.0"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
}

# Session tracking parameters from HAR
SESSION_PARAMS = {
    "ebid": "I7rGrwlynzGIOOYmrmt4OLi_YtbUyBpm",
    "browser_id": "fo1UQcz29vAy704zUg5ErpGlErzk",
    "uaid": "1128160381"
}

# Timing configuration (in seconds)
TIMING = {
    "page_navigation": {
        "min": 3,
        "max": 8,
        "description": "Delay between pagination pages"
    },
    "action_delay": {
        "min": 0.5,
        "max": 2.0
    },
    "scroll_delay": {
        "min": 0.3,
        "max": 1.0
    },
    "retry_delay": {
        "min": 5,
        "max": 10,
        "description": "Delay before retrying failed request"
    },
    "block_recovery": {
        "min": 30,
        "max": 60,
        "description": "Delay after detecting bot block"
    }
}

def get_random_delay(delay_type: str) -> float:
    """Get a random delay within the specified range."""
    timing = TIMING.get(delay_type, TIMING["action_delay"])
    return random.uniform(timing["min"], timing["max"])

# Browser viewport settings
VIEWPORT = {
    "width": 1920,
    "height": 1080,
    "device_scale_factor": 1.25  # From HAR sec-ch-dpr
}

# Proxy configuration (optional)
PROXY_CONFIG = {
    "enabled": False,
    "http": None,
    "https": None
}

# Validation criteria
VALIDATION = {
    "expected_status_codes": [200, 304],
    "blocked_status_codes": [403, 429, 503],
    "datadome_indicators": [
        "x-datadome",
        "datadome-captcha",
        "dd-protection"
    ],
    "success_indicators": {
        "templates_page": ["personal-finance-templates", "templates"],
        "listing_page": ["listing-id", "adhd-adult-digital"],
        "shop_page": ["CustomGroupGifts", "shop-name"]
    }
}

# Chrome browser arguments for Playwright
CHROME_ARGS = [
    "--disable-blink-features=AutomationControlled",
    "--disable-dev-shm-usage",
    "--no-sandbox",
    "--disable-web-security",
    "--disable-features=IsolateOrigins,site-per-process",
    "--disable-site-isolation-trials",
    "--enable-features=NetworkService,NetworkServiceInProcess",
    "--disable-accelerated-2d-canvas",
    "--disable-gpu",
    "--window-size=1920,1080",
    "--start-maximized"
]

# curl-cffi specific configuration
CURL_CFFI_CONFIG = {
    "impersonate": "chrome124",  # Latest Chrome version supported
    "timeout": 30,
    "verify": True,
    "allow_redirects": True,
    "http2": True
}