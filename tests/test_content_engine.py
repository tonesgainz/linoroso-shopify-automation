"""
Unit tests for content_engine module.

Tests content generation, request validation, and error handling.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from content_engine import (
    ContentRequest,
    GeneratedContent,
    ContentGenerator,
    DEFAULT_PRODUCT_WORD_COUNT,
    DEFAULT_SOCIAL_WORD_COUNT,
    PLATFORM_CHAR_LIMITS,
)


class TestContentRequest:
    """Test ContentRequest dataclass."""

    def test_valid_blog_request(self):
        """Test creating valid blog post request."""
        request = ContentRequest(
            content_type='blog_post',
            topic='Test Topic',
            keywords=['keyword1', 'keyword2'],
            word_count=1000
        )
        assert request.content_type == 'blog_post'
        assert request.topic == 'Test Topic'
        assert len(request.keywords) == 2
        assert request.word_count == 1000

    def test_default_values(self):
        """Test default values for optional fields."""
        request = ContentRequest(
            content_type='blog_post',
            topic='Test',
            keywords=['test'],
            word_count=1000
        )
        assert request.tone == "professional, warm, helpful"
        assert "home cooks" in request.target_audience
        assert request.additional_context is None

    def test_additional_context(self):
        """Test request with additional context."""
        context = {'platform': 'instagram', 'custom_field': 'value'}
        request = ContentRequest(
            content_type='social_media',
            topic='Test',
            keywords=['test'],
            word_count=150,
            additional_context=context
        )
        assert request.additional_context == context
        assert request.additional_context['platform'] == 'instagram'


class TestGeneratedContent:
    """Test GeneratedContent dataclass."""

    def test_valid_content(self):
        """Test creating valid generated content."""
        now = datetime.now()
        content = GeneratedContent(
            title='Test Title',
            content='Test content body',
            meta_description='Test meta',
            keywords=['key1', 'key2'],
            word_count=500,
            created_at=now,
            content_type='blog_post'
        )
        assert content.title == 'Test Title'
        assert content.word_count == 500
        assert content.content_type == 'blog_post'

    def test_to_dict(self):
        """Test conversion to dictionary."""
        now = datetime.now()
        content = GeneratedContent(
            title='Test',
            content='Body',
            meta_description='Meta',
            keywords=['key1'],
            word_count=100,
            created_at=now,
            content_type='blog_post'
        )

        result = content.to_dict()

        assert isinstance(result, dict)
        assert result['title'] == 'Test'
        assert result['word_count'] == 100
        assert result['content_type'] == 'blog_post'
        assert isinstance(result['created_at'], str)  # Should be ISO format


class TestContentGenerator:
    """Test ContentGenerator class."""

    @patch('content_engine.config')
    def test_init_with_api_key(self, mock_config):
        """Test initialization with valid API key."""
        mock_config.claude.api_key = 'test_key'
        mock_config.claude.model = 'test-model'
        mock_config.brand.voice = 'professional'
        mock_config.brand.name = 'TestBrand'
        mock_config.brand.tagline = 'Test Tagline'

        generator = ContentGenerator()

        assert generator.model == 'test-model'
        assert generator.brand_name == 'TestBrand'

    @patch('content_engine.config')
    def test_init_without_api_key_raises_error(self, mock_config):
        """Test initialization without API key raises ValueError."""
        mock_config.claude.api_key = ''

        with pytest.raises(ValueError, match="ANTHROPIC_API_KEY is required"):
            ContentGenerator()

    @patch('content_engine.config')
    def test_build_system_prompt(self, mock_config):
        """Test system prompt generation."""
        mock_config.claude.api_key = 'test_key'
        mock_config.claude.model = 'test-model'
        mock_config.brand.voice = 'professional'
        mock_config.brand.name = 'TestBrand'
        mock_config.brand.tagline = 'Test Tagline'
        mock_config.brand.target_audience = 'test audience'
        mock_config.brand.main_categories = ['category1', 'category2']

        generator = ContentGenerator()
        prompt = generator._build_system_prompt()

        assert 'TestBrand' in prompt
        assert 'Test Tagline' in prompt
        assert 'professional' in prompt

    @patch('content_engine.config')
    def test_build_social_media_prompt_instagram(self, mock_config):
        """Test social media prompt for Instagram."""
        mock_config.claude.api_key = 'test_key'
        mock_config.claude.model = 'test-model'
        mock_config.brand.voice = 'professional'
        mock_config.brand.name = 'TestBrand'
        mock_config.brand.tagline = 'Test Tagline'

        generator = ContentGenerator()
        request = ContentRequest(
            content_type='social_media',
            topic='Test Topic',
            keywords=['key1', 'key2'],
            word_count=150,
            additional_context={'platform': 'instagram'}
        )

        prompt = generator._build_social_media_prompt(request)

        assert 'Instagram' in prompt
        assert str(PLATFORM_CHAR_LIMITS['instagram']['optimal']) in prompt
        assert 'Test Topic' in prompt

    @patch('content_engine.config')
    @patch('content_engine.anthropic.Anthropic')
    def test_generate_blog_post_success(self, mock_anthropic, mock_config):
        """Test successful blog post generation."""
        # Setup mocks
        mock_config.claude.api_key = 'test_key'
        mock_config.claude.model = 'test-model'
        mock_config.claude.max_tokens = 4000
        mock_config.brand.voice = 'professional'
        mock_config.brand.name = 'TestBrand'
        mock_config.brand.tagline = 'Test Tagline'
        mock_config.brand.target_audience = 'test audience'
        mock_config.brand.main_categories = ['category1']
        mock_config.content.min_word_count = 800

        # Mock API response
        mock_response = Mock()
        mock_response.content = [Mock(text='{"title": "Test Title", "content": "Test content body", "meta_description": "Test meta", "secondary_keywords": ["key1", "key2"]}')]
        mock_client = Mock()
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        generator = ContentGenerator()
        result = generator.generate_blog_post(
            topic='Test Topic',
            keywords=['keyword1'],
            word_count=1000
        )

        assert isinstance(result, GeneratedContent)
        assert result.title == 'Test Title'
        assert result.content == 'Test content body'
        assert result.content_type == 'blog_post'

    @patch('content_engine.config')
    @patch('content_engine.anthropic.Anthropic')
    def test_generate_blog_post_error_handling(self, mock_anthropic, mock_config):
        """Test error handling in blog post generation."""
        mock_config.claude.api_key = 'test_key'
        mock_config.claude.model = 'test-model'
        mock_config.brand.voice = 'professional'
        mock_config.brand.name = 'TestBrand'
        mock_config.brand.tagline = 'Test Tagline'
        mock_config.brand.target_audience = 'test audience'
        mock_config.brand.main_categories = ['category1']
        mock_config.content.min_word_count = 800

        # Mock API error
        mock_client = Mock()
        mock_client.messages.create.side_effect = Exception("API Error")
        mock_anthropic.return_value = mock_client

        generator = ContentGenerator()

        with pytest.raises(Exception, match="API Error"):
            generator.generate_blog_post(
                topic='Test Topic',
                keywords=['keyword1']
            )

    @patch('content_engine.config')
    def test_save_content(self, mock_config):
        """Test saving content to file."""
        mock_config.claude.api_key = 'test_key'
        mock_config.claude.model = 'test-model'
        mock_config.brand.voice = 'professional'
        mock_config.brand.name = 'TestBrand'
        mock_config.brand.tagline = 'Test Tagline'
        mock_config.content.output_path = Path('/tmp/test_content')

        generator = ContentGenerator()

        content = GeneratedContent(
            title='Test Title',
            content='Test content',
            meta_description='Meta',
            keywords=['key1'],
            word_count=100,
            created_at=datetime.now(),
            content_type='blog_post'
        )

        with patch('content_engine.Path.mkdir'):
            with patch('builtins.open', create=True) as mock_open:
                with patch('content_engine.slugify', return_value='test-title'):
                    result_path = generator.save_content(content)

                    assert isinstance(result_path, Path)
                    mock_open.assert_called_once()


class TestConstants:
    """Test module constants."""

    def test_default_word_counts(self):
        """Test default word count constants."""
        assert DEFAULT_PRODUCT_WORD_COUNT == 300
        assert DEFAULT_SOCIAL_WORD_COUNT == 150

    def test_platform_char_limits(self):
        """Test platform character limits."""
        assert 'instagram' in PLATFORM_CHAR_LIMITS
        assert 'tiktok' in PLATFORM_CHAR_LIMITS
        assert 'pinterest' in PLATFORM_CHAR_LIMITS
        assert 'facebook' in PLATFORM_CHAR_LIMITS

        assert PLATFORM_CHAR_LIMITS['instagram']['optimal'] == 125
        assert PLATFORM_CHAR_LIMITS['tiktok']['optimal'] == 100
