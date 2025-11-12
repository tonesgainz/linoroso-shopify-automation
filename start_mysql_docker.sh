#!/bin/bash

# ============================================
# Start MySQL with Docker for Linoroso
# ============================================

echo "🐳 Starting MySQL with Docker..."
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "⚠️  Docker is not running"
    echo "Starting Docker Desktop..."
    open -a Docker
    echo "⏳ Waiting for Docker to start (30 seconds)..."
    sleep 30
fi

# Check if container already exists
if docker ps -a --format '{{.Names}}' | grep -q '^linoroso-mysql$'; then
    echo "📦 Container 'linoroso-mysql' already exists"
    
    # Check if it's running
    if docker ps --format '{{.Names}}' | grep -q '^linoroso-mysql$'; then
        echo "✓ Container is already running"
    else
        echo "🔄 Starting existing container..."
        docker start linoroso-mysql
        echo "✓ Container started"
    fi
else
    echo "📦 Creating new MySQL container..."
    docker run -d \
      --name linoroso-mysql \
      -e MYSQL_ROOT_PASSWORD=linoroso2024 \
      -e MYSQL_DATABASE=linoroso_automation \
      -p 3306:3306 \
      mysql:8.0
    
    if [ $? -eq 0 ]; then
        echo "✓ Container created successfully"
        echo "⏳ Waiting for MySQL to initialize (30 seconds)..."
        sleep 30
    else
        echo "❌ Failed to create container"
        exit 1
    fi
fi

# Test MySQL connection
echo ""
echo "🔍 Testing MySQL connection..."

max_attempts=10
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if docker exec linoroso-mysql mysql -uroot -plinoroso2024 -e "SELECT 1" > /dev/null 2>&1; then
        echo "✓ MySQL is ready!"
        break
    else
        attempt=$((attempt + 1))
        echo "⏳ Waiting for MySQL... (attempt $attempt/$max_attempts)"
        sleep 3
    fi
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ MySQL did not start in time"
    exit 1
fi

# Import schema
echo ""
echo "📊 Importing database schema..."

docker exec -i linoroso-mysql mysql -uroot -plinoroso2024 linoroso_automation < database/schema.sql

if [ $? -eq 0 ]; then
    echo "✓ Schema imported successfully"
else
    echo "❌ Failed to import schema"
    exit 1
fi

# Verify tables
echo ""
echo "🔍 Verifying database..."

table_count=$(docker exec linoroso-mysql mysql -uroot -plinoroso2024 linoroso_automation -e "SHOW TABLES" | wc -l)
table_count=$((table_count - 1))  # Subtract header row

echo "✓ Found $table_count tables"

# Update .env file
echo ""
echo "📝 Updating .env file..."

if [ -f .env ]; then
    # Check if DB settings exist
    if grep -q "DB_HOST=" .env; then
        # Update existing settings
        sed -i '' 's/^DB_HOST=.*/DB_HOST=localhost/' .env
        sed -i '' 's/^DB_PORT=.*/DB_PORT=3306/' .env
        sed -i '' 's/^DB_NAME=.*/DB_NAME=linoroso_automation/' .env
        sed -i '' 's/^DB_USER=.*/DB_USER=root/' .env
        sed -i '' 's/^DB_PASSWORD=.*/DB_PASSWORD=linoroso2024/' .env
    else
        # Add new settings
        echo "" >> .env
        echo "# Database Configuration (Docker)" >> .env
        echo "DB_HOST=localhost" >> .env
        echo "DB_PORT=3306" >> .env
        echo "DB_NAME=linoroso_automation" >> .env
        echo "DB_USER=root" >> .env
        echo "DB_PASSWORD=linoroso2024" >> .env
    fi
    echo "✓ .env file updated"
else
    echo "⚠️  .env file not found"
fi

# Test with Python
echo ""
echo "🧪 Testing database connection with Python..."

python3 << 'EOF'
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

try:
    conn = pymysql.connect(
        host='localhost',
        port=3306,
        user='root',
        password='linoroso2024',
        database='linoroso_automation'
    )
    
    cursor = conn.cursor()
    cursor.execute('SHOW TABLES')
    tables = cursor.fetchall()
    
    print(f'✓ Python connection successful!')
    print(f'✓ Database has {len(tables)} tables')
    
    conn.close()
    
except Exception as e:
    print(f'✗ Python connection failed: {e}')
    exit(1)
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 MySQL Docker setup complete!"
    echo ""
    echo "Database Info:"
    echo "  Host: localhost"
    echo "  Port: 3306"
    echo "  Database: linoroso_automation"
    echo "  User: root"
    echo "  Password: linoroso2024"
    echo ""
    echo "Container Management:"
    echo "  Start:   docker start linoroso-mysql"
    echo "  Stop:    docker stop linoroso-mysql"
    echo "  Logs:    docker logs linoroso-mysql"
    echo "  Shell:   docker exec -it linoroso-mysql mysql -uroot -plinoroso2024"
    echo ""
    echo "Next steps:"
    echo "1. Run: python3 test_setup.py"
    echo "2. Start automation: python3 content_engine.py"
else
    echo ""
    echo "❌ Setup failed"
    exit 1
fi
