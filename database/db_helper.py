"""
Database Helper Utilities
Provides convenient database operations for the automation system
"""

import pymysql
from typing import List, Dict, Optional, Any
from datetime import datetime, date
from contextlib import contextmanager
from loguru import logger
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from settings import config


class DatabaseHelper:
    """Helper class for database operations"""

    def __init__(self):
        self.db_config = {
            'host': config.database.host,
            'port': config.database.port,
            'user': config.database.user,
            'password': config.database.password,
            'database': config.database.database,
            'charset': 'utf8mb4',
            'cursorclass': pymysql.cursors.DictCursor
        }

    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = None
        try:
            conn = pymysql.connect(**self.db_config)
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def execute_query(self, query: str, params: tuple = None) -> List[Dict]:
        """Execute a SELECT query and return results"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            return cursor.fetchall()

    def execute_update(self, query: str, params: tuple = None) -> int:
        """Execute an INSERT/UPDATE/DELETE query and return affected rows"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            return cursor.rowcount

    def insert_and_get_id(self, query: str, params: tuple = None) -> int:
        """Execute an INSERT query and return the last insert ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            return cursor.lastrowid

    # ============================================
    # CONTENT MANAGEMENT
    # ============================================

    def save_generated_content(self, content_data: Dict) -> int:
        """Save generated content to database"""
        query = """
            INSERT INTO generated_content
            (content_type, title, content, meta_description, keywords,
             word_count, seo_score, status, platform, metadata)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            content_data.get('content_type', 'blog_post'),
            content_data.get('title'),
            content_data.get('content'),
            content_data.get('meta_description'),
            json.dumps(content_data.get('keywords', [])),
            content_data.get('word_count', 0),
            content_data.get('seo_score'),
            content_data.get('status', 'draft'),
            content_data.get('platform'),
            json.dumps(content_data.get('metadata', {}))
        )

        content_id = self.insert_and_get_id(query, params)
        logger.success(f"Saved content with ID: {content_id}")
        return content_id

    def get_content_by_id(self, content_id: int) -> Optional[Dict]:
        """Get content by ID"""
        query = "SELECT * FROM generated_content WHERE id = %s"
        results = self.execute_query(query, (content_id,))
        return results[0] if results else None

    def get_recent_content(self, limit: int = 10, content_type: str = None) -> List[Dict]:
        """Get recent generated content"""
        if content_type:
            query = """
                SELECT * FROM generated_content
                WHERE content_type = %s
                ORDER BY created_at DESC
                LIMIT %s
            """
            return self.execute_query(query, (content_type, limit))
        else:
            query = """
                SELECT * FROM generated_content
                ORDER BY created_at DESC
                LIMIT %s
            """
            return self.execute_query(query, (limit,))

    def update_content_status(self, content_id: int, status: str) -> int:
        """Update content status"""
        query = "UPDATE generated_content SET status = %s WHERE id = %s"
        return self.execute_update(query, (status, content_id))

    # ============================================
    # KEYWORDS
    # ============================================

    def save_keyword(self, keyword_data: Dict) -> int:
        """Save keyword to database"""
        query = """
            INSERT INTO keywords
            (keyword, search_volume, competition, cpc, difficulty_score,
             category, current_rank, target_rank, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                search_volume = VALUES(search_volume),
                competition = VALUES(competition),
                cpc = VALUES(cpc),
                difficulty_score = VALUES(difficulty_score),
                updated_at = CURRENT_TIMESTAMP
        """
        params = (
            keyword_data.get('keyword'),
            keyword_data.get('search_volume'),
            keyword_data.get('competition'),
            keyword_data.get('cpc'),
            keyword_data.get('difficulty_score'),
            keyword_data.get('category'),
            keyword_data.get('current_rank'),
            keyword_data.get('target_rank'),
            keyword_data.get('status', 'researching')
        )

        return self.insert_and_get_id(query, params)

    def get_top_keywords(self, limit: int = 50) -> List[Dict]:
        """Get top keywords by search volume"""
        query = """
            SELECT * FROM keywords
            ORDER BY search_volume DESC
            LIMIT %s
        """
        return self.execute_query(query, (limit,))

    def save_keyword_ranking(self, keyword_id: int, rank_position: int,
                            page_url: str = None, search_volume: int = None) -> int:
        """Save keyword ranking data"""
        query = """
            INSERT INTO keyword_rankings
            (keyword_id, rank_position, page_url, search_volume, date)
            VALUES (%s, %s, %s, %s, %s)
        """
        params = (keyword_id, rank_position, page_url, search_volume, date.today())
        return self.insert_and_get_id(query, params)

    # ============================================
    # PRODUCTS
    # ============================================

    def save_product(self, product_data: Dict) -> int:
        """Save or update product"""
        query = """
            INSERT INTO products
            (shopify_id, handle, title, description, vendor, product_type,
             price, sku, tags, images, seo_title, seo_description, seo_score)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                title = VALUES(title),
                description = VALUES(description),
                price = VALUES(price),
                seo_title = VALUES(seo_title),
                seo_description = VALUES(seo_description),
                seo_score = VALUES(seo_score),
                updated_at = CURRENT_TIMESTAMP
        """
        params = (
            product_data.get('shopify_id'),
            product_data.get('handle'),
            product_data.get('title'),
            product_data.get('description'),
            product_data.get('vendor', 'Linoroso'),
            product_data.get('product_type'),
            product_data.get('price'),
            product_data.get('sku'),
            json.dumps(product_data.get('tags', [])),
            json.dumps(product_data.get('images', [])),
            product_data.get('seo_title'),
            product_data.get('seo_description'),
            product_data.get('seo_score')
        )

        return self.insert_and_get_id(query, params)

    def get_product_by_handle(self, handle: str) -> Optional[Dict]:
        """Get product by handle"""
        query = "SELECT * FROM products WHERE handle = %s"
        results = self.execute_query(query, (handle,))
        return results[0] if results else None

    def save_product_optimization(self, optimization_data: Dict) -> int:
        """Save product optimization record"""
        query = """
            INSERT INTO product_optimizations
            (product_id, original_title, optimized_title, original_description,
             optimized_description, original_seo_score, optimized_seo_score,
             keywords_added, optimization_date, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            optimization_data.get('product_id'),
            optimization_data.get('original_title'),
            optimization_data.get('optimized_title'),
            optimization_data.get('original_description'),
            optimization_data.get('optimized_description'),
            optimization_data.get('original_seo_score'),
            optimization_data.get('optimized_seo_score'),
            json.dumps(optimization_data.get('keywords_added', [])),
            datetime.now(),
            optimization_data.get('status', 'pending')
        )

        return self.insert_and_get_id(query, params)

    # ============================================
    # AUTOMATION LOGS
    # ============================================

    def start_task_execution(self, task_name: str, task_type: str) -> int:
        """Log the start of a task execution"""
        query = """
            INSERT INTO task_execution_log
            (task_name, task_type, status, start_time)
            VALUES (%s, %s, 'running', %s)
        """
        params = (task_name, task_type, datetime.now())
        task_id = self.insert_and_get_id(query, params)
        logger.info(f"Started task execution: {task_name} (ID: {task_id})")
        return task_id

    def complete_task_execution(self, task_id: int, status: str = 'completed',
                               items_processed: int = 0, error_message: str = None,
                               execution_details: Dict = None) -> int:
        """Log the completion of a task execution"""
        query = """
            UPDATE task_execution_log
            SET status = %s,
                end_time = %s,
                duration_seconds = TIMESTAMPDIFF(SECOND, start_time, %s),
                items_processed = %s,
                error_message = %s,
                execution_details = %s
            WHERE id = %s
        """
        end_time = datetime.now()
        params = (
            status,
            end_time,
            end_time,
            items_processed,
            error_message,
            json.dumps(execution_details) if execution_details else None,
            task_id
        )

        rows = self.execute_update(query, params)
        logger.info(f"Completed task execution ID: {task_id} with status: {status}")
        return rows

    def get_recent_task_executions(self, limit: int = 10) -> List[Dict]:
        """Get recent task executions"""
        query = """
            SELECT * FROM task_execution_log
            ORDER BY start_time DESC
            LIMIT %s
        """
        return self.execute_query(query, (limit,))

    # ============================================
    # API USAGE TRACKING
    # ============================================

    def log_api_usage(self, api_name: str, endpoint: str = None,
                     request_count: int = 1, tokens_used: int = None,
                     cost: float = None) -> int:
        """Log API usage"""
        query = """
            INSERT INTO api_usage
            (api_name, endpoint, request_count, tokens_used, cost, date)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                request_count = request_count + VALUES(request_count),
                tokens_used = COALESCE(tokens_used, 0) + COALESCE(VALUES(tokens_used), 0),
                cost = COALESCE(cost, 0) + COALESCE(VALUES(cost), 0)
        """
        params = (api_name, endpoint, request_count, tokens_used, cost, date.today())
        return self.insert_and_get_id(query, params)

    def get_api_usage_summary(self, days: int = 30) -> List[Dict]:
        """Get API usage summary"""
        query = """
            SELECT
                api_name,
                SUM(request_count) as total_requests,
                SUM(tokens_used) as total_tokens,
                SUM(cost) as total_cost
            FROM api_usage
            WHERE date >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
            GROUP BY api_name
            ORDER BY total_cost DESC
        """
        return self.execute_query(query, (days,))

    # ============================================
    # SYSTEM SETTINGS
    # ============================================

    def get_setting(self, key: str) -> Optional[Any]:
        """Get a system setting value"""
        query = "SELECT setting_value, setting_type FROM system_settings WHERE setting_key = %s"
        results = self.execute_query(query, (key,))

        if not results:
            return None

        result = results[0]
        value = result['setting_value']
        value_type = result['setting_type']

        # Convert based on type
        if value_type == 'boolean':
            return value.lower() in ('true', '1', 'yes')
        elif value_type == 'number':
            return float(value) if '.' in value else int(value)
        elif value_type == 'json':
            return json.loads(value)
        else:
            return value

    def set_setting(self, key: str, value: Any, setting_type: str = 'string',
                   description: str = None) -> int:
        """Set a system setting value"""
        # Convert value to string
        if isinstance(value, bool):
            value_str = 'true' if value else 'false'
            setting_type = 'boolean'
        elif isinstance(value, (int, float)):
            value_str = str(value)
            setting_type = 'number'
        elif isinstance(value, (dict, list)):
            value_str = json.dumps(value)
            setting_type = 'json'
        else:
            value_str = str(value)

        query = """
            INSERT INTO system_settings
            (setting_key, setting_value, setting_type, description)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                setting_value = VALUES(setting_value),
                setting_type = VALUES(setting_type),
                description = COALESCE(VALUES(description), description)
        """
        params = (key, value_str, setting_type, description)
        return self.execute_update(query, params)

    # ============================================
    # ANALYTICS QUERIES
    # ============================================

    def get_content_performance_summary(self, days: int = 30) -> Dict:
        """Get content performance summary"""
        query = """
            SELECT
                COUNT(DISTINCT gc.id) as total_content,
                COUNT(DISTINCT CASE WHEN gc.status = 'published' THEN gc.id END) as published_content,
                COALESCE(SUM(cp.views), 0) as total_views,
                COALESCE(SUM(cp.clicks), 0) as total_clicks,
                COALESCE(SUM(cp.conversions), 0) as total_conversions,
                COALESCE(SUM(cp.revenue), 0) as total_revenue
            FROM generated_content gc
            LEFT JOIN content_performance cp ON gc.id = cp.content_id
                AND cp.date >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
            WHERE gc.created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
        """
        results = self.execute_query(query, (days, days))
        return results[0] if results else {}

    def get_top_performing_content(self, limit: int = 10, metric: str = 'views') -> List[Dict]:
        """Get top performing content"""
        query = f"""
            SELECT
                gc.id,
                gc.title,
                gc.content_type,
                gc.published_date,
                SUM(cp.views) as total_views,
                SUM(cp.clicks) as total_clicks,
                SUM(cp.conversions) as total_conversions,
                SUM(cp.revenue) as total_revenue
            FROM generated_content gc
            INNER JOIN content_performance cp ON gc.id = cp.content_id
            WHERE gc.status = 'published'
            GROUP BY gc.id, gc.title, gc.content_type, gc.published_date
            ORDER BY total_{metric} DESC
            LIMIT %s
        """
        return self.execute_query(query, (limit,))


# Convenience instance
db = DatabaseHelper()


if __name__ == "__main__":
    # Test database connection
    print("Testing database connection...")

    try:
        # Test content save
        content_id = db.save_generated_content({
            'content_type': 'blog_post',
            'title': 'Test Blog Post',
            'content': 'This is test content',
            'meta_description': 'Test description',
            'keywords': ['test', 'sample'],
            'word_count': 10
        })
        print(f"✅ Saved test content with ID: {content_id}")

        # Test content retrieval
        content = db.get_content_by_id(content_id)
        print(f"✅ Retrieved content: {content['title']}")

        # Test recent content
        recent = db.get_recent_content(limit=5)
        print(f"✅ Found {len(recent)} recent content pieces")

        # Test API usage logging
        db.log_api_usage('claude', 'messages.create', tokens_used=500, cost=0.015)
        print("✅ Logged API usage")

        # Test settings
        db.set_setting('test_setting', True, description='Test setting')
        value = db.get_setting('test_setting')
        print(f"✅ Setting test: {value}")

        print("\n✨ All database operations working correctly!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
