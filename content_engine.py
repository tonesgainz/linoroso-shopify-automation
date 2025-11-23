"""
Content Generation Engine - Powered by Claude AI.

Generates SEO-optimized blog posts, product descriptions, and marketing copy
using Anthropic's Claude AI. Supports multiple content types and platforms.
"""

import anthropic
from typing import Dict, List, Optional, Literal, Union
from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path
from loguru import logger

from settings import config

# Constants
DEFAULT_PRODUCT_WORD_COUNT = 300
DEFAULT_SOCIAL_WORD_COUNT = 150
MAX_TITLE_LENGTH = 60
MAX_META_DESCRIPTION_LENGTH = 155
PLATFORM_CHAR_LIMITS = {
    'instagram': {'caption': 2200, 'optimal': 125},
    'tiktok': {'caption': 150, 'optimal': 100},
    'pinterest': {'description': 500, 'optimal': 200},
    'facebook': {'post': 63206, 'optimal': 40}
}

@dataclass
class ContentRequest:
    """Content generation request specification.

    Attributes:
        content_type: Type of content to generate
        topic: Main topic or title
        keywords: Target keywords for SEO
        word_count: Target word count
        tone: Writing tone and style
        target_audience: Target audience description
        additional_context: Additional context or requirements
    """
    content_type: Literal['blog_post', 'product_description', 'social_media', 'email']
    topic: str
    keywords: List[str]
    word_count: int
    tone: str = "professional, warm, helpful"
    target_audience: str = "home cooks and culinary enthusiasts"
    additional_context: Optional[Dict[str, any]] = None


@dataclass
class GeneratedContent:
    """Generated content response.

    Attributes:
        title: Content title
        content: Main content body
        meta_description: SEO meta description
        keywords: Keywords used in content
        word_count: Actual word count
        created_at: Creation timestamp
        content_type: Type of content generated
    """
    title: str
    content: str
    meta_description: str
    keywords: List[str]
    word_count: int
    created_at: datetime
    content_type: str

    def to_dict(self) -> Dict[str, any]:
        """Convert to dictionary for JSON serialization.

        Returns:
            Dictionary representation of the content
        """
        return {
            'title': self.title,
            'content': self.content,
            'meta_description': self.meta_description,
            'keywords': self.keywords,
            'word_count': self.word_count,
            'created_at': self.created_at.isoformat(),
            'content_type': self.content_type
        }

