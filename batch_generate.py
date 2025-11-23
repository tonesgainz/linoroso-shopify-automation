"""
Batch Content Generator.

Quickly generate multiple pieces of content for initial content library building.
Supports pre-defined content plans and custom content generation from JSON files.
"""

from pathlib import Path
from typing import List, Dict
import json
from datetime import datetime
from loguru import logger

from content_engine import ContentGenerator, ContentRequest

# Constants
ESTIMATED_MINUTES_PER_PIECE = 2

class BatchContentGenerator:
    """Generate multiple pieces of content in batch.

    Attributes:
        generator: Content generation engine
    """

    def __init__(self) -> None:
        """Initialize batch content generator."""
        self.generator = ContentGenerator()

    def generate_content_library(self, content_plan: List[Dict[str, any]]) -> List[Dict[str, any]]:
        """Generate a complete content library from a plan"""
        
        logger.info(f"Starting batch generation of {len(content_plan)} pieces")
        
        results = []
        
        for idx, item in enumerate(content_plan, 1):
            try:
                logger.info(f"[{idx}/{len(content_plan)}] Generating: {item['topic']}")
                
                if item['type'] == 'blog_post':
                    content = self.generator.generate_blog_post(
                        topic=item['topic'],
                        keywords=item['keywords'],
                        word_count=item.get('word_count', 1000)
                    )
                    
                    # Save content
                    filepath = self.generator.save_content(content)
                    
                    results.append({
                        'type': 'blog_post',
                        'topic': item['topic'],
                        'title': content.title,
                        'word_count': content.word_count,
                        'filepath': str(filepath),
                        'status': 'success'
                    })
                    
                elif item['type'] == 'social_post':
                    post = self.generator.generate_social_post(
                        topic=item['topic'],
                        keywords=item['keywords'],
                        platform=item.get('platform', 'instagram')
                    )
                    
                    results.append({
                        'type': 'social_post',
                        'platform': item.get('platform', 'instagram'),
                        'topic': item['topic'],
                        'caption': post['caption'][:50] + '...',
                        'status': 'success'
                    })
                
                logger.success(f"✅ Generated: {item['topic']}")
                
            except Exception as e:
                logger.error(f"❌ Error generating {item['topic']}: {e}")
                results.append({
                    'type': item['type'],
                    'topic': item['topic'],
                    'status': 'error',
                    'error': str(e)
                })
                
        return results
    
    def generate_summary_report(self, results: List[Dict]) -> Path:
        """Generate summary report of batch generation"""
        
        output_path = Path('./reports') / f"batch_generation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        successful = [r for r in results if r['status'] == 'success']
        failed = [r for r in results if r['status'] == 'error']
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total': len(results),
                'successful': len(successful),
                'failed': len(failed),
                'success_rate': f"{(len(successful)/len(results)*100):.1f}%" if results else "0%"
            },
            'results': results,
            'blog_posts': [r for r in successful if r['type'] == 'blog_post'],
            'social_posts': [r for r in successful if r['type'] == 'social_post'],
            'errors': failed
        }
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.success(f"Report saved: {output_path}")
        return output_path


# Pre-defined content plans for quick start

STARTER_CONTENT_PLAN = [
    {
        'type': 'blog_post',
        'topic': '10 Essential Kitchen Knife Skills Every Home Cook Should Master',
        'keywords': ['knife skills', 'kitchen techniques', 'cooking basics', 'chef knife'],
        'word_count': 1500
    },
    {
        'type': 'blog_post',
        'topic': 'How to Choose the Perfect Chef Knife: A Complete Buying Guide',
        'keywords': ['chef knife', 'buying guide', 'kitchen knives', 'professional knives'],
        'word_count': 1200
    },
    {
        'type': 'blog_post',
        'topic': 'The Ultimate Guide to Knife Maintenance and Sharpening',
        'keywords': ['knife sharpening', 'knife care', 'knife maintenance', 'blade care'],
        'word_count': 1300
    },
    {
        'type': 'blog_post',
        'topic': '5 Time-Saving Meal Prep Techniques with the Right Tools',
        'keywords': ['meal prep', 'time-saving cooking', 'kitchen efficiency', 'batch cooking'],
        'word_count': 1100
    },
    {
        'type': 'blog_post',
        'topic': 'Kitchen Organization Hacks: Storing Your Knives and Tools Properly',
        'keywords': ['kitchen organization', 'knife storage', 'kitchen tips', 'tool organization'],
        'word_count': 1000
    }
]

