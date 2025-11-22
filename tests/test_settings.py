"""
Unit tests for settings module.

Tests configuration loading, validation, and error handling.
"""

import os
import pytest
from pathlib import Path
from unittest.mock import patch
import warnings

from settings import (
    ClaudeConfig,
    ShopifyConfig,
    DatabaseConfig,
    BrandConfig,
    ContentConfig,
    InfluencerConfig,
    Config,
    DEFAULT_CLAUDE_MODEL,
    DEFAULT_MAX_TOKENS,
    DEFAULT_SHOPIFY_API_VERSION,
)


class TestClaudeConfig:
    """Test ClaudeConfig class."""

    def test_valid_config(self):
        """Test creating valid Claude configuration."""
        config = ClaudeConfig(
            api_key="test_key_123",
            model="claude-sonnet-4-20250514",
            max_tokens=4000
        )
        assert config.api_key == "test_key_123"
        assert config.model == "claude-sonnet-4-20250514"
        assert config.max_tokens == 4000

    def test_default_values(self):
        """Test default configuration values."""
        config = ClaudeConfig(api_key="test_key")
        assert config.model == DEFAULT_CLAUDE_MODEL
        assert config.max_tokens == DEFAULT_MAX_TOKENS

    def test_warns_on_missing_api_key(self):
        """Test warning when API key is missing."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            config = ClaudeConfig(api_key="")
            assert len(w) == 1
            assert "ANTHROPIC_API_KEY is not set" in str(w[0].message)

    def test_invalid_max_tokens_raises_error(self):
        """Test that invalid max_tokens raises ValueError."""
        with pytest.raises(ValueError, match="max_tokens must be between"):
            ClaudeConfig(api_key="test", max_tokens=0)

        with pytest.raises(ValueError, match="max_tokens must be between"):
            ClaudeConfig(api_key="test", max_tokens=300000)

    @patch.dict(os.environ, {
        'ANTHROPIC_API_KEY': 'env_test_key',
        'CLAUDE_MODEL': 'test-model',
        'MAX_TOKENS': '5000'
    })
    def test_from_env(self):
        """Test loading configuration from environment."""
        config = ClaudeConfig.from_env()
        assert config.api_key == 'env_test_key'
        assert config.model == 'test-model'
        assert config.max_tokens == 5000

    @patch.dict(os.environ, {'MAX_TOKENS': 'invalid'})
    def test_from_env_invalid_max_tokens(self):
        """Test handling of invalid MAX_TOKENS in environment."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            config = ClaudeConfig.from_env()
            assert config.max_tokens == DEFAULT_MAX_TOKENS
            assert any("Invalid MAX_TOKENS value" in str(warning.message) for warning in w)


class TestShopifyConfig:
    """Test ShopifyConfig class."""

    def test_valid_config(self):
        """Test creating valid Shopify configuration."""
        config = ShopifyConfig(
            store_url="test.myshopify.com",
            api_key="test_key",
            api_secret="test_secret",
            access_token="test_token"
        )
        assert config.store_url == "test.myshopify.com"
        assert config.api_key == "test_key"
        assert config.access_token == "test_token"

    def test_warns_on_incomplete_credentials(self):
        """Test warning when credentials are incomplete."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            config = ShopifyConfig(
                store_url="test.myshopify.com",
                api_key="",
                api_secret="secret",
                access_token=""
            )
            assert any("Shopify credentials are incomplete" in str(warning.message) for warning in w)

    def test_warns_on_invalid_store_url(self):
        """Test warning when store URL format is invalid."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            config = ShopifyConfig(
                store_url="invalid-url.com",
                api_key="key",
                api_secret="secret",
                access_token="token"
            )
            assert any("may be invalid" in str(warning.message) for warning in w)


