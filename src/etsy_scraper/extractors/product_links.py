"""
Product link extractor for Etsy templates pages.
Parses HTML to extract comprehensive product information from listing cards.
"""

import re
from typing import Dict, List, Optional
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)


class ProductLinkExtractor:
    """Extracts product links and comprehensive metadata from Etsy search/category pages."""
    
    def __init__(self):
        """Initialize the extractor."""
        self.listing_id_pattern = re.compile(r'/listing/(\d+)/')
        
    def extract_listing_id(self, url: str) -> Optional[str]:
        """
        Extract listing ID from Etsy URL.
        
        Args:
            url: Etsy product URL
            
        Returns:
            Listing ID or None if not found
        """
        match = self.listing_id_pattern.search(url)
        return match.group(1) if match else None
    
    def extract_shop_name_from_url(self, url: str) -> Optional[str]:
        """
        Extract shop name from shop URL.
        
        Args:
            url: Shop URL
            
        Returns:
            Shop name or None
        """
        if '/shop/' in url:
            parts = url.split('/shop/')
            if len(parts) > 1:
                shop_name = parts[1].split('?')[0].split('/')[0]
                return shop_name
        return None
    
    def clean_price(self, price_text: str) -> str:
        """
        Clean and standardize price text.
        
        Args:
            price_text: Raw price text from HTML
            
        Returns:
            Cleaned price string
        """
        # Remove extra whitespace and normalize
        price = ' '.join(price_text.split())
        # Remove "Sale Price:" or similar prefixes
        price = re.sub(r'^(Sale\s+)?Price:\s*', '', price, flags=re.IGNORECASE)
        # Remove currency symbols for consistent formatting
        price = re.sub(r'[^\d.,]', '', price)
        return price.strip()
    
    def _extract_price_info(self, card) -> Dict:
        """
        Extract all price-related information from a listing card.
        
        Args:
            card: BeautifulSoup element for the listing card
            
        Returns:
            Dictionary with price information
        """
        price_info = {
            'sale_price': '',
            'original_price': '',
            'discount_percentage': '',
            'is_on_sale': False
        }
        
        # Look for the main price container
        price_container = card.select_one('div.n-listing-card__price, div.lc-price')
        
        if price_container:
            # Get the current/sale price
            current_price = price_container.select_one('span.currency-value')
            if current_price:
                price_info['sale_price'] = self.clean_price(current_price.text)
            
            # Check for original price (strikethrough)
            original_price = price_container.select_one('span.wt-text-strikethrough span.currency-value')
            if original_price:
                price_info['original_price'] = self.clean_price(original_price.text)
                price_info['is_on_sale'] = True
                
                # Extract discount percentage
                discount_elem = price_container.select_one('span.wt-text-grey')
                if discount_elem:
                    discount_text = discount_elem.text.strip()
                    # Extract percentage from text like "(50% off)"
                    match = re.search(r'(\d+)%\s*off', discount_text, re.IGNORECASE)
                    if match:
                        price_info['discount_percentage'] = match.group(1)
            
            # If no sale, original price is the current price
            if not price_info['is_on_sale'] and price_info['sale_price']:
                price_info['original_price'] = price_info['sale_price']
        
        return price_info
    
    def _is_advertisement(self, card) -> bool:
        """
        Check if the listing is an advertisement.
        
        Args:
            card: BeautifulSoup element for the listing card
            
        Returns:
            True if listing is an ad
        """
        # Look for the seller name container with empty attribute
        seller_container = card.select_one('p[data-seller-name-container=""]')
        if seller_container:
            # Get all text content (Etsy splits "advertisement" across spans)
            full_text = seller_container.get_text().lower()
            # Check for advertisement markers
            if 'advertisement' in full_text or 'ad by' in full_text:
                return True
        
        # Alternative: check for ad-specific classes
        if card.select_one('.promoted-listing, .ad-listing, [class*="promoted"]'):
            return True
            
        return False
    
    def _extract_product_attributes(self, card) -> Dict:
        """
        Extract product attributes like digital download, bestseller status.
        
        Args:
            card: BeautifulSoup element for the listing card
            
        Returns:
            Dictionary with product attributes
        """
        attributes = {
            'is_digital_download': False,
            'is_bestseller': False,
            'free_shipping': False
        }
        
        # Check for digital download
        digital_indicators = [
            'Digital Download',
            'Instant Download',
            'Digital File',
            'PDF Download'
        ]
        
        card_text = card.get_text()
        for indicator in digital_indicators:
            if indicator in card_text:
                attributes['is_digital_download'] = True
                break
        
        # Alternative: look for digital download text with icon
        digital_elem = card.find('p', string=lambda text: text and 'Digital Download' in text if text else False)
        if digital_elem:
            attributes['is_digital_download'] = True
        
        # Check for bestseller badge
        bestseller_elem = card.find(class_=lambda x: x and 'bestseller' in x.lower() if x else False)
        if bestseller_elem or 'bestseller' in card_text.lower():
            attributes['is_bestseller'] = True
        
        # Check for free shipping
        if 'free shipping' in card_text.lower() or card.select_one('[class*="free-shipping"]'):
            attributes['free_shipping'] = True
        
        return attributes
    
    def _extract_ratings(self, card) -> Dict:
        """
        Extract rating and review count.
        
        Args:
            card: BeautifulSoup element for the listing card
            
        Returns:
            Dictionary with rating information
        """
        rating_info = {
            'rating': '',
            'review_count': ''
        }
        
        # Look for star rating container
        rating_container = card.select_one('span[data-stars-svg-container], .star-rating-5, [class*="star-rating"]')
        
        if rating_container:
            # Try to get rating from hidden input or data attribute
            rating_input = rating_container.select_one('input[name*="rating"]')
            if rating_input:
                rating_info['rating'] = rating_input.get('value', '')
            else:
                # Try to extract from aria-label
                stars_elem = card.select_one('[aria-label*="out of 5 stars"]')
                if stars_elem:
                    aria_label = stars_elem.get('aria-label', '')
                    match = re.search(r'([\d.]+)\s*out of 5', aria_label)
                    if match:
                        rating_info['rating'] = match.group(1)
        
        # Extract review count - look for parentheses with numbers
        review_elem = card.find('span', class_='wt-text-gray')
        if review_elem and '(' in review_elem.text:
            review_text = review_elem.text.strip()
            # Extract number from text like "(7,301)" or "7301 reviews"
            match = re.search(r'\(([\d,]+)\)', review_text)
            if match:
                rating_info['review_count'] = match.group(1).replace(',', '')
        
        return rating_info
    
    def _extract_seller_badges(self, card) -> Dict:
        """
        Extract seller badges like Star Seller.
        
        Args:
            card: BeautifulSoup element for the listing card
            
        Returns:
            Dictionary with seller badge information
        """
        badges = {
            'is_star_seller': False
        }
        
        # Check for Star Seller badge - look for the star icon and text
        star_icon = card.select_one('.wt-icon--star-seller, .wt-icon--core.wt-fill-star-seller-dark')
        star_text = card.find('p', class_='star-seller-badge-lavender-text-light')
        
        if star_icon or star_text:
            badges['is_star_seller'] = True
        
        # Alternative: check text content
        if 'star seller' in card.get_text().lower():
            badges['is_star_seller'] = True
        
        return badges
    
    def extract_products_from_html(self, html_content: str) -> List[Dict]:
        """
        Extract all product links and comprehensive metadata from page HTML.
        
        Args:
            html_content: Raw HTML of the page
            
        Returns:
            List of product dictionaries with all fields
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        products = []
        
        # Multiple possible selectors for listing cards
        card_selectors = [
            'div.v2-listing-card',
            'div.wt-grid__item-xs-6',
            'div[data-listing-id]',
            'article.listing-card'
        ]
        
        listing_cards = []
        for selector in card_selectors:
            cards = soup.select(selector)
            if cards:
                listing_cards = cards
                logger.debug(f"Found {len(cards)} products using selector: {selector}")
                break
        
        if not listing_cards:
            # Fallback: look for any links to /listing/
            listing_links = soup.find_all('a', href=re.compile(r'/listing/\d+'))
            logger.warning(f"Using fallback extraction, found {len(listing_links)} listing links")
            
            for link in listing_links:
                url = link.get('href', '')
                if not url.startswith('http'):
                    url = f"https://www.etsy.com{url}"
                
                listing_id = self.extract_listing_id(url)
                if listing_id and listing_id not in [p['listing_id'] for p in products]:
                    # Create minimal product entry for fallback
                    products.append({
                        'listing_id': listing_id,
                        'url': url.split('?')[0],
                        'title': link.get('title', link.text.strip()),
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
                    })
            
            return products
        
        # Process each listing card
        for card in listing_cards:
            try:
                product = self._extract_from_card(card)
                if product and product['listing_id']:
                    # Check for duplicates
                    if product['listing_id'] not in [p['listing_id'] for p in products]:
                        products.append(product)
            except Exception as e:
                logger.error(f"Error extracting product from card: {e}")
                continue
        
        # Log statistics
        total = len(products)
        ads = sum(1 for p in products if p.get('is_advertisement'))
        digital = sum(1 for p in products if p.get('is_digital_download'))
        on_sale = sum(1 for p in products if p.get('is_on_sale'))
        
        logger.info(f"Extracted {total} products: {ads} ads, {digital} digital, {on_sale} on sale")
        
        return products
    
    def _extract_from_card(self, card) -> Optional[Dict]:
        """
        Extract comprehensive product data from a single listing card.
        
        Args:
            card: BeautifulSoup element for the listing card
            
        Returns:
            Product dictionary with all fields or None
        """
        product = {
            'listing_id': '',
            'url': '',
            'title': '',
            'shop_name': '',
            'shop_url': ''
        }
        
        # Try to get listing ID from data attribute first
        listing_id = card.get('data-listing-id')
        
        # Find the main product link
        link_element = card.find('a', href=re.compile(r'/listing/\d+'))
        if not link_element:
            # Try alternative selectors
            link_element = card.select_one('a.listing-link, a.listing-card-title')
        
        if link_element:
            url = link_element.get('href', '')
            if not url.startswith('http'):
                url = f"https://www.etsy.com{url}"
            
            product['url'] = url.split('?')[0]  # Remove query params
            
            if not listing_id:
                listing_id = self.extract_listing_id(url)
            
            product['listing_id'] = listing_id or ''
            
            # Extract title
            title_element = link_element.find('h3') or link_element.find('h2')
            if title_element:
                product['title'] = title_element.text.strip()
            else:
                product['title'] = link_element.get('title', link_element.text.strip())
        
        # Extract all price information
        price_info = self._extract_price_info(card)
        product.update(price_info)
        
        # Extract shop info
        shop_link = card.select_one('a[href*="/shop/"]')
        if not shop_link:
            # Try to extract from seller name area - looking for the actual shop name span
            seller_elem = card.select_one('span.iti7duazu')
            if seller_elem:
                # Get the text, excluding "advertisement" part
                shop_text = seller_elem.text.strip()
                if shop_text and shop_text not in ['advertisement', 'ad', 'by Etsy seller']:
                    product['shop_name'] = shop_text
        else:
            shop_url = shop_link.get('href', '')
            if not shop_url.startswith('http'):
                shop_url = f"https://www.etsy.com{shop_url}"
            
            product['shop_url'] = shop_url.split('?')[0]
            product['shop_name'] = self.extract_shop_name_from_url(shop_url) or ''
            
            # If shop name not in URL, try text
            if not product['shop_name']:
                product['shop_name'] = shop_link.text.strip()
        
        # Check if advertisement
        product['is_advertisement'] = self._is_advertisement(card)
        
        # Extract product attributes
        attributes = self._extract_product_attributes(card)
        product.update(attributes)
        
        # Extract ratings
        ratings = self._extract_ratings(card)
        product.update(ratings)
        
        # Extract seller badges
        badges = self._extract_seller_badges(card)
        product.update(badges)
        
        return product if product['listing_id'] else None