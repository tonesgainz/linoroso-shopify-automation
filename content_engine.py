"""
Content Generation Engine - Powered by Claude AI
Generates SEO-optimized blog posts, product descriptions, and marketing copy
"""

import anthropic
from typing import Dict, List, Optional, Literal
from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path
import sys
import os

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from settings import config
from loguru import logger
from utils.error_handling import (
    retry_with_backoff,
    handle_api_error,
    validate_input,
    RateLimiter
)

@dataclass
class ContentRequest:
    """Content generation request"""
    content_type: Literal['blog_post', 'product_description', 'social_media', 'email']
    topic: str
    keywords: List[str]
    word_count: int
    tone: str = "professional, warm, helpful"
    target_audience: str = "home cooks and culinary enthusiasts"
    additional_context: Optional[Dict] = None

@dataclass
class GeneratedContent:
    """Generated content response"""
    title: str
    content: str
    meta_description: str
    keywords: List[str]
    word_count: int
    created_at: datetime
    content_type: str
    
    def to_dict(self):
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
    """AI-powered content generation using Claude"""

    def __init__(self):
        validate_input(
            bool(config.claude.api_key),
            "Claude API key is required. Set ANTHROPIC_API_KEY in .env"
        )
        self.client = anthropic.Anthropic(api_key=config.claude.api_key)
        self.model = config.claude.model
        self.brand_voice = config.brand.voice
        self.brand_name = config.brand.name
        self.brand_tagline = config.brand.tagline
        self.rate_limiter = RateLimiter(requests_per_minute=50)
        
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
        """Build prompt for social media content"""
        platform = request.additional_context.get('platform', 'instagram') if request.additional_context else 'instagram'
        
        char_limits = {
            'instagram': {'caption': 2200, 'optimal': 125},
            'tiktok': {'caption': 150, 'optimal': 100},
            'pinterest': {'description': 500, 'optimal': 200},
            'facebook': {'post': 63206, 'optimal': 40}
        }
        
        limit = char_limits.get(platform, {'optimal': 150})['optimal']
        
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

    @retry_with_backoff(
        max_retries=3,
        exceptions=(anthropic.APIError, anthropic.RateLimitError)
    )
    @handle_api_error
    def generate_blog_post(self, topic: str, keywords: List[str],
                          word_count: Optional[int] = None) -> GeneratedContent:
        """Generate SEO-optimized blog post"""

        # Validate inputs
        validate_input(bool(topic), "Topic cannot be empty")
        validate_input(len(keywords) > 0, "At least one keyword is required")
        validate_input(
            word_count is None or word_count > 0,
            "Word count must be positive"
        )

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

        # Apply rate limiting
        self.rate_limiter.wait_if_needed()

        message = self.client.messages.create(
            model=self.model,
            max_tokens=config.claude.max_tokens,
            system=self._build_system_prompt(),
            messages=[{
                "role": "user",
                "content": self._build_blog_prompt(request)
            }]
        )

        # Parse JSON response (handle markdown code blocks)
        response_text = message.content[0].text.strip()

        # Remove markdown code blocks if present
        if response_text.startswith('```'):
            # Find the actual JSON content
            lines = response_text.split('\n')
            response_text = '\n'.join(lines[1:-1]) if len(lines) > 2 else response_text
            response_text = response_text.replace('```json', '').replace('```', '').strip()

        try:
            content_json = json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Claude response as JSON: {e}")
            logger.debug(f"Response text: {response_text[:500]}...")
            raise

        # Validate response structure
        required_fields = ['title', 'content', 'meta_description']
        for field in required_fields:
            validate_input(
                field in content_json,
                f"Claude response missing required field: {field}"
            )

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

    def generate_product_description(self, product_name: str, 
                                     keywords: List[str],
                                     product_details: Optional[Dict] = None) -> GeneratedContent:
        """Generate compelling product description"""
        
        request = ContentRequest(
            content_type='product_description',
            topic=product_name,
            keywords=keywords,
            word_count=300,  # Standard product description length
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

    def save_content(self, content: GeneratedContent, output_dir: Optional[Path] = None):
        """Save generated content to file"""
        
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
