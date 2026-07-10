"""
Jian Hua migration test
"""

import os
import tempfile

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text


def _resolve_upgrade_target(db_url: str) -> str:
 """Resolve the Alembic upgrade target for the given database URL.

 The project primarily targets MySQL in production. Some later migrations use
 MySQL-only DDL (e.g. type/constraint alterations) that SQLite can't execute.
 For the SQLite-based unit suite, we validate a compatible prefix of the
 migration history.
 """

 if db_url.startswith("sqlite:"):
 return "0002_add_user_management_fields"
 return "head"


@pytest.mark.integration
def test_migration_basic():
 """test Ji Ben migration function"""
 # create temporary database file
 db_fd, db_path = tempfile.mkstemp(suffix=".db")
 os.close(db_fd) # close file Miao Shu Fu

 try:
 db_url = f"sqlite:///{db_path}"

 # configurationAlembic
 alembic_cfg = Config("alembic.ini")
 alembic_cfg.set_main_option("sqlalchemy.url", db_url)

 # Yun Xing Qian Yi
 command.upgrade(alembic_cfg, _resolve_upgrade_target(db_url))

 # Jian Cha Biao Shi Fou exists
 engine = create_engine(db_url)
 inspector = inspect(engine)
 tables = inspector.get_table_names()
 engine.dispose()

 # validate key table exists
 expected_tables = ["users", "virtual_ips", "stories", "alembic_version"]
 for table in expected_tables:
 assert table in tables, f"Table {table} not found in {tables}"

 finally:
 # clean up Lin Shi Wen Jian
 if os.path.exists(db_path):
 try:
 os.unlink(db_path)
 except PermissionError:
 pass # Hu Lve permission error


@pytest.mark.integration
def test_migration_sqlite_compatibility():
 """testSQLiteJian Rong Xing"""
 # create temporary database file
 db_fd, db_path = tempfile.mkstemp(suffix=".db")
 os.close(db_fd) # close file Miao Shu Fu

 try:
 db_url = f"sqlite:///{db_path}"

 # configurationAlembic
 alembic_cfg = Config("alembic.ini")
 alembic_cfg.set_main_option("sqlalchemy.url", db_url)

 # Yun Xing Qian Yi
 command.upgrade(alembic_cfg, _resolve_upgrade_target(db_url))

 # create Yin Qing He connection
 engine = create_engine(db_url)

 # Ce Shi Ji BenSQLoperation
 with engine.connect() as conn:
 # test Cha Ru user
 conn.execute(
 text(
 """
 INSERT INTO users (username, email, hashed_password, full_name, is_active, is_superuser)
 VALUES ('testuser', 'test@example.com', 'hashed_password', 'Test User', 1, 0)
 """
)
)
 conn.commit()

 # test Cha Xun user
 result = conn.execute(
 text("SELECT username FROM users WHERE username = 'testuser'")
)
 user = result.fetchone()
 assert user is not None
 assert user[0] == "testuser"

 # testJSONLie(Ru Guo Zhi Chi)
 conn.execute(
 text(
 """
 INSERT INTO virtual_ips (name, description, tags, is_active, is_public)
 VALUES ('Test IP', 'Test description', '["tag1", "tag2"]', 1, 0)
 """
)
)
 conn.commit()

 result = conn.execute(
 text("SELECT tags FROM virtual_ips WHERE name = 'Test IP'")
)
 tags = result.fetchone()
 assert tags is not None

 engine.dispose()

 finally:
 # clean up Lin Shi Wen Jian
 if os.path.exists(db_path):
 try:
 os.unlink(db_path)
 except PermissionError:
 pass # Hu Lve permission error


@pytest.mark.integration
def test_migration_downgrade():
 """test migration Hui Tui"""
 # create temporary database file
 db_fd, db_path = tempfile.mkstemp(suffix=".db")
 os.close(db_fd) # close file Miao Shu Fu

 try:
 db_url = f"sqlite:///{db_path}"

 # configurationAlembic
 alembic_cfg = Config("alembic.ini")
 alembic_cfg.set_main_option("sqlalchemy.url", db_url)

 # Yun Xing Qian Yi
 command.upgrade(alembic_cfg, _resolve_upgrade_target(db_url))

 # Jian Cha Biao exists
 engine = create_engine(db_url)
 inspector = inspect(engine)
 tables_before = inspector.get_table_names()
 assert "users" in tables_before
 engine.dispose()

 # Hui Tui Qian Yi
 command.downgrade(alembic_cfg, "base")

 # Jian Cha Biao Bei delete
 engine = create_engine(db_url)
 inspector = inspect(engine)
 tables_after = inspector.get_table_names()

 # only Ying Gai Sheng Xiaalembic_versiontable
 assert "users" not in tables_after
 assert "virtual_ips" not in tables_after

 engine.dispose()

 finally:
 # clean up Lin Shi Wen Jian
 if os.path.exists(db_path):
 try:
 os.unlink(db_path)
 except PermissionError:
 pass # Hu Lve permission error
