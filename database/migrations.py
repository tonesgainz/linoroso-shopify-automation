"""
Database Migration Manager
Handles database initialization, migrations, and version control
"""

import pymysql
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict
from loguru import logger
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from settings import config


class DatabaseMigration:
    """Manage database migrations and schema updates"""

    def __init__(self):
        self.db_config = {
            'host': config.database.host,
            'port': config.database.port,
            'user': config.database.user,
            'password': config.database.password,
            'charset': 'utf8mb4',
            'cursorclass': pymysql.cursors.DictCursor
        }

    def get_connection(self, database: Optional[str] = None):
        """Get database connection"""
        conn_config = self.db_config.copy()
        if database:
            conn_config['database'] = database
        return pymysql.connect(**conn_config)

    def database_exists(self) -> bool:
        """Check if database exists"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = %s",
                (config.database.database,)
            )
            result = cursor.fetchone()
            conn.close()
            return result is not None
        except Exception as e:
            logger.error(f"Error checking database existence: {e}")
            return False

    def create_database(self) -> bool:
        """Create the database if it doesn't exist"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            logger.info(f"Creating database: {config.database.database}")
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS {config.database.database} "
                f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )

            conn.commit()
            conn.close()

            logger.success(f"Database '{config.database.database}' created successfully")
            return True

        except Exception as e:
            logger.error(f"Error creating database: {e}")
            return False

    def run_schema_file(self, schema_path: Path) -> bool:
        """Run SQL schema file"""
        try:
            if not schema_path.exists():
                logger.error(f"Schema file not found: {schema_path}")
                return False

            logger.info(f"Running schema file: {schema_path}")

            with open(schema_path, 'r', encoding='utf-8') as f:
                schema_sql = f.read()

            # Split into individual statements
            statements = [s.strip() for s in schema_sql.split(';') if s.strip()]

            conn = self.get_connection(database=config.database.database)
            cursor = conn.cursor()

            success_count = 0
            error_count = 0

            for i, statement in enumerate(statements, 1):
                # Skip comments
                if statement.startswith('--') or statement.startswith('#'):
                    continue

                try:
                    cursor.execute(statement)
                    success_count += 1
                except Exception as e:
                    # Some errors are OK (like table already exists)
                    if 'already exists' not in str(e).lower():
                        logger.warning(f"Statement {i} warning: {e}")
                    error_count += 1

            conn.commit()
            conn.close()

            logger.success(
                f"Schema executed: {success_count} statements successful, "
                f"{error_count} skipped/warnings"
            )
            return True

        except Exception as e:
            logger.error(f"Error running schema file: {e}")
            return False

    def create_migration_table(self) -> bool:
        """Create migrations tracking table"""
        try:
            conn = self.get_connection(database=config.database.database)
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    version VARCHAR(100) NOT NULL UNIQUE,
                    description TEXT,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_version (version)
                ) ENGINE=InnoDB
            """)

            conn.commit()
            conn.close()

            logger.success("Migration tracking table created")
            return True

        except Exception as e:
            logger.error(f"Error creating migration table: {e}")
            return False

    def record_migration(self, version: str, description: str = "") -> bool:
        """Record a completed migration"""
        try:
            conn = self.get_connection(database=config.database.database)
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO schema_migrations (version, description) VALUES (%s, %s)",
                (version, description)
            )

            conn.commit()
            conn.close()

            logger.info(f"Recorded migration: {version}")
            return True

        except pymysql.IntegrityError:
            # Migration already recorded
            return True
        except Exception as e:
            logger.error(f"Error recording migration: {e}")
            return False

    def get_applied_migrations(self) -> List[str]:
        """Get list of applied migrations"""
        try:
            conn = self.get_connection(database=config.database.database)
            cursor = conn.cursor()

            cursor.execute("SELECT version FROM schema_migrations ORDER BY id")
            results = cursor.fetchall()

            conn.close()

            return [row['version'] for row in results]

        except Exception as e:
            logger.warning(f"Could not fetch migrations (might not be initialized): {e}")
            return []

    def initialize_database(self) -> bool:
        """Complete database initialization"""
        try:
            logger.info("Starting database initialization...")

            # Step 1: Create database
            if not self.database_exists():
                if not self.create_database():
                    return False
            else:
                logger.info(f"Database '{config.database.database}' already exists")

            # Step 2: Create migration tracking table
            if not self.create_migration_table():
                return False

            # Step 3: Run main schema
            schema_path = Path(__file__).parent / 'schema.sql'
            if not self.run_schema_file(schema_path):
                return False

            # Step 4: Record initial migration
            self.record_migration('001_initial_schema', 'Initial database schema')

            logger.success("✅ Database initialized successfully!")
            return True

        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            return False

    def verify_database(self) -> Dict[str, any]:
        """Verify database setup and return status"""
        try:
            conn = self.get_connection(database=config.database.database)
            cursor = conn.cursor()

            # Count tables
            cursor.execute("""
                SELECT COUNT(*) as table_count
                FROM information_schema.tables
                WHERE table_schema = %s
            """, (config.database.database,))
            table_count = cursor.fetchone()['table_count']

            # Get applied migrations
            cursor.execute("SELECT COUNT(*) as migration_count FROM schema_migrations")
            migration_count = cursor.fetchone()['migration_count']

            conn.close()

            status = {
                'database_exists': True,
                'table_count': table_count,
                'migration_count': migration_count,
                'healthy': table_count > 0
            }

            logger.info(f"Database verification: {status}")
            return status

        except Exception as e:
            logger.error(f"Error verifying database: {e}")
            return {
                'database_exists': False,
                'table_count': 0,
                'migration_count': 0,
                'healthy': False,
                'error': str(e)
            }

    def reset_database(self, confirm: bool = False) -> bool:
        """DANGER: Drop and recreate database"""
        if not confirm:
            logger.error("Must confirm database reset!")
            return False

        try:
            logger.warning(f"⚠️  RESETTING DATABASE: {config.database.database}")

            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute(f"DROP DATABASE IF EXISTS {config.database.database}")
            conn.commit()
            conn.close()

            logger.info("Database dropped, reinitializing...")
            return self.initialize_database()

        except Exception as e:
            logger.error(f"Error resetting database: {e}")
            return False


def main():
    """CLI interface for database management"""
    import argparse

    parser = argparse.ArgumentParser(description='Linoroso Database Migration Manager')
    parser.add_argument(
        'action',
        choices=['init', 'verify', 'reset'],
        help='Action to perform'
    )
    parser.add_argument(
        '--confirm',
        action='store_true',
        help='Confirm destructive actions like reset'
    )

    args = parser.parse_args()

    migration = DatabaseMigration()

    if args.action == 'init':
        logger.info("Initializing database...")
        success = migration.initialize_database()
        if success:
            status = migration.verify_database()
            print(f"\n✅ Database initialized successfully!")
            print(f"   Tables created: {status['table_count']}")
            print(f"   Migrations applied: {status['migration_count']}")
        else:
            print("\n❌ Database initialization failed!")
            sys.exit(1)

    elif args.action == 'verify':
        logger.info("Verifying database...")
        status = migration.verify_database()
        print(f"\n📊 Database Status:")
        print(f"   Exists: {status['database_exists']}")
        print(f"   Tables: {status['table_count']}")
        print(f"   Migrations: {status['migration_count']}")
        print(f"   Healthy: {'✅' if status['healthy'] else '❌'}")

    elif args.action == 'reset':
        if not args.confirm:
            print("\n⚠️  Database reset requires --confirm flag!")
            print("   This will DELETE ALL DATA!")
            sys.exit(1)

        print("\n⚠️  WARNING: This will delete all data!")
        response = input("Type 'DELETE' to confirm: ")

        if response == 'DELETE':
            success = migration.reset_database(confirm=True)
            if success:
                print("\n✅ Database reset and reinitialized!")
            else:
                print("\n❌ Database reset failed!")
                sys.exit(1)
        else:
            print("\n❌ Reset cancelled")
            sys.exit(0)


if __name__ == "__main__":
    main()
