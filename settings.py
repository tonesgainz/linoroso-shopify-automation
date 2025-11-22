"""
Configuration Management for Linoroso Shopify Automation
Loads and validates environment variables and settings.

This module provides centralized configuration management for the entire application,
including API credentials, database settings, and business logic parameters.
"""

import os
import warnings
from pathlib import Path
from typing import Optional, List, Dict
from dotenv import load_dotenv
from dataclasses import dataclass, field

# Load environment variables from .env file
load_dotenv()

# Constants
DEFAULT_CLAUDE_MODEL = "claude-sonnet-4-20250514"
DEFAULT_MAX_TOKENS = 4000
DEFAULT_SHOPIFY_API_VERSION = "2024-01"
DEFAULT_MYSQL_PORT = 3306
DEFAULT_MIN_WORD_COUNT = 800
DEFAULT_MAX_WORD_COUNT = 1500
DEFAULT_SOCIAL_POSTS_PER_DAY = 3

@dataclass
class ClaudeConfig:
    """Claude AI API configuration.

    Attributes:
        api_key: Anthropic API key for Claude AI
        model: Claude model version to use
        max_tokens: Maximum tokens for API responses
    """
    api_key: str
    model: str = DEFAULT_CLAUDE_MODEL
    max_tokens: int = DEFAULT_MAX_TOKENS

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if not self.api_key:
            warnings.warn("ANTHROPIC_API_KEY is not set", UserWarning)
        if self.max_tokens < 1 or self.max_tokens > 200000:
            raise ValueError(f"max_tokens must be between 1 and 200000, got {self.max_tokens}")

    @classmethod
    def from_env(cls) -> 'ClaudeConfig':
        """Create configuration from environment variables.

        Returns:
            ClaudeConfig instance populated from environment
        """
        max_tokens_str = os.getenv('MAX_TOKENS', str(DEFAULT_MAX_TOKENS))
        try:
            max_tokens = int(max_tokens_str)
        except ValueError:
            warnings.warn(f"Invalid MAX_TOKENS value: {max_tokens_str}, using default")
            max_tokens = DEFAULT_MAX_TOKENS

        return cls(
            api_key=os.getenv('ANTHROPIC_API_KEY', ''),
            model=os.getenv('CLAUDE_MODEL', DEFAULT_CLAUDE_MODEL),
            max_tokens=max_tokens
        )

@dataclass
class ShopifyConfig:
    """Shopify API configuration.

    Attributes:
        store_url: Shopify store URL (e.g., 'store.myshopify.com')
        api_key: Shopify API key
        api_secret: Shopify API secret
        access_token: Shopify access token
        api_version: Shopify API version to use
    """
    store_url: str
    api_key: str
    api_secret: str
    access_token: str
    api_version: str = DEFAULT_SHOPIFY_API_VERSION

    def __post_init__(self) -> None:
        """Validate Shopify configuration."""
        if not self.api_key or not self.access_token:
            warnings.warn("Shopify credentials are incomplete", UserWarning)
        if self.store_url and not self.store_url.endswith('.myshopify.com'):
            warnings.warn(
                f"Store URL '{self.store_url}' may be invalid. "
                "Expected format: 'store.myshopify.com'",
                UserWarning
            )

    @classmethod
    def from_env(cls) -> 'ShopifyConfig':
        """Create configuration from environment variables.

        Returns:
            ShopifyConfig instance populated from environment
        """
        return cls(
            store_url=os.getenv('SHOPIFY_STORE_URL', 'linoroso.myshopify.com'),
            api_key=os.getenv('SHOPIFY_API_KEY', ''),
            api_secret=os.getenv('SHOPIFY_API_SECRET', ''),
            access_token=os.getenv('SHOPIFY_ACCESS_TOKEN', ''),
            api_version=os.getenv('SHOPIFY_API_VERSION', DEFAULT_SHOPIFY_API_VERSION)
        )

@dataclass
class DatabaseConfig:
    """Database configuration.

    Attributes:
        host: Database server hostname
        port: Database server port
        database: Database name
        user: Database username
        password: Database password
    """
    host: str
    port: int
    database: str
    user: str
    password: str

    def __post_init__(self) -> None:
        """Validate database configuration."""
        if not self.password:
            warnings.warn("MYSQL_PASSWORD is not set", UserWarning)
        if self.port < 1 or self.port > 65535:
            raise ValueError(f"Invalid port number: {self.port}")

    @property
    def connection_string(self) -> str:
        """Generate SQLAlchemy connection string.

        Returns:
            MySQL connection string for SQLAlchemy
        """
        return f"mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"

    @classmethod
    def from_env(cls) -> 'DatabaseConfig':
        """Create configuration from environment variables.

        Returns:
            DatabaseConfig instance populated from environment
        """
        port_str = os.getenv('MYSQL_PORT', str(DEFAULT_MYSQL_PORT))
        try:
            port = int(port_str)
        except ValueError:
            warnings.warn(f"Invalid MYSQL_PORT value: {port_str}, using default")
            port = DEFAULT_MYSQL_PORT

        return cls(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            port=port,
            database=os.getenv('MYSQL_DATABASE', 'linoroso_automation'),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', '')
        )

