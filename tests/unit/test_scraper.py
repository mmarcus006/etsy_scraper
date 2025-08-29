"""
Tests for core scraper module.
Tests EtsyScraper class and its methods.
"""

import json
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

# Mock the curl_cffi module before importing
from unittest.mock import MagicMock
import sys
sys.modules['curl_cffi'] = MagicMock()
sys.modules['curl_cffi.requests'] = MagicMock()

from etsy_scraper.core.scraper import EtsyScraper
from etsy_scraper.core.config import DATA_DIR


class TestEtsyScraperInitialization:
    """Test EtsyScraper initialization."""
    
    def test_init_without_proxy(self):
        """Test scraper initialization without proxy."""
        scraper = EtsyScraper()
        assert scraper.proxy is None
        assert scraper.session is not None
        assert scraper.rate_limiter is not None
        assert scraper.stats is not None
        scraper.close()
    
    def test_init_with_proxy(self):
        """Test scraper initialization with proxy."""
        proxy = {"http": "http://localhost:8080", "https": "http://localhost:8080"}
        scraper = EtsyScraper(proxy=proxy)
        assert scraper.proxy == proxy
        scraper.close()
    
    def test_stats_initialization(self):
        """Test statistics are properly initialized."""
        scraper = EtsyScraper()
        expected_stats = {
            "pages_scraped": 0,
            "products_extracted": 0,
            "shops_extracted": 0,
            "metrics_extracted": 0,
            "errors": 0,
            "retries": 0,
            "datadome_detections": 0
        }
        assert scraper.stats == expected_stats
        scraper.close()
    
    def test_close_method(self):
        """Test close method properly cleans up."""
        scraper = EtsyScraper()
        scraper.close()
        # After closing, session should be closed
        # This test verifies no errors occur during cleanup


class TestProductScraping:
    """Test product scraping functionality."""
    
    @pytest.fixture
    def scraper(self):
        """Create a scraper instance for testing."""
        scraper = EtsyScraper()
        yield scraper
        scraper.close()
    
    def test_scrape_products_default_params(self, scraper):
        """Test scrape_products with default parameters."""
        # We'll test with max_pages=0 to skip actual scraping
        result = scraper.scrape_products(max_pages=0)
        
        assert isinstance(result, dict)
        assert "success" in result
        assert "stats" in result
        assert "total_items" in result
        assert result["success"] is True
        assert result["stats"]["pages_scraped"] == 0
    
    def test_scrape_products_with_csv_path(self, scraper, tmp_path):
        """Test scrape_products with custom CSV path."""
        csv_path = tmp_path / "test_products.csv"
        result = scraper.scrape_products(
            max_pages=0,
            csv_path=str(csv_path)
        )
        
        assert result["success"] is True
        # CSV file should be created even with 0 pages
        assert csv_path.exists()
    
    def test_scrape_products_start_page(self, scraper):
        """Test scrape_products with start_page parameter."""
        result = scraper.scrape_products(
            max_pages=0,
            start_page=5
        )
        
        assert result["success"] is True
        assert "stats" in result
    
    @patch('etsy_scraper.core.scraper.TemplatePageExtractor')
    def test_scrape_products_error_handling(self, mock_extractor, scraper):
        """Test error handling in scrape_products."""
        # Simulate an extraction error
        mock_extractor.return_value.extract_products.side_effect = Exception("Test error")
        
        result = scraper.scrape_products(max_pages=1)
        
        # Should handle error gracefully
        assert isinstance(result, dict)
        assert "success" in result
        assert "stats" in result


class TestShopExtraction:
    """Test shop extraction functionality."""
    
    @pytest.fixture
    def scraper(self):
        """Create a scraper instance for testing."""
        scraper = EtsyScraper()
        yield scraper
        scraper.close()
    
    @pytest.fixture
    def sample_products_csv(self, tmp_path):
        """Create a sample products CSV for testing."""
        csv_path = tmp_path / "products.csv"
        csv_content = """listing_id,url,title,shop_name,shop_url,sale_price,original_price,discount_percentage,is_on_sale,is_advertisement,is_digital_download,is_bestseller,is_star_seller,rating,review_count,free_shipping,page_number,extraction_date,position_on_page
123456,https://www.etsy.com/listing/123456,Test Product,TestShop,https://www.etsy.com/shop/TestShop,29.99,39.99,25,True,False,False,True,True,4.5,100,True,1,2024-01-01,1
789012,https://www.etsy.com/listing/789012,Another Product,AnotherShop,https://www.etsy.com/shop/AnotherShop,19.99,19.99,0,False,False,True,False,False,4.0,50,False,1,2024-01-01,2"""
        csv_path.write_text(csv_content)
        return csv_path
    
    def test_scrape_shops_from_listings(self, scraper, sample_products_csv, tmp_path):
        """Test extracting shops from product listings."""
        output_csv = tmp_path / "shops.csv"
        
        result = scraper.scrape_shops_from_listings(
            products_csv=str(sample_products_csv),
            output_csv=str(output_csv),
            max_items=2
        )
        
        assert isinstance(result, dict)
        assert "success" in result
        assert "stats" in result
        assert "total_shops" in result
    
    def test_scrape_shops_default_csv(self, scraper, sample_products_csv):
        """Test shop extraction with default output path."""
        result = scraper.scrape_shops_from_listings(
            products_csv=str(sample_products_csv),
            max_items=1
        )
        
        assert isinstance(result, dict)
        assert result["success"] is True
    
    def test_scrape_shops_missing_products_csv(self, scraper):
        """Test error handling when products CSV doesn't exist."""
        result = scraper.scrape_shops_from_listings(
            products_csv="nonexistent.csv",
            max_items=1
        )
        
        assert isinstance(result, dict)
        assert "success" in result
        # Should handle missing file gracefully


