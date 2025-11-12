"""
Unit tests for Settings/Configuration
"""

import pytest
import os
from unittest.mock import patch
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestConfiguration:
    """Test configuration loading and validation"""

    @patch.dict(os.environ, {
        'ANTHROPIC_API_KEY': 'test-key',
        'SHOPIFY_API_KEY': 'shop-key',
        'SHOPIFY_ACCESS_TOKEN': 'shop-token',
        'MYSQL_PASSWORD': 'db-pass',
        'ENVIRONMENT': 'testing'
    })
    def test_config_loads_from_env(self):
        """Test that config loads from environment variables"""
        # Reload settings module to pick up new env vars
        import settings
        from importlib import reload
        reload(settings)

        assert settings.config.claude.api_key == 'test-key'
        assert settings.config.shopify.api_key == 'shop-key'
        assert settings.config.environment == 'testing'

    @patch.dict(os.environ, {
        'ANTHROPIC_API_KEY': 'key',
        'SHOPIFY_API_KEY': 'key',
        'SHOPIFY_ACCESS_TOKEN': 'token',
        'MYSQL_PASSWORD': 'pass'
    })
    def test_validation_passes_with_required_config(self):
        """Test validation passes when required config is present"""
        import settings
        from importlib import reload
        reload(settings)

        missing = settings.config.validate()
        assert len(missing) == 0

    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': ''}, clear=True)
    def test_validation_fails_without_required_config(self):
        """Test validation fails when required config is missing"""
        import settings
        from importlib import reload
        reload(settings)

        missing = settings.config.validate()
        assert len(missing) > 0
        assert 'ANTHROPIC_API_KEY' in missing[0]

    @patch.dict(os.environ, {'ENVIRONMENT': 'production'})
    def test_is_production(self):
        """Test is_production property"""
        import settings
        from importlib import reload
        reload(settings)

        assert settings.config.is_production is True
        assert settings.config.is_development is False

    @patch.dict(os.environ, {'ENVIRONMENT': 'development'})
    def test_is_development(self):
        """Test is_development property"""
        import settings
        from importlib import reload
        reload(settings)

        assert settings.config.is_development is True
        assert settings.config.is_production is False

    def test_database_connection_string(self):
        """Test database connection string generation"""
        from settings import DatabaseConfig

        db = DatabaseConfig(
            host='localhost',
            port=3306,
            database='test_db',
            user='test_user',
            password='test_pass'
        )

        conn_str = db.connection_string
        assert 'mysql+pymysql://' in conn_str
        assert 'test_user:test_pass' in conn_str
        assert 'localhost:3306' in conn_str
        assert 'test_db' in conn_str


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
