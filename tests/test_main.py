"""
Unit tests for main orchestration module.

Tests automation workflow, task scheduling, and orchestration logic.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call, mock_open
from pathlib import Path
import json
from datetime import datetime

from main import (
    LinorosoAutomation,
    main,
    DEFAULT_CONTENT_SCHEDULE_TIME,
    DEFAULT_SEO_AUDIT_DAY,
    DEFAULT_SEO_AUDIT_TIME,
    DEFAULT_PRODUCT_OPT_TIME,
    SLEEP_INTERVAL_SECONDS,
    MAX_LOG_ENTRIES,
    CTR_THRESHOLD,
)


class TestLinorosoAutomation:
    """Test LinorosoAutomation orchestration class."""

    @patch('main.ProductOptimizer')
    @patch('main.SEOAutomation')
    @patch('main.ContentGenerator')
    def test_init(self, mock_content, mock_seo, mock_optimizer):
        """Test automation initialization."""
        automation = LinorosoAutomation()

        assert automation.content_generator is not None
        assert automation.seo_engine is not None
        assert automation.product_optimizer is not None
        assert automation.execution_log == []

    @patch('main.ProductOptimizer')
    @patch('main.SEOAutomation')
    @patch('main.ContentGenerator')
    def test_get_daily_topics(self, mock_content, mock_seo, mock_optimizer):
        """Test daily topics retrieval."""
        automation = LinorosoAutomation()
        topics = automation._get_daily_topics()

        assert isinstance(topics, list)
        assert len(topics) >= 1
        assert 'topic' in topics[0]
        assert 'keywords' in topics[0]
        assert 'word_count' in topics[0]

    @patch('main.ProductOptimizer')
    @patch('main.SEOAutomation')
    @patch('main.ContentGenerator')
    def test_get_social_topics(self, mock_content, mock_seo, mock_optimizer):
        """Test social media topics retrieval."""
        automation = LinorosoAutomation()
        topics = automation._get_social_topics()

        assert isinstance(topics, list)
        assert len(topics) >= 3  # Returns at least 3 social topics
        assert 'topic' in topics[0]
        assert 'keywords' in topics[0]

    @patch('main.ProductOptimizer')
    @patch('main.SEOAutomation')
    @patch('main.ContentGenerator')
    def test_save_social_post(self, mock_content, mock_seo, mock_optimizer, tmp_path, monkeypatch):
        """Test social post saving."""
        # Change the output directory to tmp_path for testing
        monkeypatch.setattr(Path, 'cwd', lambda: tmp_path)

        automation = LinorosoAutomation()

        post_data = {
            'caption': 'Test caption',
            'hashtags': ['test', 'automation']
        }

        # Mock the path to use tmp_path
        with patch('main.Path') as mock_path:
            mock_dir = tmp_path / 'social_posts' / 'instagram'
            mock_dir.mkdir(parents=True, exist_ok=True)
            mock_file = mock_dir / 'test.json'

            mock_path.return_value = mock_dir

            automation._save_social_post(post_data, 'instagram')

            # Verify directory structure would be created
            mock_path.return_value.mkdir.assert_called_once()

    @patch('main.ProductOptimizer')
    @patch('main.SEOAutomation')
    @patch('main.ContentGenerator')
    def test_log_execution(self, mock_content, mock_seo, mock_optimizer, tmp_path):
        """Test task execution logging."""
        automation = LinorosoAutomation()

        # Create a temporary log file
        log_file = tmp_path / 'execution_log.json'

        with patch('main.Path') as mock_path:
            mock_path.return_value = log_file
            mock_path.return_value.parent.mkdir = Mock()
            mock_path.return_value.exists.return_value = False

            automation._log_execution('test_task', {'status': 'success'})

        # Verify log entry was added to in-memory log
        assert len(automation.execution_log) == 1
        assert automation.execution_log[0]['task'] == 'test_task'
        assert automation.execution_log[0]['details'] == {'status': 'success'}

    @patch('main.ProductOptimizer')
    @patch('main.SEOAutomation')
    @patch('main.ContentGenerator')
    def test_log_execution_respects_max_entries(self, mock_content, mock_seo, mock_optimizer, tmp_path):
        """Test that log file respects MAX_LOG_ENTRIES limit."""
        automation = LinorosoAutomation()

        # Pre-populate with MAX_LOG_ENTRIES + 10 entries
        existing_logs = [{'task': f'old_task_{i}'} for i in range(MAX_LOG_ENTRIES + 10)]

        log_file = tmp_path / 'execution_log.json'
        log_file.parent.mkdir(parents=True, exist_ok=True)

        with open(log_file, 'w') as f:
            json.dump(existing_logs, f)

        with patch('main.Path') as mock_path:
            mock_path.return_value = log_file
            mock_path.return_value.parent.mkdir = Mock()
            mock_path.return_value.exists.return_value = True

            # The _log_execution method should trim to MAX_LOG_ENTRIES
            with patch('builtins.open', mock_open(read_data=json.dumps(existing_logs))):
                automation._log_execution('new_task', {'status': 'success'})

    @patch('main.ProductOptimizer')
    @patch('main.SEOAutomation')
    @patch('main.ContentGenerator')
    def test_send_alert(self, mock_content, mock_seo, mock_optimizer, tmp_path):
        """Test alert sending."""
        automation = LinorosoAutomation()

        alert_file = tmp_path / 'alerts.log'
        alert_file.parent.mkdir(parents=True, exist_ok=True)

        with patch('main.Path') as mock_path:
            mock_path.return_value = alert_file
            mock_path.return_value.parent.mkdir = Mock()

            automation._send_alert("Test alert message")

    @patch('main.ProductOptimizer')
    @patch('main.SEOAutomation')
    @patch('main.ContentGenerator')
    def test_run_daily_content_generation_success(self, mock_content, mock_seo, mock_optimizer):
        """Test successful daily content generation."""
        automation = LinorosoAutomation()

        # Mock the content generator methods
        mock_blog_post = Mock()
        mock_blog_post.title = "Test Blog Post"
        mock_blog_post.word_count = 1000

        automation.content_generator.generate_blog_post = Mock(return_value=mock_blog_post)
        automation.content_generator.save_content = Mock(return_value=Path('/test/path.md'))
        automation.content_generator.generate_social_post = Mock(return_value={'caption': 'Test'})

        # Mock helper methods
        automation._save_social_post = Mock()
        automation._log_execution = Mock()

        # Run the task
        automation.run_daily_content_generation()

        # Verify content was generated
        assert automation.content_generator.generate_blog_post.called
        assert automation.content_generator.save_content.called
        assert automation._log_execution.called

    @patch('main.ProductOptimizer')
    @patch('main.SEOAutomation')
    @patch('main.ContentGenerator')
    def test_run_daily_content_generation_handles_errors(self, mock_content, mock_seo, mock_optimizer):
        """Test that content generation handles individual topic errors gracefully."""
        automation = LinorosoAutomation()

        # Make the first blog post generation fail
        automation.content_generator.generate_blog_post = Mock(
            side_effect=Exception("API Error")
        )
        automation._log_execution = Mock()

        # Should raise exception since all topics failed
        with pytest.raises(Exception):
            automation.run_daily_content_generation()

    @patch('main.ProductOptimizer')
    @patch('main.SEOAutomation')
    @patch('main.ContentGenerator')
    def test_run_weekly_seo_audit_success(self, mock_content, mock_seo, mock_optimizer, tmp_path):
        """Test successful weekly SEO audit."""
        automation = LinorosoAutomation()

        # Create mock GSC data files
        pages_csv = tmp_path / "Pages.csv"
        queries_csv = tmp_path / "Queries.csv"

        pages_csv.write_text("Top pages,Clicks,Impressions,CTR,Position\n/page1,100,1000,10.0%,5.0")
        queries_csv.write_text("Top queries,Clicks,Impressions,CTR,Position\ntest,50,500,10.0%,3.0")

        mock_analysis = {
            'total_clicks': 100,
            'total_impressions': 1000,
            'avg_ctr': 10.0,
            'avg_position': 5.0,
            'opportunities': []
        }

        automation.seo_engine.analyze_current_performance = Mock(return_value=mock_analysis)
        automation._send_alert = Mock()
        automation._log_execution = Mock()

        # Mock the file paths
        with patch('main.Path') as mock_path:
            mock_path.return_value = tmp_path / 'reports'
            mock_path.return_value.parent.mkdir = Mock()

            # Mock pages_csv.exists() and queries_csv.exists()
            with patch('main.Path.__truediv__') as mock_div:
                mock_csv = Mock()
                mock_csv.exists.return_value = True
                mock_div.return_value = mock_csv

                with patch('builtins.open', mock_open()):
                    automation.run_weekly_seo_audit()

        assert automation._log_execution.called

    @patch('main.ProductOptimizer')
    @patch('main.SEOAutomation')
    @patch('main.ContentGenerator')
    def test_run_weekly_seo_audit_sends_alert_on_low_ctr(self, mock_content, mock_seo, mock_optimizer):
        """Test that SEO audit sends alert when CTR is low."""
        automation = LinorosoAutomation()

        mock_analysis = {
            'total_clicks': 100,
            'avg_ctr': 1.5,  # Below CTR_THRESHOLD (2.0)
            'avg_position': 5.0,
        }

        automation.seo_engine.analyze_current_performance = Mock(return_value=mock_analysis)
        automation._send_alert = Mock()
        automation._log_execution = Mock()

        with patch('main.Path') as mock_path:
            mock_csv = Mock()
            mock_csv.exists.return_value = True
            mock_path.return_value = mock_csv

            with patch('builtins.open', mock_open()):
                automation.run_weekly_seo_audit()

        # Verify alert was sent
        automation._send_alert.assert_called_once()
        alert_message = automation._send_alert.call_args[0][0]
        assert 'CTR' in alert_message

    @patch('main.ProductOptimizer')
    @patch('main.SEOAutomation')
    @patch('main.ContentGenerator')
    def test_run_weekly_seo_audit_missing_files(self, mock_content, mock_seo, mock_optimizer):
        """Test SEO audit when GSC files are missing."""
        automation = LinorosoAutomation()

        with patch('main.Path') as mock_path:
            mock_csv = Mock()
            mock_csv.exists.return_value = False
            mock_path.return_value = mock_csv

            # Should not raise exception, just log warning
            automation.run_weekly_seo_audit()

    @patch('main.ProductOptimizer')
    @patch('main.SEOAutomation')
    @patch('main.ContentGenerator')
    def test_run_monthly_product_optimization_success(self, mock_content, mock_seo, mock_optimizer):
        """Test successful monthly product optimization."""
        automation = LinorosoAutomation()

        mock_results = [
            {'product_handle': 'product-1'},
            {'product_handle': 'product-2'}
        ]

        automation.product_optimizer.optimize_all_products = Mock(return_value=mock_results)
        automation.product_optimizer.generate_optimization_report = Mock(return_value=Path('/report.json'))
        automation.product_optimizer.create_shopify_import_csv = Mock()
        automation._send_alert = Mock()
        automation._log_execution = Mock()

        with patch('main.Path') as mock_path:
            mock_csv = Mock()
            mock_csv.exists.return_value = True
            mock_path.return_value = mock_csv
            mock_path.return_value.parent.mkdir = Mock()

            automation.run_monthly_product_optimization()

        assert automation.product_optimizer.optimize_all_products.called
        assert automation.product_optimizer.generate_optimization_report.called
        assert automation._send_alert.called

    @patch('main.ProductOptimizer')
    @patch('main.SEOAutomation')
    @patch('main.ContentGenerator')
    def test_run_quarterly_strategy_review(self, mock_content, mock_seo, mock_optimizer):
        """Test quarterly strategy review."""
        automation = LinorosoAutomation()

        automation.seo_engine.generate_seo_report = Mock(return_value=Path('/strategy.json'))
        automation._send_alert = Mock()
        automation._log_execution = Mock()

        automation.run_quarterly_strategy_review()

        assert automation.seo_engine.generate_seo_report.called
        assert automation._log_execution.called
        assert automation._send_alert.called

    @patch('main.ProductOptimizer')
    @patch('main.SEOAutomation')
    @patch('main.ContentGenerator')
    @patch('main.schedule')
    def test_setup_schedule(self, mock_schedule, mock_content, mock_seo, mock_optimizer):
        """Test schedule setup."""
        automation = LinorosoAutomation()

        # Mock schedule methods
        mock_every = Mock()
        mock_schedule.every.return_value = mock_every
        mock_every.day.at.return_value.do = Mock()
        mock_every.monday.at.return_value.do = Mock()
        mock_every.month.at.return_value.do = Mock()

        automation.setup_schedule()

        # Verify schedule was configured
        assert mock_schedule.every.called

    @patch('main.ProductOptimizer')
    @patch('main.SEOAutomation')
    @patch('main.ContentGenerator')
    @patch('main.schedule')
    @patch('main.time_module')
    def test_run_scheduler(self, mock_time, mock_schedule, mock_content, mock_seo, mock_optimizer):
        """Test scheduler loop."""
        automation = LinorosoAutomation()

        # Make the scheduler run once then raise KeyboardInterrupt
        mock_schedule.run_pending.side_effect = [None, KeyboardInterrupt()]

        automation.run_scheduler()

        # Verify scheduler was running
        assert mock_schedule.run_pending.called

    @patch('main.ProductOptimizer')
    @patch('main.SEOAutomation')
    @patch('main.ContentGenerator')
    def test_run_manual_task_content(self, mock_content, mock_seo, mock_optimizer):
        """Test manual task execution for content generation."""
        automation = LinorosoAutomation()
        automation.run_daily_content_generation = Mock()

        automation.run_manual_task('content')

        automation.run_daily_content_generation.assert_called_once()

    @patch('main.ProductOptimizer')
    @patch('main.SEOAutomation')
    @patch('main.ContentGenerator')
    def test_run_manual_task_seo_audit(self, mock_content, mock_seo, mock_optimizer):
        """Test manual task execution for SEO audit."""
        automation = LinorosoAutomation()
        automation.run_weekly_seo_audit = Mock()

        automation.run_manual_task('seo_audit')

        automation.run_weekly_seo_audit.assert_called_once()

    @patch('main.ProductOptimizer')
    @patch('main.SEOAutomation')
    @patch('main.ContentGenerator')
    def test_run_manual_task_invalid(self, mock_content, mock_seo, mock_optimizer):
        """Test manual task execution with invalid task name."""
        automation = LinorosoAutomation()

        # Should not raise exception, just log error
        automation.run_manual_task('invalid_task')


class TestMainFunction:
    """Test main entry point function."""

    @patch('main.LinorosoAutomation')
    @patch('main.argparse.ArgumentParser.parse_args')
    def test_main_scheduler_mode(self, mock_args, mock_automation_class):
        """Test main function in scheduler mode."""
        mock_args.return_value = Mock(mode='scheduler', task=None)
        mock_automation = Mock()
        mock_automation_class.return_value = mock_automation

        main()

        mock_automation.run_scheduler.assert_called_once()

    @patch('main.LinorosoAutomation')
    @patch('main.argparse.ArgumentParser.parse_args')
    def test_main_manual_mode_single_task(self, mock_args, mock_automation_class):
        """Test main function in manual mode with single task."""
        mock_args.return_value = Mock(mode='manual', task='content')
        mock_automation = Mock()
        mock_automation_class.return_value = mock_automation

        main()

        mock_automation.run_manual_task.assert_called_once_with('content')

    @patch('main.LinorosoAutomation')
    @patch('main.argparse.ArgumentParser.parse_args')
    def test_main_manual_mode_all_tasks(self, mock_args, mock_automation_class):
        """Test main function in manual mode running all tasks."""
        mock_args.return_value = Mock(mode='manual', task='all')
        mock_automation = Mock()
        mock_automation_class.return_value = mock_automation

        main()

        # Verify all tasks were called
        mock_automation.run_daily_content_generation.assert_called_once()
        mock_automation.run_weekly_seo_audit.assert_called_once()
        mock_automation.run_monthly_product_optimization.assert_called_once()

    @patch('main.LinorosoAutomation')
    @patch('main.argparse.ArgumentParser.parse_args')
    def test_main_manual_mode_no_task(self, mock_args, mock_automation_class):
        """Test main function in manual mode without specifying task."""
        mock_args.return_value = Mock(mode='manual', task=None)
        mock_automation = Mock()
        mock_automation_class.return_value = mock_automation

        # Should not raise exception, just log error
        main()


class TestConstants:
    """Test module constants."""

    def test_schedule_time_constants(self):
        """Test schedule time constants are valid."""
        assert DEFAULT_CONTENT_SCHEDULE_TIME == "02:00"
        assert DEFAULT_SEO_AUDIT_TIME == "09:00"
        assert DEFAULT_PRODUCT_OPT_TIME == "03:00"
        assert DEFAULT_SEO_AUDIT_DAY == "monday"

    def test_operational_constants(self):
        """Test operational constants are reasonable."""
        assert SLEEP_INTERVAL_SECONDS > 0
        assert MAX_LOG_ENTRIES > 0
        assert CTR_THRESHOLD > 0
