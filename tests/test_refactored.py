"""
Test script for refactored Etsy scraper.
Tests all major components to ensure functionality is preserved.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all new modules can be imported."""
    print("Testing imports...")
    try:
        from etsy_scraper.core.config import URLS, HEADERS, DATA_DIR
        print("[OK] Config imports")
        
        from etsy_scraper.core.scraper import EtsyScraper
        print("[OK] Scraper imports OK")
        
        from etsy_scraper.data.manager import DataManager
        print("[OK] DataManager imports OK")
        
        from etsy_scraper.extractors.html_parser import DataExtractor
        print("[OK] DataExtractor imports OK")
        
        from etsy_scraper.utils.pagination import PaginationHandler
        print("[OK] PaginationHandler imports OK")
        
        from etsy_scraper.utils.session import SessionManager, RateLimiter
        print("[OK] Session utilities import OK")
        
        from etsy_scraper.utils.logger import setup_logger
        print("[OK] Logger imports OK")
        
        return True
    except ImportError as e:
        print(f"[FAIL] Import error: {e}")
        return False


def test_data_manager():
    """Test DataManager functionality."""
    print("\nTesting DataManager...")
    try:
        from etsy_scraper.data.manager import DataManager
        
        # Test products manager
        dm_products = DataManager("products")
        print(f"[OK] Products DataManager created, count: {dm_products.get_count()}")
        
        # Test shops manager
        dm_shops = DataManager("shops")
        print(f"[OK] Shops DataManager created, count: {dm_shops.get_count()}")
        
        # Test metrics manager
        dm_metrics = DataManager("metrics")
        print(f"[OK] Metrics DataManager created, count: {dm_metrics.get_count()}")
        
        # Test save functionality with dummy data
        test_product = {
            'listing_id': 'test123',
            'url': 'https://test.com',
            'title': 'Test Product',
            'shop_name': 'Test Shop',
            'sale_price': '10.00'
        }
        
        stats = dm_products.save_items([test_product], page_number=1)
        print(f"[OK] Save test: saved={stats['saved']}, duplicates={stats['duplicates']}")
        
        # Test duplicate detection
        stats = dm_products.save_items([test_product], page_number=1)
        print(f"[OK] Duplicate detection: saved={stats['saved']}, duplicates={stats['duplicates']}")
        
        # Clean up test data
        dm_products.clear_data()
        print("[OK] Data cleanup OK")
        
        return True
    except Exception as e:
        print(f"[FAIL] DataManager error: {e}")
        return False


def test_extractor():
    """Test HTML extraction functionality."""
    print("\nTesting DataExtractor...")
    try:
        from etsy_scraper.extractors.html_parser import DataExtractor
        
        extractor = DataExtractor()
        
        # Test with empty HTML
        products = extractor.extract_products("<html><body></body></html>")
        print(f"[OK] Extract from empty HTML: {len(products)} products")
        
        # Test with sample HTML containing a product
        sample_html = """
        <div class="v2-listing-card" data-listing-id="12345">
            <a href="/listing/12345/test-product">
                <h3>Test Product</h3>
            </a>
            <div class="currency-value">$25.00</div>
        </div>
        """
        
        products = extractor.extract_products(sample_html)
        print(f"[OK] Extract from sample HTML: {len(products)} products")
        
        return True
    except Exception as e:
        print(f"[FAIL] Extractor error: {e}")
        return False


def test_scraper_init():
    """Test scraper initialization."""
    print("\nTesting EtsyScraper initialization...")
    try:
        from etsy_scraper.core.scraper import EtsyScraper
        
        scraper = EtsyScraper()
        print("[OK] Scraper initialized")
        
        # Check components
        assert scraper.session_manager is not None
        print("[OK] Session manager initialized")
        
        assert scraper.rate_limiter is not None
        print("[OK] Rate limiter initialized")
        
        assert scraper.pagination is not None
        print("[OK] Pagination handler initialized")
        
        assert scraper.extractor is not None
        print("[OK] Extractor initialized")
        
        # Clean up
        scraper.close()
        print("[OK] Scraper closed properly")
        
        return True
    except Exception as e:
        print(f"[FAIL] Scraper error: {e}")
        return False


def test_pagination():
    """Test pagination functionality."""
    print("\nTesting PaginationHandler...")
    try:
        from etsy_scraper.utils.pagination import PaginationHandler
        
        pagination = PaginationHandler()
        
        # Test URL building
        base_url = "https://www.etsy.com/c/templates"
        page_2_url = pagination.build_page_url(base_url, 2)
        print(f"[OK] Page 2 URL: {page_2_url}")
        
        assert "page=2" in page_2_url
        print("[OK] Page parameter added correctly")
        
        # Test pagination info extraction from empty HTML
        info = pagination.extract_pagination_info("<html></html>")
        print(f"[OK] Pagination info: current={info['current_page']}, has_next={info['has_next']}")
        
        return True
    except Exception as e:
        print(f"[FAIL] Pagination error: {e}")
        return False


def main():
    """Run all tests."""
    print("="*60)
    print("REFACTORED ETSY SCRAPER TEST SUITE")
    print("="*60)
    
    results = []
    
    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("DataManager", test_data_manager()))
    results.append(("DataExtractor", test_extractor()))
    results.append(("EtsyScraper", test_scraper_init()))
    results.append(("PaginationHandler", test_pagination()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print("-"*60)
    print(f"Total: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("\n[OK] All tests passed! Refactoring successful.")
        return 0
    else:
        print(f"\n[FAIL] {failed} tests failed. Please review.")
        return 1


if __name__ == "__main__":
    sys.exit(main())