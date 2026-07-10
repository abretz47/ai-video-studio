#!/usr/bin/env python3
"""
Database migration management script

Usage:
    python migrate.py init          # Initialize migrations (first-time use only)
    python migrate.py generate      # Generate a new migration file
    python migrate.py upgrade       # Apply migrations to the database
    python migrate.py downgrade     # Roll back migrations
    python migrate.py current       # Show the current migration revision
    python migrate.py history       # Show migration history
    python migrate.py reset         # Reset the database (dangerous operation)
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd):
    """Run a command and return the result"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            return False
        if result.stdout:
            print(result.stdout)
        return True
    except Exception as e:
        print(f"Error while running command: {e}")
        return False


def init_migration():
    """Initialize migrations"""
    print("Initializing database migrations...")
    if not run_command("alembic stamp head"):
        print("Initialization failed")
        return False
    print("Migration initialization complete")
    return True


def generate_migration():
    """Generate a new migration file"""
    message = input("Enter a migration description (optional): ").strip()
    if message:
        cmd = f'alembic revision --autogenerate -m "{message}"'
    else:
        cmd = "alembic revision --autogenerate"

    print("Generating migration file...")
    if not run_command(cmd):
        print("Failed to generate migration file")
        return False
    print("Migration file generation complete")
    return True


def upgrade_database():
    """Apply migrations to the database"""
    print("Applying migrations to the database...")
    if not run_command("alembic upgrade head"):
        print("Failed to apply migrations")
        return False
    print("Migration application complete")
    return True


def downgrade_database():
    """Roll back migrations"""
    print("Warning: this will roll the database back to the previous revision!")
    confirm = input("Are you sure you want to continue? (y/N): ").strip().lower()
    if confirm != "y":
        print("Operation cancelled")
        return False

    print("Rolling back migrations...")
    if not run_command("alembic downgrade -1"):
        print("Failed to roll back migrations")
        return False
    print("Migration rollback complete")
    return True


def show_current():
    """Show current migration revision"""
    print("Current migration revision:")
    run_command("alembic current")


def show_history():
    """Show migration history"""
    print("Migration history:")
    run_command("alembic history")


def reset_database():
    """Reset database (dangerous operation)"""
    print("Warning: this will delete all data and reset the database!")
    confirm = input("Are you sure you want to continue? (y/N): ").strip().lower()
    if confirm != "y":
        print("Operation cancelled")
        return False

    double_confirm = input("Confirm again, this will delete all data! Type 'RESET' to confirm: ").strip()
    if double_confirm != "RESET":
        print("Operation cancelled")
        return False

    print("Resetting database...")
    # Roll back to the initial state
    if not run_command("alembic downgrade base"):
        print("Reset failed")
        return False

    # Reapply all migrations
    if not run_command("alembic upgrade head"):
        print("Failed to reapply migrations")
        return False

    print("Database reset complete")
    return True


def main():
    """Main function"""
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1].lower()

    # Ensure we are in the correct directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)

    commands = {
        "init": init_migration,
        "generate": generate_migration,
        "upgrade": upgrade_database,
        "downgrade": downgrade_database,
        "current": show_current,
        "history": show_history,
        "reset": reset_database,
    }

    if command not in commands:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)

    try:
        commands[command]()
    except KeyboardInterrupt:
        print("\nOperation interrupted by user")
    except Exception as e:
        print(f"Error while running command: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
