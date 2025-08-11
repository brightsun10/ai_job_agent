"""Retry Logic with Exponential Backoff for AI Job Agent

Provides robust retry mechanisms with exponential backoff and jitter.
"""

import time
import random
import logging
from typing import Any, Callable, Optional, Union, Type, List
from functools import wraps
from dataclasses import dataclass
from enum import Enum


class RetryStrategy(Enum):
    """Retry strategy types."""
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    FIXED_DELAY = "fixed_delay"
    FIBONACCI_BACKOFF = "fibonacci_backoff"


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""
    max_attempts: int = 3
    base_delay: float = 1.0  # seconds
    max_delay: float = 60.0  # seconds
    exponential_factor: float = 2.0
    jitter: bool = True
    jitter_factor: float = 0.1
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF
    retryable_exceptions: tuple = (Exception,)
    non_retryable_exceptions: tuple = ()
    

class RetryableError(Exception):
    """Exception that should trigger a retry."""
    pass


class NonRetryableError(Exception):
    """Exception that should not trigger a retry."""
    pass


class RetryExhaustedError(Exception):
    """Exception raised when all retry attempts are exhausted."""
    
    def __init__(self, attempts: int, last_exception: Exception):
        self.attempts = attempts
        self.last_exception = last_exception
        super().__init__(f"Retry exhausted after {attempts} attempts. Last error: {last_exception}")


class RetryHandler:
    """Handles retry logic with various backoff strategies."""
    
    def __init__(self, config: Optional[RetryConfig] = None):
        """Initialize retry handler with configuration.
        
        Args:
            config: Retry configuration, defaults to RetryConfig()
        """
        self.config = config or RetryConfig()
        self.logger = logging.getLogger(__name__)
        
        # Pre-calculate fibonacci sequence for fibonacci backoff
        self._fibonacci_sequence = self._generate_fibonacci_sequence(
            self.config.max_attempts + 5  # Extra buffer
        )
    
    def _generate_fibonacci_sequence(self, n: int) -> List[int]:
        """Generate fibonacci sequence up to n terms."""
        if n <= 0:
            return []
        elif n == 1:
            return [1]
        
        sequence = [1, 1]
        for i in range(2, n):
            sequence.append(sequence[i-1] + sequence[i-2])
        
        return sequence
    
    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt number.
        
        Args:
            attempt: Current attempt number (0-indexed)
            
        Returns:
            Delay in seconds
        """
        if self.config.strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            delay = self.config.base_delay * (self.config.exponential_factor ** attempt)
        elif self.config.strategy == RetryStrategy.LINEAR_BACKOFF:
            delay = self.config.base_delay * (attempt + 1)
        elif self.config.strategy == RetryStrategy.FIXED_DELAY:
            delay = self.config.base_delay
        elif self.config.strategy == RetryStrategy.FIBONACCI_BACKOFF:
            if attempt < len(self._fibonacci_sequence):
                delay = self.config.base_delay * self._fibonacci_sequence[attempt]
            else:
                # Fall back to exponential for large attempts
                delay = self.config.base_delay * (self.config.exponential_factor ** attempt)
        else:
            delay = self.config.base_delay
        
        # Apply maximum delay limit
        delay = min(delay, self.config.max_delay)
        
        # Add jitter if enabled
        if self.config.jitter:
            jitter_amount = delay * self.config.jitter_factor * random.random()
            delay += jitter_amount
        
        return delay
    
    def _should_retry(self, exception: Exception, attempt: int) -> bool:
        """Determine if operation should be retried.
        
        Args:
            exception: Exception that occurred
            attempt: Current attempt number (0-indexed)
            
        Returns:
            True if should retry, False otherwise
        """
        # Check if we've exhausted max attempts
        if attempt >= self.config.max_attempts:
            return False
        
        # Check for non-retryable exceptions
        if self.config.non_retryable_exceptions and isinstance(
            exception, self.config.non_retryable_exceptions
        ):
            return False
        
        # Check for retryable exceptions
        return isinstance(exception, self.config.retryable_exceptions)
    
    def execute_with_retry(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with retry logic.
        
        Args:
            func: Function to execute
            *args: Positional arguments for function
            **kwargs: Keyword arguments for function
            
        Returns:
            Function result
            
        Raises:
            RetryExhaustedError: When all retry attempts are exhausted
            NonRetryableError: When a non-retryable exception occurs
        """
        last_exception = None
        
        for attempt in range(self.config.max_attempts):
            try:
                self.logger.debug(f"Attempting operation (attempt {attempt + 1}/{self.config.max_attempts})")
                result = func(*args, **kwargs)
                
                if attempt > 0:
                    self.logger.info(f"Operation succeeded after {attempt + 1} attempts")
                
                return result
                
            except Exception as e:
                last_exception = e
                
                if not self._should_retry(e, attempt):
                    if isinstance(e, self.config.non_retryable_exceptions):
                        self.logger.error(f"Non-retryable exception occurred: {e}")
                        raise NonRetryableError(f"Non-retryable exception: {e}") from e
                    else:
                        self.logger.error(f"Retry attempts exhausted. Last error: {e}")
                        raise RetryExhaustedError(attempt + 1, e)
                
                # Calculate delay for next attempt
                if attempt < self.config.max_attempts - 1:  # Don't delay after last attempt
                    delay = self._calculate_delay(attempt)
                    self.logger.warning(
                        f"Operation failed (attempt {attempt + 1}/{self.config.max_attempts}): {e}. "
                        f"Retrying in {delay:.2f} seconds..."
                    )
                    time.sleep(delay)
                else:
                    self.logger.error(f"Final attempt failed: {e}")
        
        # This should never be reached, but just in case
        raise RetryExhaustedError(self.config.max_attempts, last_exception)


