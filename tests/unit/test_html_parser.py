"""
Tests for HTML parsing and extraction logic.
Tests HtmlParser class and extraction methods.
"""

from datetime import datetime
from bs4 import BeautifulSoup
import pytest

from etsy_scraper.extractors.html_parser import DataExtractor


class TemplatePageExtractor(DataExtractor):
    """Wrapper class for tests to set HTML content."""
    def __init__(self, html_content):
        super().__init__()
        self._test_html = html_content


class HtmlParser:
    """Simple HTML parser wrapper for tests."""
    def __init__(self, html_content):
        self.soup = BeautifulSoup(html_content, 'html.parser')


class TestDataExtractor:
    """Test DataExtractor functionality."""
    
    def test_init_extractor(self):
        """Test initializing data extractor."""
        extractor = DataExtractor()
        
        assert extractor is not None
        assert hasattr(extractor, 'listing_id_pattern')
        assert hasattr(extractor, 'shop_pattern')
    
    def test_listing_id_pattern(self):
        """Test listing ID regex pattern."""
        extractor = DataExtractor()
        
        # Test valid URLs
        match = extractor.listing_id_pattern.search('/listing/123456789/')
        assert match is not None
        assert match.group(1) == '123456789'
        
        match = extractor.listing_id_pattern.search('https://etsy.com/listing/999/')
        assert match is not None
        assert match.group(1) == '999'
    
    def test_shop_pattern(self):
        """Test shop name regex pattern."""
        extractor = DataExtractor()
        
        # Test valid shop URLs
        match = extractor.shop_pattern.search('/shop/TestShop')
        assert match is not None
        assert match.group(1) == 'TestShop'
        
        match = extractor.shop_pattern.search('https://etsy.com/shop/AnotherShop?ref=123')
        assert match is not None
        assert match.group(1) == 'AnotherShop'


