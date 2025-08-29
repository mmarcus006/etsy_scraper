"""
Tests for core configuration module.
Tests configuration loading, path creation, and settings.
"""

import os
from pathlib import Path
import tempfile
import pytest

from etsy_scraper.core.config import (
    BASE_DIR,
    DATA_DIR,
    LOGS_DIR,
    CACHE_DIR,
    URLS,
    HEADERS,
    CURL_CONFIG,
    TIMING,
    VALIDATION,
    PRODUCT_FIELDS,
    SHOP_FIELDS,
    MAX_RETRIES,
    MAX_REQUESTS_PER_SESSION,
    MAX_SESSION_AGE,
    get_random_delay,
    LOG_LEVEL,
    PROXY_URL,
    MAX_PAGES
)


class TestConfigPaths:
    """Test configuration paths and directory creation."""
    
    def test_base_dir_exists(self):
        """Test that BASE_DIR is correctly set and exists."""
        assert BASE_DIR.exists()
        assert BASE_DIR.is_dir()
        # Should be 3 levels up from config.py
        assert (BASE_DIR / "src" / "etsy_scraper").exists()
    
    def test_data_dir_created(self):
        """Test that DATA_DIR is created."""
        assert DATA_DIR.exists()
        assert DATA_DIR.is_dir()
        assert DATA_DIR.parent == BASE_DIR
    
    def test_logs_dir_created(self):
        """Test that LOGS_DIR is created."""
        assert LOGS_DIR.exists()
        assert LOGS_DIR.is_dir()
        assert LOGS_DIR.parent == BASE_DIR
    
    def test_cache_dir_created(self):
        """Test that CACHE_DIR is created."""
        assert CACHE_DIR.exists()
        assert CACHE_DIR.is_dir()
        assert CACHE_DIR.parent == DATA_DIR


class TestConfigURLs:
    """Test URL configuration."""
    
    def test_urls_structure(self):
        """Test that URLS dictionary has required keys."""
        assert isinstance(URLS, dict)
        assert "base" in URLS
        assert "templates" in URLS
    
    def test_base_url(self):
        """Test base URL is correct."""
        assert URLS["base"] == "https://www.etsy.com"
    
    def test_templates_url(self):
        """Test templates URL is valid."""
        assert URLS["templates"].startswith("https://www.etsy.com/c/")
        assert "templates" in URLS["templates"]


class TestConfigHeaders:
    """Test request headers configuration."""
    
    def test_headers_structure(self):
        """Test that HEADERS dictionary has required keys."""
        assert isinstance(HEADERS, dict)
        assert "accept" in HEADERS
        assert "user-agent" in HEADERS
        assert "accept-language" in HEADERS
    
    def test_user_agent(self):
        """Test user agent is properly formatted."""
        ua = HEADERS["user-agent"]
        assert "Mozilla" in ua
        assert "Chrome" in ua
        assert "Safari" in ua
    
    def test_sec_headers(self):
        """Test security headers are present."""
        assert "sec-ch-ua" in HEADERS
        assert "sec-ch-ua-mobile" in HEADERS
        assert "sec-ch-ua-platform" in HEADERS
        assert "sec-fetch-dest" in HEADERS
        assert "sec-fetch-mode" in HEADERS


class TestCurlConfig:
    """Test curl-cffi configuration."""
    
    def test_curl_config_structure(self):
        """Test CURL_CONFIG has required settings."""
        assert isinstance(CURL_CONFIG, dict)
        assert "impersonate" in CURL_CONFIG
        assert "timeout" in CURL_CONFIG
        assert "verify" in CURL_CONFIG
        assert "allow_redirects" in CURL_CONFIG
        assert "http2" in CURL_CONFIG
    
    def test_impersonate_setting(self):
        """Test browser impersonation setting."""
        assert CURL_CONFIG["impersonate"] == "chrome124"
    
    def test_timeout_setting(self):
        """Test timeout is reasonable."""
        assert CURL_CONFIG["timeout"] == 30
        assert isinstance(CURL_CONFIG["timeout"], int)
    
    def test_security_settings(self):
        """Test security settings are enabled."""
        assert CURL_CONFIG["verify"] is True
        assert CURL_CONFIG["http2"] is True


class TestTimingConfig:
    """Test timing configuration."""
    
    def test_timing_structure(self):
        """Test TIMING dictionary has required keys."""
        assert isinstance(TIMING, dict)
        assert "page_min" in TIMING
        assert "page_max" in TIMING
        assert "retry_min" in TIMING
        assert "retry_max" in TIMING
        assert "block_recovery_min" in TIMING
        assert "block_recovery_max" in TIMING
    
    def test_page_timing_range(self):
        """Test page timing is reasonable."""
        assert TIMING["page_min"] >= 1.0
        assert TIMING["page_max"] >= TIMING["page_min"]
        assert TIMING["page_max"] <= 10.0
    
    def test_retry_timing_range(self):
        """Test retry timing is reasonable."""
        assert TIMING["retry_min"] >= 1
        assert TIMING["retry_max"] >= TIMING["retry_min"]
        assert TIMING["retry_max"] <= 30
    
    def test_block_recovery_timing(self):
        """Test block recovery timing is reasonable."""
        assert TIMING["block_recovery_min"] >= 10
        assert TIMING["block_recovery_max"] >= TIMING["block_recovery_min"]
        assert TIMING["block_recovery_max"] <= 120


