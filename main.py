"""
Main Automation Orchestrator.

Coordinates all marketing automation tasks for Linoroso, including:
- Daily content generation (blog posts, social media)
- Weekly SEO audits and performance analysis
- Monthly product listing optimization
- Quarterly strategy reviews

This module provides both scheduled automation and manual task execution modes.
"""

from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import schedule
import time as time_module
from loguru import logger
import json

from settings import config
from content_engine import ContentGenerator
from seo_engine import SEOAutomation
from optimizer import ProductOptimizer

# Constants
DEFAULT_CONTENT_SCHEDULE_TIME = "02:00"
DEFAULT_SEO_AUDIT_DAY = "monday"
DEFAULT_SEO_AUDIT_TIME = "09:00"
DEFAULT_PRODUCT_OPT_TIME = "03:00"
SLEEP_INTERVAL_SECONDS = 60
MAX_LOG_ENTRIES = 1000
CTR_THRESHOLD = 2.0  # Alert threshold for CTR percentage

class LinorosoAutomation:
    """Main automation coordinator for Linoroso marketing tasks.

    This class orchestrates all automated marketing tasks including content generation,
    SEO optimization, and product listing management. It supports both scheduled
    automated execution and manual task triggering.

    Attributes:
        content_generator: Instance for generating blog and social content
        seo_engine: Instance for SEO analysis and optimization
        product_optimizer: Instance for product listing optimization
        execution_log: List of task execution records
    """

    def __init__(self) -> None:
        """Initialize automation coordinator with all necessary engines."""
        self.content_generator = ContentGenerator()
        self.seo_engine = SEOAutomation()
        self.product_optimizer = ProductOptimizer()
        self.execution_log: List[Dict] = []

        # Configure logging with rotation and retention
        logger.add(
            "logs/automation_{time}.log",
            rotation="1 day",
            retention="30 days",
            level="INFO",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}"
        )
        
    def run_daily_content_generation(self) -> None:
        """Generate daily blog posts and social media content.

        This method:
        1. Retrieves daily topics from the content calendar
        2. Generates blog posts for each topic
        3. Creates social media posts for multiple platforms
        4. Saves all generated content
        5. Logs execution details

        Raises:
            Exception: If content generation fails critically
        """
        logger.info("🚀 Starting daily content generation")
        
        try:
            # Load content calendar or generate topics
            topics = self._get_daily_topics()
            
            generated_content = []
            
            for topic_data in topics:
                try:
                    # Generate blog post
                    blog_post = self.content_generator.generate_blog_post(
                        topic=topic_data['topic'],
                        keywords=topic_data['keywords'],
                        word_count=topic_data.get('word_count', 1000)
                    )
                    
                    # Save to file
                    filepath = self.content_generator.save_content(blog_post)
                    generated_content.append({
                        'type': 'blog_post',
                        'title': blog_post.title,
                        'filepath': str(filepath),
                        'word_count': blog_post.word_count
                    })
                    
                    logger.success(f"Generated blog post: {blog_post.title}")
                    
                except Exception as e:
                    logger.error(f"Error generating content for {topic_data['topic']}: {e}")
                    continue
            
            # Generate social media posts
            social_topics = self._get_social_topics()
            
            for social_topic in social_topics[:3]:  # 3 posts per day
                try:
                    for platform in ['instagram', 'pinterest']:
                        post = self.content_generator.generate_social_post(
                            topic=social_topic['topic'],
                            keywords=social_topic['keywords'],
                            platform=platform
                        )
                        
                        # Save for scheduling
                        self._save_social_post(post, platform)
                        
                        generated_content.append({
                            'type': f'{platform}_post',
                            'topic': social_topic['topic']
                        })
                        
                except Exception as e:
                    logger.error(f"Error generating social post: {e}")
                    continue
            
            # Log execution
            self._log_execution('daily_content_generation', {
                'generated_count': len(generated_content),
                'content': generated_content
            })
            
            logger.success(f"✅ Generated {len(generated_content)} pieces of content")
            
        except Exception as e:
            logger.error(f"Error in daily content generation: {e}")
            raise
    
    def run_weekly_seo_audit(self) -> None:
        """Weekly SEO performance audit and optimization suggestions.

        Analyzes current SEO performance using Google Search Console data,
        generates optimization recommendations, and sends alerts if performance
        drops below thresholds.

        Raises:
            Exception: If SEO audit fails critically
        """
        logger.info("🔍 Starting weekly SEO audit")
        
        try:
            # Analyze current performance
            pages_csv = Path("/mnt/project/Pages.csv")
            queries_csv = Path("/mnt/project/Queries.csv")

            if pages_csv.exists() and queries_csv.exists():
                analysis = self.seo_engine.analyze_current_performance(
                    pages_csv, queries_csv
                )

                # Generate report
                report_path = Path('./reports') / f"seo_audit_{datetime.now().strftime('%Y%m%d')}.json"
                report_path.parent.mkdir(parents=True, exist_ok=True)

                with open(report_path, 'w', encoding='utf-8') as f:
                    json.dump(analysis, f, indent=2, ensure_ascii=False)

                logger.success(f"SEO audit report saved: {report_path}")

                # Send alert if performance drops below threshold
                if analysis['avg_ctr'] < CTR_THRESHOLD:
                    self._send_alert(f"⚠️ CTR below {CTR_THRESHOLD}% - optimization needed")
                
                self._log_execution('weekly_seo_audit', {
                    'report_path': str(report_path),
                    'total_clicks': analysis['total_clicks'],
                    'avg_ctr': analysis['avg_ctr']
                })
            else:
                logger.warning("GSC data files not found - skipping audit")
                
        except Exception as e:
            logger.error(f"Error in weekly SEO audit: {e}")
            raise
    
    def run_monthly_product_optimization(self) -> None:
        """Monthly optimization of all product listings.

        Optimizes all Shopify product listings for SEO and conversion,
        generates reports, and creates import-ready CSV files.

        Raises:
            Exception: If product optimization fails critically
        """
        logger.info("💎 Starting monthly product optimization")
        
        try:
            products_csv = Path("/mnt/project/products_export_1 2.csv")
            
            if products_csv.exists():
                # Optimize all products
                results = self.product_optimizer.optimize_all_products(products_csv)
                
                # Generate reports
                report_path = self.product_optimizer.generate_optimization_report(results)
                
                # Create Shopify import CSV
                import_path = Path('./data') / f"shopify_import_{datetime.now().strftime('%Y%m%d')}.csv"
                import_path.parent.mkdir(parents=True, exist_ok=True)
                self.product_optimizer.create_shopify_import_csv(results, import_path)
                
                logger.success(f"Optimized {len(results)} products")
                
                self._log_execution('monthly_product_optimization', {
                    'products_optimized': len(results),
                    'report_path': str(report_path),
                    'import_csv': str(import_path)
                })
                
                # Send summary email
                self._send_alert(f"✅ Monthly optimization complete: {len(results)} products updated")
                
            else:
                logger.warning("Products CSV not found - skipping optimization")
                
        except Exception as e:
            logger.error(f"Error in monthly product optimization: {e}")
            raise
    
    def run_quarterly_strategy_review(self):
        """Quarterly comprehensive SEO strategy and keyword research"""
        
        logger.info("📊 Starting quarterly strategy review")
        
        try:
            # Generate fresh SEO strategy
            report_path = self.seo_engine.generate_seo_report()
            
            logger.success(f"Quarterly strategy report: {report_path}")
            
            self._log_execution('quarterly_strategy_review', {
                'report_path': str(report_path)
            })
            
            self._send_alert(f"📈 Quarterly strategy report ready: {report_path}")
            
        except Exception as e:
            logger.error(f"Error in quarterly review: {e}")
            raise
    
    def _get_daily_topics(self) -> List[Dict[str, any]]:
        """Get topics for today's content generation.

        In production, this would read from a content calendar or database.
        Currently returns sample topics for demonstration.

        Returns:
            List of topic dictionaries with topic, keywords, and word_count
        """
        # TODO: Implement content calendar integration
        topics = [
            {
                'topic': '5 Time-Saving Knife Techniques Every Home Cook Should Know',
                'keywords': ['knife techniques', 'cooking tips', 'kitchen skills', 'time-saving cooking'],
                'word_count': 1200
            },
            {
                'topic': 'How to Properly Maintain Your Kitchen Knives',
                'keywords': ['knife maintenance', 'knife care', 'kitchen tools', 'knife sharpening'],
                'word_count': 1000
            }
        ]
        
        return topics[:1]  # 1 blog post per day
    
    def _get_social_topics(self) -> List[Dict[str, any]]:
        """Get topics for social media posts.

        Returns:
            List of topic dictionaries for social media content
        """
        
        topics = [
            {
                'topic': 'Quick tip: The proper way to hold a chef knife',
                'keywords': ['knife skills', 'cooking tips', 'kitchen basics']
            },
            {
                'topic': 'Transform your meal prep with these organization ideas',
                'keywords': ['meal prep', 'kitchen organization', 'cooking efficiency']
            },
            {
                'topic': 'The secret to perfectly diced vegetables',
                'keywords': ['knife skills', 'vegetable prep', 'cooking techniques']
            }
        ]
        
        return topics
    
    def _save_social_post(self, post: Dict[str, any], platform: str) -> None:
        """Save social media post for scheduling.

        Args:
            post: Social media post data
            platform: Social media platform name
        """
        
        output_dir = Path('./data/social_posts') / platform
        output_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = output_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(post, f, indent=2)
        
        logger.info(f"Saved {platform} post: {filepath}")
    
    def _log_execution(self, task_name: str, details: Dict[str, any]) -> None:
        """Log task execution to file and in-memory log.

        Args:
            task_name: Name of the executed task
            details: Task execution details and results
        """
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'task': task_name,
            'details': details
        }
        
        self.execution_log.append(log_entry)
        
        # Save to file
        log_file = Path('./logs/execution_log.json')
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing logs
        if log_file.exists():
            with open(log_file, 'r') as f:
                all_logs = json.load(f)
        else:
            all_logs = []
        
        all_logs.append(log_entry)

        # Keep last MAX_LOG_ENTRIES entries to prevent unbounded growth
        all_logs = all_logs[-MAX_LOG_ENTRIES:]
        
        with open(log_file, 'w') as f:
            json.dump(all_logs, f, indent=2)
    
    def _send_alert(self, message: str) -> None:
        """Send alert via configured channels.

        Args:
            message: Alert message to send
        """
        
        logger.info(f"ALERT: {message}")
        
        # In production, send via:
        # - Email (to config.alert_email)
        # - Slack (to config.slack_webhook)
        # - SMS for critical alerts
        
        # For now, just log
        alert_file = Path('./logs/alerts.log')
        alert_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(alert_file, 'a') as f:
            f.write(f"{datetime.now().isoformat()} - {message}\n")
    
    def setup_schedule(self) -> None:
        """Set up automated task schedule.

        Configures scheduled tasks for:
        - Daily content generation
        - Weekly SEO audits
        - Monthly product optimization
        """
        logger.info("⏰ Setting up automation schedule")

        # Daily content generation at 2 AM PST
        schedule.every().day.at(DEFAULT_CONTENT_SCHEDULE_TIME).do(self.run_daily_content_generation)

        # Weekly SEO audit every Monday at 9 AM PST
        schedule.every().monday.at(DEFAULT_SEO_AUDIT_TIME).do(self.run_weekly_seo_audit)

        # Monthly product optimization on the 1st at 3 AM PST
        schedule.every().month.at(DEFAULT_PRODUCT_OPT_TIME).do(self.run_monthly_product_optimization)
        
        # Quarterly strategy review (manual trigger recommended)
        # schedule.every(90).days.do(self.run_quarterly_strategy_review)
        
        logger.success("✅ Automation schedule configured")
    
    def run_scheduler(self) -> None:
        """Run the scheduler loop.

        Starts the continuous scheduler that executes tasks at configured times.
        Runs until interrupted by user (Ctrl+C).
        """
        logger.info("🚀 Starting Linoroso Marketing Automation")
        logger.info(f"Environment: {config.environment}")

        self.setup_schedule()

        logger.success("✅ Scheduler running - press Ctrl+C to stop")

        try:
            while True:
                schedule.run_pending()
                time_module.sleep(SLEEP_INTERVAL_SECONDS)
        except KeyboardInterrupt:
            logger.info("⏹️  Scheduler stopped by user")

    def run_manual_task(self, task_name: str) -> None:
        """Manually run a specific task.

        Args:
            task_name: Name of the task to run (content, seo_audit, product_optimization, strategy)
        """
        
        tasks = {
            'content': self.run_daily_content_generation,
            'seo_audit': self.run_weekly_seo_audit,
            'product_optimization': self.run_monthly_product_optimization,
            'strategy': self.run_quarterly_strategy_review
        }
        
        if task_name in tasks:
            logger.info(f"🎯 Running manual task: {task_name}")
            tasks[task_name]()
        else:
            logger.error(f"Unknown task: {task_name}")
            logger.info(f"Available tasks: {', '.join(tasks.keys())}")


def main() -> None:
    """Main entry point for the automation system.

    Parses command line arguments and either starts the scheduler
    or runs manual tasks based on user input.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Linoroso Shopify Marketing Automation')
    parser.add_argument(
        '--mode',
        choices=['scheduler', 'manual'],
        default='scheduler',
        help='Run mode: scheduler (automated) or manual (one-time)'
    )
    parser.add_argument(
        '--task',
        choices=['content', 'seo_audit', 'product_optimization', 'strategy', 'all'],
        help='Task to run in manual mode'
    )
    
    args = parser.parse_args()
    
    automation = LinorosoAutomation()
    
    if args.mode == 'scheduler':
        # Run continuous automation
        automation.run_scheduler()
    else:
        # Manual execution
        if args.task == 'all':
            logger.info("Running all tasks...")
            automation.run_daily_content_generation()
            automation.run_weekly_seo_audit()
            automation.run_monthly_product_optimization()
        elif args.task:
            automation.run_manual_task(args.task)
        else:
            logger.error("Please specify --task when using manual mode")
            parser.print_help()


if __name__ == "__main__":
    main()
