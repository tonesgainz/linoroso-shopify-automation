# Linoroso Shopify Marketing Automation - Quick Start Guide

## 🚀 Getting Started in 15 Minutes

This guide will help you set up and run your first automation tasks.

### Prerequisites

- Python 3.9 or higher
- MySQL database (for tracking and analytics)
- Anthropic API key (Claude)
- Shopify store credentials

### Step 1: Installation (5 minutes)

```bash
# Clone or extract the project
cd linoroso-shopify-automation

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configuration (5 minutes)

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials
# At minimum, you need:
# - ANTHROPIC_API_KEY
# - SHOPIFY_STORE_URL
# - SHOPIFY_ACCESS_TOKEN
```

#### Getting Your API Keys

**Anthropic API Key:**
1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Navigate to API Keys
4. Create a new key and copy it to `.env`

**Shopify Credentials:**
1. Log in to your Shopify admin
2. Go to Settings → Apps and sales channels → Develop apps
3. Create a private app with permissions:
   - Products: Read and write
   - Orders: Read
   - Analytics: Read
4. Copy the API credentials to `.env`

### Step 3: First Run (5 minutes)

#### Test Content Generation

```bash
# Generate a sample blog post
python src/content_generation/content_engine.py
```

This will create a sample blog post in `data/generated_content/`

#### Run SEO Analysis

```bash
# Generate SEO strategy report
python src/seo_automation/seo_engine.py
```

Check `reports/` folder for the generated strategy.

#### Optimize Product Listings

```bash
# Optimize your products
python src/product_optimizer/optimizer.py
```

This reads your products CSV and generates optimized versions.

### Step 4: Run Full Automation

```bash
# Manual run of all tasks
python main.py --mode manual --task all

# Or run specific tasks
python main.py --mode manual --task content
python main.py --mode manual --task seo_audit
python main.py --mode manual --task product_optimization

# Run continuous automation (scheduled)
python main.py --mode scheduler
```

## 📋 Common Tasks

### Generate Blog Content

```python
from src.content_generation.content_engine import ContentGenerator

generator = ContentGenerator()

# Generate blog post
post = generator.generate_blog_post(
    topic="10 Essential Kitchen Knife Techniques",
    keywords=["knife skills", "kitchen techniques", "cooking tips"],
    word_count=1200
)

# Save to file
generator.save_content(post)
```

### Optimize Products

```python
from src.product_optimizer.optimizer import ProductOptimizer
from pathlib import Path

optimizer = ProductOptimizer()

# Optimize all products from CSV
results = optimizer.optimize_all_products(
    csv_path=Path("data/products.csv")
)

# Generate report
optimizer.generate_optimization_report(results)

# Create Shopify import CSV
optimizer.create_shopify_import_csv(
    results, 
    output_path=Path("data/optimized_products.csv")
)
```

### Run SEO Research

```python
from src.seo_automation.seo_engine import SEOAutomation

seo = SEOAutomation()

# Research keywords
keywords = seo.research_keywords([
    "kitchen knives",
    "chef knife",
    "knife set"
])

# Create content calendar
clusters = seo.cluster_keywords(keywords)
calendar = seo.generate_content_calendar(clusters, months=12)

# Save calendar
calendar.to_csv("content_calendar.csv", index=False)
```

### Generate Social Media Posts

```python
from src.content_generation.content_engine import ContentGenerator

generator = ContentGenerator()

# Generate Instagram post
instagram_post = generator.generate_social_post(
    topic="Quick knife sharpening tip",
    keywords=["knife care", "kitchen tips"],
    platform="instagram"
)

print(instagram_post['caption'])
print(instagram_post['hashtags'])
```

## 🎯 Recommended Workflow

### Week 1: Setup and Testing

1. **Day 1-2**: Installation and configuration
2. **Day 3-4**: Generate 5-10 blog posts to build content library
3. **Day 5-6**: Optimize all product listings
4. **Day 7**: Review and manually post best content

### Week 2-4: Automation

1. Enable daily content generation (2 AM PST)
2. Schedule social media posts
3. Monitor SEO performance weekly
4. Adjust strategy based on results

### Monthly Routine

1. **Week 1**: Review previous month's performance
2. **Week 2**: Update content calendar based on trends
3. **Week 3**: Refresh product listings
4. **Week 4**: Generate quarterly strategy report

## 📊 Measuring Success

### Key Metrics to Track

1. **Organic Traffic**: Target 10x growth over 12 months
2. **Content Output**: 50-100 pieces per month
3. **SEO Rankings**: Track keyword positions weekly
4. **Conversion Rate**: Monitor and optimize
5. **Revenue Impact**: $350K-450K additional annual revenue goal

### Access Your Dashboards

```bash
# Generate performance dashboard
python scripts/dashboard.py

# View in browser at http://localhost:8000
```

## 🆘 Troubleshooting

### Issue: "API key not found"
**Solution**: Ensure `.env` file exists and contains `ANTHROPIC_API_KEY=your_key_here`

### Issue: "Module not found"
**Solution**: Make sure you're in the virtual environment and dependencies are installed:
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Issue: "Database connection error"
**Solution**: Check MySQL is running and credentials in `.env` are correct

### Issue: "Rate limit exceeded"
**Solution**: Claude API has rate limits. Adjust `API_RATE_LIMIT` in `.env` or upgrade your API plan

## 🔧 Advanced Configuration

### Custom Content Topics

Edit `config/content_topics.yaml` to define your content themes:

```yaml
blog_topics:
  - category: "Knife Skills"
    keywords: ["knife techniques", "cutting skills"]
    frequency: weekly
  
  - category: "Meal Prep"
    keywords: ["meal prep", "batch cooking"]
    frequency: weekly
```

### Integration with External Tools

#### Connect Google Analytics

```python
# config/analytics_setup.py
GOOGLE_ANALYTICS_PROPERTY_ID = "your_property_id"
```

#### Connect Email Marketing

```python
# config/email_setup.py
KLAVIYO_API_KEY = "your_api_key"
```

## 📚 Next Steps

1. **Read Full Documentation**: Check `/docs` folder for detailed guides
2. **Review Generated Content**: Always review AI-generated content before publishing
3. **Customize Templates**: Modify prompts in content_engine.py for your brand voice
4. **Scale Gradually**: Start with 1-2 blog posts per day, then increase
5. **Monitor Performance**: Use weekly SEO audit to track progress

## 🤝 Support

- **Email**: tony@linoroso.com
- **Documentation**: `/docs` folder
- **Logs**: Check `logs/` folder for detailed execution logs
- **Issues**: Review `logs/errors.log` for troubleshooting

## ✅ Success Checklist

- [ ] Installation complete
- [ ] API keys configured
- [ ] Generated first blog post
- [ ] Optimized first product
- [ ] Created content calendar
- [ ] Set up automation schedule
- [ ] Reviewed generated content quality
- [ ] Published first optimized content
- [ ] Monitoring traffic growth
- [ ] Achieving revenue targets

## 🎉 You're Ready!

Your Linoroso marketing automation is now set up. The system will:

- Generate 50-100 SEO-optimized content pieces monthly
- Optimize all product listings automatically
- Monitor and improve SEO performance
- Track progress toward your 10x traffic growth goal

**Remember**: The system is a tool to amplify your marketing efforts. Always review generated content for brand alignment and accuracy before publishing.

Good luck scaling Linoroso to $5M+ revenue! 🚀
