#!/usr/bin/env python3
"""
Django-style management script

Provides a unified CLI interface for managing the FastAPI application
"""

import sys
from pathlib import Path

import click

# Add the project root directory to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.core.config import settings


@click.group(invoke_without_command=True)
@click.pass_context
def manage(ctx):
    """AI Video Studio management tool."""
    if ctx.invoked_subcommand is None:
        click.echo("🎬 AI Video Studio Management Tool")
        click.echo("=" * 50)
        click.echo(f"Project: {settings.PROJECT_NAME}")
        click.echo(f"Version: {settings.VERSION}")
        click.echo(
            f"Database: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else 'SQLite'}"
        )
        click.echo()
        click.echo("Available commands:")
        click.echo("  migration  - Database migration management")
        click.echo("  seed      - Data seed management")
        click.echo("  server    - Server management")
        click.echo("  dev       - Development tools")
        click.echo()
        click.echo("Use 'python manage.py <command> --help' to view detailed help")


# Add migration command groups
from app.cli.migration_commands import migration, seed

manage.add_command(migration)
manage.add_command(seed)


# Server management commands
@manage.group()
def server():
    """Server management commands."""
    pass


@server.command()
@click.option("--host", default="0.0.0.0", help="Server host address")
@click.option("--port", default=8000, help="Server port")
@click.option("--reload/--no-reload", default=True, help="Whether to enable hot reload")
@click.option("--workers", default=1, help="Number of worker processes")
def run(host: str, port: int, reload: bool, workers: int):
    """Start the development server."""
    import uvicorn

    click.echo(f"🚀 Starting server: http://{host}:{port}")
    click.echo(f"Hot reload: {'enabled' if reload else 'disabled'}")
    click.echo(f"Worker processes: {workers}")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        workers=workers if not reload else 1,
        log_level="info",
    )


@server.command()
@click.option("--host", default="0.0.0.0", help="Server host address")
@click.option("--port", default=8000, help="Server port")
@click.option("--workers", default=4, help="Number of worker processes")
def production(host: str, port: int, workers: int):
    """Start the production server."""
    import uvicorn

    click.echo(f"🏭 Starting production server: http://{host}:{port}")
    click.echo(f"Worker processes: {workers}")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        workers=workers,
        log_level="warning",
        access_log=True,
    )


# Development tool commands
@manage.group()
def dev():
    """Development tool commands."""
    pass


@dev.command()
def check():
    """Check project configuration and dependencies."""
    click.echo("🔍 Checking project configuration...")

    issues = []

    # Check environment variables
    if settings.SECRET_KEY == "your-secret-key-here":
        issues.append("⚠️  SECRET_KEY is using the default value; please change it")

    # Check database connection
    try:
        from app.core.migrations import migration_manager

        status = migration_manager.check_migration_status()
        if not status["database_exists"]:
            issues.append("❌ Database connection failed")
        elif not status["is_up_to_date"]:
            issues.append("⚠️  Database needs to be upgraded")
        else:
            click.echo("✅ Database connection is healthy")
    except Exception as e:
        issues.append(f"❌ Database check failed: {e}")

    # Check required files
    required_files = [
        "requirements.txt",
        "alembic.ini",
        "app/core/config.py",
        "app/models/__init__.py",
    ]

    for file_path in required_files:
        if not Path(file_path).exists():
            issues.append(f"❌ Missing file: {file_path}")

    # Check directory structure
    required_dirs = ["app/api", "app/core", "app/models", "alembic/versions"]

    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            issues.append(f"❌ Missing directory: {dir_path}")

    if issues:
        click.echo("\nThe following issues were found:")
        for issue in issues:
            click.echo(f"  {issue}")
        click.echo(f"\nA total of {len(issues)} issues were found")
    else:
        click.echo("✅ Project configuration check passed")


@dev.command()
def test():
    """Run tests."""
    import subprocess

    click.echo("🧪 Running tests...")

    try:
        result = subprocess.run(
            [sys.executable, "run_tests.py", "quick"], capture_output=True, text=True
        )

        click.echo(result.stdout)
        if result.stderr:
            click.echo(result.stderr)

        if result.returncode == 0:
            click.echo("✅ Tests passed")
        else:
            click.echo("❌ Tests failed")
            sys.exit(1)

    except FileNotFoundError:
        click.echo("❌ Could not find the test script run_tests.py")
        sys.exit(1)


@dev.command()
def lint():
    """Run code quality checks."""
    import subprocess

    click.echo("🔍 Running code quality checks...")

    commands = [
        (
            "flake8",
            ["flake8", "app/", "--max-line-length=88", "--extend-ignore=E203,W503"],
        ),
        ("black", ["black", "--check", "app/"]),
        ("isort", ["isort", "--check-only", "app/"]),
    ]

    all_passed = True

    for name, cmd in commands:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                click.echo(f"✅ {name} check passed")
            else:
                click.echo(f"❌ {name} check failed:")
                click.echo(result.stdout)
                all_passed = False
        except FileNotFoundError:
            click.echo(f"⚠️  {name} is not installed, skipping check")

    if all_passed:
        click.echo("✅ All code quality checks passed")
    else:
        click.echo("❌ Code quality checks found issues; please fix them and try again")
        sys.exit(1)


@dev.command()
def format():
    """Format code."""
    import subprocess

    click.echo("🎨 Formatting code...")

    commands = [("isort", ["isort", "app/"]), ("black", ["black", "app/"])]

    for name, cmd in commands:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                click.echo(f"✅ {name} formatting completed")
            else:
                click.echo(f"❌ {name} formatting failed:")
                click.echo(result.stderr)
        except FileNotFoundError:
            click.echo(f"⚠️  {name} is not installed, skipping formatting")


@dev.command()
def shell():
    """Start an interactive Python shell."""
    import code

    # Import commonly used modules
    import sys

    sys.path.insert(0, str(project_root))

    import app.models
    from app.core.config import settings
    from app.core.database import SessionLocal, engine

    click.echo("🐍 Starting Python shell...")
    click.echo("Imported modules:")
    click.echo("  - SessionLocal, engine (database)")
    click.echo("  - settings (configuration)")
    click.echo("  - all models (from app.models import *)")
    click.echo()

    # Create a database session
    db = SessionLocal()

    # Start the interactive shell
    code.interact(
        banner="AI Video Studio Development Shell",
        local={"db": db, "engine": engine, "settings": settings, "models": app.models},
    )


# Shortcut command
@manage.command()
def quickstart():
    """Quickly start the project."""
    click.echo("🚀 Starting the project quickly...")

    # Check the database
    try:
        from app.core.migrations import migration_manager

        status = migration_manager.check_migration_status()

        if not status["database_exists"]:
            click.echo("📦 Initializing database...")
            if click.confirm("The database does not exist. Would you like to create it?"):
                # The database initialization script can be called here
                pass

        if not status["is_up_to_date"]:
            click.echo("🔄 Upgrading database...")
            if click.confirm("The database needs to be upgraded. Continue?"):
                migration_manager.upgrade()

    except Exception as e:
        click.echo(f"❌ Database check failed: {e}")
        return

    # Start the server
    click.echo("🚀 Starting development server...")
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    manage()
