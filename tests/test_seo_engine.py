"""
Unit tests for seo_engine module.

Tests keyword research, clustering, and SEO automation.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import pandas as pd
from datetime import datetime

from seo_engine import (
    Keyword,
    KeywordCluster,
    SEOAutomation,
    DEFAULT_LOCATION,
    DEFAULT_MAX_CLUSTERS,
    MIN_CLUSTER_SIZE,
    MONTHLY_CONTENT_TARGET,
    TRAFFIC_CAPTURE_RATE,
    HIGH_PRIORITY_VOLUME_THRESHOLD,
)


class TestKeyword:
    """Test Keyword dataclass."""

    def test_valid_keyword(self):
        """Test creating valid keyword."""
        keyword = Keyword(
            term="kitchen knives",
            search_volume=5000,
            difficulty=45.0,
            cpc=2.50,
            intent="commercial",
            relevance_score=0.85,
        )

        assert keyword.term == "kitchen knives"
        assert keyword.search_volume == 5000
        assert keyword.difficulty == 45.0
        assert keyword.intent == "commercial"

    def test_optional_cpc(self):
        """Test keyword with None CPC."""
        keyword = Keyword(
            term="test",
            search_volume=100,
            difficulty=20.0,
            cpc=None,
            intent="informational",
            relevance_score=0.5,
        )

        assert keyword.cpc is None


class TestKeywordCluster:
    """Test KeywordCluster dataclass."""

    def test_valid_cluster(self):
        """Test creating valid keyword cluster."""
        primary = Keyword(
            term="chef knife",
            search_volume=3000,
            difficulty=40.0,
            cpc=2.0,
            intent="commercial",
            relevance_score=0.9,
        )

        secondary = [
            Keyword(
                term="best chef knife",
                search_volume=1000,
                difficulty=35.0,
                cpc=1.8,
                intent="commercial",
                relevance_score=0.85,
            )
        ]

        cluster = KeywordCluster(
            topic="chef knife",
            primary_keyword=primary,
            secondary_keywords=secondary,
            total_volume=4000,
            avg_difficulty=37.5,
            content_opportunities=["Blog post", "Comparison guide"],
        )

        assert cluster.topic == "chef knife"
        assert cluster.total_volume == 4000
        assert len(cluster.secondary_keywords) == 1
        assert len(cluster.content_opportunities) == 2


class TestSEOAutomation:
    """Test SEOAutomation class."""

    @patch('seo_engine.config')
    def test_init(self, mock_config):
        """Test SEO automation initialization."""
        mock_config.serpapi_key = "test_api_key"

        seo = SEOAutomation()

        assert seo.serpapi_key == "test_api_key"
        assert seo.base_url == "https://serpapi.com/search"

    @patch('seo_engine.config')
    def test_classify_intent_transactional(self, mock_config):
        """Test intent classification for transactional queries."""
        seo = SEOAutomation()

        assert seo._classify_intent("buy kitchen knives") == "transactional"
        assert seo._classify_intent("purchase chef knife") == "transactional"
        assert seo._classify_intent("knife set discount") == "transactional"
        assert seo._classify_intent("shop for knives") == "transactional"

    @patch('seo_engine.config')
    def test_classify_intent_commercial(self, mock_config):
        """Test intent classification for commercial queries."""
        seo = SEOAutomation()

        assert seo._classify_intent("best kitchen knives") == "commercial"
        assert seo._classify_intent("chef knife review") == "commercial"
        assert seo._classify_intent("compare knife sets") == "commercial"
        assert seo._classify_intent("knife vs scissors") == "commercial"

    @patch('seo_engine.config')
    def test_classify_intent_navigational(self, mock_config):
        """Test intent classification for navigational queries."""
        mock_config.brand.main_categories = ["kitchen knives"]
        seo = SEOAutomation()

        assert seo._classify_intent("linoroso knives") == "navigational"
        assert seo._classify_intent("kitchen knives brand") == "navigational"

    @patch('seo_engine.config')
    def test_classify_intent_informational(self, mock_config):
        """Test intent classification for informational queries."""
        mock_config.brand.main_categories = ["kitchen knives"]
        seo = SEOAutomation()

        assert seo._classify_intent("how to sharpen knives") == "informational"
        assert seo._classify_intent("what are kitchen shears") == "informational"

    @patch('seo_engine.config')
    def test_calculate_relevance_high(self, mock_config):
        """Test relevance calculation for highly relevant queries."""
        mock_config.brand.main_categories = ["kitchen knives", "kitchen shears"]
        seo = SEOAutomation()

        # Should score high: category match + kitchen terms
        score = seo._calculate_relevance("professional kitchen knives for chefs")
        assert score >= 0.4  # Category (0.3) + kitchen (0.1) + chef (0.1) + professional (0.05)

    @patch('seo_engine.config')
    def test_calculate_relevance_medium(self, mock_config):
        """Test relevance calculation for moderately relevant queries."""
        mock_config.brand.main_categories = ["kitchen knives"]
        seo = SEOAutomation()

        score = seo._calculate_relevance("cooking utensils")
        assert 0.0 < score < 0.5

    @patch('seo_engine.config')
    def test_calculate_relevance_low(self, mock_config):
        """Test relevance calculation for low relevance queries."""
        mock_config.brand.main_categories = ["kitchen knives"]
        seo = SEOAutomation()

        score = seo._calculate_relevance("random unrelated topic")
        assert score < 0.2

    @patch('seo_engine.config')
    def test_calculate_relevance_capped_at_one(self, mock_config):
        """Test that relevance score never exceeds 1.0."""
        mock_config.brand.main_categories = [
            "kitchen knives",
            "kitchen shears",
            "kitchen tools",
        ]
        seo = SEOAutomation()

        # Query with many matching terms
        score = seo._calculate_relevance(
            "premium professional kitchen knives chef culinary cooking quality durable sharp"
        )
        assert score <= 1.0

    @patch('seo_engine.config')
    def test_estimate_volume_short_query(self, mock_config):
        """Test volume estimation for short queries (higher volume)."""
        seo = SEOAutomation()

        volume = seo._estimate_volume("knife")  # 1 word
        assert volume == 3000  # base_volume (1000) * 3.0

    @patch('seo_engine.config')
    def test_estimate_volume_medium_query(self, mock_config):
        """Test volume estimation for medium queries."""
        seo = SEOAutomation()

        volume = seo._estimate_volume("kitchen knife set")  # 3 words
        assert volume == 1500  # base_volume (1000) * 1.5

    @patch('seo_engine.config')
    def test_estimate_volume_long_query(self, mock_config):
        """Test volume estimation for long queries (lower volume)."""
        seo = SEOAutomation()

        volume = seo._estimate_volume("how to sharpen kitchen knives properly")  # 6 words
        assert volume == 800  # base_volume (1000) * 0.8

    @patch('seo_engine.config')
    def test_estimate_difficulty_short_query(self, mock_config):
        """Test difficulty estimation for short queries (harder)."""
        seo = SEOAutomation()

        difficulty = seo._estimate_difficulty("knife")  # 1 word
        assert difficulty == 50.0  # 60.0 - (10 * 1)

    @patch('seo_engine.config')
    def test_estimate_difficulty_long_tail(self, mock_config):
        """Test difficulty estimation for long-tail queries (easier)."""
        seo = SEOAutomation()

        difficulty = seo._estimate_difficulty("how to sharpen kitchen knives safely")  # 6 words
        assert difficulty == 45.0  # 25.0 + (10 * 2)

    @patch('seo_engine.config')
    def test_estimate_cpc(self, mock_config):
        """Test CPC estimation based on intent."""
        seo = SEOAutomation()

        # Mock _classify_intent for controlled testing
        with patch.object(seo, '_classify_intent') as mock_classify:
            mock_classify.return_value = 'transactional'
            assert seo._estimate_cpc("buy knife") == 2.50

            mock_classify.return_value = 'commercial'
            assert seo._estimate_cpc("best knife") == 1.80

            mock_classify.return_value = 'navigational'
            assert seo._estimate_cpc("linoroso") == 1.20

            mock_classify.return_value = 'informational'
            assert seo._estimate_cpc("how to") == 0.50

    @patch('seo_engine.config')
    @patch('seo_engine.requests.get')
    def test_research_keywords_success(self, mock_get, mock_config):
        """Test successful keyword research."""
        mock_config.serpapi_key = "test_key"

        mock_response = Mock()
        mock_response.json.return_value = {
            "related_searches": [
                {"query": "best kitchen knives"},
                {"query": "professional chef knife"},
            ]
        }
        mock_get.return_value = mock_response

        seo = SEOAutomation()
        keywords = seo.research_keywords(["kitchen knives"], location="United States")

        assert len(keywords) >= 2
        assert all(isinstance(kw, Keyword) for kw in keywords)
        assert mock_get.called

    @patch('seo_engine.config')
    @patch('seo_engine.requests.get')
    def test_research_keywords_api_error(self, mock_get, mock_config):
        """Test keyword research handles API errors gracefully."""
        mock_config.serpapi_key = "test_key"
        mock_get.side_effect = Exception("API Error")

        seo = SEOAutomation()
        keywords = seo.research_keywords(["test"], location="US")

        # Should return empty list, not raise exception
        assert keywords == []

    @patch('seo_engine.config')
    @patch('seo_engine.requests.get')
    def test_research_keywords_removes_duplicates(self, mock_get, mock_config):
        """Test that duplicate keywords are removed."""
        mock_config.serpapi_key = "test_key"

        mock_response = Mock()
        mock_response.json.return_value = {
            "related_searches": [
                {"query": "knife set"},
                {"query": "knife set"},  # Duplicate
                {"query": "kitchen knives"},
            ]
        }
        mock_get.return_value = mock_response

        seo = SEOAutomation()
        keywords = seo.research_keywords(["test"])

        # Check for duplicates
        terms = [kw.term for kw in keywords]
        assert len(terms) == len(set(terms))  # No duplicates

    @patch('seo_engine.config')
    def test_cluster_keywords(self, mock_config):
        """Test keyword clustering."""
        seo = SEOAutomation()

        keywords = [
            Keyword("chef knife", 3000, 40.0, 2.0, "commercial", 0.9),
            Keyword("chef knife set", 1000, 35.0, 1.8, "commercial", 0.85),
            Keyword("kitchen shears", 2000, 30.0, 1.5, "commercial", 0.8),
            Keyword("kitchen shears professional", 500, 25.0, 1.2, "commercial", 0.75),
        ]

        clusters = seo.cluster_keywords(keywords, max_clusters=10)

        assert len(clusters) >= 1
        assert all(isinstance(c, KeywordCluster) for c in clusters)
        assert all(c.total_volume > 0 for c in clusters)

    @patch('seo_engine.config')
    def test_cluster_keywords_respects_min_size(self, mock_config):
        """Test that clusters below minimum size are excluded."""
        seo = SEOAutomation()

        keywords = [
            Keyword("single keyword", 1000, 40.0, 2.0, "commercial", 0.9),
            Keyword("chef knife", 3000, 40.0, 2.0, "commercial", 0.9),
            Keyword("chef knife set", 1000, 35.0, 1.8, "commercial", 0.85),
        ]

        clusters = seo.cluster_keywords(keywords)

        # Only "chef knife" cluster should remain (has 2 keywords)
        assert all(len(c.secondary_keywords) + 1 >= MIN_CLUSTER_SIZE for c in clusters)

    @patch('seo_engine.config')
    def test_cluster_keywords_respects_max_clusters(self, mock_config):
        """Test that max_clusters limit is respected."""
        seo = SEOAutomation()

        # Create many keywords with different topics
        keywords = []
        for i in range(50):
            keywords.append(
                Keyword(f"topic{i} keyword", 1000, 40.0, 2.0, "commercial", 0.9)
            )
            keywords.append(
                Keyword(f"topic{i} related", 500, 35.0, 1.8, "commercial", 0.85)
            )

        clusters = seo.cluster_keywords(keywords, max_clusters=5)

        assert len(clusters) <= 5

    @patch('seo_engine.config')
    def test_identify_content_opportunities(self, mock_config):
        """Test content opportunity identification."""
        seo = SEOAutomation()

        keywords = [
            Keyword("chef knife", 3000, 40.0, 2.0, "informational", 0.9),
            Keyword("best chef knife", 1000, 35.0, 1.8, "commercial", 0.85),
            Keyword("buy chef knife", 500, 30.0, 2.5, "transactional", 0.8),
        ]

        opportunities = seo._identify_content_opportunities("chef knife", keywords)

        assert len(opportunities) > 0
        # Should have opportunities for all three intent types
        assert any("blog post" in opp.lower() for opp in opportunities)
        assert any("comparison" in opp.lower() or "buyer" in opp.lower() for opp in opportunities)
        assert any("product page" in opp.lower() or "landing page" in opp.lower() for opp in opportunities)

    @patch('seo_engine.config')
    def test_generate_content_calendar(self, mock_config):
        """Test content calendar generation."""
        seo = SEOAutomation()

        primary = Keyword("chef knife", 8000, 40.0, 2.0, "commercial", 0.9)
        clusters = [
            KeywordCluster(
                topic="chef knife",
                primary_keyword=primary,
                secondary_keywords=[],
                total_volume=8000,
                avg_difficulty=40.0,
                content_opportunities=[
                    "Blog post: Complete guide to chef knife",
                    "Comparison guide: Best chef knife",
                ],
            )
        ]

        calendar = seo.generate_content_calendar(clusters, months=1)

        assert isinstance(calendar, pd.DataFrame)
        assert len(calendar) > 0
        assert "week" in calendar.columns
        assert "month" in calendar.columns
        assert "primary_keyword" in calendar.columns
        assert "priority" in calendar.columns

    @patch('seo_engine.config')
    def test_generate_content_calendar_priority(self, mock_config):
        """Test that high-volume clusters get high priority."""
        seo = SEOAutomation()

        high_volume = Keyword("popular topic", 10000, 40.0, 2.0, "commercial", 0.9)
        low_volume = Keyword("niche topic", 500, 40.0, 2.0, "commercial", 0.9)

        clusters = [
            KeywordCluster(
                topic="popular",
                primary_keyword=high_volume,
                secondary_keywords=[],
                total_volume=10000,
                avg_difficulty=40.0,
                content_opportunities=["Blog post"],
            ),
            KeywordCluster(
                topic="niche",
                primary_keyword=low_volume,
                secondary_keywords=[],
                total_volume=500,
                avg_difficulty=40.0,
                content_opportunities=["Blog post"],
            ),
        ]

        calendar = seo.generate_content_calendar(clusters, months=1)

        # High volume should be marked as high priority
        high_priority_items = calendar[calendar['priority'] == 'High']
        assert len(high_priority_items) > 0

    @patch('seo_engine.config')
    def test_analyze_current_performance(self, mock_config, tmp_path):
        """Test GSC performance analysis."""
        seo = SEOAutomation()

        # Create mock CSV files
        pages_data = pd.DataFrame({
            'Top pages': ['/page1', '/page2', '/page3'],
            'Clicks': [100, 50, 200],
            'Impressions': [1000, 500, 2000],
            'CTR': ['10.0%', '10.0%', '10.0%'],
            'Position': [5.0, 8.0, 3.0],
        })

        queries_data = pd.DataFrame({
            'Top queries': ['query1', 'query2', 'query3'],
            'Clicks': [80, 40, 30],
            'Impressions': [800, 400, 300],
            'CTR': ['10.0%', '10.0%', '10.0%'],
            'Position': [6.0, 9.0, 4.0],
        })

        pages_csv = tmp_path / "pages.csv"
        queries_csv = tmp_path / "queries.csv"

        pages_data.to_csv(pages_csv, index=False)
        queries_data.to_csv(queries_csv, index=False)

        analysis = seo.analyze_current_performance(pages_csv, queries_csv)

        assert analysis['total_pages'] == 3
        assert analysis['total_clicks'] == 350
        assert analysis['total_impressions'] == 3500
        assert 'avg_ctr' in analysis
        assert 'avg_position' in analysis
        assert len(analysis['top_pages']) > 0
        assert len(analysis['top_queries']) > 0

    @patch('seo_engine.config')
    def test_analyze_current_performance_identifies_opportunities(self, mock_config, tmp_path):
        """Test that performance analysis identifies optimization opportunities."""
        seo = SEOAutomation()

        # Create data with low CTR page (opportunity)
        pages_data = pd.DataFrame({
            'Top pages': ['/low-ctr-page'],
            'Clicks': [5],
            'Impressions': [1000],  # High impressions
            'CTR': ['0.5%'],  # Low CTR < 2%
            'Position': [5.0],
        })

        queries_data = pd.DataFrame({
            'Top queries': ['almost ranking'],
            'Clicks': [10],
            'Impressions': [200],
            'CTR': ['5.0%'],
            'Position': [7.0],  # Position 4-10 (quick win)
        })

        pages_csv = tmp_path / "pages.csv"
        queries_csv = tmp_path / "queries.csv"

        pages_data.to_csv(pages_csv, index=False)
        queries_data.to_csv(queries_csv, index=False)

        analysis = seo.analyze_current_performance(pages_csv, queries_csv)

        # Should identify opportunities
        assert len(analysis['opportunities']) > 0
        assert any(opp['type'] == 'Improve CTR' for opp in analysis['opportunities'])
        assert any('Quick Win' in opp['type'] for opp in analysis['opportunities'])

    @patch('seo_engine.config')
    @patch.object(SEOAutomation, 'research_keywords')
    @patch.object(SEOAutomation, 'cluster_keywords')
    @patch.object(SEOAutomation, 'generate_content_calendar')
    def test_generate_seo_report(
        self, mock_calendar, mock_cluster, mock_research, mock_config, tmp_path
    ):
        """Test SEO report generation."""
        mock_config.serpapi_key = "test_key"

        # Mock the methods
        mock_keywords = [
            Keyword("chef knife", 3000, 40.0, 2.0, "commercial", 0.9),
        ]
        mock_research.return_value = mock_keywords

        mock_clusters = [
            KeywordCluster(
                topic="chef knife",
                primary_keyword=mock_keywords[0],
                secondary_keywords=[],
                total_volume=3000,
                avg_difficulty=40.0,
                content_opportunities=["Blog post"],
            )
        ]
        mock_cluster.return_value = mock_clusters

        mock_calendar.return_value = pd.DataFrame({
            'week': [1],
            'topic_cluster': ['chef knife'],
            'primary_keyword': ['chef knife'],
        })

        seo = SEOAutomation()
        report_path = seo.generate_seo_report(output_path=tmp_path / "report.json")

        assert report_path.exists()
        assert (tmp_path / f"content_calendar_{datetime.now().strftime('%Y%m%d')}.csv").exists()

        # Verify report content
        import json
        with open(report_path) as f:
            report = json.load(f)

        assert 'generated_at' in report
        assert 'goal' in report
        assert 'keyword_research' in report
        assert 'top_opportunities' in report


class TestConstants:
    """Test module constants."""

    def test_constants_are_reasonable(self):
        """Test that constants have reasonable values."""
        assert DEFAULT_LOCATION == "United States"
        assert DEFAULT_MAX_CLUSTERS > 0
        assert MIN_CLUSTER_SIZE >= 2
        assert MONTHLY_CONTENT_TARGET > 0
        assert 0 < TRAFFIC_CAPTURE_RATE < 1
        assert HIGH_PRIORITY_VOLUME_THRESHOLD > 0
