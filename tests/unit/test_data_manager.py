"""
Tests for data management module.
Tests DataManager class for CSV operations and data handling.
"""

import csv
import json
from pathlib import Path
from datetime import datetime
import pytest

from etsy_scraper.data.manager import DataManager
from etsy_scraper.core.config import PRODUCT_FIELDS, SHOP_FIELDS


class TestDataManagerInitialization:
    """Test DataManager initialization."""
    
    def test_init_products_manager(self, tmp_path):
        """Test initializing products data manager."""
        csv_path = tmp_path / "products.csv"
        dm = DataManager("products", str(csv_path))
        
        assert dm.data_type == "products"
        assert dm.csv_path == Path(csv_path)
        assert dm.fields == PRODUCT_FIELDS
        assert dm.existing_ids == set()
        assert dm.stats["saved"] == 0
        assert dm.stats["duplicates"] == 0
    
    def test_init_shops_manager(self, tmp_path):
        """Test initializing shops data manager."""
        csv_path = tmp_path / "shops.csv"
        dm = DataManager("shops", str(csv_path))
        
        assert dm.data_type == "shops"
        assert dm.csv_path == Path(csv_path)
        assert dm.fields == SHOP_FIELDS
        assert dm.existing_ids == set()
    
    def test_init_with_existing_csv(self, tmp_path):
        """Test initialization with existing CSV file."""
        csv_path = tmp_path / "existing.csv"
        
        # Create existing CSV with data
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=PRODUCT_FIELDS)
            writer.writeheader()
            writer.writerow({
                "listing_id": "123",
                "title": "Test Product",
                "url": "https://test.com",
                "shop_name": "Test Shop",
                "shop_url": "https://shop.com",
                "sale_price": "19.99",
                "original_price": "29.99",
                "discount_percentage": "33",
                "is_on_sale": "True",
                "is_advertisement": "False",
                "is_digital_download": "False",
                "is_bestseller": "True",
                "is_star_seller": "True",
                "rating": "4.5",
                "review_count": "100",
                "free_shipping": "True",
                "page_number": "1",
                "extraction_date": "2024-01-01",
                "position_on_page": "1"
            })
        
        dm = DataManager("products", str(csv_path))
        assert "123" in dm.existing_ids
        assert len(dm.existing_ids) == 1
    
    def test_init_invalid_data_type(self, tmp_path):
        """Test initialization with invalid data type."""
        csv_path = tmp_path / "test.csv"
        with pytest.raises(ValueError):
            DataManager("invalid_type", str(csv_path))


class TestDataSaving:
    """Test data saving functionality."""
    
    @pytest.fixture
    def products_manager(self, tmp_path):
        """Create a products data manager for testing."""
        csv_path = tmp_path / "products.csv"
        return DataManager("products", str(csv_path))
    
    @pytest.fixture
    def sample_product(self):
        """Create sample product data."""
        return {
            "listing_id": "456789",
            "url": "https://etsy.com/listing/456789",
            "title": "Sample Product",
            "shop_name": "Sample Shop",
            "shop_url": "https://etsy.com/shop/SampleShop",
            "sale_price": 24.99,
            "original_price": 29.99,
            "discount_percentage": 17,
            "is_on_sale": True,
            "is_advertisement": False,
            "is_digital_download": False,
            "is_bestseller": True,
            "is_star_seller": True,
            "rating": 4.8,
            "review_count": 250,
            "free_shipping": True,
            "page_number": 1,
            "extraction_date": datetime.now().strftime("%Y-%m-%d"),
            "position_on_page": 5
        }
    
    def test_save_single_item(self, products_manager, sample_product):
        """Test saving a single item."""
        products_manager.save([sample_product])
        
        assert products_manager.stats["saved"] == 1
        assert products_manager.stats["duplicates"] == 0
        assert "456789" in products_manager.existing_ids
        assert products_manager.csv_path.exists()
    
    def test_save_multiple_items(self, products_manager):
        """Test saving multiple items."""
        items = [
            {"listing_id": f"{i}", "title": f"Product {i}", **{
                field: "" for field in PRODUCT_FIELDS if field not in ["listing_id", "title"]
            }} for i in range(5)
        ]
        
        products_manager.save(items)
        
        assert products_manager.stats["saved"] == 5
        assert products_manager.stats["duplicates"] == 0
        assert len(products_manager.existing_ids) == 5
    
    def test_save_duplicate_detection(self, products_manager, sample_product):
        """Test duplicate detection when saving."""
        # Save item first time
        products_manager.save([sample_product])
        assert products_manager.stats["saved"] == 1
        
        # Try to save same item again
        products_manager.save([sample_product])
        assert products_manager.stats["saved"] == 1  # Should not increase
        assert products_manager.stats["duplicates"] == 1
    
    def test_save_mixed_new_and_duplicates(self, products_manager):
        """Test saving mix of new items and duplicates."""
        items_batch1 = [
            {"listing_id": "1", "title": "Product 1", **{
                field: "" for field in PRODUCT_FIELDS if field not in ["listing_id", "title"]
            }},
            {"listing_id": "2", "title": "Product 2", **{
                field: "" for field in PRODUCT_FIELDS if field not in ["listing_id", "title"]
            }}
        ]
        
        items_batch2 = [
            {"listing_id": "2", "title": "Product 2 Updated", **{
                field: "" for field in PRODUCT_FIELDS if field not in ["listing_id", "title"]
            }},  # Duplicate
            {"listing_id": "3", "title": "Product 3", **{
                field: "" for field in PRODUCT_FIELDS if field not in ["listing_id", "title"]
            }}  # New
        ]
        
        products_manager.save(items_batch1)
        assert products_manager.stats["saved"] == 2
        
        products_manager.save(items_batch2)
        assert products_manager.stats["saved"] == 3  # Only one new item
        assert products_manager.stats["duplicates"] == 1
    
    def test_save_empty_list(self, products_manager):
        """Test saving empty list."""
        products_manager.save([])
        
        assert products_manager.stats["saved"] == 0
        assert products_manager.stats["duplicates"] == 0


