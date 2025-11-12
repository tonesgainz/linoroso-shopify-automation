# Database Setup & Usage Guide

## ✅ Setup Complete!

Your MySQL database has been successfully configured with 16 tables for comprehensive automation tracking.

---

## 📊 Database Overview

### Connection Details
- **Host**: localhost
- **Port**: 3306
- **Database**: linoroso_automation
- **User**: root
- **Password**: linoroso2024

### Tables Created (16 total)

#### Content Management
- `generated_content` - All generated content (blogs, products, social posts)
- `content_performance` - Performance metrics per content piece
- `content_calendar` - Content scheduling and planning

#### SEO & Keywords
- `keywords` - Keyword research and tracking
- `keyword_rankings` - Historical ranking data

#### Products
- `products` - Product catalog
- `product_optimizations` - Product optimization history
- `product_performance` - Product performance metrics

#### Automation
- `task_execution_log` - Task execution history
- `scheduled_tasks` - Scheduled automation tasks

#### Analytics
- `traffic_analytics` - Website traffic data
- `seo_audits` - SEO audit results
- `social_media_posts` - Social media tracking

#### System
- `system_settings` - Configuration settings
- `api_usage` - API usage tracking

---

## 🚀 Quick Start

### 1. Verify Database
```bash
python database/migrations.py verify
```

Expected output:
```
📊 Database Status:
   Exists: True
   Tables: 16
   Migrations: 1
   Healthy: ✅
```

### 2. Test Database Helper
```bash
python database/db_helper.py
```

### 3. View Dashboard
```bash
python database/db_dashboard.py
```

---

## 💻 Using the Database Helper

### Import the Helper
```python
from database.db_helper import db
```

### Save Generated Content
```python
content_id = db.save_generated_content({
    'content_type': 'blog_post',
    'title': 'My Amazing Blog Post',
    'content': 'Content here...',
    'meta_description': 'Description',
    'keywords': ['seo', 'marketing'],
    'word_count': 1200,
    'status': 'draft'
})
```

### Get Recent Content
```python
recent = db.get_recent_content(limit=10)
for content in recent:
    print(f"{content['title']} - {content['status']}")
```

### Save Keywords
```python
keyword_id = db.save_keyword({
    'keyword': 'kitchen knives',
    'search_volume': 50000,
    'competition': 'medium',
    'difficulty_score': 65,
    'category': 'products'
})
```

### Track Task Execution
```python
# Start task
task_id = db.start_task_execution(
    'content_generation',
    'content_generation'
)

# ... do work ...

# Complete task
db.complete_task_execution(
    task_id,
    status='completed',
    items_processed=5
)
```

### Log API Usage
```python
db.log_api_usage(
    'claude',
    'messages.create',
    request_count=1,
    tokens_used=1500,
    cost=0.045
)
```

### System Settings
```python
# Set setting
db.set_setting('auto_publish', True)

# Get setting
auto_publish = db.get_setting('auto_publish')
```

---

## 📊 Database Dashboard

### Interactive Dashboard
Launch the interactive dashboard:
```bash
python database/db_dashboard.py
```

Features:
- 📊 Database statistics
- 📝 Recent content list
- 🔍 Top keywords
- ⚙️ Task execution history
- 🔌 API usage tracking
- 📈 Content performance
- ⚙️ System settings

---

## 🔧 Database Management

### Initialize/Reset Database
```bash
# Initialize (safe - creates if not exists)
python database/migrations.py init

# Reset (DANGEROUS - deletes all data)
python database/migrations.py reset --confirm
```

### Manual SQL Queries
```bash
# Connect to database
mysql -u root -plinoroso2024 linoroso_automation

# Common queries
SELECT * FROM generated_content ORDER BY created_at DESC LIMIT 10;
SELECT * FROM task_execution_log ORDER BY start_time DESC LIMIT 10;
SELECT * FROM api_usage ORDER BY date DESC;
```

### Backup Database
```bash
# Create backup
mysqldump -u root -plinoroso2024 linoroso_automation > backup_$(date +%Y%m%d).sql

# Restore from backup
mysql -u root -plinoroso2024 linoroso_automation < backup_20251110.sql
```

---

## 📈 Useful Queries

### Content Performance
```sql
SELECT
    gc.title,
    gc.content_type,
    SUM(cp.views) as total_views,
    SUM(cp.clicks) as total_clicks,
    SUM(cp.conversions) as conversions
FROM generated_content gc
LEFT JOIN content_performance cp ON gc.id = cp.content_id
GROUP BY gc.id
ORDER BY total_views DESC
LIMIT 10;
```

### API Usage Summary
```sql
SELECT
    api_name,
    SUM(request_count) as total_requests,
    SUM(tokens_used) as total_tokens,
    SUM(cost) as total_cost
FROM api_usage
WHERE date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
GROUP BY api_name;
```

