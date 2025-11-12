"""
Unit tests for Content Generation Engine
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import json
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from content_engine import ContentGenerator, GeneratedContent, ContentRequest
from utils.error_handling import ValidationError


class TestContentGenerator:
    """Test ContentGenerator class"""

    @pytest.fixture
    def mock_config(self):
        """Mock configuration"""
        with patch('content_engine.config') as mock_cfg:
            mock_cfg.claude.api_key = 'test-api-key'
            mock_cfg.claude.model = 'claude-3-5-sonnet-20241022'
            mock_cfg.claude.max_tokens = 4000
            mock_cfg.brand.voice = 'professional, warm'
            mock_cfg.brand.name = 'Linoroso'
            mock_cfg.brand.tagline = 'Simplicity, Elegance, Functionality'
            mock_cfg.brand.target_audience = 'home cooks'
            mock_cfg.brand.main_categories = ['kitchen knives', 'shears']
            mock_cfg.content.min_word_count = 800
            mock_cfg.content.output_path = Path('/tmp/test_content')
            yield mock_cfg

    @pytest.fixture
    def generator(self, mock_config):
        """Create ContentGenerator instance"""
        return ContentGenerator()

    def test_initialization(self, generator):
        """Test generator initialization"""
        assert generator.client is not None
        assert generator.model is not None
        assert generator.brand_voice is not None
        assert generator.rate_limiter is not None

    def test_initialization_without_api_key(self, mock_config):
        """Test that initialization fails without API key"""
        mock_config.claude.api_key = ''
        with pytest.raises(ValidationError):
            ContentGenerator()

    def test_build_system_prompt(self, generator):
        """Test system prompt generation"""
        prompt = generator._build_system_prompt()
        assert 'Linoroso' in prompt
        assert 'kitchen tools' in prompt.lower()
        assert 'professional' in prompt.lower()

    def test_build_blog_prompt(self, generator):
        """Test blog post prompt generation"""
        request = ContentRequest(
            content_type='blog_post',
            topic='Knife Skills',
            keywords=['knife', 'cooking'],
            word_count=1000
        )
        prompt = generator._build_blog_prompt(request)
        assert 'Knife Skills' in prompt
        assert '1000 words' in prompt
        assert 'knife' in prompt.lower()

    @patch('content_engine.anthropic.Anthropic')
    def test_generate_blog_post_success(self, mock_anthropic, generator):
        """Test successful blog post generation"""
        # Mock Claude API response
        mock_response = Mock()
        mock_response.content = [Mock()]
        mock_response.content[0].text = json.dumps({
            'title': 'Test Blog Post',
            'content': 'This is a test blog post content.',
            'meta_description': 'Test meta description',
            'secondary_keywords': ['test', 'blog']
        })

        generator.client.messages.create = Mock(return_value=mock_response)

        # Generate blog post
        result = generator.generate_blog_post(
            topic='Test Topic',
            keywords=['test', 'keyword'],
            word_count=500
        )

        # Verify result
        assert isinstance(result, GeneratedContent)
        assert result.title == 'Test Blog Post'
        assert result.content_type == 'blog_post'
        assert result.word_count > 0

    def test_generate_blog_post_empty_topic(self, generator):
        """Test that empty topic raises ValidationError"""
        with pytest.raises(ValidationError):
            generator.generate_blog_post(
                topic='',
                keywords=['test'],
                word_count=500
            )

    def test_generate_blog_post_no_keywords(self, generator):
        """Test that empty keywords list raises ValidationError"""
        with pytest.raises(ValidationError):
            generator.generate_blog_post(
                topic='Test Topic',
                keywords=[],
                word_count=500
            )

    def test_generate_blog_post_invalid_word_count(self, generator):
        """Test that negative word count raises ValidationError"""
        with pytest.raises(ValidationError):
            generator.generate_blog_post(
                topic='Test Topic',
                keywords=['test'],
                word_count=-100
            )

    @patch('content_engine.anthropic.Anthropic')
    def test_generate_blog_post_handles_markdown_response(self, mock_anthropic, generator):
        """Test handling of markdown-wrapped JSON response"""
        # Mock response with markdown code block
        mock_response = Mock()
        mock_response.content = [Mock()]
        mock_response.content[0].text = '''```json
{
    "title": "Test Title",
    "content": "Test content",
    "meta_description": "Test description"
}
```'''

        generator.client.messages.create = Mock(return_value=mock_response)

        result = generator.generate_blog_post(
            topic='Test',
            keywords=['test'],
            word_count=500
        )

        assert result.title == 'Test Title'

    def test_save_content(self, generator, tmp_path):
        """Test saving generated content"""
        content = GeneratedContent(
            title='Test Post',
            content='Test content here',
            meta_description='Test description',
            keywords=['test'],
            word_count=3,
            created_at=None,
            content_type='blog_post'
        )

        # Override output path
        with patch('content_engine.config') as mock_cfg:
            mock_cfg.content.output_path = tmp_path
            filepath = generator.save_content(content)

        assert filepath.exists()
        assert filepath.suffix == '.json'

        # Verify saved content
        with open(filepath, 'r') as f:
            saved_data = json.load(f)
        assert saved_data['title'] == 'Test Post'


class TestGeneratedContent:
    """Test GeneratedContent dataclass"""

    def test_to_dict(self):
        """Test conversion to dictionary"""
        from datetime import datetime
        now = datetime.now()

        content = GeneratedContent(
            title='Test',
            content='Content',
            meta_description='Description',
            keywords=['key1', 'key2'],
            word_count=10,
            created_at=now,
            content_type='blog_post'
        )

        data = content.to_dict()

        assert data['title'] == 'Test'
        assert data['keywords'] == ['key1', 'key2']
        assert data['word_count'] == 10
        assert data['content_type'] == 'blog_post'


class TestContentRequest:
    """Test ContentRequest dataclass"""

    def test_creation_with_defaults(self):
        """Test creating request with default values"""
        request = ContentRequest(
            content_type='blog_post',
            topic='Test',
            keywords=['test'],
            word_count=1000
        )

        assert request.tone == "professional, warm, helpful"
        assert request.target_audience == "home cooks and culinary enthusiasts"
        assert request.additional_context is None

    def test_creation_with_custom_values(self):
        """Test creating request with custom values"""
        request = ContentRequest(
            content_type='email',
            topic='Newsletter',
            keywords=['news'],
            word_count=500,
            tone='casual',
            target_audience='subscribers',
            additional_context={'segment': 'VIP'}
        )

        assert request.tone == 'casual'
        assert request.target_audience == 'subscribers'
        assert request.additional_context == {'segment': 'VIP'}


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