class TestRandomDelay:
    """Test get_random_delay function."""
    
    def test_page_delay_range(self):
        """Test page delay is within expected range."""
        for _ in range(10):
            delay = get_random_delay("page")
            assert TIMING["page_min"] <= delay <= TIMING["page_max"]
    
    def test_retry_delay_range(self):
        """Test retry delay is within expected range."""
        for _ in range(10):
            delay = get_random_delay("retry")
            assert TIMING["retry_min"] <= delay <= TIMING["retry_max"]
    
    def test_block_recovery_delay_range(self):
        """Test block recovery delay is within expected range."""
        for _ in range(10):
            delay = get_random_delay("block")
            assert TIMING["block_recovery_min"] <= delay <= TIMING["block_recovery_max"]
    
    def test_default_delay_type(self):
        """Test unknown delay type uses block recovery range."""
        delay = get_random_delay("unknown")
        assert TIMING["block_recovery_min"] <= delay <= TIMING["block_recovery_max"]


class TestValidationConfig:
    """Test validation configuration."""
    
    def test_validation_structure(self):
        """Test VALIDATION dictionary has required keys."""
        assert isinstance(VALIDATION, dict)
        assert "blocked_status_codes" in VALIDATION
        assert "datadome_indicators" in VALIDATION
        assert "success_indicators" in VALIDATION
    
    def test_blocked_status_codes(self):
        """Test blocked status codes are defined."""
        codes = VALIDATION["blocked_status_codes"]
        assert isinstance(codes, list)
        assert 403 in codes
        assert 429 in codes
        assert 503 in codes
    
    def test_datadome_indicators(self):
        """Test DataDome indicators are defined."""
        indicators = VALIDATION["datadome_indicators"]
        assert isinstance(indicators, list)
        assert "x-datadome" in indicators
        assert "datadome-captcha" in indicators
    
    def test_success_indicators(self):
        """Test success indicators are defined."""
        indicators = VALIDATION["success_indicators"]
        assert isinstance(indicators, dict)
        assert "templates_page" in indicators
        assert "listing_page" in indicators
        assert "shop_page" in indicators


class TestFieldDefinitions:
    """Test CSV field definitions."""
    
    def test_product_fields(self):
        """Test product fields are comprehensive."""
        assert isinstance(PRODUCT_FIELDS, list)
        assert len(PRODUCT_FIELDS) == 19  # 19 fields as per spec
        
        # Core fields
        assert "listing_id" in PRODUCT_FIELDS
        assert "url" in PRODUCT_FIELDS
        assert "title" in PRODUCT_FIELDS
        assert "shop_name" in PRODUCT_FIELDS
        
        # Pricing fields
        assert "sale_price" in PRODUCT_FIELDS
        assert "original_price" in PRODUCT_FIELDS
        assert "discount_percentage" in PRODUCT_FIELDS
        assert "is_on_sale" in PRODUCT_FIELDS
        
        # Product attributes
        assert "is_advertisement" in PRODUCT_FIELDS
        assert "is_digital_download" in PRODUCT_FIELDS
        assert "is_bestseller" in PRODUCT_FIELDS
        assert "is_star_seller" in PRODUCT_FIELDS
        
        # Reviews
        assert "rating" in PRODUCT_FIELDS
        assert "review_count" in PRODUCT_FIELDS
        
        # Metadata
        assert "page_number" in PRODUCT_FIELDS
        assert "extraction_date" in PRODUCT_FIELDS
        assert "position_on_page" in PRODUCT_FIELDS
    
    def test_shop_fields(self):
        """Test shop fields are defined."""
        assert isinstance(SHOP_FIELDS, list)
        assert len(SHOP_FIELDS) >= 5
        
        assert "shop_name" in SHOP_FIELDS
        assert "shop_url" in SHOP_FIELDS
        assert "total_sales" in SHOP_FIELDS
        assert "admirers" in SHOP_FIELDS
        assert "extraction_date" in SHOP_FIELDS


class TestSessionConfig:
    """Test session configuration."""
    
    def test_max_retries(self):
        """Test MAX_RETRIES setting."""
        assert isinstance(MAX_RETRIES, int)
        assert MAX_RETRIES >= 1
        assert MAX_RETRIES <= 10
    
    def test_max_requests_per_session(self):
        """Test MAX_REQUESTS_PER_SESSION setting."""
        assert isinstance(MAX_REQUESTS_PER_SESSION, int)
        assert MAX_REQUESTS_PER_SESSION >= 10
        assert MAX_REQUESTS_PER_SESSION <= 100
    
    def test_max_session_age(self):
        """Test MAX_SESSION_AGE setting."""
        assert isinstance(MAX_SESSION_AGE, int)
        assert MAX_SESSION_AGE >= 60  # At least 1 minute
        assert MAX_SESSION_AGE <= 3600  # Max 1 hour


class TestEnvironmentConfig:
    """Test environment-based configuration."""
    
    def test_log_level(self):
        """Test LOG_LEVEL setting."""
        assert LOG_LEVEL in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    
    def test_proxy_url(self):
        """Test PROXY_URL can be None or string."""
        assert PROXY_URL is None or isinstance(PROXY_URL, str)
    
    def test_max_pages(self):
        """Test MAX_PAGES setting."""
        assert isinstance(MAX_PAGES, int)
        assert MAX_PAGES >= 0  # 0 means all pages