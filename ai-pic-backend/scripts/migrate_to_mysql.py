#!/usr/bin/env python3
"""
Database migration script: migrate from SQLite to MySQL

This script migrates existing SQLite data to a MySQL database
"""

import logging
import sys
from pathlib import Path
from typing import Any, Dict

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import sqlite3

from app.core.config import settings
from sqlalchemy import create_engine, text

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def parse_mysql_url(database_url: str) -> Dict[str, Any]:
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


def find_sqlite_db() -> str:
    """Find the SQLite database file"""
    possible_paths = [
        project_root / "ai_pic.db",
        project_root / "app.db",
        project_root / "database.db",
    ]

    for path in possible_paths:
        if path.exists():
            return str(path)

    raise FileNotFoundError("SQLite database file not found")


def get_sqlite_tables(db_path: str) -> list:
    """Get the list of tables in the SQLite database"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    )
    tables = [row[0] for row in cursor.fetchall()]

    conn.close()
    return tables


def migrate_table_data(sqlite_path: str, table_name: str, mysql_engine):
    """Migrate data from a single table"""
    logger.info(f"Starting migration for table: {table_name}")

    # Connect to SQLite
    sqlite_conn = sqlite3.connect(sqlite_path)
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cursor = sqlite_conn.cursor()

    try:
        # Get SQLite table data
        sqlite_cursor.execute(f"SELECT * FROM {table_name}")
        rows = sqlite_cursor.fetchall()

        if not rows:
            logger.info(f"Table {table_name} has no data, skipping")
            return

        # Get column names
        column_names = [description[0] for description in sqlite_cursor.description]

        # Build MySQL insert statement
        placeholders = ", ".join(["%s"] * len(column_names))
        columns = ", ".join([f"`{col}`" for col in column_names])
        insert_sql = f"INSERT INTO `{table_name}` ({columns}) VALUES ({placeholders})"

        # Convert Row objects to tuples
        data_tuples = [tuple(row) for row in rows]

        # Insert into MySQL
        with mysql_engine.connect() as mysql_conn:
            # Clear the target table (optional)
            mysql_conn.execute(text(f"DELETE FROM `{table_name}`"))

            # Insert data in batches
            mysql_conn.execute(text(insert_sql), data_tuples)
            mysql_conn.commit()

        logger.info(f"Table {table_name} migration complete, migrated {len(data_tuples)} records")

    except Exception as e:
        logger.error(f"Failed to migrate table {table_name}: {str(e)}")
        raise

    finally:
        sqlite_conn.close()


def main():
    """Main function"""
    print("=" * 60)
    print("SQLite to MySQL data migration script")
    print("=" * 60)

    try:
        # Find the SQLite database
        sqlite_path = find_sqlite_db()
        logger.info(f"Found SQLite database: {sqlite_path}")

        # Create MySQL engine
        mysql_engine = create_engine(settings.DATABASE_URL)
        logger.info(f"Connected to MySQL: {settings.DATABASE_URL}")

        # Test MySQL connection
        with mysql_engine.connect() as conn:
            result = conn.execute(text("SELECT VERSION()"))
            version = result.fetchone()[0]
            logger.info(f"MySQL version: {version}")

        # Get SQLite table list
        tables = get_sqlite_tables(sqlite_path)
        logger.info(f"Found {len(tables)} tables: {', '.join(tables)}")

        # Confirm whether to continue
        response = input(
            "\n是否继续迁移数据到MySQL？这将清空现有MySQL表中的数据。(y/N): "
        )
        if response.lower() != "y":
            logger.info("Migration cancelled")
            return

        # Migrate each table
        success_count = 0
        for table in tables:
            try:
                migrate_table_data(sqlite_path, table, mysql_engine)
                success_count += 1
            except Exception as e:
                logger.error(f"Skipping table {table}: {str(e)}")
                continue

        print()
        print("=" * 60)
        print("✅ Data migration complete!")
        print(f"Successfully migrated {success_count}/{len(tables)} tables")
        print("=" * 60)

    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