class TestDataLoading:
    """Test data loading functionality."""
    
    @pytest.fixture
    def existing_csv(self, tmp_path):
        """Create an existing CSV file with data."""
        csv_path = tmp_path / "existing_products.csv"
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=PRODUCT_FIELDS)
            writer.writeheader()
            for i in range(3):
                writer.writerow({
                    "listing_id": str(i),
                    "title": f"Product {i}",
                    **{field: "" for field in PRODUCT_FIELDS if field not in ["listing_id", "title"]}
                })
        
        return csv_path
    
    def test_load_existing_data(self, existing_csv):
        """Test loading existing data from CSV."""
        dm = DataManager("products", str(existing_csv))
        data = dm.load_existing_data()
        
        assert len(data) == 3
        assert all("listing_id" in item for item in data)
        assert data[0]["listing_id"] == "0"
        assert data[2]["title"] == "Product 2"
    
    def test_load_nonexistent_file(self, tmp_path):
        """Test loading from non-existent file."""
        csv_path = tmp_path / "nonexistent.csv"
        dm = DataManager("products", str(csv_path))
        data = dm.load_existing_data()
        
        assert data == []
    
    def test_existing_ids_loaded(self, existing_csv):
        """Test that existing IDs are loaded on initialization."""
        dm = DataManager("products", str(existing_csv))
        
        assert len(dm.existing_ids) == 3
        assert "0" in dm.existing_ids
        assert "1" in dm.existing_ids
        assert "2" in dm.existing_ids


class TestDataClearing:
    """Test data clearing functionality."""
    
    @pytest.fixture
    def manager_with_data(self, tmp_path):
        """Create a manager with existing data."""
        csv_path = tmp_path / "data.csv"
        dm = DataManager("products", str(csv_path))
        
        # Add some data
        items = [
            {"listing_id": str(i), "title": f"Product {i}", **{
                field: "" for field in PRODUCT_FIELDS if field not in ["listing_id", "title"]
            }} for i in range(3)
        ]
        dm.save(items)
        
        return dm
    
    def test_clear_data(self, manager_with_data):
        """Test clearing all data."""
        # Verify data exists
        assert manager_with_data.stats["saved"] == 3
        assert len(manager_with_data.existing_ids) == 3
        assert manager_with_data.csv_path.exists()
        
        # Clear data
        manager_with_data.clear_data()
        
        # Verify data is cleared
        assert manager_with_data.stats["saved"] == 0
        assert manager_with_data.stats["duplicates"] == 0
        assert len(manager_with_data.existing_ids) == 0
        assert not manager_with_data.csv_path.exists()
    
    def test_clear_nonexistent_file(self, tmp_path):
        """Test clearing when file doesn't exist."""
        csv_path = tmp_path / "nonexistent.csv"
        dm = DataManager("products", str(csv_path))
        
        # Should not raise error
        dm.clear_data()
        
        assert dm.stats["saved"] == 0
        assert len(dm.existing_ids) == 0