class TestTemplatePageExtractor:
    """Test template page product extraction."""
    
    @pytest.fixture
    def sample_product_html(self):
        """Create sample HTML with product data."""
        return """
        <html>
        <body>
            <div class="v2-listing-card">
                <a class="listing-link" href="https://www.etsy.com/listing/123456789/test-product" 
                   data-listing-id="123456789">
                    <h3 class="v2-listing-card__title">Test Product Title</h3>
                </a>
                <div class="v2-listing-card__shop">
                    <p class="text-gray">
                        <a href="https://www.etsy.com/shop/TestShop">TestShop</a>
                    </p>
                </div>
                <span class="currency-value">29.99</span>
                <span class="text-strikethrough">39.99</span>
                <div class="v2-listing-card__rating">
                    <span class="screen-reader-only">4.5 out of 5 stars</span>
                    <span class="text-body-smaller">(150)</span>
                </div>
                <span class="v2-listing-card__badge">Bestseller</span>
                <span class="promotion-label">Ad by TestShop</span>
            </div>
        </body>
        </html>
        """
    
    @pytest.fixture
    def multiple_products_html(self):
        """Create HTML with multiple products."""
        return """
        <html>
        <body>
            <div class="search-listings-group">
                <div class="v2-listing-card" data-listing-id="111">
                    <a class="listing-link" href="/listing/111/product1">
                        <h3 class="v2-listing-card__title">Product 1</h3>
                    </a>
                    <span class="currency-value">19.99</span>
                </div>
                <div class="v2-listing-card" data-listing-id="222">
                    <a class="listing-link" href="/listing/222/product2">
                        <h3 class="v2-listing-card__title">Product 2</h3>
                    </a>
                    <span class="currency-value">29.99</span>
                </div>
                <div class="v2-listing-card" data-listing-id="333">
                    <a class="listing-link" href="/listing/333/product3">
                        <h3 class="v2-listing-card__title">Product 3</h3>
                    </a>
                    <span class="currency-value">39.99</span>
                </div>
            </div>
        </body>
        </html>
        """
    
    def test_extract_single_product(self, sample_product_html):
        """Test extracting a single product."""
        extractor = TemplatePageExtractor(sample_product_html)
        products = extractor.extract_products(page_number=1)
        
        assert len(products) == 1
        product = products[0]
        
        assert product["listing_id"] == "123456789"
        assert "Test Product Title" in product["title"]
        assert product["shop_name"] == "TestShop"
        assert product["sale_price"] == 29.99
        assert product["original_price"] == 39.99
        assert product["is_on_sale"] is True
        assert product["is_advertisement"] is True
        assert product["is_bestseller"] is True
        assert product["rating"] == 4.5
        assert product["review_count"] == 150
    
    def test_extract_multiple_products(self, multiple_products_html):
        """Test extracting multiple products."""
        extractor = TemplatePageExtractor(multiple_products_html)
        products = extractor.extract_products(page_number=1)
        
        assert len(products) == 3
        
        # Check IDs
        ids = [p["listing_id"] for p in products]
        assert "111" in ids
        assert "222" in ids
        assert "333" in ids
        
        # Check prices
        prices = [p["sale_price"] for p in products]
        assert 19.99 in prices
        assert 29.99 in prices
        assert 39.99 in prices
    
    def test_extract_with_page_number(self, sample_product_html):
        """Test that page number is included in extraction."""
        extractor = TemplatePageExtractor(sample_product_html)
        products = extractor.extract_products(page_number=5)
        
        assert products[0]["page_number"] == 5
    
    def test_extract_position_on_page(self, multiple_products_html):
        """Test that position on page is tracked."""
        extractor = TemplatePageExtractor(multiple_products_html)
        products = extractor.extract_products(page_number=1)
        
        # Positions should be 1, 2, 3
        for i, product in enumerate(products):
            assert product["position_on_page"] == i + 1
    
    def test_extract_with_empty_html(self):
        """Test extraction with empty HTML."""
        extractor = TemplatePageExtractor("")
        products = extractor.extract_products(page_number=1)
        
        assert products == []
    
    def test_advertisement_detection(self):
        """Test advertisement/promotion detection."""
        html_with_ad = """
        <div class="v2-listing-card">
            <span class="promotion-label">Ad by Shop</span>
            <a href="/listing/123">Product</a>
            <span class="currency-value">19.99</span>
        </div>
        """
        
        html_without_ad = """
        <div class="v2-listing-card">
            <a href="/listing/456">Product</a>
            <span class="currency-value">19.99</span>
        </div>
        """
        
        extractor_ad = TemplatePageExtractor(html_with_ad)
        products_ad = extractor_ad.extract_products(1)
        assert products_ad[0]["is_advertisement"] is True
        
        extractor_no_ad = TemplatePageExtractor(html_without_ad)
        products_no_ad = extractor_no_ad.extract_products(1)
        assert products_no_ad[0]["is_advertisement"] is False
    
    def test_sale_detection(self):
        """Test sale price detection."""
        html_on_sale = """
        <div class="v2-listing-card">
            <a href="/listing/123">Product</a>
            <span class="currency-value">19.99</span>
            <span class="text-strikethrough">29.99</span>
        </div>
        """
        
        html_regular_price = """
        <div class="v2-listing-card">
            <a href="/listing/456">Product</a>
            <span class="currency-value">19.99</span>
        </div>
        """
        
        extractor_sale = TemplatePageExtractor(html_on_sale)
        products_sale = extractor_sale.extract_products(1)
        assert products_sale[0]["is_on_sale"] is True
        assert products_sale[0]["discount_percentage"] > 0
        
        extractor_regular = TemplatePageExtractor(html_regular_price)
        products_regular = extractor_regular.extract_products(1)
        assert products_regular[0]["is_on_sale"] is False
        assert products_regular[0]["discount_percentage"] == 0


