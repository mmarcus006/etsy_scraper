"""
CSV data manager for storing and managing scraped product links.
Handles deduplication, persistence, and data validation.
"""

import csv
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set
import logging

logger = logging.getLogger(__name__)


class ProductCSVManager:
    """Manages CSV storage for scraped Etsy product data."""
    
    FIELDNAMES = [
        'listing_id',
        'url', 
        'title',
        'shop_name',
        'shop_url',
        'sale_price',
        'original_price',
        'discount_percentage',
        'is_on_sale',
        'is_advertisement',
        'is_digital_download',
        'is_bestseller',
        'is_star_seller',
        'rating',
        'review_count',
        'free_shipping',
        'page_number',
        'extraction_date',
        'position_on_page'
    ]
    
    def __init__(self, filepath: Optional[str] = None):
        """
        Initialize CSV manager.
        
        Args:
            filepath: Path to CSV file. Defaults to data/products.csv
        """
        if filepath is None:
            base_dir = Path(__file__).resolve().parent.parent.parent.parent
            data_dir = base_dir / "data"
            data_dir.mkdir(exist_ok=True)
            self.filepath = data_dir / "etsy_products.csv"
        else:
            self.filepath = Path(filepath)
            
        self.existing_ids: Set[str] = set()
        self._load_existing_ids()
        
    def _load_existing_ids(self):
        """Load existing listing IDs to prevent duplicates."""
        if not self.filepath.exists():
            return
            
        try:
            with open(self.filepath, 'r', encoding='utf-8', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('listing_id'):
                        self.existing_ids.add(row['listing_id'])
            logger.info(f"Loaded {len(self.existing_ids)} existing product IDs")
        except Exception as e:
            logger.error(f"Error loading existing IDs: {e}")
    
    def _ensure_headers(self):
        """Ensure CSV file has headers."""
        if not self.filepath.exists() or os.path.getsize(self.filepath) == 0:
            with open(self.filepath, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=self.FIELDNAMES)
                writer.writeheader()
    
    def save_products(self, products: List[Dict], page_number: int) -> Dict:
        """
        Save products to CSV, skipping duplicates.
        
        Args:
            products: List of product dictionaries
            page_number: Current page number
            
        Returns:
            Dictionary with save statistics
        """
        self._ensure_headers()
        
        stats = {
            'total': len(products),
            'saved': 0,
            'duplicates': 0,
            'errors': 0
        }
        
        extraction_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        with open(self.filepath, 'a', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.FIELDNAMES)
            
            for position, product in enumerate(products, 1):
                listing_id = product.get('listing_id', '')
                
                # Skip duplicates
                if listing_id in self.existing_ids:
                    stats['duplicates'] += 1
                    logger.debug(f"Skipping duplicate listing: {listing_id}")
                    continue
                
                try:
                    # Prepare row data
                    row = {
                        'listing_id': listing_id,
                        'url': product.get('url', ''),
                        'title': product.get('title', ''),
                        'shop_name': product.get('shop_name', ''),
                        'shop_url': product.get('shop_url', ''),
                        'sale_price': product.get('sale_price', ''),
                        'original_price': product.get('original_price', ''),
                        'discount_percentage': product.get('discount_percentage', ''),
                        'is_on_sale': product.get('is_on_sale', False),
                        'is_advertisement': product.get('is_advertisement', False),
                        'is_digital_download': product.get('is_digital_download', False),
                        'is_bestseller': product.get('is_bestseller', False),
                        'is_star_seller': product.get('is_star_seller', False),
                        'rating': product.get('rating', ''),
                        'review_count': product.get('review_count', ''),
                        'free_shipping': product.get('free_shipping', False),
                        'page_number': page_number,
                        'extraction_date': extraction_date,
                        'position_on_page': position
                    }
                    
                    writer.writerow(row)
                    self.existing_ids.add(listing_id)
                    stats['saved'] += 1
                    
                except Exception as e:
                    logger.error(f"Error saving product {listing_id}: {e}")
                    stats['errors'] += 1
        
        logger.info(
            f"Page {page_number}: Saved {stats['saved']}/{stats['total']} products "
            f"({stats['duplicates']} duplicates, {stats['errors']} errors)"
        )
        
        return stats
    
    def get_product_count(self) -> int:
        """Get total number of unique products saved."""
        return len(self.existing_ids)
    
    def get_last_page_scraped(self) -> int:
        """Get the highest page number scraped so far."""
        if not self.filepath.exists():
            return 0
            
        max_page = 0
        try:
            with open(self.filepath, 'r', encoding='utf-8', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    page = int(row.get('page_number', 0))
                    max_page = max(max_page, page)
        except Exception as e:
            logger.error(f"Error getting last page: {e}")
            
        return max_page
    
    def clear_data(self):
        """Clear all data (use with caution)."""
        if self.filepath.exists():
            os.remove(self.filepath)
        self.existing_ids.clear()
        logger.info("Cleared all product data")