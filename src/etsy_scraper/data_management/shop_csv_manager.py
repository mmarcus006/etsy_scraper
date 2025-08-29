"""
CSV data managers for shop information.
Handles storage and deduplication for shop data extraction.
"""

import csv
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set
import logging

logger = logging.getLogger(__name__)


class ShopListingCSVManager:
    """Manages CSV storage for shops extracted from listing pages."""
    
    FIELDNAMES = [
        'shop_name',
        'shop_url',
        'listing_url',
        'extraction_date'
    ]
    
    def __init__(self, filepath: Optional[str] = None):
        """
        Initialize CSV manager for shops from listings.
        
        Args:
            filepath: Path to CSV file. Defaults to data/shops_from_listings.csv
        """
        if filepath is None:
            base_dir = Path(__file__).resolve().parent.parent.parent.parent
            data_dir = base_dir / "data"
            data_dir.mkdir(exist_ok=True)
            self.filepath = data_dir / "shops_from_listings.csv"
        else:
            self.filepath = Path(filepath)
            
        self.existing_shops: Set[str] = set()
        self.processed_listings: Set[str] = set()
        self._load_existing_data()
        
    def _load_existing_data(self):
        """Load existing shop names and processed listings to prevent duplicates."""
        if not self.filepath.exists():
            return
            
        try:
            with open(self.filepath, 'r', encoding='utf-8', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('shop_name'):
                        self.existing_shops.add(row['shop_name'])
                    if row.get('listing_url'):
                        self.processed_listings.add(row['listing_url'])
            logger.info(f"Loaded {len(self.existing_shops)} existing shops, {len(self.processed_listings)} processed listings")
        except Exception as e:
            logger.error(f"Error loading existing data: {e}")
    
    def _ensure_headers(self):
        """Ensure CSV file has headers."""
        if not self.filepath.exists() or os.path.getsize(self.filepath) == 0:
            with open(self.filepath, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=self.FIELDNAMES)
                writer.writeheader()
    
    def is_listing_processed(self, listing_url: str) -> bool:
        """Check if a listing has already been processed."""
        return listing_url in self.processed_listings
    
    def save_shop(self, shop_data: Dict, listing_url: str) -> bool:
        """
        Save a shop to CSV.
        
        Args:
            shop_data: Dictionary with shop_name and shop_url
            listing_url: URL of the listing where shop was found
            
        Returns:
            True if saved (new shop), False if skipped (duplicate)
        """
        self._ensure_headers()
        
        shop_name = shop_data.get('shop_name', '')
        if not shop_name:
            logger.warning(f"No shop name found for listing: {listing_url}")
            return False
        
        # Mark listing as processed
        self.processed_listings.add(listing_url)
        
        # Skip if shop already exists
        if shop_name in self.existing_shops:
            logger.debug(f"Shop already exists: {shop_name}")
            return False
        
        extraction_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        try:
            with open(self.filepath, 'a', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=self.FIELDNAMES)
                
                row = {
                    'shop_name': shop_name,
                    'shop_url': shop_data.get('shop_url', ''),
                    'listing_url': listing_url,
                    'extraction_date': extraction_date
                }
                
                writer.writerow(row)
                self.existing_shops.add(shop_name)
                logger.info(f"Saved new shop: {shop_name}")
                return True
                
        except Exception as e:
            logger.error(f"Error saving shop {shop_name}: {e}")
            return False
    
    def get_shop_count(self) -> int:
        """Get total number of unique shops saved."""
        return len(self.existing_shops)
    
    def get_processed_count(self) -> int:
        """Get total number of listings processed."""
        return len(self.processed_listings)
    
    def get_all_shops(self) -> List[Dict]:
        """Get all shops from the CSV."""
        shops = []
        if not self.filepath.exists():
            return shops
            
        try:
            with open(self.filepath, 'r', encoding='utf-8', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    shops.append(row)
        except Exception as e:
            logger.error(f"Error reading shops: {e}")
            
        return shops


class ShopMetricsCSVManager:
    """Manages CSV storage for shop metrics data."""
    
    FIELDNAMES = [
        'shop_name',
        'shop_url',
        'sales_count',
        'sales_has_href',
        'sales_url',
        'admirers_count',
        'admirers_has_href',
        'admirers_url',
        'extraction_date'
    ]
    
    def __init__(self, filepath: Optional[str] = None):
        """
        Initialize CSV manager for shop metrics.
        
        Args:
            filepath: Path to CSV file. Defaults to data/shop_metrics.csv
        """
        if filepath is None:
            base_dir = Path(__file__).resolve().parent.parent.parent.parent
            data_dir = base_dir / "data"
            data_dir.mkdir(exist_ok=True)
            self.filepath = data_dir / "shop_metrics.csv"
        else:
            self.filepath = Path(filepath)
            
        self.processed_shops: Set[str] = set()
        self._load_existing_data()
        
    def _load_existing_data(self):
        """Load existing shop names to track processed shops."""
        if not self.filepath.exists():
            return
            
        try:
            with open(self.filepath, 'r', encoding='utf-8', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('shop_name'):
                        self.processed_shops.add(row['shop_name'])
            logger.info(f"Loaded {len(self.processed_shops)} processed shops")
        except Exception as e:
            logger.error(f"Error loading existing data: {e}")
    
    def _ensure_headers(self):
        """Ensure CSV file has headers."""
        if not self.filepath.exists() or os.path.getsize(self.filepath) == 0:
            with open(self.filepath, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=self.FIELDNAMES)
                writer.writeheader()
    
    def is_shop_processed(self, shop_name: str) -> bool:
        """Check if a shop has already been processed."""
        return shop_name in self.processed_shops
    
    def save_metrics(self, shop_name: str, shop_url: str, metrics: Dict) -> bool:
        """
        Save shop metrics to CSV.
        
        Args:
            shop_name: Name of the shop
            shop_url: URL of the shop
            metrics: Dictionary with metrics data
            
        Returns:
            True if saved, False if skipped (already processed)
        """
        self._ensure_headers()
        
        # Skip if already processed
        if shop_name in self.processed_shops:
            logger.debug(f"Shop already processed: {shop_name}")
            return False
        
        extraction_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        try:
            with open(self.filepath, 'a', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=self.FIELDNAMES)
                
                row = {
                    'shop_name': shop_name,
                    'shop_url': shop_url,
                    'sales_count': metrics.get('sales_count', ''),
                    'sales_has_href': metrics.get('sales_has_href', False),
                    'sales_url': metrics.get('sales_url', ''),
                    'admirers_count': metrics.get('admirers_count', ''),
                    'admirers_has_href': metrics.get('admirers_has_href', False),
                    'admirers_url': metrics.get('admirers_url', ''),
                    'extraction_date': extraction_date
                }
                
                writer.writerow(row)
                self.processed_shops.add(shop_name)
                logger.info(f"Saved metrics for shop: {shop_name}")
                return True
                
        except Exception as e:
            logger.error(f"Error saving metrics for {shop_name}: {e}")
            return False
    
    def get_processed_count(self) -> int:
        """Get total number of shops processed."""
        return len(self.processed_shops)
    
    def get_metrics_summary(self) -> Dict:
        """Get summary statistics of all shop metrics."""
        if not self.filepath.exists():
            return {}
            
        total_sales = 0
        total_admirers = 0
        shops_with_sales_link = 0
        shops_with_admirers_link = 0
        shop_count = 0
        
        try:
            with open(self.filepath, 'r', encoding='utf-8', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    shop_count += 1
                    
                    # Sum sales
                    sales = row.get('sales_count', '')
                    if sales and sales.isdigit():
                        total_sales += int(sales)
                    
                    # Sum admirers
                    admirers = row.get('admirers_count', '')
                    if admirers and admirers.isdigit():
                        total_admirers += int(admirers)
                    
                    # Count links
                    if row.get('sales_has_href') == 'True':
                        shops_with_sales_link += 1
                    if row.get('admirers_has_href') == 'True':
                        shops_with_admirers_link += 1
                        
        except Exception as e:
            logger.error(f"Error calculating summary: {e}")
            
        return {
            'total_shops': shop_count,
            'total_sales': total_sales,
            'total_admirers': total_admirers,
            'avg_sales': total_sales // shop_count if shop_count > 0 else 0,
            'avg_admirers': total_admirers // shop_count if shop_count > 0 else 0,
            'shops_with_sales_link': shops_with_sales_link,
            'shops_with_admirers_link': shops_with_admirers_link
        }