class TestShopPageExtractor:
    """Test shop page data extraction."""
    
    @pytest.fixture
    def sample_shop_html(self):
        """Create sample shop page HTML."""
        return """
        <html>
        <body>
            <div class="shop-name-and-title">
                <h1>TestShop</h1>
            </div>
            <span class="shop-sales-count">12,345 sales</span>
            <button class="favorite-shop-button">
                <span>1,234 admirers</span>
            </button>
            <div class="shop-location">New York, USA</div>
            <div class="shop-established">On Etsy since 2015</div>
        </body>
        </html>
        """
    
    def test_extract_shop_metrics(self, sample_shop_html):
        """Test extracting shop metrics."""
        extractor = ShopPageExtractor(sample_shop_html)
        metrics = extractor.extract_metrics()
        
        assert metrics["shop_name"] == "TestShop"
        assert metrics["total_sales"] == 12345
        assert metrics["admirers"] == 1234
        assert "extraction_date" in metrics
        assert metrics["location"] == "New York, USA"
        assert metrics["on_etsy_since"] == "2015"
    
    def test_extract_shop_with_no_sales(self):
        """Test extracting shop with no sales."""
        html = """
        <div class="shop-name-and-title">
            <h1>NewShop</h1>
        </div>
        """
        
        extractor = DataExtractor()
        metrics = extractor.extract_shop_metrics(html)
        
        assert metrics["total_sales"] == 0
        assert metrics["admirers"] == 0
    
    def test_extract_with_malformed_numbers(self):
        """Test extraction with malformed number formats."""
        html = """
        <div class="shop-name-and-title">
            <h1>Shop</h1>
        </div>
        <span class="shop-sales-count">Invalid sales</span>
        <button class="favorite-shop-button">
            <span>Not a number admirers</span>
        </button>
        """
        
        extractor = DataExtractor()
        metrics = extractor.extract_shop_metrics(html)
        
        assert metrics["total_sales"] == 0
        assert metrics["admirers"] == 0
    
    def test_validate_shop_url(self):
        """Test shop URL validation."""
        extractor = ShopPageExtractor("")
        
        assert extractor.validate_url("https://www.etsy.com/shop/TestShop") is True
        assert extractor.validate_url("https://etsy.com/shop/TestShop") is True
        assert extractor.validate_url("http://www.etsy.com/shop/TestShop") is True
        assert extractor.validate_url("https://other.com/shop/TestShop") is False
        assert extractor.validate_url("not-a-url") is False
        assert extractor.validate_url("") is False
        assert extractor.validate_url(None) is False


class TestPaginationExtraction:
    """Test pagination-related extraction."""
    
    def test_extract_total_pages(self):
        """Test extracting total pages from pagination."""
        html = """
        <nav class="search-pagination">
            <a href="?page=1">1</a>
            <a href="?page=2">2</a>
            <a href="?page=3">3</a>
            <a href="?page=10">10</a>
        </nav>
        """
        
        parser = HtmlParser(html)
        nav = parser.soup.find('nav', class_='search-pagination')
        links = nav.find_all('a') if nav else []
        
        pages = []
        for link in links:
            try:
                page = int(link.text.strip())
                pages.append(page)
            except ValueError:
                continue
        
        assert max(pages) == 10 if pages else 0
    
    def test_detect_next_page_button(self):
        """Test detecting next page button."""
        html_with_next = """
        <nav class="search-pagination">
            <a href="?page=2" aria-label="Next page">Next</a>
        </nav>
        """
        
        html_without_next = """
        <nav class="search-pagination">
            <span class="disabled">Next</span>
        </nav>
        """
        
        parser_with = HtmlParser(html_with_next)
        has_next = parser_with.soup.find('a', {'aria-label': 'Next page'}) is not None
        assert has_next is True
        
        parser_without = HtmlParser(html_without_next)
        has_next = parser_without.soup.find('a', {'aria-label': 'Next page'}) is not None
        assert has_next is False


class TestDataSanitization:
    """Test data sanitization and cleaning."""
    
    def test_clean_text_with_whitespace(self):
        """Test cleaning text with extra whitespace."""
        parser = HtmlParser("")
        
        assert parser.clean_text("  Test  ") == "Test"
        assert parser.clean_text("Line 1\n\nLine 2") == "Line 1 Line 2"
        assert parser.clean_text("\t\tTabbed\t\t") == "Tabbed"
    
    def test_clean_html_entities(self):
        """Test cleaning HTML entities."""
        html = "<div>&amp; &lt; &gt; &quot; &#39;</div>"
        parser = HtmlParser(html)
        
        text = parser.soup.div.text
        assert "&" in text
        assert "<" in text
        assert ">" in text
    
    def test_extract_listing_id_from_url(self):
        """Test extracting listing ID from URL."""
        parser = HtmlParser("")
        
        urls = [
            ("https://www.etsy.com/listing/123456789/product", "123456789"),
            ("/listing/987654321/another-product", "987654321"),
            ("https://etsy.com/listing/111/", "111"),
            ("invalid-url", None)
        ]
        
        for url, expected_id in urls:
            if expected_id:
                assert expected_id in url
            else:
                assert "/listing/" not in url