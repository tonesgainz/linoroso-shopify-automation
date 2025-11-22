"""
Unit tests for optimizer module.

Tests product optimization, analysis, and validation.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import pandas as pd

from optimizer import (
    Product,
    OptimizationResult,
    ProductOptimizer,
    MIN_TITLE_LENGTH,
    OPTIMAL_MIN_TITLE_LENGTH,
    OPTIMAL_MAX_TITLE_LENGTH,
    MAX_TITLE_LENGTH_WARNING,
    MIN_DESCRIPTION_LENGTH,
    MIN_TAG_COUNT,
    MIN_IMAGE_COUNT,
    SEO_PERFECT_SCORE,
    POST_OPTIMIZATION_SCORE,
    MAX_TAGS,
)


class TestProduct:
    """Test Product dataclass."""

    def test_valid_product(self):
        """Test creating valid product."""
        product = Product(
            handle='test-product',
            title='Test Product',
            description='Test description',
            vendor='Linoroso',
            product_type='Kitchen Knives',
            tags=['knife', 'kitchen'],
            price=29.99,
            sku='TEST-001',
            images=['image1.jpg', 'image2.jpg']
        )

        assert product.handle == 'test-product'
        assert product.title == 'Test Product'
        assert product.price == 29.99
        assert len(product.images) == 2

    def test_from_shopify_export(self):
        """Test creating product from Shopify CSV row."""
        row = pd.Series({
            'Handle': 'test-handle',
            'Title': 'Test Title',
            'Body (HTML)': '<p>Test description</p>',
            'Vendor': 'TestVendor',
            'Type': 'Knife',
            'Tags': 'tag1,tag2,tag3',
            'Variant Price': '19.99',
            'Variant SKU': 'SKU-001',
            'Image Src': 'image.jpg'
        })

        product = Product.from_shopify_export(row)

        assert product.handle == 'test-handle'
        assert product.title == 'Test Title'
        assert product.price == 19.99
        assert len(product.tags) == 3
        assert 'tag1' in product.tags

    def test_from_shopify_export_missing_data(self):
        """Test handling missing data in Shopify export."""
        row = pd.Series({
            'Handle': 'test',
            'Title': 'Title',
            'Tags': None,  # Missing tags
            'Variant Price': '10.00'
        })

        product = Product.from_shopify_export(row)

        assert product.handle == 'test'
        assert product.tags == []  # Should handle None gracefully


class TestOptimizationResult:
    """Test OptimizationResult dataclass."""

    def test_valid_result(self):
        """Test creating valid optimization result."""
        result = OptimizationResult(
            product_handle='test-product',
            original_title='Old Title',
            optimized_title='New Optimized Title',
            original_description='Old desc',
            optimized_description='New desc',
            meta_description='Meta',
            suggested_tags=['tag1', 'tag2'],
            seo_score=85.0,
            improvement_notes=['Note 1', 'Note 2'],
            created_at=datetime.now()
        )

        assert result.product_handle == 'test-product'
        assert result.seo_score == 85.0
        assert len(result.suggested_tags) == 2


class TestProductOptimizer:
    """Test ProductOptimizer class."""

    @patch('optimizer.ContentGenerator')
    def test_init(self, mock_generator):
        """Test optimizer initialization."""
        optimizer = ProductOptimizer()
        assert optimizer.content_generator is not None

    @patch('optimizer.ContentGenerator')
    @patch('optimizer.config')
    def test_analyze_product_perfect_score(self, mock_config, mock_generator):
        """Test product analysis with perfect product."""
        mock_config.brand.main_categories = ['kitchen knives']

        optimizer = ProductOptimizer()

        product = Product(
            handle='test',
            title='Premium Kitchen Knives Set - Professional Chef Quality 65 Chars',
            description='<p>' + 'x' * 400 + '</p>',  # Long enough
            vendor='Linoroso',
            product_type='Knives',
            tags=['tag1', 'tag2', 'tag3', 'tag4', 'tag5', 'tag6'],
            price=29.99,
            sku='TEST-001',
            images=['img1.jpg', 'img2.jpg', 'img3.jpg', 'img4.jpg']
        )

        analysis = optimizer.analyze_product(product)

        assert analysis['score'] == SEO_PERFECT_SCORE
        assert len(analysis['issues']) == 0

    @patch('optimizer.ContentGenerator')
    @patch('optimizer.config')
    def test_analyze_product_short_title(self, mock_config, mock_generator):
        """Test product with too short title."""
        mock_config.brand.main_categories = ['kitchen knives']

        optimizer = ProductOptimizer()

        product = Product(
            handle='test',
            title='Short',  # Too short
            description='<p>Test description</p>',
            vendor='Linoroso',
            product_type='Knives',
            tags=['tag1', 'tag2', 'tag3', 'tag4', 'tag5'],
            price=29.99,
            sku='TEST-001',
            images=['img1.jpg', 'img2.jpg', 'img3.jpg']
        )

        analysis = optimizer.analyze_product(product)

        assert analysis['score'] < SEO_PERFECT_SCORE
        assert any('too short' in issue.lower() for issue in analysis['issues'])

    @patch('optimizer.ContentGenerator')
    @patch('optimizer.config')
    def test_analyze_product_missing_keyword(self, mock_config, mock_generator):
        """Test product missing primary keyword in title."""
        mock_config.brand.main_categories = ['kitchen knives']

        optimizer = ProductOptimizer()

        product = Product(
            handle='test',
            title='Some Random Product Title That Is Long Enough But Missing Keywords',
            description='<p>' + 'x' * 400 + '</p>',
            vendor='Linoroso',
            product_type='Misc',
            tags=['tag1', 'tag2', 'tag3', 'tag4', 'tag5'],
            price=29.99,
            sku='TEST-001',
            images=['img1.jpg', 'img2.jpg', 'img3.jpg']
        )

        analysis = optimizer.analyze_product(product)

        assert any('missing primary keyword' in issue.lower() for issue in analysis['issues'])

    @patch('optimizer.ContentGenerator')
    @patch('optimizer.config')
    def test_analyze_product_few_images(self, mock_config, mock_generator):
        """Test product with too few images."""
        mock_config.brand.main_categories = ['kitchen knives']

        optimizer = ProductOptimizer()

        product = Product(
            handle='test',
            title='Kitchen Knives Professional Set Long Title For SEO',
            description='<p>' + 'x' * 400 + '</p>',
            vendor='Linoroso',
            product_type='Knives',
            tags=['tag1', 'tag2', 'tag3', 'tag4', 'tag5'],
            price=29.99,
            sku='TEST-001',
            images=['img1.jpg']  # Only 1 image
        )

        analysis = optimizer.analyze_product(product)

        assert any(f'at least {MIN_IMAGE_COUNT}' in issue for issue in analysis['issues'])

    @patch('optimizer.config')
    def test_extract_keywords(self, mock_config):
        """Test keyword extraction from product."""
        mock_config.brand.main_categories = ['kitchen knives', 'knife sets']
        mock_config.brand.name = 'Linoroso'

        optimizer = ProductOptimizer()

        product = Product(
            handle='test',
            title='Professional Kitchen Knives Set',
            description='<p>Premium kitchen knives for home chefs</p>',
            vendor='Linoroso',
            product_type='Knife Set',
            tags=['premium', 'professional', 'chef'],
            price=29.99,
            sku='TEST-001',
            images=['img1.jpg']
        )

        keywords = optimizer._extract_keywords(product)

        assert 'knife set' in [k.lower() for k in keywords]
        assert 'linoroso' in [k.lower() for k in keywords]

    @patch('optimizer.config')
    def test_generate_tags(self, mock_config):
        """Test tag generation."""
        mock_config.brand.main_categories = ['kitchen knives']
        mock_config.brand.name = 'Linoroso'

        optimizer = ProductOptimizer()

        product = Product(
            handle='test',
            title='Kitchen Knives',
            description='Test',
            vendor='Linoroso',
            product_type='Knife',
            tags=[],
            price=29.99,
            sku='TEST-001',
            images=['img1.jpg']
        )

        keywords = ['knife', 'kitchen', 'professional']
        tags = optimizer._generate_tags(product, keywords)

        assert len(tags) <= MAX_TAGS
        assert 'knife' in tags or 'kitchen' in tags  # Some keywords should be in tags


class TestConstants:
    """Test module constants."""

    def test_title_length_constants(self):
        """Test title length constants are logical."""
        assert MIN_TITLE_LENGTH < OPTIMAL_MIN_TITLE_LENGTH
        assert OPTIMAL_MIN_TITLE_LENGTH < OPTIMAL_MAX_TITLE_LENGTH
        assert OPTIMAL_MAX_TITLE_LENGTH < MAX_TITLE_LENGTH_WARNING

    def test_seo_score_constants(self):
        """Test SEO score constants."""
        assert SEO_PERFECT_SCORE == 100.0
        assert POST_OPTIMIZATION_SCORE > 0
        assert POST_OPTIMIZATION_SCORE <= SEO_PERFECT_SCORE

    def test_validation_constants(self):
        """Test validation constants are reasonable."""
        assert MIN_DESCRIPTION_LENGTH > 0
        assert MIN_TAG_COUNT > 0
        assert MIN_IMAGE_COUNT > 0
        assert MAX_TAGS > MIN_TAG_COUNT
