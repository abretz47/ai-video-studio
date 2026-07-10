#!/usr/bin/env python3
"""
MySQL database migration management script

Provides database creation, migration, rollback, and related features
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def run_command(cmd: str, description: str = "") -> bool:
    """Run a command and return the result"""
    if description:
        print(f"\n{'='*60}")
        print(f"🔄 {description}")
        print(f"{'='*60}")

    print(f"Running command: {cmd}")

    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if result.stdout:
            print(result.stdout)

        if result.stderr:
            print(f"Error output: {result.stderr}")

        if result.returncode != 0:
            print(f"❌ Command failed with exit code: {result.returncode}")
            return False
        else:
            print("✅ Command succeeded")
            return True

    except Exception as e:
        print(f"❌ Error while running command: {e}")
        return False


def init_database():
    """Initialize database"""
    try:
        print("=" * 60)
        print("Initialize MySQL database")
        print("=" * 60)

        # Run the database initialization script
        if not os.path.exists("scripts/init_mysql_db.py"):
            print("❌ Database initialization script not found")
            return False

        return run_command("python scripts/init_mysql_db.py", "Initialize database")

    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        return False


def create_migration(message: str):
    """Create a new migration file"""
    if not message:
        print("❌ Please provide a migration message")
        return False

    cmd = f'alembic revision --autogenerate -m "{message}"'
    return run_command(cmd, f"Create migration: {message}")


def upgrade_database(revision: str = "head"):
    """Upgrade the database to the specified revision"""
    cmd = f"alembic upgrade {revision}"
    return run_command(cmd, f"Upgrade database to revision: {revision}")


def downgrade_database(revision: str):
    """Downgrade the database to the specified revision"""
    if not revision:
        print("❌ Please provide the target downgrade revision")
        return False

    cmd = f"alembic downgrade {revision}"
    return run_command(cmd, f"Downgrade database to revision: {revision}")


def show_current_revision():
    """Show current database revision"""
    return run_command("alembic current", "Show current database revision")


def show_migration_history():
    """Show migration history"""
    return run_command("alembic history", "Show migration history")


def show_migration_heads():
    """Show migration heads"""
    return run_command("alembic heads", "Show migration heads")


def test_connection():
    """Test database connection"""
    if not os.path.exists("test_mysql_connection.py"):
        print("❌ Database connection test script not found")
        return False

    return run_command("python test_mysql_connection.py", "Test database connection")


def migrate_from_sqlite():
    """Migrate data from SQLite"""
    if not os.path.exists("scripts/migrate_to_mysql.py"):
        print("❌ SQLite migration script not found")
        return False

    return run_command("python scripts/migrate_to_mysql.py", "Migrate data from SQLite")


def reset_database():
    """Reset database (dangerous operation)"""
    response = input("⚠️  This will delete all data and recreate the schema. Are you sure you want to continue? (y/N): ")
    if response.lower() != "y":
        print("Operation cancelled")
        return False

    success = True

    # Downgrade to base
    if not downgrade_database("base"):
        success = False

    # Upgrade back to head
    if success and not upgrade_database("head"):
        success = False

    return success


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="MySQL database migration management script")
    parser.add_argument(
        "command",
        choices=[
            "init",
            "create",
            "upgrade",
            "downgrade",
            "current",
            "history",
            "heads",
            "test",
            "migrate",
            "reset",
        ],
        help="Command to execute",
    )
    parser.add_argument("--message", "-m", help="Migration message (for the create command)")
    parser.add_argument(
        "--revision", "-r", help="Target revision (for the upgrade/downgrade commands)"
    )

    args = parser.parse_args()

    print("=" * 60)
    print("MySQL database migration management")
    print("=" * 60)
    print(f"Project directory: {project_root}")
    print(f"Command: {args.command}")
    print()

    success = True

    if args.command == "init":
        success = init_database()
    elif args.command == "create":
        if not args.message:
            print("❌ Creating a migration requires a message. Use --message or -m")
            success = False
        else:
            success = create_migration(args.message)
    elif args.command == "upgrade":
        revision = args.revision or "head"
        success = upgrade_database(revision)
    elif args.command == "downgrade":
        if not args.revision:
            print("❌ Downgrade requires a target revision. Use --revision or -r")
            success = False
        else:
            success = downgrade_database(args.revision)
    elif args.command == "current":
        success = show_current_revision()
    elif args.command == "history":
        success = show_migration_history()
    elif args.command == "heads":
        success = show_migration_heads()
    elif args.command == "test":
        success = test_connection()
    elif args.command == "migrate":
        success = migrate_from_sqlite()
    elif args.command == "reset":
        success = reset_database()

    if success:
        print("\n🎉 Operation completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Operation failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
