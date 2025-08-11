"""Error handling utilities for the AI job agent."""

import logging
import traceback
from typing import Optional, Any, Callable
from functools import wraps
from enum import Enum


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class JobAgentError(Exception):
    """Base exception class for job agent errors."""
    
    def __init__(self, message: str, severity: ErrorSeverity = ErrorSeverity.MEDIUM, 
                 context: Optional[dict] = None):
        """Initialize job agent error."""
        super().__init__(message)
        self.message = message
        self.severity = severity
        self.context = context or {}
    
    def __str__(self):
        return f"[{self.severity.value.upper()}] {self.message}"


class WebScrapingError(JobAgentError):
    """Error during web scraping operations."""
    pass


class APIError(JobAgentError):
    """Error during API operations."""
    pass


class ValidationError(JobAgentError):
    """Error during data validation."""
    pass


class ConfigurationError(JobAgentError):
    """Error in configuration or setup."""
    pass


class ErrorHandler:
    """Central error handling and logging system."""
    
    def __init__(self, logger_name: str = __name__):
        """Initialize error handler."""
        self.logger = logging.getLogger(logger_name)
        self.error_counts = {
            ErrorSeverity.LOW: 0,
            ErrorSeverity.MEDIUM: 0,
            ErrorSeverity.HIGH: 0,
            ErrorSeverity.CRITICAL: 0
        }
    
    def handle_error(self, error: Exception, severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                    context: Optional[dict] = None, reraise: bool = False) -> bool:
        """Handle and log an error."""
        try:
            # Update error counts
            self.error_counts[severity] += 1
            
            # Create error message
            error_msg = f"Error: {str(error)}"
            if context:
                error_msg += f" | Context: {context}"
            
            # Log based on severity
            if severity == ErrorSeverity.CRITICAL:
                self.logger.critical(error_msg, exc_info=True)
            elif severity == ErrorSeverity.HIGH:
                self.logger.error(error_msg, exc_info=True)
            elif severity == ErrorSeverity.MEDIUM:
                self.logger.warning(error_msg)
            else:
                self.logger.info(error_msg)
            
            # Reraise if requested
            if reraise:
                raise error
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error in error handler: {e}")
            return False
    
    def get_error_summary(self) -> dict:
        """Get summary of error counts."""
        return self.error_counts.copy()
    
    def reset_counts(self):
        """Reset error counts."""
        for severity in self.error_counts:
            self.error_counts[severity] = 0


def error_handler_decorator(severity: ErrorSeverity = ErrorSeverity.MEDIUM, 
                          reraise: bool = False, 
                          default_return: Any = None):
    """Decorator for automatic error handling."""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            handler = ErrorHandler()
            try:
                return func(*args, **kwargs)
            except Exception as e:
                handler.handle_error(e, severity, reraise=reraise)
                return default_return
        return wrapper
    return decorator


def safe_execute(func: Callable, *args, max_retries: int = 3, 
                delay: float = 1.0, **kwargs):
    """Safely execute a function with retries."""
    import time
    
    handler = ErrorHandler()
    last_error = None
    
    for attempt in range(max_retries + 1):
        try:
            result = func(*args, **kwargs)
            return True, result
        except Exception as e:
            last_error = e
            severity = ErrorSeverity.HIGH if attempt == max_retries else ErrorSeverity.MEDIUM
            handler.handle_error(e, severity, 
                               context={"attempt": attempt + 1, "max_retries": max_retries})
            
            if attempt < max_retries:
                time.sleep(delay)
    
    return False, last_error