class TestProgressTracking:
    """Test progress tracking functionality."""
    
    @pytest.fixture
    def progress_file(self, tmp_path):
        """Create a progress tracking file."""
        progress_path = tmp_path / "progress.json"
        progress_data = {
            "last_page": 5,
            "total_products": 150,
            "last_updated": "2024-01-01 12:00:00"
        }
        with open(progress_path, 'w') as f:
            json.dump(progress_data, f)
        return progress_path
    
    def test_save_progress(self, tmp_path):
        """Test saving progress information."""
        csv_path = tmp_path / "products.csv"
        dm = DataManager("products", str(csv_path))
        
        # Save progress
        progress_file = tmp_path / "progress.json"
        dm.save_progress(str(progress_file), page=3, total=90)
        
        # Verify progress file
        assert progress_file.exists()
        with open(progress_file) as f:
            progress = json.load(f)
        
        assert progress["last_page"] == 3
        assert progress["total_products"] == 90
        assert "last_updated" in progress
    
    def test_load_progress(self, progress_file):
        """Test loading progress information."""
        csv_path = progress_file.parent / "products.csv"
        dm = DataManager("products", str(csv_path))
        
        progress = dm.load_progress(str(progress_file))
        
        assert progress["last_page"] == 5
        assert progress["total_products"] == 150
        assert progress["last_updated"] == "2024-01-01 12:00:00"
    
    def test_load_missing_progress(self, tmp_path):
        """Test loading non-existent progress file."""
        csv_path = tmp_path / "products.csv"
        dm = DataManager("products", str(csv_path))
        
        progress = dm.load_progress(str(tmp_path / "missing.json"))
        
        assert progress is None


class TestShopDataManager:
    """Test shop-specific data management."""
    
    @pytest.fixture
    def shops_manager(self, tmp_path):
        """Create a shops data manager."""
        csv_path = tmp_path / "shops.csv"
        return DataManager("shops", str(csv_path))
    
    @pytest.fixture
    def sample_shop(self):
        """Create sample shop data."""
        return {
            "shop_name": "TestShop",
            "shop_url": "https://etsy.com/shop/TestShop",
            "total_sales": 5000,
            "admirers": 1200,
            "extraction_date": datetime.now().strftime("%Y-%m-%d"),
            "url_valid": True
        }
    
    def test_save_shop_data(self, shops_manager, sample_shop):
        """Test saving shop data."""
        shops_manager.save([sample_shop])
        
        assert shops_manager.stats["saved"] == 1
        assert "TestShop" in shops_manager.existing_ids
        
        # Verify CSV content
        data = shops_manager.load_existing_data()
        assert len(data) == 1
        assert data[0]["shop_name"] == "TestShop"
    
    def test_shop_duplicate_detection(self, shops_manager):
        """Test duplicate detection for shops."""
        shop1 = {
            "shop_name": "Shop1",
            "shop_url": "https://etsy.com/shop/Shop1",
            **{field: "" for field in SHOP_FIELDS if field not in ["shop_name", "shop_url"]}
        }
        
        shops_manager.save([shop1])
        assert shops_manager.stats["saved"] == 1
        
        # Try to save same shop again
        shops_manager.save([shop1])
        assert shops_manager.stats["saved"] == 1  # Should not increase
        assert shops_manager.stats["duplicates"] == 1


class TestFieldValidation:
    """Test field validation and handling."""
    
    @pytest.fixture
    def products_manager(self, tmp_path):
        """Create a products data manager."""
        csv_path = tmp_path / "products.csv"
        return DataManager("products", str(csv_path))
    
    def test_missing_fields_handled(self, products_manager):
        """Test handling of items with missing fields."""
        incomplete_item = {
            "listing_id": "999",
            "title": "Incomplete Product"
            # Missing other fields
        }
        
        # Should handle gracefully by filling missing fields
        products_manager.save([incomplete_item])
        
        assert products_manager.stats["saved"] == 1
        
        # Verify saved data has all fields
        data = products_manager.load_existing_data()
        assert len(data[0]) >= len(PRODUCT_FIELDS)
    
    def test_extra_fields_ignored(self, products_manager):
        """Test that extra fields are ignored."""
        item_with_extra = {
            "listing_id": "888",
            "title": "Product with extras",
            "extra_field": "Should be ignored",
            **{field: "" for field in PRODUCT_FIELDS if field not in ["listing_id", "title"]}
        }
        
        products_manager.save([item_with_extra])
        
        data = products_manager.load_existing_data()
        assert "extra_field" not in data[0]