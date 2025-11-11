"""
Configuration Management for Linoroso Shopify Automation
Loads and validates environment variables and settings
"""

import os
from pathlib import Path
from typing import Optional, List
from dotenv import load_dotenv
from dataclasses import dataclass
import yaml

# Load environment variables
load_dotenv()

@dataclass
class ClaudeConfig:
    """Claude AI API configuration"""
    api_key: str
    model: str = "claude-sonnet-4-20250514"
    max_tokens: int = 4000
    
    @classmethod
    def from_env(cls):
        return cls(
            api_key=os.getenv('ANTHROPIC_API_KEY', ''),
            model=os.getenv('CLAUDE_MODEL', 'claude-sonnet-4-20250514'),
            max_tokens=int(os.getenv('MAX_TOKENS', 4000))
        )

@dataclass
class ShopifyConfig:
    """Shopify API configuration"""
    store_url: str
    api_key: str
    api_secret: str
    access_token: str
    api_version: str = "2024-01"
    
    @classmethod
    def from_env(cls):
        return cls(
            store_url=os.getenv('SHOPIFY_STORE_URL', 'linoroso.myshopify.com'),
            api_key=os.getenv('SHOPIFY_API_KEY', ''),
            api_secret=os.getenv('SHOPIFY_API_SECRET', ''),
            access_token=os.getenv('SHOPIFY_ACCESS_TOKEN', ''),
            api_version=os.getenv('SHOPIFY_API_VERSION', '2024-01')
        )

@dataclass
class DatabaseConfig:
    """Database configuration"""
    host: str
    port: int
    database: str
    user: str
    password: str
    
    @property
    def connection_string(self):
        return f"mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
    
    @classmethod
    def from_env(cls):
        return cls(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            port=int(os.getenv('MYSQL_PORT', 3306)),
            database=os.getenv('MYSQL_DATABASE', 'linoroso_automation'),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', '')
        )

@dataclass
class BrandConfig:
    """Linoroso brand configuration"""
    name: str = "Linoroso"
    tagline: str = "Simplicity, Elegance, Functionality"
    voice: str = "professional, warm, helpful, family-oriented"
    target_audience: str = "quality-conscious home cooks, culinary enthusiasts"
    main_categories: List[str] = None
    
    def __post_init__(self):
        if self.main_categories is None:
            self.main_categories = [
                "kitchen knives",
                "kitchen shears", 
                "knife sets",
                "storage solutions"
            ]
    
    @classmethod
    def from_env(cls):
        categories_str = os.getenv('MAIN_CATEGORIES', 'kitchen knives,kitchen shears,knife sets,storage solutions')
        return cls(
            name=os.getenv('BRAND_NAME', 'Linoroso'),
            tagline=os.getenv('BRAND_TAGLINE', 'Simplicity, Elegance, Functionality'),
            voice=os.getenv('BRAND_VOICE', 'professional, warm, helpful, family-oriented'),
            target_audience=os.getenv('TARGET_AUDIENCE', 'quality-conscious home cooks, culinary enthusiasts'),
            main_categories=[cat.strip() for cat in categories_str.split(',')]
        )

@dataclass
class ContentConfig:
    """Content generation configuration"""
    output_path: Path
    frequency: str = "daily"
    min_word_count: int = 800
    max_word_count: int = 1500
    posts_per_day: int = 3
    
    @classmethod
    def from_env(cls):
        return cls(
            output_path=Path(os.getenv('CONTENT_OUTPUT_PATH', './data/generated_content')),
            frequency=os.getenv('BLOG_POST_FREQUENCY', 'daily'),
            min_word_count=int(os.getenv('MIN_WORD_COUNT', 800)),
            max_word_count=int(os.getenv('MAX_WORD_COUNT', 1500)),
            posts_per_day=int(os.getenv('SOCIAL_POSTS_PER_DAY', 3))
        )

@dataclass
class InfluencerConfig:
    """Influencer program configuration"""
    outreach_limit: int = 50
    min_follower_count: int = 10000
    min_engagement_rate: float = 3.0
    commission_basic: int = 10
    commission_intermediate: int = 15
    commission_advanced: int = 20
    
    @classmethod
    def from_env(cls):
        return cls(
            outreach_limit=int(os.getenv('INFLUENCER_OUTREACH_LIMIT', 50)),
            min_follower_count=int(os.getenv('MIN_FOLLOWER_COUNT', 10000)),
            min_engagement_rate=float(os.getenv('MIN_ENGAGEMENT_RATE', 3.0)),
            commission_basic=int(os.getenv('COMMISSION_BASIC', 10)),
            commission_intermediate=int(os.getenv('COMMISSION_INTERMEDIATE', 15)),
            commission_advanced=int(os.getenv('COMMISSION_ADVANCED', 20))
        )

class Config:
    """Main configuration class"""
    
    def __init__(self):
        self.environment = os.getenv('ENVIRONMENT', 'development')
        self.debug = os.getenv('DEBUG', 'False').lower() == 'true'
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        
        # Load sub-configurations
        self.claude = ClaudeConfig.from_env()
        self.shopify = ShopifyConfig.from_env()
        self.database = DatabaseConfig.from_env()
        self.brand = BrandConfig.from_env()
        self.content = ContentConfig.from_env()
        self.influencer = InfluencerConfig.from_env()
        
        # Social media tokens
        self.instagram_username = os.getenv('INSTAGRAM_USERNAME', '')
        self.instagram_password = os.getenv('INSTAGRAM_PASSWORD', '')
        self.tiktok_session_id = os.getenv('TIKTOK_SESSION_ID', '')
        self.pinterest_token = os.getenv('PINTEREST_ACCESS_TOKEN', '')
        
        # Email marketing
        self.klaviyo_api_key = os.getenv('KLAVIYO_API_KEY', '')
        
        # Analytics
        self.google_analytics_id = os.getenv('GOOGLE_ANALYTICS_PROPERTY_ID', '')
        self.google_credentials_path = os.getenv('GOOGLE_CREDENTIALS_PATH', './config/google-credentials.json')
        
        # Monitoring
        self.sentry_dsn = os.getenv('SENTRY_DSN', '')
        self.slack_webhook = os.getenv('SLACK_WEBHOOK_URL', '')
        self.alert_email = os.getenv('ALERT_EMAIL', 'tony@linoroso.com')
        
        # SEO
        self.serpapi_key = os.getenv('SERPAPI_KEY', '')
        
    def validate(self) -> List[str]:
        """Validate required configuration and return list of missing items"""
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
        return self.environment == 'production'
    
    @property
    def is_development(self) -> bool:
        return self.environment == 'development'

# Global configuration instance
config = Config()

# Validate on import
missing_config = config.validate()
if missing_config and not config.is_development:
    import warnings
    warnings.warn(f"Missing required configuration: {', '.join(missing_config)}")