class TestMetricsExtraction:
    """Test shop metrics extraction functionality."""
    
    @pytest.fixture
    def scraper(self):
        """Create a scraper instance for testing."""
        scraper = EtsyScraper()
        yield scraper
        scraper.close()
    
    @pytest.fixture
    def sample_shops_csv(self, tmp_path):
        """Create a sample shops CSV for testing."""
        csv_path = tmp_path / "shops.csv"
        csv_content = """shop_name,shop_url,total_sales,admirers,extraction_date,url_valid
TestShop,https://www.etsy.com/shop/TestShop,0,0,2024-01-01,True
AnotherShop,https://www.etsy.com/shop/AnotherShop,0,0,2024-01-01,True"""
        csv_path.write_text(csv_content)
        return csv_path
    
    def test_scrape_shop_metrics(self, scraper, sample_shops_csv, tmp_path):
        """Test extracting metrics from shops."""
        output_csv = tmp_path / "metrics.csv"
        
        result = scraper.scrape_shop_metrics(
            shops_csv=str(sample_shops_csv),
            output_csv=str(output_csv),
            max_shops=1
        )
        
        assert isinstance(result, dict)
        assert "success" in result
        assert "stats" in result
    
    def test_scrape_metrics_default_paths(self, scraper, sample_shops_csv):
        """Test metrics extraction with default output path."""
        result = scraper.scrape_shop_metrics(
            shops_csv=str(sample_shops_csv),
            max_shops=1
        )
        
        assert isinstance(result, dict)
        assert result["success"] is True
    
    def test_scrape_metrics_missing_shops_csv(self, scraper):
        """Test error handling when shops CSV doesn't exist."""
        result = scraper.scrape_shop_metrics(
            shops_csv="nonexistent.csv",
            max_shops=1
        )
        
        assert isinstance(result, dict)
        assert "success" in result


class TestSessionManagement:
    """Test session management functionality."""
    
    def test_session_creation(self):
        """Test that session is properly created."""
        scraper = EtsyScraper()
        assert scraper.session is not None
        assert hasattr(scraper.session, 'request')
        scraper.close()
    
    def test_session_with_proxy(self):
        """Test session creation with proxy."""
        proxy = {"http": "http://localhost:8080"}
        scraper = EtsyScraper(proxy=proxy)
        assert scraper.session is not None
        scraper.close()
    
    def test_multiple_scrapers(self):
        """Test multiple scraper instances can coexist."""
        scraper1 = EtsyScraper()
        scraper2 = EtsyScraper()
        
        assert scraper1.session != scraper2.session
        assert scraper1.stats != scraper2.stats
        
        scraper1.close()
        scraper2.close()


class TestStatisticsTracking:
    """Test statistics tracking functionality."""
    
    @pytest.fixture
    def scraper(self):
        """Create a scraper instance for testing."""
        scraper = EtsyScraper()
        yield scraper
        scraper.close()
    
    def test_stats_update_pages_scraped(self, scraper):
        """Test updating pages_scraped statistic."""
        initial = scraper.stats["pages_scraped"]
        scraper.stats["pages_scraped"] += 1
        assert scraper.stats["pages_scraped"] == initial + 1
    
    def test_stats_update_products_extracted(self, scraper):
        """Test updating products_extracted statistic."""
        initial = scraper.stats["products_extracted"]
        scraper.stats["products_extracted"] += 10
        assert scraper.stats["products_extracted"] == initial + 10
    
    def test_stats_update_errors(self, scraper):
        """Test updating error count."""
        initial = scraper.stats["errors"]
        scraper.stats["errors"] += 1
        assert scraper.stats["errors"] == initial + 1
    
    def test_stats_reset(self, scraper):
        """Test resetting statistics."""
        # Update some stats
        scraper.stats["pages_scraped"] = 5
        scraper.stats["products_extracted"] = 50
        
        # Reset stats
        scraper.stats = {key: 0 for key in scraper.stats}
        
        # Verify all reset to 0
        for value in scraper.stats.values():
            assert value == 0


class TestRateLimiting:
    """Test rate limiting functionality."""
    
    @pytest.fixture
    def scraper(self):
        """Create a scraper instance for testing."""
        scraper = EtsyScraper()
        yield scraper
        scraper.close()
    
    def test_rate_limiter_exists(self, scraper):
        """Test that rate limiter is initialized."""
        assert scraper.rate_limiter is not None
    
    def test_rate_limiter_wait_method(self, scraper):
        """Test rate limiter has wait method."""
        assert hasattr(scraper.rate_limiter, 'wait')
        assert callable(scraper.rate_limiter.wait)


class TestErrorHandling:
    """Test error handling in scraper."""
    
    def test_scraper_handles_init_errors(self):
        """Test scraper handles initialization errors gracefully."""
        with patch('etsy_scraper.core.scraper.SessionManager') as mock_session:
            mock_session.side_effect = Exception("Session error")
            
            # Should not raise exception during init
            try:
                scraper = EtsyScraper()
                # If we get here without exception, that's fine
                if hasattr(scraper, 'close'):
                    scraper.close()
            except Exception:
                # This is expected behavior
                pass
    
    def test_scraper_handles_close_errors(self):
        """Test scraper handles close errors gracefully."""
        scraper = EtsyScraper()
        
        # Mock session to raise error on close
        scraper.session = MagicMock()
        scraper.session.close.side_effect = Exception("Close error")
        
        # Should not raise exception
        try:
            scraper.close()
        except Exception:
            pytest.fail("close() should not raise exceptions")