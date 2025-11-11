#!/bin/bash

# ============================================
# Linoroso Database Setup Script
# ============================================

echo "🗄️  Linoroso MySQL Database Setup"
echo "===================================="
echo ""

# Check if MySQL is installed
if ! command -v mysql &> /dev/null; then
    echo "❌ MySQL is not installed"
    echo ""
    echo "Choose installation method:"
    echo "1. Install via Homebrew (recommended)"
    echo "2. Use Docker (easiest)"
    echo "3. Skip and use cloud database"
    echo ""
    read -p "Enter choice (1-3): " choice
    
    case $choice in
        1)
            echo "📦 Installing MySQL via Homebrew..."
            brew install mysql
            brew services start mysql
            echo "✓ MySQL installed and started"
            echo ""
            echo "⚠️  Run 'mysql_secure_installation' to set root password"
            ;;
        2)
            echo "🐳 Setting up MySQL with Docker..."
            docker run -d \
              --name linoroso-mysql \
              -e MYSQL_ROOT_PASSWORD=linoroso2024 \
              -e MYSQL_DATABASE=linoroso_automation \
              -p 3306:3306 \
              mysql:8.0
            
            echo "⏳ Waiting for MySQL to start (30 seconds)..."
            sleep 30
            
            echo "✓ MySQL container started"
            echo ""
            echo "Database credentials:"
            echo "  Host: localhost"
            echo "  Port: 3306"
            echo "  Database: linoroso_automation"
            echo "  User: root"
            echo "  Password: linoroso2024"
            ;;
        3)
            echo "☁️  Using cloud database"
            echo ""
            echo "Options:"
            echo "- PlanetScale: https://planetscale.com/"
            echo "- Railway: https://railway.app/"
            echo "- AWS RDS: https://aws.amazon.com/rds/"
            echo ""
            echo "See DATABASE_SETUP.md for detailed instructions"
            exit 0
            ;;
        *)
            echo "Invalid choice"
            exit 1
            ;;
    esac
fi

# Check if database exists
echo ""
echo "🔍 Checking database connection..."

read -p "MySQL root password: " -s mysql_password
echo ""

# Test connection
if mysql -u root -p"$mysql_password" -e "SELECT 1" &> /dev/null; then
    echo "✓ MySQL connection successful"
else
    echo "❌ Could not connect to MySQL"
    echo "Please check your password and try again"
    exit 1
fi

# Create database and import schema
echo ""
echo "📊 Creating database and importing schema..."

mysql -u root -p"$mysql_password" < database/schema.sql

if [ $? -eq 0 ]; then
    echo "✓ Database schema imported successfully"
else
    echo "❌ Failed to import schema"
    exit 1
fi

# Update .env file
echo ""
echo "📝 Updating .env file..."

if [ -f .env ]; then
    # Update or add database settings
    if grep -q "DB_HOST=" .env; then
        sed -i '' 's/^DB_HOST=.*/DB_HOST=localhost/' .env
        sed -i '' 's/^DB_PORT=.*/DB_PORT=3306/' .env
        sed -i '' 's/^DB_NAME=.*/DB_NAME=linoroso_automation/' .env
        sed -i '' 's/^DB_USER=.*/DB_USER=root/' .env
        sed -i '' "s/^DB_PASSWORD=.*/DB_PASSWORD=$mysql_password/" .env
    else
        echo "" >> .env
        echo "# Database Configuration" >> .env
        echo "DB_HOST=localhost" >> .env
        echo "DB_PORT=3306" >> .env
        echo "DB_NAME=linoroso_automation" >> .env
        echo "DB_USER=root" >> .env
        echo "DB_PASSWORD=$mysql_password" >> .env
    fi
    echo "✓ .env file updated"
else
    echo "⚠️  .env file not found"
fi

# Test database connection with Python
echo ""
echo "🧪 Testing database connection with Python..."

python3 << 'EOF'
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

try:
    conn = pymysql.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', 3306)),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME', 'linoroso_automation')
    )
    
    cursor = conn.cursor()
    cursor.execute('SHOW TABLES')
    tables = cursor.fetchall()
    
    print(f'✓ Database connection successful!')
    print(f'✓ Found {len(tables)} tables')
    
    # List tables
    print('\nTables created:')
    for table in tables:
        print(f'  - {table[0]}')
    
    conn.close()
    
except Exception as e:
    print(f'✗ Database connection failed: {e}')
    exit(1)
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Database setup complete!"
    echo ""
    echo "Next steps:"
    echo "1. Run: python3 test_setup.py"
    echo "2. Start generating content: python3 content_engine.py"
    echo "3. Check database for stored data"
else
    echo ""
    echo "❌ Database setup failed"
    echo "See DATABASE_SETUP.md for manual setup instructions"
    exit 1
fi