@dataclass
class BrandConfig:
    """Linoroso brand configuration.

    Attributes:
        name: Brand name
        tagline: Brand tagline/slogan
        voice: Brand voice characteristics
        target_audience: Target customer description
        main_categories: Primary product categories
    """
    name: str = "Linoroso"
    tagline: str = "Simplicity, Elegance, Functionality"
    voice: str = "professional, warm, helpful, family-oriented"
    target_audience: str = "quality-conscious home cooks, culinary enthusiasts"
    main_categories: List[str] = field(default_factory=lambda: [
        "kitchen knives",
        "kitchen shears",
        "knife sets",
        "storage solutions"
    ])

    @classmethod
    def from_env(cls) -> 'BrandConfig':
        """Create configuration from environment variables.

        Returns:
            BrandConfig instance populated from environment
        """
        categories_str = os.getenv(
            'MAIN_CATEGORIES',
            'kitchen knives,kitchen shears,knife sets,storage solutions'
        )
        main_categories = [cat.strip() for cat in categories_str.split(',') if cat.strip()]

        return cls(
            name=os.getenv('BRAND_NAME', 'Linoroso'),
            tagline=os.getenv('BRAND_TAGLINE', 'Simplicity, Elegance, Functionality'),
            voice=os.getenv('BRAND_VOICE', 'professional, warm, helpful, family-oriented'),
            target_audience=os.getenv('TARGET_AUDIENCE', 'quality-conscious home cooks, culinary enthusiasts'),
            main_categories=main_categories
        )

@dataclass
class ContentConfig:
    """Content generation configuration.

    Attributes:
        output_path: Directory path for generated content
        frequency: Content generation frequency
        min_word_count: Minimum word count for content
        max_word_count: Maximum word count for content
        posts_per_day: Number of social posts to generate daily
    """
    output_path: Path
    frequency: str = "daily"
    min_word_count: int = DEFAULT_MIN_WORD_COUNT
    max_word_count: int = DEFAULT_MAX_WORD_COUNT
    posts_per_day: int = DEFAULT_SOCIAL_POSTS_PER_DAY

    def __post_init__(self) -> None:
        """Validate content configuration."""
        if self.min_word_count > self.max_word_count:
            raise ValueError(
                f"min_word_count ({self.min_word_count}) cannot exceed "
                f"max_word_count ({self.max_word_count})"
            )
        if self.posts_per_day < 0:
            raise ValueError(f"posts_per_day must be >= 0, got {self.posts_per_day}")

    @classmethod
    def from_env(cls) -> 'ContentConfig':
        """Create configuration from environment variables.

        Returns:
            ContentConfig instance populated from environment
        """
        # Parse integer values with error handling
        def parse_int(key: str, default: int) -> int:
            try:
                return int(os.getenv(key, str(default)))
            except ValueError:
                warnings.warn(f"Invalid {key} value, using default {default}")
                return default

        return cls(
            output_path=Path(os.getenv('CONTENT_OUTPUT_PATH', './data/generated_content')),
            frequency=os.getenv('BLOG_POST_FREQUENCY', 'daily'),
            min_word_count=parse_int('MIN_WORD_COUNT', DEFAULT_MIN_WORD_COUNT),
            max_word_count=parse_int('MAX_WORD_COUNT', DEFAULT_MAX_WORD_COUNT),
            posts_per_day=parse_int('SOCIAL_POSTS_PER_DAY', DEFAULT_SOCIAL_POSTS_PER_DAY)
        )

@dataclass
class InfluencerConfig:
    """Influencer program configuration.

    Attributes:
        outreach_limit: Maximum number of influencers to contact
        min_follower_count: Minimum follower count for influencers
        min_engagement_rate: Minimum engagement rate percentage
        commission_basic: Basic tier commission percentage
        commission_intermediate: Intermediate tier commission percentage
        commission_advanced: Advanced tier commission percentage
    """
    outreach_limit: int = 50
    min_follower_count: int = 10000
    min_engagement_rate: float = 3.0
    commission_basic: int = 10
    commission_intermediate: int = 15
    commission_advanced: int = 20

    def __post_init__(self) -> None:
        """Validate influencer configuration."""
        if self.min_follower_count < 0:
            raise ValueError(f"min_follower_count must be >= 0, got {self.min_follower_count}")
        if not 0 <= self.min_engagement_rate <= 100:
            raise ValueError(f"min_engagement_rate must be 0-100, got {self.min_engagement_rate}")

    @classmethod
    def from_env(cls) -> 'InfluencerConfig':
        """Create configuration from environment variables.

        Returns:
            InfluencerConfig instance populated from environment
        """
        def parse_int(key: str, default: int) -> int:
            try:
                return int(os.getenv(key, str(default)))
            except ValueError:
                warnings.warn(f"Invalid {key} value, using default {default}")
                return default

        def parse_float(key: str, default: float) -> float:
            try:
                return float(os.getenv(key, str(default)))
            except ValueError:
                warnings.warn(f"Invalid {key} value, using default {default}")
                return default

        return cls(
            outreach_limit=parse_int('INFLUENCER_OUTREACH_LIMIT', 50),
            min_follower_count=parse_int('MIN_FOLLOWER_COUNT', 10000),
            min_engagement_rate=parse_float('MIN_ENGAGEMENT_RATE', 3.0),
            commission_basic=parse_int('COMMISSION_BASIC', 10),
            commission_intermediate=parse_int('COMMISSION_INTERMEDIATE', 15),
            commission_advanced=parse_int('COMMISSION_ADVANCED', 20)
        )

