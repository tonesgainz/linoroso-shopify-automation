"""
Main Automation Orchestrator
Coordinates all marketing automation tasks for Linoroso
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from datetime import datetime, time
from typing import List, Dict
import schedule
import time as time_module
from loguru import logger
import json

from settings import config
from content_engine import ContentGenerator
from seo_engine import SEOAutomation
from optimizer import ProductOptimizer

class LinorosoAutomation:
    """Main automation coordinator"""
    
    def __init__(self):
        self.content_generator = ContentGenerator()
        self.seo_engine = SEOAutomation()
        self.product_optimizer = ProductOptimizer()
        self.execution_log = []
        
        logger.add(
            "logs/automation_{time}.log",
            rotation="1 day",
            retention="30 days",
            level="INFO"
        )
        
    def run_daily_content_generation(self):
        """Generate daily blog posts and social media content"""
        
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
    
    def run_weekly_seo_audit(self):
        """Weekly SEO performance audit and optimization suggestions"""

        logger.info("🔍 Starting weekly SEO audit")

        try:
            # Analyze current performance
            pages_csv = config.gsc_pages_csv
            queries_csv = config.gsc_queries_csv

            if pages_csv.exists() and queries_csv.exists():
                analysis = self.seo_engine.analyze_current_performance(
                    pages_csv, queries_csv
                )
                
                # Generate report
                report_path = Path('./reports') / f"seo_audit_{datetime.now().strftime('%Y%m%d')}.json"
                report_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(report_path, 'w') as f:
                    json.dump(analysis, f, indent=2)
                
                logger.success(f"SEO audit report saved: {report_path}")
                
                # Send alert if performance drops
                if analysis['avg_ctr'] < 2.0:
                    self._send_alert("⚠️ CTR below 2% - optimization needed")
                
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
    
    def run_monthly_product_optimization(self):
        """Monthly optimization of all product listings"""

        logger.info("💎 Starting monthly product optimization")

        try:
            products_csv = config.products_csv

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
    
    def _get_daily_topics(self) -> List[Dict]:
        """Get topics for today's content generation"""
        
        # In production, this would read from content calendar
        # For now, return sample topics
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
    
    def _get_social_topics(self) -> List[Dict]:
        """Get topics for social media posts"""
        
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
    
    def _save_social_post(self, post: Dict, platform: str):
        """Save social media post for scheduling"""
        
        output_dir = Path('./data/social_posts') / platform
        output_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = output_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(post, f, indent=2)
        
        logger.info(f"Saved {platform} post: {filepath}")
    
    def _log_execution(self, task_name: str, details: Dict):
        """Log task execution"""
        
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
        
        # Keep last 1000 entries
        all_logs = all_logs[-1000:]
        
        with open(log_file, 'w') as f:
            json.dump(all_logs, f, indent=2)
    
    def _send_alert(self, message: str):
        """Send alert via configured channels"""
        
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
    
    def setup_schedule(self):
        """Set up automated task schedule"""
        
        logger.info("⏰ Setting up automation schedule")
        
        # Daily content generation at 2 AM PST
        schedule.every().day.at("02:00").do(self.run_daily_content_generation)
        
        # Weekly SEO audit every Monday at 9 AM PST
        schedule.every().monday.at("09:00").do(self.run_weekly_seo_audit)
        
        # Monthly product optimization on the 1st at 3 AM PST
        schedule.every().month.at("03:00").do(self.run_monthly_product_optimization)
        
        # Quarterly strategy review (manual trigger recommended)
        # schedule.every(90).days.do(self.run_quarterly_strategy_review)
        
        logger.success("✅ Automation schedule configured")
    
    def run_scheduler(self):
        """Run the scheduler loop"""
        
        logger.info("🚀 Starting Linoroso Marketing Automation")
        logger.info(f"Environment: {config.environment}")
        
        self.setup_schedule()
        
        logger.success("✅ Scheduler running - press Ctrl+C to stop")
        
        try:
            while True:
                schedule.run_pending()
                time_module.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("⏹️  Scheduler stopped by user")
    
    def run_manual_task(self, task_name: str):
        """Manually run a specific task"""
        
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


def main():
    """Main entry point"""
    
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
