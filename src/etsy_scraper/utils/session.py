"""
Session management with retry logic for Etsy scraper.
Handles retries, session rotation, and error recovery.
"""

import time
import random
from typing import Dict, Optional, Tuple, Callable
import logging
import sys

try:
    from curl_cffi.requests import Session
except ImportError as e:
    logging.error("curl_cffi is not installed. Please install it using: uv add curl-cffi")
    logging.error(f"Import error: {e}")
    sys.exit(1)

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages curl-cffi sessions with retry and rotation capabilities."""
    
    def __init__(self, max_retries: int = 3, backoff_factor: float = 2.0):
        """
        Initialize session manager.
        
        Args:
            max_retries: Maximum number of retry attempts
            backoff_factor: Exponential backoff factor for retries
        """
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.session = None
        self.request_count = 0
        self.session_age = time.time()
        self.max_requests_per_session = 50  # Rotate after N requests
        self.max_session_age = 300  # Rotate after 5 minutes
        
    def get_session(self) -> Session:
        """
        Get current session or create new one if needed.
        
        Returns:
            Active curl-cffi session
        """
        if self.should_rotate_session():
            self.rotate_session()
            
        if not self.session:
            self.session = Session()
            self.session_age = time.time()
            self.request_count = 0
            logger.info("Created new session")
            
        return self.session
    
    def should_rotate_session(self) -> bool:
        """
        Check if session should be rotated.
        
        Returns:
            True if session should be rotated
        """
        if not self.session:
            return False
            
        # Check request count
        if self.request_count >= self.max_requests_per_session:
            logger.info(f"Session rotation needed: {self.request_count} requests made")
            return True
            
        # Check session age
        age = time.time() - self.session_age
        if age > self.max_session_age:
            logger.info(f"Session rotation needed: session is {age:.0f} seconds old")
            return True
            
        return False
    
    def rotate_session(self):
        """Rotate to a new session."""
        if self.session:
            try:
                self.session.close()
            except Exception as e:
                logger.warning(f"Error closing session: {e}")
                
        self.session = Session()
        self.session_age = time.time()
        self.request_count = 0
        logger.info("Rotated to new session")
    
    def make_request_with_retry(
        self,
        request_func: Callable,
        *args,
        **kwargs
    ) -> Tuple[bool, any]:
        """
        Make request with retry logic.
        
        Args:
            request_func: Function to call for making request
            *args: Positional arguments for request function
            **kwargs: Keyword arguments for request function
            
        Returns:
            Tuple of (success, result)
        """
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                result = request_func(*args, **kwargs)
                self.request_count += 1
                return True, result
                
            except Exception as e:
                last_error = e
                logger.warning(f"Request attempt {attempt + 1} failed: {e}")
                
                if attempt < self.max_retries - 1:
                    # Calculate delay with exponential backoff
                    delay = (self.backoff_factor ** attempt) * (1 + random.random())
                    logger.info(f"Retrying in {delay:.1f} seconds...")
                    time.sleep(delay)
                    
                    # Rotate session on certain errors
                    if self._should_rotate_on_error(e):
                        self.rotate_session()
                        
        logger.error(f"All retry attempts failed. Last error: {last_error}")
        return False, None
    
    def _should_rotate_on_error(self, error: Exception) -> bool:
        """
        Determine if session should be rotated based on error.
        
        Args:
            error: Exception that occurred
            
        Returns:
            True if session should be rotated
        """
        error_str = str(error).lower()
        
        # Rotate on connection/network errors
        rotate_keywords = [
            "connection", "timeout", "reset", "refused",
            "broken pipe", "ssl", "certificate"
        ]
        
        for keyword in rotate_keywords:
            if keyword in error_str:
                logger.info(f"Rotating session due to {keyword} error")
                return True
                
        return False
    
    def handle_block_detection(self, wait_time: Optional[int] = None):
        """
        Handle bot detection/blocking.
        
        Args:
            wait_time: Time to wait in seconds (default: random 30-60)
        """
        if wait_time is None:
            wait_time = random.randint(1, 10)
            
        logger.warning(f"Block detected. Waiting {wait_time} seconds...")
        time.sleep(wait_time)
        
        # Always rotate session after block
        self.rotate_session()
    
    def close(self):
        """Close current session."""
        if self.session:
            try:
                self.session.close()
                logger.info("Session closed")
            except Exception as e:
                logger.warning(f"Error closing session: {e}")
            finally:
                self.session = None


class RateLimiter:
    """Rate limiting to avoid triggering anti-bot measures."""
    
    def __init__(self, min_delay: float = 1.0, max_delay: float = 3.0):
        """
        Initialize rate limiter.
        
        Args:
            min_delay: Minimum delay between requests
            max_delay: Maximum delay between requests
        """
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.last_request_time = 0
        
    def wait_if_needed(self):
        """Wait if necessary to respect rate limits."""
        elapsed = time.time() - self.last_request_time
        delay = random.uniform(self.min_delay, self.max_delay)
        
        if elapsed < delay:
            wait_time = delay - elapsed
            logger.debug(f"Rate limiting: waiting {wait_time:.1f} seconds")
            time.sleep(wait_time)
            
        self.last_request_time = time.time()
    
    def adaptive_delay(self, success_count: int, error_count: int):
        """
        Adjust delays based on success/error rates.
        
        Args:
            success_count: Number of successful requests
            error_count: Number of failed requests
        """
        if error_count > success_count * 0.2:  # More than 20% errors
            # Increase delays
            self.min_delay = min(self.min_delay * 1.5, 10)
            self.max_delay = min(self.max_delay * 1.5, 15)
            logger.info(f"Increased delays: {self.min_delay:.1f}-{self.max_delay:.1f}s")
        elif error_count < success_count * 0.05:  # Less than 5% errors
            # Decrease delays slightly
            self.min_delay = max(self.min_delay * 0.9, 0.5)
            self.max_delay = max(self.max_delay * 0.9, 2)
            logger.debug(f"Decreased delays: {self.min_delay:.1f}-{self.max_delay:.1f}s")