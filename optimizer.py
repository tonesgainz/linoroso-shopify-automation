"""
Product Listing Optimizer.

AI-powered optimization of Shopify product listings for maximum conversion.
Analyzes product data, generates optimized titles and descriptions, and
provides SEO scoring and recommendations.
"""

from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd
from dataclasses import dataclass
import json
from datetime import datetime
from loguru import logger

from settings import config
from content_engine import ContentGenerator

# Constants
MIN_TITLE_LENGTH = 30
OPTIMAL_MIN_TITLE_LENGTH = 60
OPTIMAL_MAX_TITLE_LENGTH = 70
MAX_TITLE_LENGTH_WARNING = 80
MIN_DESCRIPTION_LENGTH = 300
MIN_TAG_COUNT = 5
MIN_IMAGE_COUNT = 3
SEO_PERFECT_SCORE = 100.0
POST_OPTIMIZATION_SCORE = 90.0
MAX_TAGS = 15  # Shopify recommends 10-15 tags

@dataclass
class Product:
    """Product data structure.

    Attributes:
        handle: Product URL handle
        title: Product title
        description: Product description HTML
        vendor: Product vendor/brand
        product_type: Product type/category
        tags: Product tags
        price: Product price
        sku: Stock keeping unit
        images: List of image URLs
    """
    handle: str
    title: str
    description: str
    vendor: str
    product_type: str
    tags: List[str]
    price: float
    sku: str
    images: List[str]

    @classmethod
    def from_shopify_export(cls, row: pd.Series) -> 'Product':
        """Create Product from Shopify CSV export row.

        Args:
            row: Pandas Series from Shopify CSV

        Returns:
            Product instance
        """
        return cls(
            handle=row.get('Handle', ''),
            title=row.get('Title', ''),
            description=row.get('Body (HTML)', ''),
            vendor=row.get('Vendor', 'Linoroso'),
            product_type=row.get('Type', ''),
            tags=row.get('Tags', '').split(',') if pd.notna(row.get('Tags')) else [],
            price=float(row.get('Variant Price', 0)),
            sku=row.get('Variant SKU', ''),
            images=[row.get('Image Src', '')] if pd.notna(row.get('Image Src')) else []
        )

@dataclass
class OptimizationResult:
    """Result of product optimization"""
    product_handle: str
    original_title: str
    optimized_title: str
    original_description: str
    optimized_description: str
    meta_description: str
    suggested_tags: List[str]
    seo_score: float
    improvement_notes: List[str]
    created_at: datetime

