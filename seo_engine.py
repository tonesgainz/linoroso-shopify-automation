"""
SEO Automation Module
Handles keyword research, competitor analysis, and on-page optimization
Goal: 10x organic traffic growth over 12 months
"""

import requests
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from settings import config
from loguru import logger
import pandas as pd
from collections import defaultdict

@dataclass
class Keyword:
    """Keyword data structure"""
    term: str
    search_volume: int
    difficulty: float  # 0-100
    cpc: Optional[float]
    intent: str  # informational, commercial, transactional, navigational
    relevance_score: float  # 0-1, how relevant to Linoroso
    
@dataclass
class KeywordCluster:
    """Grouped keywords by topic"""
    topic: str
    primary_keyword: Keyword
    secondary_keywords: List[Keyword]
    total_volume: int
    avg_difficulty: float
    content_opportunities: List[str]

class SEOAutomation:
    """Automated SEO analysis and optimization"""
    
    def __init__(self):
        self.serpapi_key = config.serpapi_key
        self.base_url = "https://serpapi.com/search"
        
    def research_keywords(self, seed_keywords: List[str], 
                         location: str = "United States") -> List[Keyword]:
        """Research keywords from seed terms"""
        
        logger.info(f"Starting keyword research for {len(seed_keywords)} seed terms")
        all_keywords = []
        
        for seed in seed_keywords:
            try:
                # Get related keywords from SERP
                params = {
                    "engine": "google",
                    "q": seed,
                    "location": location,
                    "google_domain": "google.com",
                    "gl": "us",
                    "hl": "en",
                    "api_key": self.serpapi_key
                }
                
                response = requests.get(self.base_url, params=params)
                data = response.json()
                
                # Extract related searches
                related = data.get("related_searches", [])
                
                for item in related:
                    query = item.get("query", "")
                    if query:
                        # Estimate metrics (in production, use proper SEO tool API)
                        keyword = self._create_keyword_from_query(query)
                        all_keywords.append(keyword)
                        
                logger.info(f"Found {len(related)} related keywords for '{seed}'")
                
            except Exception as e:
                logger.error(f"Error researching keyword '{seed}': {e}")
                continue
        
        # Remove duplicates and sort by relevance and volume
        unique_keywords = {kw.term: kw for kw in all_keywords}.values()
        sorted_keywords = sorted(
            unique_keywords, 
            key=lambda x: (x.relevance_score * x.search_volume), 
            reverse=True
        )
        
        logger.success(f"Researched {len(sorted_keywords)} unique keywords")
        return sorted_keywords
    
    def _create_keyword_from_query(self, query: str) -> Keyword:
        """Create keyword object with estimated metrics"""
        
        # Determine intent based on query terms
        intent = self._classify_intent(query)
        
        # Calculate relevance to Linoroso
        relevance = self._calculate_relevance(query)
        
        # Estimate metrics (replace with actual API calls in production)
        return Keyword(
            term=query,
            search_volume=self._estimate_volume(query),
            difficulty=self._estimate_difficulty(query),
            cpc=self._estimate_cpc(query),
            intent=intent,
            relevance_score=relevance
        )
    
    def _classify_intent(self, query: str) -> str:
        """Classify search intent"""
        query_lower = query.lower()
        
        # Transactional indicators
        if any(word in query_lower for word in ['buy', 'purchase', 'order', 'deal', 'discount', 'shop', 'price']):
            return 'transactional'
        
        # Commercial investigation indicators
        elif any(word in query_lower for word in ['best', 'review', 'compare', 'vs', 'top', 'alternative']):
            return 'commercial'
        
        # Navigational indicators
        elif 'linoroso' in query_lower or any(brand in query_lower for brand in config.brand.main_categories):
            return 'navigational'
        
        # Default to informational
        else:
            return 'informational'
    
    def _calculate_relevance(self, query: str) -> float:
        """Calculate relevance score to Linoroso products"""
        query_lower = query.lower()
        score = 0.0
        
        # Check for product category matches
        for category in config.brand.main_categories:
            if category.lower() in query_lower:
                score += 0.3
        
        # Check for related kitchen terms
        kitchen_terms = [
            'kitchen', 'cooking', 'chef', 'culinary', 'food prep',
            'cutting', 'chopping', 'slicing', 'dicing', 'meal prep',
            'storage', 'organize', 'utensil', 'tool'
        ]
        
        for term in kitchen_terms:
            if term in query_lower:
                score += 0.1
        
        # Check for quality indicators
        quality_terms = ['premium', 'professional', 'quality', 'durable', 'sharp']
        for term in quality_terms:
            if term in query_lower:
                score += 0.05
        
        return min(score, 1.0)
    
    def _estimate_volume(self, query: str) -> int:
        """Estimate search volume (simplified version)"""
        # In production, use actual SEO tool API
        # This is a simplified estimation
        base_volume = 1000
        
        # Adjust by query length (shorter = more volume typically)
        words = len(query.split())
        if words <= 2:
            multiplier = 3.0
        elif words <= 4:
            multiplier = 1.5
        else:
            multiplier = 0.8
            
        return int(base_volume * multiplier)
    
    def _estimate_difficulty(self, query: str) -> float:
        """Estimate keyword difficulty"""
        # Simplified estimation
        words = len(query.split())
        
        # Long-tail keywords are generally easier
        if words >= 4:
            return 25.0 + (10 * (words - 4))
        else:
            return 60.0 - (10 * words)
    
    def _estimate_cpc(self, query: str) -> float:
        """Estimate CPC"""
        # Commercial intent = higher CPC
        intent = self._classify_intent(query)
        
        cpc_map = {
            'transactional': 2.50,
            'commercial': 1.80,
            'navigational': 1.20,
            'informational': 0.50
        }
        
        return cpc_map.get(intent, 1.00)
    
    def cluster_keywords(self, keywords: List[Keyword], 
                        max_clusters: int = 20) -> List[KeywordCluster]:
        """Group keywords into topical clusters"""
        
        logger.info(f"Clustering {len(keywords)} keywords into topics")
        
        # Simple clustering by common terms
        clusters_dict = defaultdict(list)
        
        for kw in keywords:
            # Extract main topic (first 2 words as simplified approach)
            words = kw.term.split()
            topic = ' '.join(words[:2]) if len(words) >= 2 else kw.term
            clusters_dict[topic].append(kw)
        
        # Create KeywordCluster objects
        clusters = []
        for topic, kw_list in clusters_dict.items():
            if len(kw_list) < 2:
                continue
                
            # Sort by volume to find primary keyword
            sorted_kws = sorted(kw_list, key=lambda x: x.search_volume, reverse=True)
            
            cluster = KeywordCluster(
                topic=topic,
                primary_keyword=sorted_kws[0],
                secondary_keywords=sorted_kws[1:],
                total_volume=sum(kw.search_volume for kw in kw_list),
                avg_difficulty=sum(kw.difficulty for kw in kw_list) / len(kw_list),
                content_opportunities=self._identify_content_opportunities(topic, kw_list)
            )
            clusters.append(cluster)
        
        # Sort by total volume and limit
        clusters.sort(key=lambda x: x.total_volume, reverse=True)
        clusters = clusters[:max_clusters]
        
        logger.success(f"Created {len(clusters)} keyword clusters")
        return clusters
    
    def _identify_content_opportunities(self, topic: str, keywords: List[Keyword]) -> List[str]:
        """Identify content types to create for keyword cluster"""
        opportunities = []
        
        # Analyze intent distribution
        intents = [kw.intent for kw in keywords]
        
        if 'informational' in intents:
            opportunities.append(f"Blog post: Complete guide to {topic}")
            opportunities.append(f"How-to article: {topic} for beginners")
        
        if 'commercial' in intents:
            opportunities.append(f"Comparison guide: Best {topic}")
            opportunities.append(f"Buyer's guide: Choosing {topic}")
        
        if 'transactional' in intents:
            opportunities.append(f"Product page optimization for {topic}")
            opportunities.append(f"Landing page: Buy {topic}")
        
        return opportunities
    
    def generate_content_calendar(self, clusters: List[KeywordCluster], 
                                  months: int = 12) -> pd.DataFrame:
        """Generate 12-month content calendar from keyword clusters"""
        
        logger.info(f"Generating {months}-month content calendar")
        
        # Target: 50-100 pieces monthly = ~3 pieces per day
        target_pieces = months * 75  # Average of 75 per month
        
        calendar_data = []
        piece_count = 0
        
        # Distribute content across clusters
        for cluster in clusters:
            # Create multiple pieces per cluster
            for opportunity in cluster.content_opportunities[:3]:
                if piece_count >= target_pieces:
                    break
                    
                # Schedule across weeks
                week_num = (piece_count // 3) + 1
                
                calendar_data.append({
                    'week': week_num,
                    'month': (week_num // 4) + 1,
                    'topic_cluster': cluster.topic,
                    'primary_keyword': cluster.primary_keyword.term,
                    'search_volume': cluster.primary_keyword.search_volume,
                    'difficulty': cluster.primary_keyword.difficulty,
                    'content_type': opportunity,
                    'target_intent': cluster.primary_keyword.intent,
                    'priority': 'High' if cluster.total_volume > 5000 else 'Medium',
                    'estimated_traffic': int(cluster.total_volume * 0.15)  # 15% capture rate
                })
                
                piece_count += 1
        
        df = pd.DataFrame(calendar_data)
        
        logger.success(f"Generated calendar with {len(df)} content pieces")
        return df
    
    def analyze_current_performance(self, pages_csv: Path, 
                                   queries_csv: Path) -> Dict:
        """Analyze current SEO performance from GSC data"""
        
        logger.info("Analyzing current SEO performance")
        
        try:
            # Load GSC data
            pages_df = pd.read_csv(pages_csv)
            queries_df = pd.read_csv(queries_csv)
            
            # Calculate key metrics
            analysis = {
                'total_pages': len(pages_df),
                'total_clicks': pages_df['Clicks'].sum(),
                'total_impressions': pages_df['Impressions'].sum(),
                'avg_ctr': pages_df['CTR'].str.rstrip('%').astype(float).mean(),
                'avg_position': pages_df['Position'].mean(),
                'total_queries': len(queries_df),
                'top_pages': pages_df.nlargest(10, 'Clicks')[['Top pages', 'Clicks', 'CTR']].to_dict('records'),
                'top_queries': queries_df.nlargest(10, 'Clicks')[['Top queries', 'Clicks', 'Position']].to_dict('records'),
                'opportunities': []
            }
            
            # Identify opportunities
            # 1. High impression, low CTR pages
            low_ctr = pages_df[
                (pages_df['Impressions'] > 100) & 
                (pages_df['CTR'].str.rstrip('%').astype(float) < 2.0)
            ]
            
            for _, row in low_ctr.head(5).iterrows():
                analysis['opportunities'].append({
                    'type': 'Improve CTR',
                    'page': row['Top pages'],
                    'current_ctr': row['CTR'],
                    'impressions': row['Impressions'],
                    'action': 'Optimize title and meta description'
                })
            
            # 2. Keywords ranking 4-10 (easy wins)
            quick_wins = queries_df[
                (queries_df['Position'] >= 4) & 
                (queries_df['Position'] <= 10)
            ]
            
            for _, row in quick_wins.head(5).iterrows():
                analysis['opportunities'].append({
                    'type': 'Quick Win - Move to Page 1',
                    'query': row['Top queries'],
                    'current_position': row['Position'],
                    'clicks': row['Clicks'],
                    'action': 'Add internal links and update content'
                })
            
            logger.success("Completed SEO performance analysis")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing performance: {e}")
            raise
    
    def generate_seo_report(self, output_path: Optional[Path] = None) -> Path:
        """Generate comprehensive SEO strategy report"""
        
        if output_path is None:
            output_path = Path('./reports') / f"seo_strategy_{datetime.now().strftime('%Y%m%d')}.json"
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info("Generating SEO strategy report")
        
        # Research keywords
        seed_keywords = [
            "kitchen knives",
            "chef knife",
            "kitchen shears",
            "knife set",
            "knife sharpening",
            "kitchen organization",
            "meal prep tools",
            "cooking essentials"
        ]
        
        keywords = self.research_keywords(seed_keywords)
        clusters = self.cluster_keywords(keywords)
        calendar = self.generate_content_calendar(clusters)
        
        # Compile report
        report = {
            'generated_at': datetime.now().isoformat(),
            'goal': '10x organic traffic growth over 12 months',
            'target_revenue': '$350K-450K additional annual revenue',
            'strategy': {
                'approach': 'Zero ad spend, SEO-first content marketing',
                'monthly_content_target': '50-100 pieces',
                'focus_areas': [c.topic for c in clusters[:10]]
            },
            'keyword_research': {
                'total_keywords': len(keywords),
                'total_clusters': len(clusters),
                'total_search_volume': sum(c.total_volume for c in clusters)
            },
            'top_opportunities': [
                {
                    'topic': c.topic,
                    'primary_keyword': c.primary_keyword.term,
                    'search_volume': c.total_volume,
                    'difficulty': round(c.avg_difficulty, 1),
                    'content_ideas': c.content_opportunities
                }
                for c in clusters[:10]
            ],
            'content_calendar_preview': calendar.head(20).to_dict('records')
        }
        
        # Save report
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Also save calendar as CSV
        calendar_path = output_path.parent / f"content_calendar_{datetime.now().strftime('%Y%m%d')}.csv"
        calendar.to_csv(calendar_path, index=False)
        
        logger.success(f"Generated SEO report: {output_path}")
        logger.success(f"Generated content calendar: {calendar_path}")
        
        return output_path


# Example usage
if __name__ == "__main__":
    seo = SEOAutomation()

    # Generate comprehensive strategy
    report_path = seo.generate_seo_report()
    print(f"\n✅ SEO strategy report generated: {report_path}")

    # Analyze current performance if GSC data available
    try:
        pages_csv = config.gsc_pages_csv
        queries_csv = config.gsc_queries_csv

        if pages_csv.exists() and queries_csv.exists():
            analysis = seo.analyze_current_performance(pages_csv, queries_csv)
            print(f"\n📊 Current Performance:")
            print(f"Total Clicks: {analysis['total_clicks']:,}")
            print(f"Total Impressions: {analysis['total_impressions']:,}")
            print(f"Average CTR: {analysis['avg_ctr']:.2f}%")
            print(f"Average Position: {analysis['avg_position']:.1f}")
            print(f"\n💡 Found {len(analysis['opportunities'])} optimization opportunities")
    except Exception as e:
        print(f"Note: Could not analyze current performance: {e}")
