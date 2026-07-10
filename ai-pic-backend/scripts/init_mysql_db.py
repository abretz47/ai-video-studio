#!/usr/bin/env python3
"""
MySQL database initialization script

Used to create the database and set basic configuration
"""

import logging
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pymysql
from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def parse_mysql_url(database_url: str):
    """Parse MySQL database URL"""
    import re

    pattern = r"mysql\+pymysql://([^:]+):([^@]+)@([^:]+):(\d+)/([^?]+)"
    match = re.match(pattern, database_url)

    if not match:
        raise ValueError(f"Unable to parse database URL: {database_url}")

    return {
        "user": match.group(1),
        "password": match.group(2),
        "host": match.group(3),
        "port": int(match.group(4)),
        "database": match.group(5),
    }


def create_database():
    """Create database"""
    try:
        # Parse database connection information
        db_config = parse_mysql_url(settings.DATABASE_URL)
        database_name = db_config.pop("database")

        logger.info(f"Connecting to MySQL server: {db_config['host']}:{db_config['port']}")

        # Connect to the MySQL server (without specifying a database)
        connection = pymysql.connect(**db_config)

        try:
            with connection.cursor() as cursor:
                # Check whether the database exists
                cursor.execute("SHOW DATABASES LIKE %s", (database_name,))
                if cursor.fetchone():
                    logger.info(f"Database '{database_name}' already exists")
                else:
                    # Create database
                    cursor.execute(
                        f"""
                        CREATE DATABASE `{database_name}`
                        CHARACTER SET utf8mb4
                        COLLATE utf8mb4_unicode_ci
                    """
                    )
                    logger.info(f"Database '{database_name}' created successfully")

                # Show database information
                cursor.execute(f"SHOW CREATE DATABASE `{database_name}`")
                result = cursor.fetchone()
                logger.info(f"Database configuration: {result[1]}")

                connection.commit()

        finally:
            connection.close()

        logger.info("Database initialization complete")
        return True

    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        return False


def test_connection():
    """Test database connection"""
    try:
        from app.core.database import engine

        logger.info("Test database connection...")

        # Test connection
        connection = engine.connect()
        connection.close()

        logger.info("Database connection test succeeded")
        return True

    except Exception as e:
        logger.error(f"Database connection test failed: {str(e)}")
        return False


def main():
    """Main function"""
    print("=" * 60)
    print("MySQL database initialization script")
    print("=" * 60)

    print(f"Project directory: {project_root}")
    print(f"Database URL: {settings.DATABASE_URL}")
    print()

    # Create database
    if not create_database():
        sys.exit(1)

    print()

    # Test connection
    if not test_connection():
        sys.exit(1)

    print()
    print("=" * 60)
    print("✅ Database initialization succeeded!")
    print()
    print("Next steps:")
    print("1. Run database migrations: alembic upgrade head")
    print("2. Or use the script: python migrate.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
