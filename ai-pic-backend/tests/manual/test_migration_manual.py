#!/usr/bin/env python3
import os
import tempfile

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect

# create temporary database
db_fd, db_path = tempfile.mkstemp(suffix=".db")
os.close(db_fd)

try:
    db_url = f"sqlite:///{db_path}"
    print(f"test database: {db_url}")

    # configurationAlembic
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", db_url)

    print("run migration...")

    # Shou Dong run migration Jiao Ben

    # create Yin Qing
    engine = create_engine(db_url)

    # Shou Dong create Biao
    print("Shou Dong create Biao...")
    from app.core.database import Base

    Base.metadata.create_all(engine)

    # Jian Cha Biao
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    print("Shou Dong create after Biao:")
    for table in tables:
        print(f"  - {table}")

    engine.dispose()

    # Xian Zai Chang Shi Yongalembicescalate
    print("\nXian Zai Chang Shialembicescalate...")
    try:
        command.upgrade(alembic_cfg, "head")
        print("Alembicescalate Cheng Gong")
    except Exception as e:
        print(f"Alembicescalate failed: {e}")
        import traceback

        traceback.print_exc()

    # Zai Ci Jian Cha Biao
    engine = create_engine(db_url)
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    print("Alembicescalate after Biao:")
    for table in tables:
        print(f"  - {table}")

    engine.dispose()

finally:
    if os.path.exists(db_path):
        try:
            os.unlink(db_path)
        except:
            pass
