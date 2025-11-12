"""
Unit tests for Error Handling Utilities
"""

import pytest
import time
from unittest.mock import Mock, patch
import anthropic
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.error_handling import (
    retry_with_backoff,
    handle_api_error,
    validate_input,
    safe_execute,
    RateLimiter,
    ValidationError,
    APIError,
    RateLimitError
)


class TestRetryWithBackoff:
    """Test retry_with_backoff decorator"""

    def test_successful_execution(self):
        """Test that successful function executes without retry"""
        call_count = 0

        @retry_with_backoff(max_retries=3)
        def success_function():
            nonlocal call_count
            call_count += 1
            return "success"

        result = success_function()
        assert result == "success"
        assert call_count == 1

    def test_retry_on_exception(self):
        """Test that function retries on exception"""
        call_count = 0

        @retry_with_backoff(max_retries=3, initial_delay=0.01)
        def failing_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Temporary error")
            return "success"

        result = failing_function()
        assert result == "success"
        assert call_count == 3

    def test_max_retries_exceeded(self):
        """Test that exception is raised after max retries"""
        @retry_with_backoff(max_retries=2, initial_delay=0.01)
        def always_fails():
            raise ValueError("Always fails")

        with pytest.raises(ValueError):
            always_fails()

    def test_exponential_backoff(self):
        """Test exponential backoff timing"""
        call_times = []

        @retry_with_backoff(max_retries=3, initial_delay=0.1, exponential_base=2.0)
        def timed_function():
            call_times.append(time.time())
            if len(call_times) < 3:
                raise ValueError("Retry me")
            return "success"

        timed_function()

        # Verify exponential delays
        assert len(call_times) == 3
        # Second call should be ~0.1s after first
        assert call_times[1] - call_times[0] >= 0.1
        # Third call should be ~0.2s after second
        assert call_times[2] - call_times[1] >= 0.2

    def test_specific_exceptions_only(self):
        """Test that only specified exceptions are retried"""
        call_count = 0

        @retry_with_backoff(max_retries=3, exceptions=(ValueError,), initial_delay=0.01)
        def selective_retry():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ValueError("Retryable")
            raise TypeError("Not retryable")

        with pytest.raises(TypeError):
            selective_retry()

        assert call_count == 2  # One original + one retry


class TestHandleAPIError:
    """Test handle_api_error decorator"""

    def test_successful_api_call(self):
        """Test successful API call passes through"""
        @handle_api_error
        def successful_api():
            return {"status": "ok"}

        result = successful_api()
        assert result == {"status": "ok"}

    def test_anthropic_api_error(self):
        """Test Anthropic API error handling"""
        @handle_api_error
        def api_error():
            raise anthropic.APIError("API failed")

        with pytest.raises(APIError):
            api_error()

    def test_rate_limit_error(self):
        """Test rate limit error handling"""
        @handle_api_error
        def rate_limit():
            raise anthropic.RateLimitError("Rate limited")

        with pytest.raises(RateLimitError):
            rate_limit()

    def test_authentication_error(self):
        """Test authentication error handling"""
        @handle_api_error
        def auth_error():
            raise anthropic.AuthenticationError("Invalid API key")

        with pytest.raises(APIError):
            auth_error()


class TestValidateInput:
    """Test validate_input function"""

    def test_valid_input_passes(self):
        """Test that valid input doesn't raise error"""
        validate_input(True, "Should pass")
        validate_input(1 > 0, "Should pass")
        validate_input(len("test") > 0, "Should pass")

    def test_invalid_input_raises(self):
        """Test that invalid input raises ValidationError"""
        with pytest.raises(ValidationError) as exc_info:
            validate_input(False, "This should fail")
        assert "This should fail" in str(exc_info.value)

    def test_empty_string_validation(self):
        """Test validation of empty strings"""
        with pytest.raises(ValidationError):
            validate_input(bool(""), "String cannot be empty")

    def test_list_length_validation(self):
        """Test validation of list lengths"""
        validate_input(len([1, 2, 3]) > 0, "List has items")

        with pytest.raises(ValidationError):
            validate_input(len([]) > 0, "List must not be empty")


class TestSafeExecute:
    """Test safe_execute function"""

    def test_successful_execution(self):
        """Test successful function execution"""
        result = safe_execute(lambda: 42)
        assert result == 42

    def test_exception_returns_default(self):
        """Test that exceptions return default value"""
        def failing_func():
            raise ValueError("Error!")

        result = safe_execute(failing_func, default="default")
        assert result == "default"

    def test_default_none(self):
        """Test that default is None when not specified"""
        result = safe_execute(lambda: 1/0)
        assert result is None

    def test_error_logging(self):
        """Test that errors are logged"""
        with patch('utils.error_handling.logger') as mock_logger:
            safe_execute(lambda: 1/0, log_error=True)
            mock_logger.error.assert_called_once()

    def test_no_error_logging(self):
        """Test that errors aren't logged when disabled"""
        with patch('utils.error_handling.logger') as mock_logger:
            safe_execute(lambda: 1/0, log_error=False)
            mock_logger.error.assert_not_called()


class TestRateLimiter:
    """Test RateLimiter class"""

    def test_initialization(self):
        """Test rate limiter initialization"""
        limiter = RateLimiter(requests_per_minute=60)
        assert limiter.requests_per_minute == 60
        assert limiter.min_interval == 1.0

    def test_rate_limiting_enforced(self):
        """Test that rate limiting enforces delays"""
        limiter = RateLimiter(requests_per_minute=60)  # 1 per second

        start_time = time.time()
        limiter.wait_if_needed()
        limiter.wait_if_needed()
        elapsed = time.time() - start_time

        # Second call should wait ~1 second
        assert elapsed >= 1.0

    def test_decorator_usage(self):
        """Test using RateLimiter as decorator"""
        limiter = RateLimiter(requests_per_minute=120)  # 0.5s interval

        @limiter
        def rate_limited_function():
            return time.time()

        call_times = []
        for _ in range(3):
            call_times.append(rate_limited_function())

        # Verify intervals
        for i in range(1, len(call_times)):
            interval = call_times[i] - call_times[i-1]
            assert interval >= 0.5

    def test_no_wait_on_first_call(self):
        """Test that first call doesn't wait"""
        limiter = RateLimiter(requests_per_minute=60)

        start = time.time()
        limiter.wait_if_needed()
        elapsed = time.time() - start

        # First call should be immediate
        assert elapsed < 0.1


class TestCustomExceptions:
    """Test custom exception classes"""

    def test_validation_error(self):
        """Test ValidationError"""
        with pytest.raises(ValidationError) as exc_info:
            raise ValidationError("Invalid input")
        assert "Invalid input" in str(exc_info.value)

    def test_api_error(self):
        """Test APIError"""
        with pytest.raises(APIError) as exc_info:
            raise APIError("API call failed")
        assert "API call failed" in str(exc_info.value)

    def test_rate_limit_error(self):
        """Test RateLimitError is subclass of APIError"""
        error = RateLimitError("Rate limited")
        assert isinstance(error, APIError)
        assert isinstance(error, Exception)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
