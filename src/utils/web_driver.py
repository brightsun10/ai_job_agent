"""Web driver utilities for browser automation."""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import logging


class WebDriverManager:
    """Manages web driver instance and common operations."""
    
    def __init__(self, headless=True, timeout=10):
        """Initialize web driver manager.
        
        Args:
            headless (bool): Run browser in headless mode
            timeout (int): Default timeout for operations
        """
        self.headless = headless
        self.timeout = timeout
        self.driver = None
        self.wait = None
        self.logger = logging.getLogger(__name__)
    
    def start_driver(self):
        """Start the web driver instance."""
        try:
            options = Options()
            if self.headless:
                options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            
            self.driver = webdriver.Chrome(options=options)
            self.wait = WebDriverWait(self.driver, self.timeout)
            self.logger.info("Web driver started successfully")
            return True
        except WebDriverException as e:
            self.logger.error(f"Failed to start web driver: {e}")
            return False
    
    def stop_driver(self):
        """Stop the web driver instance."""
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("Web driver stopped successfully")
            except Exception as e:
                self.logger.error(f"Error stopping web driver: {e}")
            finally:
                self.driver = None
                self.wait = None
    
    def navigate_to(self, url):
        """Navigate to a URL.
        
        Args:
            url (str): The URL to navigate to
            
        Returns:
            bool: True if navigation successful, False otherwise
        """
        try:
            self.driver.get(url)
            self.logger.info(f"Navigated to {url}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to navigate to {url}: {e}")
            return False
    
    def find_element_safe(self, by, value, timeout=None):
        """Safely find an element with timeout.
        
        Args:
            by: Selenium By locator
            value (str): Locator value
            timeout (int): Custom timeout (uses default if None)
            
        Returns:
            WebElement or None: Found element or None if not found
        """
        timeout = timeout or self.timeout
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            self.logger.warning(f"Element not found: {by}={value}")
            return None
    
    def click_element_safe(self, by, value, timeout=None):
        """Safely click an element.
        
        Args:
            by: Selenium By locator
            value (str): Locator value
            timeout (int): Custom timeout
            
        Returns:
            bool: True if click successful, False otherwise
        """
        element = self.find_element_safe(by, value, timeout)
        if element:
            try:
                element.click()
                return True
            except Exception as e:
                self.logger.error(f"Failed to click element {by}={value}: {e}")
        return False
    
    def get_page_source(self):
        """Get current page source.
        
        Returns:
            str: Page source or empty string if error
        """
        try:
            return self.driver.page_source
        except Exception as e:
            self.logger.error(f"Failed to get page source: {e}")
            return ""
    
    def __enter__(self):
        """Context manager entry."""
        self.start_driver()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop_driver()
