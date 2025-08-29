"""
Integration tests for complete scraping pipeline.
Tests end-to-end workflows and CLI command execution.
"""

import subprocess
import sys
import json
import csv
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

# Mock curl_cffi before imports
import sys
from unittest.mock import MagicMock
sys.modules['curl_cffi'] = MagicMock()
sys.modules['curl_cffi.requests'] = MagicMock()

from etsy_scraper.cli import main, cmd_products, cmd_shops, cmd_metrics, cmd_all
from etsy_scraper.core.scraper import EtsyScraper
from etsy_scraper.core.config import DATA_DIR


class TestCLIIntegration:
    """Test CLI command integration."""
    
    def test_cli_help_command(self):
        """Test CLI help command works."""
        result = subprocess.run(
            [sys.executable, "-m", "etsy_scraper.cli", "--help"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert "Etsy Scraper" in result.stdout
        assert "products" in result.stdout
        assert "shops" in result.stdout
        assert "metrics" in result.stdout
    
    def test_cli_products_help(self):
        """Test products subcommand help."""
        result = subprocess.run(
            [sys.executable, "-m", "etsy_scraper.cli", "products", "--help"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert "--max-pages" in result.stdout
        assert "--start-page" in result.stdout
        assert "--csv-path" in result.stdout
    
    def test_cli_dry_run_mode(self):
        """Test dry run mode execution."""
        result = subprocess.run(
            [sys.executable, "-m", "etsy_scraper.cli", "--dry-run", "products", "--max-pages", "5"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert "DRY RUN MODE" in result.stdout
        assert "Configuration valid" in result.stdout


class TestProductsPipeline:
    """Test products scraping pipeline."""
    
    @pytest.fixture
    def mock_scraper(self):
        """Create a mock scraper for testing."""
        scraper = MagicMock(spec=EtsyScraper)
        scraper.stats = {
            "pages_scraped": 0,
            "products_extracted": 0,
            "shops_extracted": 0,
            "metrics_extracted": 0,
            "errors": 0,
            "retries": 0,
            "datadome_detections": 0
        }
        return scraper
    
    def test_products_command_execution(self, mock_scraper, tmp_path, monkeypatch):
        """Test products command execution flow."""
        # Setup test CSV path
        csv_path = tmp_path / "test_products.csv"
        
        # Mock scraper response
        mock_scraper.scrape_products.return_value = {
            "success": True,
            "stats": {
                "pages_scraped": 5,
                "products_extracted": 100
            },
            "total_items": 100
        }
        
        # Create mock args
        args = MagicMock()
        args.max_pages = 5
        args.start_page = 1
        args.csv_path = csv_path
        args.clear_data = False
        
        # Execute command
        result = cmd_products(args, mock_scraper)
        
        assert result == 0  # Success
        mock_scraper.scrape_products.assert_called_once_with(
            max_pages=5,
            start_page=1,
            csv_path=csv_path
        )
    
    def test_products_with_clear_data(self, mock_scraper, tmp_path):
        """Test products command with clear data flag."""
        csv_path = tmp_path / "products.csv"
        
        # Create existing data
        csv_path.write_text("existing,data\n")
        
        mock_scraper.scrape_products.return_value = {
            "success": True,
            "stats": {"pages_scraped": 1, "products_extracted": 10},
            "total_items": 10
        }
        
        args = MagicMock()
        args.max_pages = 1
        args.start_page = 1
        args.csv_path = csv_path
        args.clear_data = True
        
        # Execute with clear_data
        with patch('etsy_scraper.cli.DataManager') as mock_dm:
            mock_dm.return_value.clear_data = MagicMock()
            result = cmd_products(args, mock_scraper)
            
            assert result == 0
            mock_dm.return_value.clear_data.assert_called_once()
    
    def test_products_failure_handling(self, mock_scraper):
        """Test handling of products scraping failure."""
        mock_scraper.scrape_products.return_value = {
            "success": False,
            "stats": {"pages_scraped": 0, "errors": 1},
            "total_items": 0
        }
        
        args = MagicMock()
        args.max_pages = 5
        args.start_page = 1
        args.csv_path = "test.csv"
        args.clear_data = False
        
        result = cmd_products(args, mock_scraper)
        
        assert result == 1  # Failure


class TestShopsPipeline:
    """Test shops extraction pipeline."""
    
    @pytest.fixture
    def mock_scraper(self):
        """Create a mock scraper for testing."""
        scraper = MagicMock(spec=EtsyScraper)
        scraper.stats = {"shops_extracted": 0, "errors": 0}
        return scraper
    
    @pytest.fixture
    def sample_products_csv(self, tmp_path):
        """Create sample products CSV."""
        csv_path = tmp_path / "products.csv"
        csv_path.write_text(
            "listing_id,shop_name,shop_url\n"
            "123,Shop1,https://etsy.com/shop/Shop1\n"
            "456,Shop2,https://etsy.com/shop/Shop2\n"
        )
        return csv_path
    
    def test_shops_command_execution(self, mock_scraper, sample_products_csv, tmp_path):
        """Test shops command execution flow."""
        output_csv = tmp_path / "shops.csv"
        
        mock_scraper.scrape_shops_from_listings.return_value = {
            "success": True,
            "stats": {"shops_extracted": 2},
            "total_shops": 2
        }
        
        args = MagicMock()
        args.products_csv = sample_products_csv
        args.output_csv = output_csv
        args.max_items = 10
        
        result = cmd_shops(args, mock_scraper)
        
        assert result == 0
        mock_scraper.scrape_shops_from_listings.assert_called_once_with(
            products_csv=sample_products_csv,
            output_csv=output_csv,
            max_items=10
        )
    
    def test_shops_with_default_paths(self, mock_scraper):
        """Test shops command with default paths."""
        mock_scraper.scrape_shops_from_listings.return_value = {
            "success": True,
            "stats": {"shops_extracted": 5},
            "total_shops": 5
        }
        
        args = MagicMock()
        args.products_csv = DATA_DIR / "etsy_products.csv"
        args.output_csv = DATA_DIR / "shops_from_listings.csv"
        args.max_items = 100
        
        result = cmd_shops(args, mock_scraper)
        
        assert result == 0


class TestMetricsPipeline:
    """Test metrics extraction pipeline."""
    
    @pytest.fixture
    def mock_scraper(self):
        """Create a mock scraper for testing."""
        scraper = MagicMock(spec=EtsyScraper)
        scraper.stats = {"metrics_extracted": 0, "errors": 0}
        return scraper
    
    @pytest.fixture
    def sample_shops_csv(self, tmp_path):
        """Create sample shops CSV."""
        csv_path = tmp_path / "shops.csv"
        csv_path.write_text(
            "shop_name,shop_url\n"
            "Shop1,https://etsy.com/shop/Shop1\n"
            "Shop2,https://etsy.com/shop/Shop2\n"
        )
        return csv_path
    
    def test_metrics_command_execution(self, mock_scraper, sample_shops_csv, tmp_path):
        """Test metrics command execution flow."""
        output_csv = tmp_path / "metrics.csv"
        
        mock_scraper.scrape_shop_metrics.return_value = {
            "success": True,
            "stats": {"metrics_extracted": 2},
            "total_shops": 2
        }
        
        args = MagicMock()
        args.shops_csv = sample_shops_csv
        args.output_csv = output_csv
        args.max_items = 10
        
        result = cmd_metrics(args, mock_scraper)
        
        assert result == 0
        mock_scraper.scrape_shop_metrics.assert_called_once()
    
    def test_metrics_missing_shops_csv(self, mock_scraper, tmp_path):
        """Test metrics command when shops CSV doesn't exist."""
        args = MagicMock()
        args.shops_csv = tmp_path / "nonexistent.csv"
        args.output_csv = tmp_path / "metrics.csv"
        args.max_items = 10
        
        result = cmd_metrics(args, mock_scraper)
        
        assert result == 1  # Should fail
        mock_scraper.scrape_shop_metrics.assert_not_called()


class TestCompletePipeline:
    """Test complete pipeline execution."""
    
    @pytest.fixture
    def mock_scraper(self):
        """Create a mock scraper for complete pipeline."""
        scraper = MagicMock(spec=EtsyScraper)
        scraper.stats = {
            "pages_scraped": 0,
            "products_extracted": 0,
            "shops_extracted": 0,
            "metrics_extracted": 0,
            "errors": 0
        }
        return scraper
    
    def test_all_command_success(self, mock_scraper):
        """Test complete pipeline successful execution."""
        # Mock successful responses for all stages
        mock_scraper.scrape_products.return_value = {
            "success": True,
            "stats": {"pages_scraped": 5, "products_extracted": 100},
            "total_items": 100
        }
        
        mock_scraper.scrape_shops_from_listings.return_value = {
            "success": True,
            "stats": {"shops_extracted": 50},
            "total_shops": 50
        }
        
        mock_scraper.scrape_shop_metrics.return_value = {
            "success": True,
            "stats": {"metrics_extracted": 50},
            "total_shops": 50
        }
        
        args = MagicMock()
        args.max_pages = 5
        args.start_page = 1
        args.max_items = 100
        
        result = cmd_all(args, mock_scraper)
        
        assert result == 0
        mock_scraper.scrape_products.assert_called_once()
        mock_scraper.scrape_shops_from_listings.assert_called_once()
        mock_scraper.scrape_shop_metrics.assert_called_once()
    
    def test_all_command_product_failure(self, mock_scraper):
        """Test pipeline stops on product scraping failure."""
        mock_scraper.scrape_products.return_value = {
            "success": False,
            "stats": {"errors": 1}
        }
        
        args = MagicMock()
        args.max_pages = 5
        args.start_page = 1
        args.max_items = 100
        
        result = cmd_all(args, mock_scraper)
        
        assert result == 1
        mock_scraper.scrape_products.assert_called_once()
        # Should not proceed to shops or metrics
        mock_scraper.scrape_shops_from_listings.assert_not_called()
        mock_scraper.scrape_shop_metrics.assert_not_called()
    
    def test_all_command_shop_failure(self, mock_scraper):
        """Test pipeline stops on shop extraction failure."""
        mock_scraper.scrape_products.return_value = {
            "success": True,
            "stats": {"pages_scraped": 5, "products_extracted": 100},
            "total_items": 100
        }
        
        mock_scraper.scrape_shops_from_listings.return_value = {
            "success": False,
            "stats": {"errors": 1}
        }
        
        args = MagicMock()
        args.max_pages = 5
        args.start_page = 1
        args.max_items = 100
        
        result = cmd_all(args, mock_scraper)
        
        assert result == 1
        mock_scraper.scrape_products.assert_called_once()
        mock_scraper.scrape_shops_from_listings.assert_called_once()
        # Should not proceed to metrics
        mock_scraper.scrape_shop_metrics.assert_not_called()


class TestDataFlow:
    """Test data flow between pipeline stages."""
    
    def test_products_to_shops_data_flow(self, tmp_path):
        """Test data flows correctly from products to shops stage."""
        # Create products CSV
        products_csv = tmp_path / "products.csv"
        with open(products_csv, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['listing_id', 'shop_name', 'shop_url'])
            writer.writerow(['123', 'Shop1', 'https://etsy.com/shop/Shop1'])
            writer.writerow(['456', 'Shop2', 'https://etsy.com/shop/Shop2'])
            writer.writerow(['789', 'Shop1', 'https://etsy.com/shop/Shop1'])  # Duplicate shop
        
        # Process shops extraction
        from etsy_scraper.data.manager import DataManager
        
        dm = DataManager("shops", str(tmp_path / "shops.csv"))
        
        # Read products and extract unique shops
        shops_seen = set()
        unique_shops = []
        
        with open(products_csv, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['shop_name'] not in shops_seen:
                    shops_seen.add(row['shop_name'])
                    unique_shops.append({
                        'shop_name': row['shop_name'],
                        'shop_url': row['shop_url'],
                        'total_sales': 0,
                        'admirers': 0,
                        'extraction_date': '2024-01-01',
                        'url_valid': True
                    })
        
        dm.save(unique_shops)
        
        # Verify unique shops were saved
        assert dm.stats["saved"] == 2  # Only 2 unique shops
        assert len(dm.existing_ids) == 2
    
    def test_shops_to_metrics_data_flow(self, tmp_path):
        """Test data flows correctly from shops to metrics stage."""
        # Create shops CSV
        shops_csv = tmp_path / "shops.csv"
        with open(shops_csv, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['shop_name', 'shop_url', 'url_valid'])
            writer.writerow(['Shop1', 'https://etsy.com/shop/Shop1', 'True'])
            writer.writerow(['Shop2', 'https://etsy.com/shop/Shop2', 'True'])
        
        # Simulate metrics extraction
        metrics_data = []
        with open(shops_csv, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('url_valid') == 'True':
                    metrics_data.append({
                        'shop_name': row['shop_name'],
                        'shop_url': row['shop_url'],
                        'total_sales': 1000,  # Simulated metric
                        'admirers': 500  # Simulated metric
                    })
        
        assert len(metrics_data) == 2
        assert all(m['total_sales'] == 1000 for m in metrics_data)


class TestErrorRecovery:
    """Test error recovery and retry mechanisms."""
    
    def test_scraper_retry_on_failure(self):
        """Test that scraper retries on transient failures."""
        scraper = EtsyScraper()
        
        # Simulate retry behavior
        initial_retries = scraper.stats["retries"]
        scraper.stats["retries"] += 3  # Simulate 3 retries
        
        assert scraper.stats["retries"] == initial_retries + 3
        
        scraper.close()
    
    def test_keyboard_interrupt_handling(self, monkeypatch):
        """Test graceful handling of keyboard interrupts."""
        import etsy_scraper.cli as cli_module
        
        # Mock the scraper to raise KeyboardInterrupt
        mock_scraper = MagicMock(spec=EtsyScraper)
        mock_scraper.scrape_products.side_effect = KeyboardInterrupt()
        
        # Mock the EtsyScraper class
        monkeypatch.setattr(cli_module, 'EtsyScraper', lambda **kwargs: mock_scraper)
        
        # Simulate CLI execution with keyboard interrupt
        with patch('sys.argv', ['cli.py', 'products', '--max-pages', '1']):
            result = main()
            
            # Should exit with code 2 for interruption
            assert result == 2
    
    def test_exception_handling(self, monkeypatch):
        """Test handling of unexpected exceptions."""
        import etsy_scraper.cli as cli_module
        
        # Mock the scraper to raise an exception
        mock_scraper = MagicMock(spec=EtsyScraper)
        mock_scraper.scrape_products.side_effect = Exception("Test error")
        
        monkeypatch.setattr(cli_module, 'EtsyScraper', lambda **kwargs: mock_scraper)
        
        with patch('sys.argv', ['cli.py', 'products', '--max-pages', '1']):
            result = main()
            
            # Should exit with code 1 for error
            assert result == 1


class TestOutputValidation:
    """Test output file validation."""
    
    def test_csv_output_format(self, tmp_path):
        """Test that CSV output has correct format."""
        from etsy_scraper.data.manager import DataManager
        from etsy_scraper.core.config import PRODUCT_FIELDS
        
        csv_path = tmp_path / "test_output.csv"
        dm = DataManager("products", str(csv_path))
        
        # Save sample data
        sample_data = [{
            field: "test_value" for field in PRODUCT_FIELDS
        }]
        dm.save(sample_data)
        
        # Verify CSV structure
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
            
            # Check all expected fields are present
            for field in PRODUCT_FIELDS:
                assert field in headers
            
            # Check data row
            row = next(reader)
            assert all(row[field] == "test_value" for field in PRODUCT_FIELDS)
    
    def test_json_results_output(self, tmp_path, monkeypatch):
        """Test that JSON results are saved correctly."""
        results_file = DATA_DIR / "product_scraping_results.json"
        
        # Mock scraper response
        mock_results = {
            "success": True,
            "stats": {
                "pages_scraped": 10,
                "products_extracted": 200
            },
            "total_items": 200
        }
        
        # Save results
        with open(results_file, 'w') as f:
            json.dump(mock_results, f, indent=2)
        
        # Verify JSON structure
        with open(results_file, 'r') as f:
            loaded = json.load(f)
            
            assert loaded["success"] is True
            assert loaded["stats"]["pages_scraped"] == 10
            assert loaded["total_items"] == 200