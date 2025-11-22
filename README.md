# Linoroso Shopify Marketing Automation

[![CI](https://github.com/tonesgainz/linoroso-shopify-automation/workflows/CI/badge.svg)](https://github.com/tonesgainz/linoroso-shopify-automation/actions)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Comprehensive marketing automation system for Linoroso's multi-channel expansion strategy, focusing on zero ad spend organic growth through SEO, content generation, and conversion optimization.

## 🎯 Project Goals

- **10x organic traffic growth** over 12 months
- Generate **50-100 SEO-optimized content pieces** monthly
- Automate **product listing optimization** across channels
- **Zero ad spend** strategy through organic and earned media
- Target: **$350K-450K additional annual revenue** from organic traffic

## 📁 Project Structure

```
linoroso-shopify-automation/
├── .github/
│   └── workflows/
│       └── ci.yml                # GitHub Actions CI/CD pipeline
├── tests/                        # Comprehensive test suite
│   ├── test_settings.py          # Configuration tests
│   ├── test_content_engine.py    # Content generation tests
│   ├── test_optimizer.py         # Product optimizer tests
│   ├── test_seo_engine.py        # SEO automation tests
│   └── test_main.py              # Orchestration tests
├── logs/                         # Application logs
├── data/                         # Data storage
│   ├── social_posts/             # Generated social media content
│   └── content/                  # Generated blog posts
├── reports/                      # SEO and optimization reports
├── settings.py                   # Configuration management
├── content_engine.py             # AI-powered content generation
├── seo_engine.py                 # SEO automation and keyword research
├── optimizer.py                  # Product listing optimization
├── batch_generate.py             # Batch content generation
├── main.py                       # Main orchestration and scheduling
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment variables template
├── .pre-commit-config.yaml       # Pre-commit hooks configuration
├── pytest.ini                    # Pytest configuration
├── TESTING.md                    # Testing guide
└── README.md                     # This file
```

## 🚀 Key Features

### 1. SEO Content Engine
- Automated blog post generation (kitchen tips, recipes, guides)
- Keyword research and optimization
- Internal linking automation
- Meta description and title tag optimization

### 2. Product Listing Optimizer
- AI-enhanced product descriptions
- SEO-optimized titles and tags
- A/B testing automation
- Cross-channel consistency (Amazon, Walmart, Wayfair)

### 3. Social Media Automation
- Content calendar generation
- Post scheduling for Instagram, TikTok, Pinterest
- User-generated content curation
- Engagement analytics

### 4. Email Marketing Flows
- Welcome series automation
- Cart abandonment recovery
- Post-purchase sequences
- Re-engagement campaigns

### 5. Influencer Program
- Automated outreach campaigns
- Tier-based commission tracking
- Content collection and approval
- Performance analytics

### 6. Analytics Dashboard
- Real-time traffic monitoring
- Conversion tracking
- Channel performance comparison
- ROI calculation

## 🔧 Installation

### Prerequisites

- Python 3.10 or higher
- pip (Python package installer)
- Git

### Setup

```bash
# Clone the repository
git clone https://github.com/tonesgainz/linoroso-shopify-automation.git
cd linoroso-shopify-automation

# Create and activate virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys and configuration
```

### Development Setup

For development with code quality tools:

```bash
# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Run all pre-commit hooks manually
pre-commit run --all-files
```

## ⚙️ Configuration

All configuration is managed through environment variables. Copy `.env.example` to `.env` and configure:

### Required Configuration

1. **Claude API** (Required for content generation)
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   CLAUDE_MODEL=claude-sonnet-4-20250514
   ```

2. **Shopify Integration**
   ```
   SHOPIFY_STORE_URL=your-store.myshopify.com
   SHOPIFY_ACCESS_TOKEN=your_access_token
   SHOPIFY_API_VERSION=2024-01
   ```

3. **Brand Configuration**
   ```
   BRAND_NAME=Linoroso
   BRAND_VOICE=professional, friendly, educational
   MAIN_CATEGORIES=kitchen knives,kitchen shears,knife sets
   ```

### Optional Configuration

- **SEO & Analytics**: SerpAPI, Google Analytics
- **Social Media**: Instagram, TikTok, Pinterest APIs
- **Email Marketing**: Klaviyo API
- **Database**: MySQL connection (optional)

See `.env.example` for complete configuration options with detailed descriptions.

## 📊 Usage

### Automated Scheduling (Production)

Run the automation scheduler for continuous operation:

```bash
# Start the scheduler (runs tasks at scheduled times)
python main.py --mode scheduler
```

This will run:
- **Daily at 2:00 AM**: Content generation (blog posts + social media)
- **Weekly (Monday 9:00 AM)**: SEO audit and performance analysis
- **Monthly (1st at 3:00 AM)**: Product listing optimization

### Manual Task Execution

Run individual tasks on-demand:

```bash
# Generate daily content (blog post + social posts)
python main.py --mode manual --task content

# Run SEO audit and analysis
python main.py --mode manual --task seo_audit

# Optimize product listings
python main.py --mode manual --task product_optimization

# Generate quarterly SEO strategy report
python main.py --mode manual --task strategy

# Run all tasks once
python main.py --mode manual --task all
```

### Module-Specific Usage

#### Content Generation

```bash
# Generate content using content_engine.py
python content_engine.py
```

#### SEO Analysis

```bash
# Generate SEO strategy report
python seo_engine.py
```

#### Product Optimization

```bash
# Optimize products from Shopify CSV export
python optimizer.py
```

#### Batch Content Generation

```bash
# Build initial content library
python batch_generate.py
```

## 🧪 Testing

We maintain comprehensive test coverage for all modules. See [TESTING.md](TESTING.md) for detailed testing guide.

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_content_engine.py

# Run tests with verbose output
pytest -v

# Run specific test function
pytest tests/test_settings.py::TestClaudeConfig::test_valid_config
```

### View Coverage

```bash
# Generate and open HTML coverage report
pytest --cov=. --cov-report=html
open htmlcov/index.html  # On macOS, use 'xdg-open' on Linux
```

## 🛠️ Development

### Code Quality Tools

This project uses several code quality tools configured via pre-commit hooks:

- **black**: Code formatting (line length: 100)
- **isort**: Import sorting
- **flake8**: Linting and style checking
- **mypy**: Static type checking
- **bandit**: Security vulnerability scanning

### Running Code Quality Checks

```bash
# Format code with black
black .

# Sort imports
isort .

# Run linter
flake8 .

# Type checking
mypy .

# Security scan
bandit -r . -ll

# Run all checks (via pre-commit)
pre-commit run --all-files
```

### Continuous Integration

GitHub Actions runs on every push and pull request:

- **Tests**: Python 3.10 and 3.11
- **Linting**: black, flake8, isort, mypy
- **Security**: bandit, safety
- **Coverage**: Uploaded to Codecov

See [.github/workflows/ci.yml](.github/workflows/ci.yml) for details.

## 📚 Module Documentation

### settings.py - Configuration Management

Central configuration module that loads and validates all settings from environment variables.

**Key Classes:**
- `ClaudeConfig`: Claude AI API configuration
- `ShopifyConfig`: Shopify store integration settings
- `BrandConfig`: Brand identity and voice settings
- `ContentConfig`: Content generation parameters
- `SocialMediaConfig`: Social platform credentials
- `EmailConfig`: Email marketing configuration
- `DatabaseConfig`: Optional database connection
- `Config`: Main configuration aggregator

**Usage:**
```python
from settings import config

# Access configuration
api_key = config.claude.api_key
store_url = config.shopify.store_url
brand_name = config.brand.name
```

### content_engine.py - AI Content Generation

Generates SEO-optimized blog posts and social media content using Claude AI.

**Key Classes:**
- `BlogPost`: Dataclass for blog post structure
- `SocialPost`: Dataclass for social media posts
- `ContentGenerator`: Main content generation engine

**Key Methods:**
- `generate_blog_post(topic, keywords, word_count)`: Generate SEO blog post
- `generate_social_post(topic, keywords, platform)`: Generate platform-specific social content
- `generate_product_description(product, keywords)`: Generate product descriptions
- `save_content(content)`: Save generated content to file

**Usage:**
```python
from content_engine import ContentGenerator

generator = ContentGenerator()
post = generator.generate_blog_post(
    topic="5 Essential Knife Skills",
    keywords=["knife skills", "cooking tips"],
    word_count=1200
)
```

### seo_engine.py - SEO Automation

Handles keyword research, clustering, and SEO strategy generation.

**Key Classes:**
- `Keyword`: Keyword data with metrics
- `KeywordCluster`: Grouped keywords by topic
- `SEOAutomation`: SEO analysis and optimization engine

**Key Methods:**
- `research_keywords(seed_keywords, location)`: Research keywords from seeds
- `cluster_keywords(keywords, max_clusters)`: Group keywords into topics
- `generate_content_calendar(clusters, months)`: Create content calendar
- `analyze_current_performance(pages_csv, queries_csv)`: Analyze GSC data
- `generate_seo_report()`: Generate comprehensive SEO strategy

**Usage:**
```python
from seo_engine import SEOAutomation

seo = SEOAutomation()
keywords = seo.research_keywords(["kitchen knives", "chef knife"])
clusters = seo.cluster_keywords(keywords)
calendar = seo.generate_content_calendar(clusters, months=12)
```

### optimizer.py - Product Optimization

Optimizes product listings for SEO and conversion.

**Key Classes:**
- `Product`: Product data structure
- `OptimizationResult`: Optimization results and suggestions
- `ProductOptimizer`: Product listing optimizer

**Key Methods:**
- `analyze_product(product)`: Analyze product for SEO issues
- `optimize_product(product)`: Generate optimized listing
- `optimize_all_products(csv_path)`: Batch optimize from CSV
- `generate_optimization_report(results)`: Create optimization report
- `create_shopify_import_csv(results, output_path)`: Generate import CSV

**Usage:**
```python
from optimizer import ProductOptimizer

optimizer = ProductOptimizer()
results = optimizer.optimize_all_products("products.csv")
optimizer.generate_optimization_report(results)
```

### main.py - Orchestration

Main automation coordinator that schedules and runs all tasks.

**Key Classes:**
- `LinorosoAutomation`: Main orchestration class

**Key Methods:**
- `run_daily_content_generation()`: Generate daily content
- `run_weekly_seo_audit()`: Weekly SEO analysis
- `run_monthly_product_optimization()`: Monthly product updates
- `run_quarterly_strategy_review()`: Quarterly strategy report
- `setup_schedule()`: Configure task schedule
- `run_scheduler()`: Start continuous scheduler
- `run_manual_task(task_name)`: Execute single task

**Usage:**
```python
from main import LinorosoAutomation

automation = LinorosoAutomation()

# Run specific task manually
automation.run_daily_content_generation()

# Or start the scheduler
automation.run_scheduler()
```

## 🎯 Strategic Focus Areas

Based on Linoroso's $3M Amazon revenue and expansion goals:

1. **Protect Amazon Core Business**: Maintain brand consistency while expanding
2. **Channel Differentiation**: Unique content for each platform
3. **Organic Traffic Growth**: SEO-first approach with zero ad spend
4. **Conversion Optimization**: Data-driven listing improvements
5. **Community Building**: User-generated content and influencer partnerships

## 📈 Success Metrics

- **Traffic**: 10x growth in organic visits
- **Conversion**: 380% improvement (matching previous WordPress automation)
- **Revenue**: $350K-450K additional annual revenue from organic
- **Content**: 50-100 pieces monthly
- **CAC Reduction**: Lower customer acquisition costs through organic channels

## 🔐 Security

- All API keys stored in environment variables
- No sensitive data committed to repository
- Regular security audits of dependencies

## 📝 License

Proprietary - Linoroso Brands Inc

## 👥 Team

- **Tony Lo**: Chief Digital Officer
- **Wenya**: TikTok Operations Lead

## 🤝 Support

For questions or issues, contact: tony@linoroso.com
