"""
Database migration CLI commands

A database migration command-line tool integrated with the FastAPI architecture
"""

import logging
import sys
from pathlib import Path
from typing import Optional

import click

# Add the project root directory to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.core.config import settings  # noqa: E402
from app.core.migrations import (  # noqa: E402
    MigrationError,
    data_seeder,
    migration_manager,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@click.group()
def migration():
    """Database migration management commands."""
    pass


@migration.command(name="create")
@click.option("--message", "-m", required=True, help="Migration description")
@click.option("--autogenerate/--no-autogenerate", default=True, help="Whether to auto-generate the migration")
def create_migration_command(message: str, autogenerate: bool):
    """Create a new database migration."""
    try:
        click.echo(f"🔄 Creating migration: {message}")
        click.echo(f"Autogenerate: {'yes' if autogenerate else 'no'}")

        revision = migration_manager.create_migration(message, autogenerate)

        click.echo("✅ Migration created successfully")
        click.echo(f"Revision ID: {revision}")

        # Show schema differences
        if autogenerate:
            diff = migration_manager.get_schema_diff()
            if diff.get("has_changes"):
                click.echo(f"Detected {diff['change_count']} changes")
                for change in diff["changes"][:5]:  # Only show the first 5 changes
                    click.echo(f"  - {change}")
                if diff["change_count"] > 5:
                    click.echo(f"  ... and {diff['change_count'] - 5} more changes")
            else:
                click.echo("⚠️  No schema changes detected")

    except MigrationError as e:
        click.echo(f"❌ Migration creation failed: {e}", err=True)
        sys.exit(1)


@migration.command()
@click.option("--revision", "-r", default="head", help="Target revision, defaults to the latest revision")
@click.option("--backup/--no-backup", default=True, help="Whether to back up the database before upgrade")
@click.option("--validate/--no-validate", default=True, help="Whether to validate migration files")
def upgrade(revision: str, backup: bool, validate: bool):
    """Upgrade the database to the specified revision."""
    try:
        click.echo(f"🔄 Upgrading database to revision: {revision}")

        # Check current status
        status = migration_manager.check_migration_status()
        click.echo(f"Current revision: {status['current_revision']}")
        click.echo(
            f"Target revision: {status['head_revision'] if revision == 'head' else revision}"
        )

        if not status["needs_upgrade"] and revision == "head":
            click.echo("✅ Database is already at the latest revision")
            return

        # Validate migration files
        if validate:
            click.echo("🔍 Validating migration files...")
            validation = migration_manager.validate_migrations()
            if not validation["valid"]:
                click.echo("❌ Migration file validation failed:")
                for error in validation["errors"]:
                    click.echo(f"  - {error}")
                sys.exit(1)

            if validation["warnings"]:
                click.echo("⚠️  Migration file warnings:")
                for warning in validation["warnings"]:
                    click.echo(f"  - {warning}")

        # Back up the database
        if backup and "mysql" in settings.DATABASE_URL:
            click.echo("💾 Creating database backup...")
            backup_file = migration_manager.backup_before_migration()
            if backup_file:
                click.echo(f"✅ Backup successful: {backup_file}")
            else:
                click.echo("⚠️  Backup failed, but continuing with migration")

        # Confirm the upgrade
        if not click.confirm("Confirm database upgrade?"):
            click.echo("Operation cancelled")
            return

        # Execute the upgrade
        migration_manager.upgrade(revision)
        click.echo("✅ Database upgrade successful")

        # Show the new status
        new_status = migration_manager.check_migration_status()
        click.echo(f"New revision: {new_status['current_revision']}")

    except MigrationError as e:
        click.echo(f"❌ Database upgrade failed: {e}", err=True)
        sys.exit(1)


@migration.command()
@click.option("--revision", "-r", required=True, help="Target revision")
@click.option("--backup/--no-backup", default=True, help="Whether to back up the database before downgrade")
def downgrade(revision: str, backup: bool):
    """Downgrade the database to the specified revision."""
    try:
        click.echo(f"🔄 Downgrading database to revision: {revision}")

        # Check current status
        status = migration_manager.check_migration_status()
        click.echo(f"Current revision: {status['current_revision']}")

        # Warning message
        click.echo("⚠️  Warning: Downgrading the database may cause data loss!")

        # Back up the database
        if backup and "mysql" in settings.DATABASE_URL:
            click.echo("💾 Creating database backup...")
            backup_file = migration_manager.backup_before_migration()
            if backup_file:
                click.echo(f"✅ Backup successful: {backup_file}")
            else:
                click.echo("❌ Backup failed")
                if not click.confirm("Backup failed. Continue with downgrade?"):
                    sys.exit(1)

        # Confirm the downgrade
        if not click.confirm("Confirm database downgrade? This may cause data loss!"):
            click.echo("Operation cancelled")
            return

        # Execute the downgrade
        migration_manager.downgrade(revision)
        click.echo("✅ Database downgrade successful")

        # Show the new status
        new_status = migration_manager.check_migration_status()
        click.echo(f"New revision: {new_status['current_revision']}")

    except MigrationError as e:
        click.echo(f"❌ Database downgrade failed: {e}", err=True)
        sys.exit(1)


@migration.command()
def status():
    """Show database migration status."""
    try:
        click.echo("📊 Database migration status")
        click.echo("=" * 50)

        status = migration_manager.check_migration_status()

        click.echo(f"Database URL: {settings.DATABASE_URL}")
        click.echo(f"Database exists: {'✅' if status['database_exists'] else '❌'}")
        click.echo(f"Current revision: {status['current_revision'] or 'Not initialized'}")
        click.echo(f"Latest revision: {status['head_revision'] or 'No migration files'}")
        click.echo(f"Status: {'✅ Up to date' if status['is_up_to_date'] else '⚠️  Upgrade required'}")

        if status.get("pending_migrations"):
            click.echo(f"Pending migrations: {status['pending_count']}")
            for migration in status["pending_migrations"][:5]:
                click.echo(f"  - {migration}")
            if status["pending_count"] > 5:
                click.echo(f"  ... and {status['pending_count'] - 5} more")

        # Show schema differences
        diff = migration_manager.get_schema_diff()
        if diff.get("has_changes"):
            click.echo(f"Uncommitted changes: {diff['change_count']}")
            click.echo("💡 Tip: Run 'migration create' to create a new migration")

    except Exception as e:
        click.echo(f"❌ Failed to retrieve status: {e}", err=True)


@migration.command()
def history():
    """Show migration history."""
    try:
        click.echo("📜 Migration history")
        click.echo("=" * 80)

        history = migration_manager.get_migration_history()
        current = migration_manager.get_current_revision()

        if not history:
            click.echo("No migration history")
            return

        for migration in history:
            is_current = migration["revision"] == current
            status_icon = "👉" if is_current else "  "

            click.echo(f"{status_icon} {migration['revision']}")
            click.echo(f"   Message: {migration['message'] or 'No description'}")
            click.echo(f"   Parent: {migration['down_revision'] or 'None'}")
            if migration.get("create_date"):
                click.echo(f"   Date: {migration['create_date']}")
            click.echo()

    except Exception as e:
        click.echo(f"❌ Failed to retrieve history: {e}", err=True)


@migration.command()
def validate():
    """Validate migration file integrity."""
    try:
        click.echo("🔍 Validating migration files...")

        validation = migration_manager.validate_migrations()

        if validation["valid"]:
            click.echo("✅ All migration files passed validation")
        else:
            click.echo("❌ Migration file validation failed:")
            for error in validation["errors"]:
                click.echo(f"  - {error}")

        if validation["warnings"]:
            click.echo("⚠️  Warnings:")
            for warning in validation["warnings"]:
                click.echo(f"  - {warning}")

        # Check schema differences
        diff = migration_manager.get_schema_diff()
        if diff.get("has_changes"):
            click.echo(f"⚠️  Detected {diff['change_count']} uncommitted schema changes")
            click.echo("💡 Suggestion: Run 'migration create' to create a new migration")

    except Exception as e:
        click.echo(f"❌ Validation failed: {e}", err=True)


@migration.command()
@click.option("--revision", "-r", required=True, help="Revision to stamp")
def stamp(revision: str):
    """Stamp the database revision without running migrations."""
    try:
        click.echo(f"🏷️  Stamping database revision: {revision}")

        if not click.confirm("Confirm stamping this revision? This will not execute actual migration operations"):
            click.echo("Operation cancelled")
            return

        migration_manager.stamp(revision)
        click.echo(f"✅ Revision stamped successfully: {revision}")

    except MigrationError as e:
        click.echo(f"❌ Revision stamping failed: {e}", err=True)
        sys.exit(1)


# Data seed commands
@click.group()
def seed():
    """Data seed management commands."""
    pass


@seed.command(name="create")
@click.option("--name", "-n", required=True, help="Seed name")
def create_seed_command(name: str):
    """Create a data seed file."""
    try:
        click.echo(f"🌱 Creating seed file: {name}")

        seed_file = data_seeder.create_seed_file(name)
        click.echo(f"✅ Seed file created successfully: {seed_file}")
        click.echo("💡 Please edit the file to add seed data")

    except Exception as e:
        click.echo(f"❌ Seed file creation failed: {e}", err=True)
        sys.exit(1)


@seed.command()
@click.option("--name", "-n", help="Specify a seed name")
@click.option("--all", "run_all", is_flag=True, help="Run all seeds")
def run(name: Optional[str], run_all: bool):
    """Run data seeds."""
    try:
        if run_all:
            click.echo("🌱 Running all seeds...")
            count = data_seeder.run_all_seeds()
            click.echo(f"✅ Successfully ran {count} seeds")
        elif name:
            click.echo(f"🌱 Running seed: {name}")
            data_seeder.run_seed(name)
            click.echo(f"✅ Seed ran successfully: {name}")
        else:
            click.echo("❌ Please specify a seed name or use --all to run all seeds")
            sys.exit(1)

    except Exception as e:
        click.echo(f"❌ Seed execution failed: {e}", err=True)
        sys.exit(1)


# Main command group
@click.group()
def cli():
    """AI Video Studio database management tool."""
    pass


cli.add_command(migration)
cli.add_command(seed)

if __name__ == "__main__":
    cli()