MONTH_ONE_CONTENT_PLAN = [
    # Week 1: Knife Basics
    {
        'type': 'blog_post',
        'topic': 'Anatomy of a Chef Knife: Understanding Each Part',
        'keywords': ['chef knife', 'knife anatomy', 'kitchen knives', 'knife parts'],
        'word_count': 1000
    },
    {
        'type': 'blog_post',
        'topic': 'The Difference Between German and Japanese Knives',
        'keywords': ['german knives', 'japanese knives', 'knife comparison', 'knife styles'],
        'word_count': 1200
    },
    {
        'type': 'blog_post',
        'topic': 'How to Hold a Knife Correctly for Safety and Precision',
        'keywords': ['knife safety', 'knife grip', 'proper technique', 'cooking safety'],
        'word_count': 900
    },
    
    # Week 2: Cutting Techniques
    {
        'type': 'blog_post',
        'topic': 'Master the Basic Cuts: Dice, Julienne, Chiffonade and More',
        'keywords': ['cutting techniques', 'knife cuts', 'culinary techniques', 'vegetable prep'],
        'word_count': 1400
    },
    {
        'type': 'blog_post',
        'topic': 'How to Dice an Onion Like a Professional Chef',
        'keywords': ['onion cutting', 'knife skills', 'cooking techniques', 'vegetable prep'],
        'word_count': 800
    },
    {
        'type': 'blog_post',
        'topic': 'The Secret to Perfectly Minced Garlic',
        'keywords': ['garlic mincing', 'garlic prep', 'cooking tips', 'knife techniques'],
        'word_count': 700
    },
    
    # Week 3: Knife Care
    {
        'type': 'blog_post',
        'topic': 'How Often Should You Sharpen Your Kitchen Knives?',
        'keywords': ['knife sharpening', 'knife maintenance', 'blade care', 'kitchen tools'],
        'word_count': 1000
    },
    {
        'type': 'blog_post',
        'topic': 'Honing vs Sharpening: What\'s the Difference?',
        'keywords': ['knife honing', 'knife sharpening', 'blade maintenance', 'knife care'],
        'word_count': 1100
    },
    {
        'type': 'blog_post',
        'topic': 'Common Knife Care Mistakes That Damage Your Blades',
        'keywords': ['knife care', 'knife mistakes', 'blade damage', 'knife maintenance'],
        'word_count': 1200
    },
    
    # Week 4: Meal Prep & Organization
    {
        'type': 'blog_post',
        'topic': 'Sunday Meal Prep: Essential Tools and Techniques',
        'keywords': ['meal prep', 'sunday prep', 'batch cooking', 'kitchen organization'],
        'word_count': 1300
    },
    {
        'type': 'blog_post',
        'topic': '15 Minute Dinner Prep with the Right Kitchen Tools',
        'keywords': ['quick dinner', 'fast cooking', 'dinner prep', 'time-saving cooking'],
        'word_count': 1000
    },
    {
        'type': 'blog_post',
        'topic': 'How to Organize Your Kitchen for Maximum Efficiency',
        'keywords': ['kitchen organization', 'kitchen efficiency', 'cooking workspace', 'kitchen setup'],
        'word_count': 1100
    }
]


def main():
    """Main entry point for batch generation"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description='Batch Content Generator')
    parser.add_argument(
        '--plan',
        choices=['starter', 'month1', 'custom'],
        default='starter',
        help='Content plan to generate'
    )
    parser.add_argument(
        '--custom-file',
        type=str,
        help='Path to custom content plan JSON file'
    )
    
    args = parser.parse_args()
    
    generator = BatchContentGenerator()
    
    # Select content plan
    if args.plan == 'starter':
        logger.info("Using STARTER content plan (5 blog posts)")
        plan = STARTER_CONTENT_PLAN
    elif args.plan == 'month1':
        logger.info("Using MONTH ONE content plan (12 blog posts)")
        plan = MONTH_ONE_CONTENT_PLAN
    elif args.plan == 'custom' and args.custom_file:
        logger.info(f"Loading custom plan from {args.custom_file}")
        with open(args.custom_file, 'r') as f:
            plan = json.load(f)
    else:
        logger.error("Please specify a valid plan or provide --custom-file")
        return
    
    # Generate content
    print("\n" + "="*60)
    print("LINOROSO BATCH CONTENT GENERATION")
    print("="*60)
    print(f"\n📝 Generating {len(plan)} pieces of content...")
    print(f"⏱️  Estimated time: {len(plan) * ESTIMATED_MINUTES_PER_PIECE} minutes\n")
    
    results = generator.generate_content_library(plan)
    
    # Generate report
    report_path = generator.generate_summary_report(results)
    
    # Print summary
    successful = [r for r in results if r['status'] == 'success']
    failed = [r for r in results if r['status'] == 'error']
    
    print("\n" + "="*60)
    print("GENERATION COMPLETE")
    print("="*60)
    print(f"\n✅ Successful: {len(successful)}/{len(results)}")
    print(f"❌ Failed: {len(failed)}/{len(results)}")
    print(f"\n📄 Report: {report_path}")
    
    if successful:
        print("\n📚 Generated Content:")
        for r in successful:
            if r['type'] == 'blog_post':
                print(f"  • {r['title']} ({r['word_count']} words)")
    
    if failed:
        print("\n⚠️  Errors:")
        for r in failed:
            print(f"  • {r['topic']}: {r['error']}")
    
    print("\n✨ Content saved to: data/generated_content/")
    print()


if __name__ == "__main__":
    main()