def retry_with_backoff(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_factor: float = 2.0,
    jitter: bool = True,
    jitter_factor: float = 0.1,
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF,
    retryable_exceptions: tuple = (Exception,),
    non_retryable_exceptions: tuple = ()
):
    """Decorator for adding retry logic to functions.
    
    Args:
        max_attempts: Maximum number of retry attempts
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds
        exponential_factor: Factor for exponential backoff
        jitter: Whether to add jitter to delays
        jitter_factor: Jitter factor (percentage of delay)
        strategy: Retry strategy to use
        retryable_exceptions: Tuple of exceptions that should trigger retry
        non_retryable_exceptions: Tuple of exceptions that should not trigger retry
    
    Returns:
        Decorated function with retry logic
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            config = RetryConfig(
                max_attempts=max_attempts,
                base_delay=base_delay,
                max_delay=max_delay,
                exponential_factor=exponential_factor,
                jitter=jitter,
                jitter_factor=jitter_factor,
                strategy=strategy,
                retryable_exceptions=retryable_exceptions,
                non_retryable_exceptions=non_retryable_exceptions
            )
            
            retry_handler = RetryHandler(config)
            return retry_handler.execute_with_retry(func, *args, **kwargs)
        
        return wrapper
    return decorator


class CircuitBreaker:
    """Circuit breaker pattern implementation for failure protection."""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 60.0):
        """Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Time to wait before attempting recovery
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
        self.logger = logging.getLogger(__name__)
    
    def _is_recovery_timeout_reached(self) -> bool:
        """Check if recovery timeout has been reached."""
        if self.last_failure_time is None:
            return False
        return time.time() - self.last_failure_time >= self.recovery_timeout
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection.
        
        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Function result
            
        Raises:
            Exception: If circuit is open or function fails
        """
        if self.state == 'OPEN':
            if self._is_recovery_timeout_reached():
                self.state = 'HALF_OPEN'
                self.logger.info("Circuit breaker moving to HALF_OPEN state")
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            
            # Success - reset failure count and close circuit
            if self.state == 'HALF_OPEN':
                self.state = 'CLOSED'
                self.logger.info("Circuit breaker closed - service recovered")
            
            self.failure_count = 0
            return result
            
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = 'OPEN'
                self.logger.error(f"Circuit breaker opened after {self.failure_count} failures")
            
            raise e


# Convenience functions for common retry scenarios
def retry_on_network_error(max_attempts: int = 3, base_delay: float = 2.0):
    """Retry decorator for network-related operations."""
    import requests
    from urllib.error import URLError
    
    return retry_with_backoff(
        max_attempts=max_attempts,
        base_delay=base_delay,
        max_delay=30.0,
        retryable_exceptions=(
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
            requests.exceptions.HTTPError,
            URLError,
            OSError,  # Network-related OS errors
        ),
        non_retryable_exceptions=(
            requests.exceptions.HTTPError,  # Client errors (4xx) shouldn't be retried
        )
    )


def retry_on_api_error(max_attempts: int = 5, base_delay: float = 1.0):
    """Retry decorator for API operations."""
    return retry_with_backoff(
        max_attempts=max_attempts,
        base_delay=base_delay,
        max_delay=60.0,
        strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
        retryable_exceptions=(
            TimeoutError,
            ConnectionError,
            OSError,
        )
    )


def retry_on_database_error(max_attempts: int = 3, base_delay: float = 0.5):
    """Retry decorator for database operations."""
    import sqlite3
    
    return retry_with_backoff(
        max_attempts=max_attempts,
        base_delay=base_delay,
        max_delay=10.0,
        retryable_exceptions=(
            sqlite3.OperationalError,
            sqlite3.DatabaseError,
        ),
        non_retryable_exceptions=(
            sqlite3.IntegrityError,  # Don't retry on constraint violations
        )
    )
