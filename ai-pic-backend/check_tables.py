#!/usr/bin/env python3
from sqlalchemy import create_engine, inspect, text

# Check the existing database
engine = create_engine("sqlite:///./ai_pic.db")
inspector = inspect(engine)
tables = inspector.get_table_names()

print("Tables in the existing database:")
for table in tables:
    print(f"  - {table}")

if not tables:
    print("  No tables found")

# Check Alembic revision
with engine.connect() as conn:
    try:
        result = conn.execute(text("SELECT version_num FROM alembic_version"))
        version = result.scalar()
        print(f"Current revision: {version}")
    except Exception as e:
        print(f"Error while checking revision: {e}")

engine.dispose()

import os

# Check the temporary database
import tempfile

db_fd, db_path = tempfile.mkstemp(suffix=".db")
os.close(db_fd)

try:
    from alembic import command
    from alembic.config import Config

    db_url = f"sqlite:///{db_path}"
    print(f"\nTest database: {db_url}")

    # Configure Alembic
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", db_url)

    # Check the state before migrations
    print("Checking before migration...")
    engine = create_engine(db_url)
    inspector = inspect(engine)
    tables_before = inspector.get_table_names()
    print(f"Tables before migration: {tables_before}")
    engine.dispose()

    # Run migrations
    print("Running migrations...")
    try:
        command.upgrade(alembic_cfg, "head")
        print("Migration complete")
    except Exception as e:
        print(f"Migration failed: {e}")
        import traceback

        traceback.print_exc()

    # Check the state after migrations
    print("Checking after migration...")
    engine = create_engine(db_url)
    inspector = inspect(engine)
    tables_after = inspector.get_table_names()

    print("Tables after migration:")
    for table in tables_after:
        print(f"  - {table}")

    if not tables_after:
        print("  No tables found")

    # Check the Alembic revision table
    with engine.connect() as conn:
        try:
            result = conn.execute(text("SELECT version_num FROM alembic_version"))
            version = result.scalar()
            print(f"New database revision: {version}")
        except Exception as e:
            print(f"Error while checking new database revision: {e}")

    engine.dispose()

finally:
    if os.path.exists(db_path):
        try:
            os.unlink(db_path)
        except:
            pass
