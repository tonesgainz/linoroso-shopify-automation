"""
Error Handling and Retry Logic Utilities
Provides decorators and functions for robust error handling
"""

import time
import functools
from typing import Callable, Type, Tuple, Optional
from loguru import logger
import anthropic


class ValidationError(Exception):
    """Raised when input validation fails"""
    pass


class APIError(Exception):
    """Raised when API calls fail"""
    pass


class RateLimitError(APIError):
    """Raised when rate limit is exceeded"""
    pass


def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """
    Decorator that retries a function with exponential backoff

    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay between retries
        exponential_base: Base for exponential backoff calculation
        exceptions: Tuple of exceptions to catch and retry

    Example:
        @retry_with_backoff(max_retries=3, exceptions=(APIError,))
        def call_api():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt == max_retries:
                        logger.error(
                            f"{func.__name__} failed after {max_retries} retries: {e}"
                        )
                        raise

                    # Check if it's a rate limit error from Anthropic
                    if isinstance(e, anthropic.RateLimitError):
                        logger.warning(
                            f"{func.__name__} hit rate limit (attempt {attempt + 1}/{max_retries + 1}). "
                            f"Waiting {delay:.1f}s..."
                        )
                    else:
                        logger.warning(
                            f"{func.__name__} failed (attempt {attempt + 1}/{max_retries + 1}): {e}. "
                            f"Retrying in {delay:.1f}s..."
                        )

                    time.sleep(delay)
                    delay = min(delay * exponential_base, max_delay)

            # This shouldn't be reached, but just in case
            if last_exception:
                raise last_exception

        return wrapper
    return decorator


def handle_api_error(func: Callable) -> Callable:
    """
    Decorator that handles common API errors with appropriate logging

    Example:
        @handle_api_error
        def call_claude_api():
            ...
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except anthropic.APIError as e:
            logger.error(f"Anthropic API error in {func.__name__}: {e}")
            raise APIError(f"API call failed: {e}") from e
        except anthropic.RateLimitError as e:
            logger.error(f"Rate limit exceeded in {func.__name__}: {e}")
            raise RateLimitError(f"Rate limit exceeded: {e}") from e
        except anthropic.APIConnectionError as e:
            logger.error(f"API connection error in {func.__name__}: {e}")
            raise APIError(f"Failed to connect to API: {e}") from e
        except anthropic.AuthenticationError as e:
            logger.error(f"Authentication error in {func.__name__}: {e}")
            raise APIError(f"Authentication failed: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {e}")
            raise

    return wrapper


def validate_input(condition: bool, message: str):
    """
    Validate input and raise ValidationError if condition is False

    Args:
        condition: Condition to check
        message: Error message if validation fails

    Example:
        validate_input(len(keywords) > 0, "Keywords list cannot be empty")
    """
    if not condition:
        logger.error(f"Validation failed: {message}")
        raise ValidationError(message)


def safe_execute(func: Callable, default=None, log_error: bool = True) -> Optional:
    """
    Safely execute a function and return default value on error

    Args:
        func: Function to execute
        default: Default value to return on error
        log_error: Whether to log errors

    Returns:
        Function result or default value

    Example:
        result = safe_execute(lambda: risky_operation(), default=[])
    """
    try:
        return func()
    except Exception as e:
        if log_error:
            logger.error(f"Error in safe_execute: {e}")
        return default


class RateLimiter:
    """
    Simple rate limiter using token bucket algorithm
    """

    def __init__(self, requests_per_minute: int = 50):
        """
        Initialize rate limiter

        Args:
            requests_per_minute: Maximum requests allowed per minute
        """
        self.requests_per_minute = requests_per_minute
        self.min_interval = 60.0 / requests_per_minute
        self.last_request_time = 0.0

    def wait_if_needed(self):
        """Wait if necessary to respect rate limit"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time

        if time_since_last_request < self.min_interval:
            sleep_time = self.min_interval - time_since_last_request
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f}s")
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def __call__(self, func: Callable) -> Callable:
        """Use as decorator"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            self.wait_if_needed()
            return func(*args, **kwargs)
        return wrapper