### Task Success Rate
```sql
SELECT
    task_type,
    status,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY task_type), 2) as percentage
FROM task_execution_log
GROUP BY task_type, status
ORDER BY task_type, count DESC;
```

### Keyword Ranking Trends
```sql
SELECT
    k.keyword,
    kr.date,
    kr.rank_position,
    LAG(kr.rank_position) OVER (PARTITION BY k.id ORDER BY kr.date) as previous_rank
FROM keywords k
JOIN keyword_rankings kr ON k.id = kr.keyword_id
WHERE kr.date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
ORDER BY k.keyword, kr.date DESC;
```

---

## 🔌 Integration Examples

### Use in Content Engine
```python
from database.db_helper import db
from content_engine import ContentGenerator

generator = ContentGenerator()

# Generate content
content = generator.generate_blog_post(
    topic='Knife Maintenance',
    keywords=['knife', 'maintenance', 'care']
)

# Save to database
content_id = db.save_generated_content({
    'content_type': 'blog_post',
    'title': content.title,
    'content': content.content,
    'meta_description': content.meta_description,
    'keywords': content.keywords,
    'word_count': content.word_count,
    'status': 'draft'
})

print(f"✅ Saved content ID: {content_id}")
```

### Use in Main Automation
```python
from database.db_helper import db

class LinorosoAutomation:
    def run_daily_content_generation(self):
        # Start task logging
        task_id = db.start_task_execution(
            'daily_content_generation',
            'content_generation'
        )

        try:
            # ... generate content ...

            # Complete task
            db.complete_task_execution(
                task_id,
                status='completed',
                items_processed=generated_count
            )

        except Exception as e:
            # Log failure
            db.complete_task_execution(
                task_id,
                status='failed',
                error_message=str(e)
            )
            raise
```

---

## 🎯 Best Practices

### 1. Always Use Context Managers
```python
# Good
with db.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")

# Bad - connection might not close
conn = db.get_connection()
cursor = conn.cursor()
```

### 2. Log All API Calls
```python
# After every API call
db.log_api_usage('claude', 'messages.create', tokens_used=1000, cost=0.03)
```

### 3. Track All Task Executions
```python
# Start, work, complete pattern
task_id = db.start_task_execution('my_task', 'task_type')
# ... do work ...
db.complete_task_execution(task_id, 'completed', items_processed=10)
```

### 4. Regular Backups
```bash
# Add to crontab for daily backups
0 2 * * * mysqldump -u root -plinoroso2024 linoroso_automation > /backups/db_$(date +\%Y\%m\%d).sql
```

### 5. Monitor Performance
```python
# Check API costs regularly
api_summary = db.get_api_usage_summary(days=7)
for api in api_summary:
    if api['total_cost'] > 100:
        print(f"⚠️ High API costs: {api['api_name']} = ${api['total_cost']}")
```

---

## 🚨 Troubleshooting

### Connection Errors
```bash
# Check MySQL is running
brew services list | grep mysql

# Restart if needed
brew services restart mysql

# Test connection
mysql -u root -plinoroso2024 -e "SELECT 1"
```

### Permission Errors
```sql
-- Grant all permissions to root user
GRANT ALL PRIVILEGES ON linoroso_automation.* TO 'root'@'localhost';
FLUSH PRIVILEGES;
```

### Slow Queries
```sql
-- Check slow queries
SHOW PROCESSLIST;

-- Analyze table
ANALYZE TABLE generated_content;

-- Check indexes
SHOW INDEX FROM generated_content;
```

---

## 📚 Additional Resources

### MySQL Documentation
- [MySQL 8.0 Reference](https://dev.mysql.com/doc/refman/8.0/en/)
- [PyMySQL Documentation](https://pymysql.readthedocs.io/)

### Database Design
- [Database Normalization](https://www.guru99.com/database-normalization.html)
- [MySQL Performance Tuning](https://dev.mysql.com/doc/refman/8.0/en/optimization.html)

### Monitoring Tools
- **MySQL Workbench**: GUI tool for database management
- **phpMyAdmin**: Web-based MySQL administration
- **Adminer**: Lightweight database management

---

## ✅ Next Steps

1. **Integrate with Main App**: Update main.py to use db_helper
2. **Set Up Monitoring**: Use dashboard to track automation
3. **Configure Backups**: Set up automated database backups
4. **Optimize Queries**: Add indexes as needed for performance
5. **Create Reports**: Build custom analytics queries

---

## 🎉 Summary

You now have:
- ✅ 16-table production database
- ✅ Python helper utilities for easy database access
- ✅ Interactive dashboard for viewing data
- ✅ Migration system for schema updates
- ✅ Complete documentation and examples

Your database is ready to support full automation operations!

---

**Created**: November 11, 2025
**Version**: 1.0
**Status**: Production Ready
