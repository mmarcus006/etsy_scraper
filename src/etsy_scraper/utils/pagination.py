"""
Pagination handler for Etsy pages.
Extracts pagination info and generates next page URLs.
"""

import re
from typing import Dict, Optional, Any
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from bs4 import BeautifulSoup, Tag
import logging

logger = logging.getLogger(__name__)


class PaginationHandler:
    """Handles pagination logic for Etsy category/search pages."""
    
    def __init__(self) -> None:
        """Initialize pagination handler."""
        self.page_param_names = ['page', 'ref', 'anchor']
        
    def extract_pagination_info(self, html_content: str) -> Dict[str, Any]:
        """
        Extract pagination information from page HTML.
        
        Args:
            html_content: Raw HTML of the page
            
        Returns:
            Dictionary with pagination info
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        info = {
            'current_page': 1,
            'total_pages': None,
            'has_next': False,
            'next_page_url': None,
            'total_results': None
        }
        
        # Method 1: Look for pagination nav
        pagination_nav = soup.select_one('nav[aria-label*="Pagination"], nav.wt-pagination')
        if pagination_nav:
            info.update(self._parse_pagination_nav(pagination_nav))
        
        # Method 2: Look for page numbers in links
        if not info['total_pages']:
            info.update(self._parse_page_links(soup))
        
        # Method 3: Extract from result count
        result_count = self._extract_result_count(soup)
        if result_count:
            info['total_results'] = result_count
            # Estimate pages (assuming ~48 items per page)
            if not info['total_pages'] and result_count > 0:
                info['total_pages'] = (result_count + 47) // 48
        
        # Check for next button
        next_button = soup.select_one('a[aria-label*="Next"], a.wt-pagination__item--next')
        if next_button and not next_button.has_attr('disabled'):
            info['has_next'] = True
            next_url = next_button.get('href')
            if next_url:
                if not next_url.startswith('http'):
                    next_url = f"https://www.etsy.com{next_url}"
                info['next_page_url'] = next_url
        
        logger.debug(f"Pagination info: {info}")
        return info
    
    def _parse_pagination_nav(self, nav_element: Tag) -> Dict[str, Any]:
        """Parse pagination nav element."""
        info = {}
        
        # Find current page
        current = nav_element.select_one('span[aria-current="page"], .wt-pagination__item--current')
        if current:
            try:
                info['current_page'] = int(current.text.strip())
            except ValueError:
                pass
        
        # Find all page links
        page_links = nav_element.select('a[href*="page="], a[href*="ref=pagination"]')
        max_page = 0
        
        for link in page_links:
            try:
                # Extract page number from link text or href
                text = link.text.strip()
                if text.isdigit():
                    max_page = max(max_page, int(text))
                else:
                    # Try to extract from href
                    href = link.get('href', '')
                    page_match = re.search(r'page=(\d+)', href)
                    if page_match:
                        max_page = max(max_page, int(page_match.group(1)))
            except Exception:
                continue
        
        if max_page > 0:
            info['total_pages'] = max_page
        
        return info
    
    def _parse_page_links(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Parse page links from the entire page."""
        info = {}
        
        # Look for pagination links anywhere on page
        page_links = soup.find_all('a', href=re.compile(r'page=\d+'))
        
        current_page = 1
        max_page = 1
        
        for link in page_links:
            href = link.get('href', '')
            page_match = re.search(r'page=(\d+)', href)
            if page_match:
                page_num = int(page_match.group(1))
                max_page = max(max_page, page_num)
                
                # Check if this is the current page
                parent = link.parent
                if parent and ('current' in parent.get('class', []) or 
                              parent.has_attr('aria-current')):
                    current_page = page_num
        
        info['current_page'] = current_page
        if max_page > 1:
            info['total_pages'] = max_page
        
        return info
    
    def _extract_result_count(self, soup) -> Optional[int]:
        """Extract total result count from page."""
        # Common patterns for result count
        patterns = [
            r'(\d+(?:,\d+)?)\s+results?',
            r'(\d+(?:,\d+)?)\s+items?',
            r'Showing\s+\d+[-–]\d+\s+of\s+(\d+(?:,\d+)?)',
            r'(\d+(?:,\d+)?)\s+listings?'
        ]
        
        # Look for result count text
        for element in soup.find_all(text=re.compile(r'\d+(?:,\d+)?')):
            text = element.strip()
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    count_str = match.group(1).replace(',', '')
                    try:
                        return int(count_str)
                    except ValueError:
                        continue
        
        return None
    
    def build_page_url(self, base_url: str, page_number: int) -> str:
        """
        Build URL for a specific page number.
        
        Args:
            base_url: Base URL (can include existing params)
            page_number: Target page number
            
        Returns:
            URL for the specified page
        """
        parsed = urlparse(base_url)
        params = parse_qs(parsed.query)
        
        # Update page parameter
        params['page'] = [str(page_number)]
        
        # Update ref parameter for Etsy
        if page_number > 1:
            params['ref'] = [f'pagination_{page_number}']
        
        # Rebuild URL
        new_query = urlencode(params, doseq=True)
        new_url = urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            new_query,
            parsed.fragment
        ))
        
        return new_url
    
    def get_next_page_url(self, current_url: str, current_page: int) -> str:
        """
        Generate next page URL from current URL.
        
        Args:
            current_url: Current page URL
            current_page: Current page number
            
        Returns:
            Next page URL
        """
        return self.build_page_url(current_url, current_page + 1)
    
    def is_last_page(self, html_content: str) -> bool:
        """
        Check if this is the last page.
        
        Args:
            html_content: Page HTML
            
        Returns:
            True if last page
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Check for disabled next button
        next_button = soup.select_one(
            'a[aria-label*="Next"][disabled], '
            'a.wt-pagination__item--next[disabled], '
            'button[aria-label*="Next"][disabled]'
        )
        if next_button:
            return True
        
        # Check if next link exists
        next_link = soup.select_one(
            'a[aria-label*="Next"]:not([disabled]), '
            'a.wt-pagination__item--next:not([disabled])'
        )
        if not next_link:
            return True
        
        # Check for "no more results" message
        no_results = soup.find(text=re.compile(
            r'no more|end of results|last page', 
            re.IGNORECASE
        ))
        if no_results:
            return True
        
        return False