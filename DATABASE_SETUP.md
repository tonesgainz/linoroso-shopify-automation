# 🗄️ MySQL Database Setup for Linoroso Automation

## Overview

The Linoroso automation system uses MySQL to track:
- Generated content and performance
- SEO keywords and rankings
- Product optimizations
- Task execution logs
- Analytics data
- Social media posts

## Option 1: Install MySQL Locally (Recommended for Development)

### Install MySQL on Mac

```bash
# Install via Homebrew
brew install mysql

# Start MySQL service
brew services start mysql

# Secure installation (set root password)
mysql_secure_installation
```

### Create Database

```bash
# Login to MySQL
mysql -u root -p

# Run the schema file
source database/schema.sql

# Or manually:
# CREATE DATABASE linoroso_automation;
# USE linoroso_automation;
# Then paste the schema contents
```

### Update .env File

```bash
DB_HOST=localhost
DB_PORT=3306
DB_NAME=linoroso_automation
DB_USER=root
DB_PASSWORD=your_mysql_password
```

## Option 2: Use Docker (Easiest)

### Start MySQL Container

```bash
# Create and start MySQL container
docker run -d \
  --name linoroso-mysql \
  -e MYSQL_ROOT_PASSWORD=linoroso2024 \
  -e MYSQL_DATABASE=linoroso_automation \
  -p 3306:3306 \
  mysql:8.0

# Wait for MySQL to start (about 30 seconds)
sleep 30

# Import schema
docker exec -i linoroso-mysql mysql -uroot -plinoroso2024 linoroso_automation < database/schema.sql
```

### Update .env File

```bash
DB_HOST=localhost
DB_PORT=3306
DB_NAME=linoroso_automation
DB_USER=root
DB_PASSWORD=linoroso2024
```

## Option 3: Use Cloud Database (Production)

### PlanetScale (Recommended - Free Tier Available)

1. Sign up at https://planetscale.com/
2. Create new database: `linoroso-automation`
3. Get connection string
4. Update .env:

```bash
DB_HOST=your-db.planetscale.com
DB_PORT=3306
DB_NAME=linoroso_automation
DB_USER=your_username
DB_PASSWORD=your_password
```

### AWS RDS MySQL

1. Create RDS MySQL instance
2. Configure security groups
3. Update .env with RDS endpoint

### Other Options

- **Railway**: https://railway.app/
- **DigitalOcean Managed Database**: https://www.digitalocean.com/products/managed-databases
- **Google Cloud SQL**: https://cloud.google.com/sql

## Database Schema Overview

### Core Tables

**Content Management:**
- `generated_content` - All AI-generated content
- `content_performance` - Content metrics and analytics
- `content_calendar` - Editorial calendar

**SEO & Keywords:**
- `keywords` - Keyword research and tracking
- `keyword_rankings` - Historical ranking data
- `seo_audits` - SEO audit results

**Products:**
- `product_optimizations` - Product listing improvements
- `product_performance` - Product metrics

**Automation:**
- `task_execution_log` - Task history and status
- `scheduled_tasks` - Automated task configuration

**Analytics:**
- `traffic_analytics` - Website traffic data
- `social_media_posts` - Social media tracking
- `api_usage` - API cost tracking

## Verify Installation

```bash
# Test database connection
python3 -c "
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

try:
    conn = pymysql.connect(
        host=os.getenv('DB_HOST'),
        port=int(os.getenv('DB_PORT', 3306)),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )
    print('✓ Database connection successful!')
    
    cursor = conn.cursor()
    cursor.execute('SHOW TABLES')
    tables = cursor.fetchall()
    print(f'✓ Found {len(tables)} tables')
    
    conn.close()
except Exception as e:
    print(f'✗ Database connection failed: {e}')
"
```

## Database Maintenance

### Backup Database

```bash
# Local backup
mysqldump -u root -p linoroso_automation > backup_$(date +%Y%m%d).sql

# Docker backup
docker exec linoroso-mysql mysqldump -uroot -plinoroso2024 linoroso_automation > backup_$(date +%Y%m%d).sql
```

### Restore Database

```bash
# Local restore
mysql -u root -p linoroso_automation < backup_20241110.sql

# Docker restore
docker exec -i linoroso-mysql mysql -uroot -plinoroso2024 linoroso_automation < backup_20241110.sql
```

### Monitor Database Size

```bash
mysql -u root -p -e "
SELECT 
    table_schema AS 'Database',
    ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS 'Size (MB)'
FROM information_schema.tables
WHERE table_schema = 'linoroso_automation'
GROUP BY table_schema;
"
```

## Optional: Database GUI Tools

- **MySQL Workbench**: https://www.mysql.com/products/workbench/
- **TablePlus**: https://tableplus.com/
- **DBeaver**: https://dbeaver.io/
- **phpMyAdmin**: Web-based interface

## Troubleshooting

### Can't Connect to MySQL

```bash
# Check if MySQL is running
brew services list  # Mac
sudo systemctl status mysql  # Linux

# Check port is open
lsof -i :3306

# Test connection
mysql -u root -p -h localhost
```

### Permission Denied

```bash
# Grant permissions
mysql -u root -p
GRANT ALL PRIVILEGES ON linoroso_automation.* TO 'root'@'localhost';
FLUSH PRIVILEGES;
```

### Docker Container Issues

```bash
# Check container status
docker ps -a

# View logs
docker logs linoroso-mysql

# Restart container
docker restart linoroso-mysql

# Remove and recreate
docker rm -f linoroso-mysql
# Then run the docker run command again
```

## Next Steps

After database setup:

1. ✅ Verify connection with test script above
2. ✅ Run: `python3 test_setup.py` to verify full setup
3. ✅ Start generating content: `python3 content_engine.py`
4. ✅ Check database for stored content

## Database is Optional

**Note:** The database is optional for basic functionality. The automation can work without it by:
- Saving content to files
- Using CSV for tracking
- Storing data in JSON files

To run without database, comment out database-related code in the scripts.