class ProductOptimizer:
    """Optimize product listings using AI.

    Uses AI-powered content generation to create optimized product titles,
    descriptions, and metadata for improved SEO and conversion rates.

    Attributes:
        content_generator: Content generation engine
    """

    def __init__(self) -> None:
        """Initialize product optimizer with content generator."""
        self.content_generator = ContentGenerator()
        
    def analyze_product(self, product: Product) -> Dict[str, any]:
        """Analyze current product listing quality.

        Args:
            product: Product to analyze

        Returns:
            Dictionary with score, issues, and metrics
        """
        issues = []
        score = SEO_PERFECT_SCORE

        # Title analysis
        title_len = len(product.title)
        if title_len < MIN_TITLE_LENGTH:
            issues.append(f"Title too short - should be {OPTIMAL_MIN_TITLE_LENGTH}-{OPTIMAL_MAX_TITLE_LENGTH} characters")
            score -= 15
        elif title_len > MAX_TITLE_LENGTH_WARNING:
            issues.append("Title too long - will be truncated in search results")
            score -= 10
        
        # Check for keywords in title
        keywords_in_title = any(
            cat.lower() in product.title.lower() 
            for cat in config.brand.main_categories
        )
        if not keywords_in_title:
            issues.append("Title missing primary keyword")
            score -= 20
        
        # Description analysis
        desc_len = len(product.description)
        if desc_len < MIN_DESCRIPTION_LENGTH:
            issues.append(f"Description too short - should be at least {MIN_DESCRIPTION_LENGTH} characters")
            score -= 15

        # Check for HTML in description
        if '<p>' in product.description or '<div>' in product.description:
            # Good - has formatting
            pass
        else:
            issues.append("Description lacks HTML formatting")
            score -= 5

        # Tags analysis
        if len(product.tags) < MIN_TAG_COUNT:
            issues.append(f"Too few product tags - add more for better discovery (minimum {MIN_TAG_COUNT})")
            score -= 10

        # Price analysis
        if product.price <= 0:
            issues.append("Invalid price")
            score -= 20

        # Images
        if not product.images or len(product.images) < MIN_IMAGE_COUNT:
            issues.append(f"Need at least {MIN_IMAGE_COUNT} product images")
            score -= 10
        
        return {
            'score': max(score, 0),
            'issues': issues,
            'title_length': title_len,
            'description_length': desc_len,
            'tag_count': len(product.tags),
            'image_count': len(product.images)
        }
    
    def optimize_product(self, product: Product, 
                        target_keywords: Optional[List[str]] = None) -> OptimizationResult:
        """Optimize a single product listing"""
        
        logger.info(f"Optimizing product: {product.title}")
        
        # Analyze current state
        analysis = self.analyze_product(product)
        
        # Determine keywords
        if not target_keywords:
            target_keywords = self._extract_keywords(product)
        
        # Generate optimized content
        product_details = {
            'current_title': product.title,
            'current_description': product.description,
            'product_type': product.product_type,
            'price': product.price,
            'existing_tags': product.tags
        }
        
        optimized_content = self.content_generator.generate_product_description(
            product_name=product.title,
            keywords=target_keywords,
            product_details=product_details
        )
        
        # Extract components
        lines = optimized_content.content.split('\n')
        optimized_title = lines[0].replace('# ', '') if lines else product.title
        
        # Generate meta description
        meta_desc = optimized_content.meta_description
        
        # Suggest tags
        suggested_tags = self._generate_tags(product, target_keywords)
        
        # Calculate improvement
        improvement_notes = []
        if analysis['score'] < 80:
            improvement_notes.append(f"SEO score improved from {analysis['score']:.1f} to 90+")
        if len(optimized_title) > analysis['title_length']:
            improvement_notes.append("Title optimized for SEO length")
        if target_keywords[0].lower() in optimized_title.lower():
            improvement_notes.append("Primary keyword added to title")
        
        result = OptimizationResult(
            product_handle=product.handle,
            original_title=product.title,
            optimized_title=optimized_title[:OPTIMAL_MAX_TITLE_LENGTH],
            original_description=product.description,
            optimized_description=optimized_content.content,
            meta_description=meta_desc,
            suggested_tags=suggested_tags,
            seo_score=POST_OPTIMIZATION_SCORE,
            improvement_notes=improvement_notes,
            created_at=datetime.now()
        )
        
        logger.success(f"Optimized product: {result.optimized_title}")
        return result
    
    def _extract_keywords(self, product: Product) -> List[str]:
        """Extract relevant keywords from product"""
        keywords = []
        
        # Add product type
        if product.product_type:
            keywords.append(product.product_type.lower())
        
        # Add matching categories
        for category in config.brand.main_categories:
            if category.lower() in product.title.lower() or \
               category.lower() in product.description.lower():
                keywords.append(category)
        
        # Add brand
        keywords.append(config.brand.name.lower())
        
        # Add from tags
        keywords.extend([tag.lower() for tag in product.tags[:3]])
        
        return keywords[:5]  # Top 5 keywords
    
    def _generate_tags(self, product: Product, keywords: List[str]) -> List[str]:
        """Generate comprehensive tag set"""
        tags = set()
        
        # Add keywords as tags
        tags.update(keywords)
        
        # Add product attributes
        tags.add(product.product_type.lower())
        tags.add(config.brand.name.lower())
        
        # Add use case tags
        use_cases = [
            'home cooking',
            'meal prep',
            'kitchen essentials',
            'gift idea',
            'professional quality'
        ]
        tags.update(use_cases[:3])
        
        # Add benefit tags
        benefits = [
            'durable',
            'premium quality',
            'easy to use',
            'dishwasher safe',
            'ergonomic design'
        ]
        tags.update(benefits[:2])
        
        return list(tags)[:MAX_TAGS]
    
    def optimize_all_products(self, csv_path: Path) -> List[OptimizationResult]:
        """Optimize all products from Shopify export CSV"""
        
        logger.info(f"Loading products from {csv_path}")
        
        try:
            df = pd.read_csv(csv_path)
            
            # Get unique products (remove variant rows)
            products_df = df.drop_duplicates(subset=['Handle'])
            
            logger.info(f"Found {len(products_df)} unique products")
            
            results = []
            
            for idx, row in products_df.iterrows():
                try:
                    product = Product.from_shopify_export(row)
                    
                    # Skip if missing critical data
                    if not product.title or not product.handle:
                        logger.warning(f"Skipping product with missing data at row {idx}")
                        continue
                    
                    # Optimize
                    result = self.optimize_product(product)
                    results.append(result)
                    
                    # Rate limiting
                    if len(results) % 10 == 0:
                        logger.info(f"Optimized {len(results)} products...")
                    
                except Exception as e:
                    logger.error(f"Error optimizing product at row {idx}: {e}")
                    continue
            
            logger.success(f"Optimized {len(results)} products")
            return results
            
        except Exception as e:
            logger.error(f"Error loading products: {e}")
            raise
    
    def generate_optimization_report(self, results: List[OptimizationResult],
                                    output_path: Optional[Path] = None) -> Path:
        """Generate report of all optimizations"""
        
        if output_path is None:
            output_path = Path('./reports') / f"product_optimization_{datetime.now().strftime('%Y%m%d')}.json"
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'total_products_optimized': len(results),
            'summary': {
                'avg_improvement': sum(r.seo_score for r in results) / len(results) if results else 0,
                'products_with_title_changes': sum(1 for r in results if r.original_title != r.optimized_title),
                'products_with_new_descriptions': len(results)
            },
            'optimizations': [
                {
                    'handle': r.product_handle,
                    'original_title': r.original_title,
                    'optimized_title': r.optimized_title,
                    'meta_description': r.meta_description,
                    'suggested_tags': r.suggested_tags,
                    'seo_score': r.seo_score,
                    'improvements': r.improvement_notes
                }
                for r in results
            ]
        }
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Also generate CSV for easy import
        csv_path = output_path.with_suffix('.csv')
        df = pd.DataFrame([
            {
                'Handle': r.product_handle,
                'Original Title': r.original_title,
                'Optimized Title': r.optimized_title,
                'Meta Description': r.meta_description,
                'Tags': ', '.join(r.suggested_tags),
                'SEO Score': r.seo_score
            }
            for r in results
        ])
        df.to_csv(csv_path, index=False)
        
        logger.success(f"Generated optimization report: {output_path}")
        logger.success(f"Generated CSV for import: {csv_path}")
        
        return output_path
    
    def create_shopify_import_csv(self, results: List[OptimizationResult],
                                  output_path: Path) -> Path:
        """Create CSV formatted for Shopify import"""
        
        import_data = []
        
        for result in results:
            import_data.append({
                'Handle': result.product_handle,
                'Title': result.optimized_title,
                'Body (HTML)': result.optimized_description,
                'SEO Title': result.optimized_title,
                'SEO Description': result.meta_description,
                'Tags': ', '.join(result.suggested_tags),
                'Published': 'TRUE'
            })
        
        df = pd.DataFrame(import_data)
        df.to_csv(output_path, index=False)
        
        logger.success(f"Created Shopify import CSV: {output_path}")
        return output_path


# Example usage
if __name__ == "__main__":
    optimizer = ProductOptimizer()
    
    # Optimize products from export
    products_csv = Path("/mnt/project/products_export_1 2.csv")
    
    if products_csv.exists():
        print("🚀 Starting product optimization...")
        results = optimizer.optimize_all_products(products_csv)
        
        print(f"\n✅ Optimized {len(results)} products")
        
        # Generate reports
        report_path = optimizer.generate_optimization_report(results)
        print(f"📄 Report generated: {report_path}")
        
        # Create import CSV
        import_csv = Path('./data/shopify_import_optimized.csv')
        import_csv.parent.mkdir(parents=True, exist_ok=True)
        optimizer.create_shopify_import_csv(results, import_csv)
        print(f"📦 Shopify import CSV ready: {import_csv}")
    else:
        print(f"❌ Products CSV not found at {products_csv}")
