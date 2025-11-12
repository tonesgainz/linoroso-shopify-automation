# Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### Step 1: Install Dependencies
```bash
# Activate virtual environment
source venv/bin/activate

# Install/upgrade all dependencies
pip install -r requirements.txt
```

### Step 2: Configure Environment
```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your API keys
# Required:
# - ANTHROPIC_API_KEY
# - SHOPIFY_ACCESS_TOKEN
# - MYSQL_PASSWORD
```

### Step 3: Initialize Database
```bash
# Make sure MySQL/MariaDB is running (Docker or local)
# Option 1: Start MySQL with Docker
./start_mysql_docker.sh

# Option 2: Use existing MySQL
# Just ensure MySQL is running and credentials in .env are correct

# Initialize database schema
python database/migrations.py init
```

### Step 4: Verify Setup
```bash
# Run tests to verify everything works
pytest

# Verify database
python database/migrations.py verify

# Test imports
python -c "import main, content_engine, optimizer; print('✅ All modules working')"
```

### Step 5: Run Your First Task
```bash
# Generate a blog post (manual mode)
python main.py --mode manual --task content

# Or run in scheduler mode for automated tasks
python main.py --mode scheduler
```

---

## 📋 Common Tasks

### Generate Content
```bash
# Generate blog post
python content_engine.py

# Generate SEO report
python seo_engine.py

# Optimize products
python optimizer.py
```

### Database Management
```bash
# Initialize database
python database/migrations.py init

# Check database status
python database/migrations.py verify

# Reset database (DANGER - deletes all data!)
python database/migrations.py reset --confirm
```

### Testing
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_content_engine.py -v

# Run with coverage report
pytest --cov=. --cov-report=html
open htmlcov/index.html
```

### Running Automation
```bash
# Run specific task manually
python main.py --mode manual --task content
python main.py --mode manual --task seo_audit
python main.py --mode manual --task product_optimization

# Run all tasks
python main.py --mode manual --task all

# Run scheduler (automated mode)
python main.py --mode scheduler
```

---

## 🔧 Configuration

### Required Environment Variables
```env
ANTHROPIC_API_KEY=your_key_here           # Claude API key
SHOPIFY_ACCESS_TOKEN=your_token_here      # Shopify API token
MYSQL_PASSWORD=your_password              # Database password
```

### Optional but Recommended
```env
SERPAPI_KEY=your_key                      # For keyword research
KLAVIYO_API_KEY=your_key                  # For email marketing
SLACK_WEBHOOK_URL=your_url                # For notifications
```

### File Paths (Customizable)
```env
GSC_PAGES_CSV=./data/gsc/Pages.csv
GSC_QUERIES_CSV=./data/gsc/Queries.csv
PRODUCTS_CSV=./data/shopify/products_export.csv
```

---

## 📁 Project Structure

```
linoroso-shopify/
├── main.py                    # Main automation orchestrator
├── content_engine.py          # AI content generation
├── seo_engine.py              # SEO analysis & optimization
├── optimizer.py               # Product listing optimizer
├── settings.py                # Configuration management
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (create from .env.example)
│
├── utils/                     # Utility modules
│   ├── __init__.py
│   └── error_handling.py      # Error handling & retry logic
│
├── database/                  # Database files
│   ├── schema.sql             # Database schema
│   └── migrations.py          # Migration management
│
├── tests/                     # Unit tests
│   ├── test_content_engine.py
│   ├── test_error_handling.py
│   └── test_settings.py
│
├── data/                      # Data storage
│   ├── generated_content/     # Generated blog posts
│   ├── gsc/                   # Google Search Console data
│   └── shopify/               # Shopify exports
│
└── logs/                      # Application logs
    ├── automation_*.log
    └── execution_log.json
```

---

## 🐛 Troubleshooting

### Import Errors
```bash
# Make sure you're in virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Database Connection Errors
```bash
# Check MySQL is running
mysql -u root -p

# Verify credentials in .env
cat .env | grep MYSQL

# Test connection
python -c "from settings import config; print(config.database.connection_string)"
```

### API Errors
```bash
# Verify API keys are set
python -c "from settings import config; print('Claude API Key:', 'SET' if config.claude.api_key else 'MISSING')"

# Check rate limits
# Built-in rate limiter set to 50 requests/minute
# Adjust in content_engine.py if needed
```

### Test Failures
```bash
# Run tests with verbose output
pytest -v

# Run specific failing test
pytest tests/test_content_engine.py::TestContentGenerator::test_initialization -v

# Skip slow tests
pytest -m "not slow"
```

---

## 💡 Tips & Best Practices

### 1. Start Small
Don't run all automation at once. Start with:
```bash
# Test content generation first
python main.py --mode manual --task content
```

### 2. Monitor Logs
```bash
# Watch logs in real-time
tail -f logs/automation_*.log
```

### 3. Use Rate Limiting
The system has built-in rate limiting (50 req/min). If you need to adjust:
```python
# In content_engine.py, line 73
self.rate_limiter = RateLimiter(requests_per_minute=30)  # Slower
```

### 4. Database Backups
```bash
# Backup database before major changes
mysqldump -u root -p linoroso_automation > backup.sql

# Restore if needed
mysql -u root -p linoroso_automation < backup.sql
```

### 5. Error Handling
All API calls have automatic retry with exponential backoff:
- Retries: 3 times
- Delays: 1s → 2s → 4s → 8s

### 6. Content Review
Generated content is saved as drafts by default. Review before publishing:
```bash
# Check generated content
ls -la data/generated_content/
```

---

## 📊 Monitoring

### Check Automation Status
```bash
# View execution log
cat logs/execution_log.json | jq '.[-5:]'  # Last 5 executions

# View alerts
cat logs/alerts.log
```

### Database Queries
```sql
-- Recent content performance
SELECT * FROM v_content_performance_summary LIMIT 10;

-- Top keywords
SELECT * FROM top_keywords LIMIT 20;

-- Upcoming content
SELECT * FROM upcoming_content;

-- Automation runs
SELECT * FROM automation_runs ORDER BY started_at DESC LIMIT 10;
```

---

## 🎯 Next Steps

1. **Review generated content** in `data/generated_content/`
2. **Monitor automation logs** in `logs/`
3. **Adjust settings** in `.env` as needed
4. **Add more keywords** to SEO engine
5. **Schedule regular runs** using cron or systemd

---

## 📞 Support

- **Documentation**: See [IMPROVEMENTS_SUMMARY.md](IMPROVEMENTS_SUMMARY.md)
- **Issues**: Check logs in `logs/`
- **Contact**: tony@linoroso.com

---

**Last Updated**: November 10, 2025
**Version**: 2.0