class Config:
    """Main configuration class that aggregates all application settings.

    This class loads and manages all configuration from environment variables,
    organizing them into logical groups for easy access throughout the application.

    Attributes:
        environment: Application environment (development, staging, production)
        debug: Debug mode flag
        log_level: Logging level
        claude: Claude AI configuration
        shopify: Shopify API configuration
        database: Database configuration
        brand: Brand-specific settings
        content: Content generation settings
        influencer: Influencer program settings
        instagram_username: Instagram API username
        instagram_password: Instagram API password
        tiktok_session_id: TikTok API session ID
        pinterest_token: Pinterest API token
        klaviyo_api_key: Klaviyo email marketing API key
        google_analytics_id: Google Analytics property ID
        google_credentials_path: Path to Google credentials JSON
        sentry_dsn: Sentry error tracking DSN
        slack_webhook: Slack webhook URL for notifications
        alert_email: Email address for alerts
        serpapi_key: SerpAPI key for SEO research
    """

    def __init__(self) -> None:
        """Initialize configuration from environment variables."""
        self.environment: str = os.getenv('ENVIRONMENT', 'development')
        self.debug: bool = os.getenv('DEBUG', 'False').lower() == 'true'
        self.log_level: str = os.getenv('LOG_LEVEL', 'INFO')

        # Load sub-configurations
        self.claude: ClaudeConfig = ClaudeConfig.from_env()
        self.shopify: ShopifyConfig = ShopifyConfig.from_env()
        self.database: DatabaseConfig = DatabaseConfig.from_env()
        self.brand: BrandConfig = BrandConfig.from_env()
        self.content: ContentConfig = ContentConfig.from_env()
        self.influencer: InfluencerConfig = InfluencerConfig.from_env()

        # Social media credentials
        self.instagram_username: str = os.getenv('INSTAGRAM_USERNAME', '')
        self.instagram_password: str = os.getenv('INSTAGRAM_PASSWORD', '')
        self.tiktok_session_id: str = os.getenv('TIKTOK_SESSION_ID', '')
        self.pinterest_token: str = os.getenv('PINTEREST_ACCESS_TOKEN', '')

        # Email marketing
        self.klaviyo_api_key: str = os.getenv('KLAVIYO_API_KEY', '')

        # Analytics
        self.google_analytics_id: str = os.getenv('GOOGLE_ANALYTICS_PROPERTY_ID', '')
        self.google_credentials_path: str = os.getenv(
            'GOOGLE_CREDENTIALS_PATH',
            './config/google-credentials.json'
        )

        # Monitoring and alerting
        self.sentry_dsn: str = os.getenv('SENTRY_DSN', '')
        self.slack_webhook: str = os.getenv('SLACK_WEBHOOK_URL', '')
        self.alert_email: str = os.getenv('ALERT_EMAIL', 'tony@linoroso.com')

        # SEO tools
        self.serpapi_key: str = os.getenv('SERPAPI_KEY', '')
        
    def validate(self) -> List[str]:
        """Validate required configuration and return list of missing items.

        Returns:
            List of missing or invalid configuration items
        """
        missing = []

        # Critical configurations
        if not self.claude.api_key:
            missing.append('ANTHROPIC_API_KEY')

        if not self.shopify.api_key or not self.shopify.access_token:
            missing.append('Shopify credentials (API_KEY, ACCESS_TOKEN)')

        if not self.database.password:
            missing.append('MYSQL_PASSWORD')

        return missing

    @property
    def is_production(self) -> bool:
        """Check if running in production environment.

        Returns:
            True if environment is 'production', False otherwise
        """
        return self.environment == 'production'

    @property
    def is_development(self) -> bool:
        """Check if running in development environment.

        Returns:
            True if environment is 'development', False otherwise
        """
        return self.environment == 'development'

    def to_dict(self) -> Dict[str, any]:
        """Convert configuration to dictionary (excluding sensitive data).

        Returns:
            Dictionary representation of non-sensitive config
        """
        return {
            'environment': self.environment,
            'debug': self.debug,
            'log_level': self.log_level,
            'brand_name': self.brand.name,
            'shopify_store': self.shopify.store_url,
            'content_frequency': self.content.frequency,
        }


# Global configuration instance
config = Config()

# Validate on import
missing_config = config.validate()
if missing_config and not config.is_development:
    warnings.warn(
        f"Missing required configuration: {', '.join(missing_config)}. "
        "Application may not function correctly.",
        UserWarning
    )