class TestDatabaseConfig:
    """Test DatabaseConfig class."""

    def test_valid_config(self):
        """Test creating valid database configuration."""
        config = DatabaseConfig(
            host="localhost",
            port=3306,
            database="test_db",
            user="test_user",
            password="test_pass"
        )
        assert config.host == "localhost"
        assert config.port == 3306
        assert config.database == "test_db"

    def test_connection_string(self):
        """Test connection string generation."""
        config = DatabaseConfig(
            host="localhost",
            port=3306,
            database="test_db",
            user="user",
            password="pass"
        )
        expected = "mysql+pymysql://user:pass@localhost:3306/test_db"
        assert config.connection_string == expected

    def test_invalid_port_raises_error(self):
        """Test that invalid port raises ValueError."""
        with pytest.raises(ValueError, match="Invalid port number"):
            DatabaseConfig(
                host="localhost",
                port=0,
                database="db",
                user="user",
                password="pass"
            )

        with pytest.raises(ValueError, match="Invalid port number"):
            DatabaseConfig(
                host="localhost",
                port=99999,
                database="db",
                user="user",
                password="pass"
            )

    @patch.dict(os.environ, {'MYSQL_PORT': 'invalid'})
    def test_from_env_invalid_port(self):
        """Test handling of invalid port in environment."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            config = DatabaseConfig.from_env()
            assert config.port == 3306  # Default port


class TestBrandConfig:
    """Test BrandConfig class."""

    def test_default_values(self):
        """Test default brand configuration values."""
        config = BrandConfig()
        assert config.name == "Linoroso"
        assert config.tagline == "Simplicity, Elegance, Functionality"
        assert len(config.main_categories) == 4
        assert "kitchen knives" in config.main_categories

    @patch.dict(os.environ, {
        'BRAND_NAME': 'TestBrand',
        'MAIN_CATEGORIES': 'cat1, cat2, cat3'
    })
    def test_from_env(self):
        """Test loading brand config from environment."""
        config = BrandConfig.from_env()
        assert config.name == 'TestBrand'
        assert len(config.main_categories) == 3
        assert 'cat1' in config.main_categories

    @patch.dict(os.environ, {'MAIN_CATEGORIES': 'cat1,  ,cat2,  ,cat3'})
    def test_from_env_filters_empty_categories(self):
        """Test that empty categories are filtered out."""
        config = BrandConfig.from_env()
        assert len(config.main_categories) == 3
        assert '' not in config.main_categories


class TestContentConfig:
    """Test ContentConfig class."""

    def test_valid_config(self):
        """Test creating valid content configuration."""
        config = ContentConfig(
            output_path=Path("./output"),
            min_word_count=800,
            max_word_count=1500,
            posts_per_day=3
        )
        assert config.min_word_count == 800
        assert config.max_word_count == 1500
        assert config.posts_per_day == 3

    def test_validation_min_exceeds_max(self):
        """Test that min > max raises ValueError."""
        with pytest.raises(ValueError, match="cannot exceed"):
            ContentConfig(
                output_path=Path("./output"),
                min_word_count=2000,
                max_word_count=1000
            )

    def test_validation_negative_posts(self):
        """Test that negative posts_per_day raises ValueError."""
        with pytest.raises(ValueError, match="must be >= 0"):
            ContentConfig(
                output_path=Path("./output"),
                posts_per_day=-1
            )

    @patch.dict(os.environ, {'MIN_WORD_COUNT': 'invalid'})
    def test_from_env_invalid_integer(self):
        """Test handling of invalid integer in environment."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            config = ContentConfig.from_env()
            # Should use default value
            assert config.min_word_count == 800


class TestInfluencerConfig:
    """Test InfluencerConfig class."""

    def test_valid_config(self):
        """Test creating valid influencer configuration."""
        config = InfluencerConfig(
            outreach_limit=50,
            min_follower_count=10000,
            min_engagement_rate=3.0
        )
        assert config.outreach_limit == 50
        assert config.min_follower_count == 10000
        assert config.min_engagement_rate == 3.0

    def test_validation_negative_followers(self):
        """Test that negative follower count raises ValueError."""
        with pytest.raises(ValueError, match="must be >= 0"):
            InfluencerConfig(min_follower_count=-1)

    def test_validation_engagement_rate_range(self):
        """Test engagement rate must be 0-100."""
        with pytest.raises(ValueError, match="must be 0-100"):
            InfluencerConfig(min_engagement_rate=-1)

        with pytest.raises(ValueError, match="must be 0-100"):
            InfluencerConfig(min_engagement_rate=150)


class TestConfig:
    """Test main Config class."""

    @patch.dict(os.environ, {
        'ENVIRONMENT': 'production',
        'DEBUG': 'true',
        'LOG_LEVEL': 'DEBUG'
    })
    def test_main_config_from_env(self):
        """Test loading main config from environment."""
        config = Config()
        assert config.environment == 'production'
        assert config.debug is True
        assert config.log_level == 'DEBUG'

    def test_is_production(self):
        """Test is_production property."""
        with patch.dict(os.environ, {'ENVIRONMENT': 'production'}):
            config = Config()
            assert config.is_production is True
            assert config.is_development is False

    def test_is_development(self):
        """Test is_development property."""
        with patch.dict(os.environ, {'ENVIRONMENT': 'development'}):
            config = Config()
            assert config.is_development is True
            assert config.is_production is False

    def test_validate_missing_credentials(self):
        """Test validation detects missing credentials."""
        with patch.dict(os.environ, {}, clear=True):
            config = Config()
            missing = config.validate()
            assert 'ANTHROPIC_API_KEY' in missing

    def test_to_dict(self):
        """Test to_dict excludes sensitive data."""
        config = Config()
        config_dict = config.to_dict()

        # Should include non-sensitive data
        assert 'environment' in config_dict
        assert 'brand_name' in config_dict

        # Should NOT include sensitive data
        assert 'api_key' not in str(config_dict).lower()
        assert 'password' not in str(config_dict).lower()
