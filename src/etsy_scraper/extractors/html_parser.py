"""
Unified data extractor for Etsy pages.
Handles product, shop, and metrics extraction in a streamlined manner.
"""

import re
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)


class DataExtractor:
    """Unified extractor for all Etsy data types."""
    
    def __init__(self):
        """Initialize the extractor."""
        self.listing_id_pattern = re.compile(r'/listing/(\d+)/')
        self.shop_pattern = re.compile(r'/shop/([^/?]+)')
    
    def extract_products(self, html_content: str) -> List[Dict]:
        """
        Extract product data from category/search pages.
        
        Args:
            html_content: Raw HTML of the page
            
        Returns:
            List of product dictionaries
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        products = []
        
        # Find all listing cards
        cards = soup.select('div.v2-listing-card, div[data-listing-id], article.listing-card')
        if not cards:
            # Fallback to any listing links
            cards = soup.find_all('a', href=self.listing_id_pattern)
        
        for card in cards:
            try:
                product = self._extract_product_from_card(card)
                if product and product['listing_id']:
                    # Check for duplicates
                    if product['listing_id'] not in [p['listing_id'] for p in products]:
                        products.append(product)
            except Exception as e:
                logger.error(f"Error extracting product: {e}")
                continue
        
        # Log extraction statistics
        total = len(products)
        ads = sum(1 for p in products if p.get('is_advertisement'))
        on_sale = sum(1 for p in products if p.get('is_on_sale'))
        logger.info(f"Extracted {total} products: {ads} ads, {on_sale} on sale")
        
        return products
    
    def _extract_product_from_card(self, card) -> Optional[Dict]:
        """Extract data from a single product card."""
        product = {
            'listing_id': '',
            'url': '',
            'title': '',
            'shop_name': '',
            'shop_url': '',
            'sale_price': '',
            'original_price': '',
            'discount_percentage': '',
            'is_on_sale': False,
            'is_advertisement': False,
            'is_digital_download': False,
            'is_bestseller': False,
            'is_star_seller': False,
            'rating': '',
            'review_count': '',
            'free_shipping': False
        }
        
        # Extract listing ID and URL
        if hasattr(card, 'get'):
            # It's a BeautifulSoup element
            listing_id = card.get('data-listing-id')
            link = card.find('a', href=self.listing_id_pattern) if not listing_id else card.find('a')
        else:
            # It's already a link element
            link = card
            listing_id = None
        
        if link:
            url = link.get('href', '')
            if not url.startswith('http'):
                url = f"https://www.etsy.com{url}"
            product['url'] = url.split('?')[0]
            
            if not listing_id:
                match = self.listing_id_pattern.search(url)
                if match:
                    listing_id = match.group(1)
            product['listing_id'] = listing_id or ''
            
            # Extract title
            title_elem = link.find(['h3', 'h2']) or link
            product['title'] = (title_elem.get('title', '') or title_elem.text).strip()
        
        if not hasattr(card, 'get'):
            return product  # Return minimal data for fallback links
        
        # Extract price information
        price_container = card.select_one('div.n-listing-card__price, div.lc-price, .currency-value')
        if price_container:
            current = price_container.select_one('span.currency-value')
            if current:
                product['sale_price'] = re.sub(r'[^\d.,]', '', current.text).strip()
            
            # Check for original price (sale)
            original = price_container.select_one('.wt-text-strikethrough .currency-value')
            if original:
                product['original_price'] = re.sub(r'[^\d.,]', '', original.text).strip()
                product['is_on_sale'] = True
                
                # Extract discount percentage
                discount = price_container.select_one('.wt-text-grey')
                if discount:
                    match = re.search(r'(\d+)%', discount.text)
                    if match:
                        product['discount_percentage'] = match.group(1)
            elif product['sale_price']:
                product['original_price'] = product['sale_price']
        
        # Check if advertisement
        seller_container = card.select_one('p[data-seller-name-container=""]')
        if seller_container and 'advertisement' in seller_container.get_text().lower():
            product['is_advertisement'] = True
        
        # Extract shop info
        shop_link = card.select_one('a[href*="/shop/"]')
        if shop_link:
            shop_url = shop_link.get('href', '')
            if not shop_url.startswith('http'):
                shop_url = f"https://www.etsy.com{shop_url}"
            product['shop_url'] = shop_url.split('?')[0]
            
            match = self.shop_pattern.search(shop_url)
            if match:
                product['shop_name'] = match.group(1)
        
        # Check for badges and attributes
        card_text = card.get_text().lower()
        product['is_digital_download'] = 'digital download' in card_text or 'instant download' in card_text
        product['is_bestseller'] = 'bestseller' in card_text
        product['is_star_seller'] = 'star seller' in card_text
        product['free_shipping'] = 'free shipping' in card_text
        
        # Extract rating
        rating_elem = card.select_one('[aria-label*="out of 5 stars"]')
        if rating_elem:
            match = re.search(r'([\d.]+)\s*out of 5', rating_elem.get('aria-label', ''))
            if match:
                product['rating'] = match.group(1)
        
        # Extract review count
        review_elem = card.find('span', string=re.compile(r'\([\d,]+\)'))
        if review_elem:
            match = re.search(r'\(([\d,]+)\)', review_elem.text)
            if match:
                product['review_count'] = match.group(1).replace(',', '')
        
        return product if product['listing_id'] else None
    
    def extract_shop_from_listing(self, html_content: str) -> Dict:
        """
        Extract shop information from a listing page.
        
        Args:
            html_content: Raw HTML of the listing page
            
        Returns:
            Dictionary with shop_name and shop_url
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        shop_info = {'shop_name': '', 'shop_url': ''}
        
        # Look for shop link
        shop_link = soup.find('a', href=self.shop_pattern)
        
        if shop_link:
            shop_url = shop_link.get('href', '')
            if not shop_url.startswith('http'):
                shop_url = f"https://www.etsy.com{shop_url}"
            shop_info['shop_url'] = shop_url.split('?')[0]
            
            # Extract shop name from URL
            match = self.shop_pattern.search(shop_url)
            if match:
                shop_info['shop_name'] = match.group(1)
            
            # Try to get shop name from text if not found
            if not shop_info['shop_name']:
                shop_info['shop_name'] = shop_link.text.strip()
        
        logger.info(f"Extracted shop: {shop_info['shop_name']}")
        return shop_info
    
    def extract_shop_metrics(self, html_content: str) -> Dict:
        """
        Extract sales and admirers from a shop page.
        
        Args:
            html_content: Raw HTML of the shop page
            
        Returns:
            Dictionary with metrics data
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        metrics = {
            'total_sales': '',
            'admirers': '',
            'url_valid': True
        }
        
        # Extract sales count
        sales_pattern = soup.find(string=re.compile(r'\d+(?:,\d+)*\s*Sales', re.IGNORECASE))
        if sales_pattern:
            match = re.search(r'(\d+(?:,\d+)*)', str(sales_pattern))
            if match:
                metrics['total_sales'] = match.group(1).replace(',', '')
        
        # Extract admirers count
        admirers_elem = soup.find(string=re.compile(r'\d+(?:,\d+)*\s*Admirers', re.IGNORECASE))
        if not admirers_elem:
            # Try finding in links
            admirers_link = soup.find('a', href=re.compile(r'/favoriters'))
            if admirers_link:
                admirers_elem = admirers_link.text
        
        if admirers_elem:
            match = re.search(r'(\d+(?:,\d+)*)', str(admirers_elem))
            if match:
                metrics['admirers'] = match.group(1).replace(',', '')
        
        # Check if shop page loaded correctly
        if not soup.find(['h1', 'h2'], string=re.compile(r'\w+')):
            metrics['url_valid'] = False
        
        logger.info(f"Extracted metrics - Sales: {metrics['total_sales']}, Admirers: {metrics['admirers']}")
        return metrics