class ContentGenerator:
    """AI-powered content generation using Claude.

    This class provides methods to generate various types of marketing content
    including blog posts, product descriptions, and social media posts using
    Anthropic's Claude AI with brand-consistent voice and messaging.

    Attributes:
        client: Anthropic API client
        model: Claude model version to use
        brand_voice: Brand voice characteristics
        brand_name: Brand name
        brand_tagline: Brand tagline
    """

    def __init__(self) -> None:
        """Initialize content generator with Claude AI client and brand settings."""
        if not config.claude.api_key:
            raise ValueError("ANTHROPIC_API_KEY is required for content generation")

        self.client = anthropic.Anthropic(api_key=config.claude.api_key)
        self.model: str = config.claude.model
        self.brand_voice: str = config.brand.voice
        self.brand_name: str = config.brand.name
        self.brand_tagline: str = config.brand.tagline
        
    def _build_system_prompt(self) -> str:
        """Build system prompt with brand guidelines"""
        return f"""You are an expert content writer for {self.brand_name}, a premium kitchen tools brand.

Brand Guidelines:
- Brand Name: {self.brand_name}
- Tagline: {self.brand_tagline}
- Voice: {self.brand_voice}
- Target Audience: {config.brand.target_audience}
- Product Categories: {', '.join(config.brand.main_categories)}

Brand Story:
Linoroso believes the heart of every home is the kitchen, where meals are prepared, memories are shared, and life happens. We create kitchen tools that embody simplicity, elegance, and functionality—at a value that empowers everyone.

Our products feature:
- Timeless Design: Complements any kitchen style
- Thoughtful Functionality: Precision and performance
- Unbeatable Value: Premium quality without premium prices

Content Requirements:
- Write in a warm, professional, and helpful tone
- Focus on practical value for home cooks
- Include emotional connection to cooking and family
- Emphasize quality, durability, and thoughtful design
- Be conversational but authoritative
- Use specific, actionable advice
- Include relevant statistics or tips when appropriate"""

    def _build_blog_prompt(self, request: ContentRequest) -> str:
        """Build prompt for blog post generation"""
        keywords_str = ', '.join(request.keywords)
        
        return f"""Write a comprehensive blog post about: {request.topic}

Requirements:
- Target word count: {request.word_count} words
- Primary keywords to naturally incorporate: {keywords_str}
- Target audience: {request.target_audience}
- Tone: {request.tone}

Structure:
1. Compelling title (60 characters max, include primary keyword)
2. Engaging introduction (hook the reader, explain why this matters)
3. Well-organized body with clear sections and headers
4. Practical tips, techniques, or step-by-step instructions
5. Strong conclusion with call-to-action
6. Meta description (155 characters max)

Content Guidelines:
- Start with a relatable scenario or question
- Use short paragraphs (2-3 sentences max)
- Include specific, actionable advice
- Reference Linoroso products naturally where relevant (don't force it)
- Add social proof or statistics where appropriate
- Use transitional phrases for better flow
- End with an engaging question or clear next step

SEO Best Practices:
- Include primary keyword in title, first paragraph, and throughout naturally
- Use semantic variations of keywords
- Create scannable content with headers (H2, H3)
- Include internal linking opportunities (mark with [INTERNAL LINK: topic])
- Optimize for featured snippets where possible

Return the content in JSON format:
{{
    "title": "SEO-optimized title",
    "content": "Full blog post content with markdown formatting",
    "meta_description": "Compelling meta description",
    "suggested_internal_links": ["topic1", "topic2"],
    "primary_keyword": "main keyword",
    "secondary_keywords": ["keyword1", "keyword2"]
}}"""

    def _build_product_description_prompt(self, request: ContentRequest) -> str:
        """Build prompt for product description"""
        product_info = request.additional_context or {}
        
        return f"""Write a compelling product description for: {request.topic}

Product Context:
{json.dumps(product_info, indent=2)}

Requirements:
- Word count: {request.word_count} words
- Keywords: {', '.join(request.keywords)}
- Focus on benefits, not just features
- Address customer pain points
- Create emotional connection

Structure:
1. Attention-grabbing headline (include primary keyword)
2. Opening paragraph: Transform the problem into desire
3. Key features with benefits (use bullet points)
4. Usage scenarios and lifestyle benefits
5. Quality and craftsmanship details
6. Call-to-action
7. Short meta description (155 characters)

Guidelines:
- Use sensory language (feel, see, experience)
- Paint a picture of life with the product
- Include social proof elements if available
- Address common objections subtly
- Create urgency without being pushy
- Maintain premium positioning

Return JSON format:
{{
    "headline": "Product headline",
    "short_description": "2-3 sentence summary",
    "long_description": "Full product description",
    "features_and_benefits": ["feature 1: benefit", "feature 2: benefit"],
    "meta_description": "SEO meta description",
    "bullet_points": ["key point 1", "key point 2"],
    "suggested_tags": ["tag1", "tag2"]
}}"""

    def _build_social_media_prompt(self, request: ContentRequest) -> str:
        """Build prompt for social media content.

        Args:
            request: Content request with platform information

        Returns:
            Formatted prompt for Claude AI
        """
        platform = request.additional_context.get('platform', 'instagram') if request.additional_context else 'instagram'

        limit = PLATFORM_CHAR_LIMITS.get(platform, {'optimal': 150})['optimal']
        
        return f"""Create engaging social media content for {platform.title()} about: {request.topic}

Platform: {platform}
Optimal length: ~{limit} characters
Keywords: {', '.join(request.keywords)}
Brand voice: {request.tone}

Content Requirements:
- Hook reader in first line
- Tell a story or share a tip
- Include emotional connection
- Natural call-to-action
- Brand-appropriate hashtags

For {platform}:
{"- First line must grab attention (appears before 'more')" if platform == 'instagram' else ""}
{"- Focus on quick, actionable tips" if platform == 'tiktok' else ""}
{"- SEO-optimized for Pinterest search" if platform == 'pinterest' else ""}
{"- Encourage conversation and engagement" if platform == 'facebook' else ""}

Return JSON:
{{
    "caption": "Main post copy",
    "hashtags": ["hashtag1", "hashtag2"],
    "call_to_action": "Specific CTA",
    "image_suggestion": "Description of ideal accompanying image",
    "posting_tips": "Best practices for this specific post"
}}"""

    def generate_blog_post(self, topic: str, keywords: List[str], 
                          word_count: Optional[int] = None) -> GeneratedContent:
        """Generate SEO-optimized blog post"""
        
        if word_count is None:
            word_count = config.content.min_word_count
            
        request = ContentRequest(
            content_type='blog_post',
            topic=topic,
            keywords=keywords,
            word_count=word_count,
            tone=self.brand_voice,
            target_audience=config.brand.target_audience
        )
        
        logger.info(f"Generating blog post about '{topic}'")
        
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=config.claude.max_tokens,
                system=self._build_system_prompt(),
                messages=[{
                    "role": "user",
                    "content": self._build_blog_prompt(request)
                }]
            )
            
            # Parse JSON response
            content_json = json.loads(message.content[0].text)
            
            result = GeneratedContent(
                title=content_json['title'],
                content=content_json['content'],
                meta_description=content_json['meta_description'],
                keywords=content_json.get('secondary_keywords', keywords),
                word_count=len(content_json['content'].split()),
                created_at=datetime.now(),
                content_type='blog_post'
            )
            
            logger.success(f"Generated blog post: '{result.title}' ({result.word_count} words)")
            return result
            
        except Exception as e:
            logger.error(f"Error generating blog post: {e}")
            raise

    def generate_product_description(
        self,
        product_name: str,
        keywords: List[str],
        product_details: Optional[Dict[str, any]] = None
    ) -> GeneratedContent:
        """Generate compelling product description.

        Args:
            product_name: Name of the product
            keywords: SEO keywords to target
            product_details: Additional product information

        Returns:
            GeneratedContent object with product description

        Raises:
            Exception: If content generation fails
        """
        request = ContentRequest(
            content_type='product_description',
            topic=product_name,
            keywords=keywords,
            word_count=DEFAULT_PRODUCT_WORD_COUNT,
            additional_context=product_details or {}
        )
        
        logger.info(f"Generating product description for '{product_name}'")
        
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                system=self._build_system_prompt(),
                messages=[{
                    "role": "user",
                    "content": self._build_product_description_prompt(request)
                }]
            )
            
            content_json = json.loads(message.content[0].text)
            
            # Combine descriptions
            full_content = f"""# {content_json['headline']}

{content_json['short_description']}

{content_json['long_description']}

## Key Features & Benefits
{chr(10).join(['- ' + item for item in content_json['features_and_benefits']])}
"""
            
            result = GeneratedContent(
                title=content_json['headline'],
                content=full_content,
                meta_description=content_json['meta_description'],
                keywords=keywords,
                word_count=len(full_content.split()),
                created_at=datetime.now(),
                content_type='product_description'
            )
            
            logger.success(f"Generated product description for '{product_name}'")
            return result
            
        except Exception as e:
            logger.error(f"Error generating product description: {e}")
            raise

    def generate_social_post(self, topic: str, keywords: List[str],
                            platform: str = 'instagram') -> Dict:
        """Generate social media post"""
        
        request = ContentRequest(
            content_type='social_media',
            topic=topic,
            keywords=keywords,
            word_count=150,
            additional_context={'platform': platform}
        )
        
        logger.info(f"Generating {platform} post about '{topic}'")
        
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                system=self._build_system_prompt(),
                messages=[{
                    "role": "user",
                    "content": self._build_social_media_prompt(request)
                }]
            )
            
            post_data = json.loads(message.content[0].text)
            post_data['platform'] = platform
            post_data['created_at'] = datetime.now().isoformat()
            
            logger.success(f"Generated {platform} post about '{topic}'")
            return post_data
            
        except Exception as e:
            logger.error(f"Error generating social post: {e}")
            raise

    def generate_content_batch(self, requests: List[ContentRequest]) -> List[GeneratedContent]:
        """Generate multiple pieces of content"""
        results = []
        
        for req in requests:
            try:
                if req.content_type == 'blog_post':
                    content = self.generate_blog_post(req.topic, req.keywords, req.word_count)
                elif req.content_type == 'product_description':
                    content = self.generate_product_description(req.topic, req.keywords, req.additional_context)
                else:
                    continue
                    
                results.append(content)
                
            except Exception as e:
                logger.error(f"Error in batch generation for {req.topic}: {e}")
                continue
                
        logger.info(f"Generated {len(results)} pieces of content from {len(requests)} requests")
        return results

    def save_content(self, content: GeneratedContent, output_dir: Optional[Path] = None) -> Path:
        """Save generated content to file.

        Args:
            content: Generated content to save
            output_dir: Output directory (uses default if not specified)

        Returns:
            Path to the saved file
        """
        
        if output_dir is None:
            output_dir = config.content.output_path
            
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create filename from title
        from slugify import slugify
        filename = f"{datetime.now().strftime('%Y%m%d')}_{slugify(content.title)}.json"
        filepath = output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(content.to_dict(), f, indent=2, ensure_ascii=False)
            
        logger.info(f"Saved content to {filepath}")
        return filepath


# Example usage
if __name__ == "__main__":
    generator = ContentGenerator()
    
    # Generate blog post
    blog = generator.generate_blog_post(
        topic="5 Essential Knife Skills Every Home Cook Should Master",
        keywords=["knife skills", "kitchen techniques", "home cooking", "chef knife"],
        word_count=1200
    )
    print(f"\nGenerated Blog Post: {blog.title}")
    print(f"Word Count: {blog.word_count}")
    
    # Save to file
    generator.save_content(blog)
